# app/main.py
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.settings import SOLR_CONFIG, settings
from app.core.logging import get_logger, setup_logging

# Point d'initialisation unique du logging — avant tout autre import applicatif
setup_logging(settings.log_level)
logger = get_logger(__name__)

from app.api.auth import router as auth_router
from app.api.v1.saved_searches import router as saved_searches_router
from app.core.env_validation import validate_environment
from app.core.exceptions import SolrInvalidQueryError, SolrTimeoutError, SolrUnavailableError
from app.models import DocsPermissionsResponse
from app.models.search_models import (
    FacetsConfigResponse,
    SearchRequest,
    SearchResponse,
    SuggestResponse,
)
from app.services.cache_service import cache_service
from app.services.interfaces import ISearchBuilder, ISearchService, ISolrClient
from app.services.search_builder import SearchBuilder
from app.services.search_service import PermissionsService, SearchService, SuggestService
from app.services.solr_client import SolrClient

# Validation de l'environnement au démarrage
try:
    env_config = validate_environment()
    logger.info("Environment validation completed successfully")
except Exception as e:
    logger.critical(f"Environment validation failed: {e}")
    raise

app = FastAPI()

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Événements de démarrage et arrêt
@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage de l'application"""
    await cache_service.connect()
    logger.info("Application startup completed")

@app.on_event("shutdown")
async def shutdown_event():
    """Nettoyage à l'arrêt de l'application"""
    await cache_service.disconnect()
    logger.info("Application shutdown completed")

# Instrumentation Prometheus pour les métriques
instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_respect_env_var=False,
    should_instrument_requests_inprogress=True,
    excluded_handlers=["/health"],
    inprogress_name="http_requests_inprogress",
    inprogress_labels=True,
)
instrumentator.instrument(app).expose(app, endpoint="/metrics")
logger.info("Prometheus metrics enabled at /metrics")

# Configuration CORS sécurisée basée sur l'environnement
if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
        expose_headers=settings.cors_expose_headers,
        max_age=settings.cors_max_age,
    )

    logger.info(
        f"CORS configured for environment '{settings.environment}': {settings.cors_origins}"
    )
else:
    logger.warning("No CORS origins configured. CORS middleware not added.")

# Redirection HTTPS en production
if settings.enable_https_redirect:
    app.add_middleware(HTTPSRedirectMiddleware)
    logger.info("HTTPS redirect middleware enabled")

# Protection contre les attaques DNS rebinding
if settings.trusted_hosts:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.trusted_hosts
    )
    logger.info(f"Trusted hosts configured: {settings.trusted_hosts}")

# Includes des routers
app.include_router(auth_router)
app.include_router(saved_searches_router)

# --- Injection de Dépendance ---

def get_solr_client() -> ISolrClient:
    """ Fournit une instance du client Solr """
    return SolrClient(base_url=SOLR_CONFIG['base_url'])

def get_search_builder() -> ISearchBuilder:
    """ Fournit une instance du SearchBuilder """
    return SearchBuilder(solr_base_url=SOLR_CONFIG['base_url'])

def get_search_service(
    builder: ISearchBuilder = Depends(get_search_builder),
    solr_client: ISolrClient = Depends(get_solr_client)
) -> ISearchService:
    """ Fournit une instance du service de recherche """
    return SearchService(builder, solr_client)

def get_suggest_service(
    builder: ISearchBuilder = Depends(get_search_builder),
    solr_client: ISolrClient = Depends(get_solr_client)
) -> SuggestService:
    """ Fournit une instance du service de suggestion """
    return SuggestService(builder, solr_client)

def get_permissions_service(
    solr_client: ISolrClient = Depends(get_solr_client)
) -> PermissionsService:
    """ Fournit une instance du service de permissions """
    return PermissionsService(solr_client)

# --- Endpoint ---

@app.get("/permissions")
@limiter.limit("15/minute")
async def get_document_permissions(
    request: Request,
    urls: str = Query(..., description="Liste des URLs de documents séparées par des virgules"),
    ip: str = Query(None, description="Adresse IP à vérifier (optionnel)"),
    service: PermissionsService = Depends(get_permissions_service)
) -> DocsPermissionsResponse:
    """Endpoint de permissions découplé."""
    # Priorité : ?ip= → X-Forwarded-For (route handler Next.js) → TEST_IP dev → client direct
    forwarded_for_header = request.headers.get("x-forwarded-for")
    forwarded_user_ip = (
        forwarded_for_header.split(",")[0].strip() if forwarded_for_header else None
    )

    remote_ip = request.client.host if request.client else None
    if ip:
        remote_ip = ip
    elif forwarded_user_ip:
        remote_ip = forwarded_user_ip
        logger.debug("IP resolved from X-Forwarded-For header")
    elif settings.dev and settings.test_ip:
        remote_ip = settings.test_ip
        logger.debug("[DEV] Using TEST_IP override")
    try:
        return await service.get_document_permissions(urls, remote_ip)
    except Exception as e:
        logger.error(f"Error in permissions endpoint: {e}")
        return DocsPermissionsResponse(
            data={"organization": None, "docs": None},
            info={"error": str(e)}
        )



@app.post("/search", response_model=SearchResponse)
@limiter.limit("120/minute")
async def perform_search(
    request: Request,
    search_request: SearchRequest,
    service: ISearchService = Depends(get_search_service),
):
    """Endpoint de recherche POST — délègue au SearchService (cache + Solr)."""
    try:
        return await service.execute_cached_search(search_request)
    except HTTPException:
        raise
    except SolrTimeoutError as e:
        raise HTTPException(status_code=503, detail="Search service unavailable (timeout)") from e
    except SolrInvalidQueryError as e:
        raise HTTPException(status_code=400, detail="Invalid search query") from e
    except SolrUnavailableError as e:
        logger.error(f"Solr unavailable: {e}")
        raise HTTPException(status_code=503, detail="Search service unavailable") from e
    except Exception as e:
        logger.error(f"Unexpected search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e

@app.get("/search", response_model=SearchResponse)
@limiter.limit("120/minute")
async def search_via_get(
    request: Request,
    q: str = Query(..., description="Terme de recherche"),
    filters: list[str] = Query([], description="Filtres 'identifier:value' (ex: platform:OB)"),
    facets: list[str] = Query([], description="Facettes à récupérer (ex: platform)"),
    page: int = Query(1, ge=1, description="Numéro de page"),
    size: int = Query(10, ge=1, le=100, description="Nombre de résultats par page"),
    service: ISearchService = Depends(get_search_service),
):
    """Recherche via paramètres URL (GET) — construit un SearchRequest et délègue au service."""
    from app.models.search_models import FacetModel, FilterModel, PaginationModel, QueryModel

    filter_models = [
        FilterModel(identifier=identifier, value=value)
        for f in filters
        if ":" in f
        for identifier, value in [f.split(":", 1)]
    ]
    facet_models = [FacetModel(identifier=f, type="list") for f in facets]
    search_request = SearchRequest(
        query=QueryModel(query=q),
        filters=filter_models,
        pagination=PaginationModel(from_=(page - 1) * size, size=size),
        facets=facet_models,
    )

    try:
        return await service.execute_cached_search(search_request)
    except HTTPException:
        raise
    except SolrTimeoutError as e:
        raise HTTPException(status_code=503, detail="Search service unavailable (timeout)") from e
    except SolrInvalidQueryError as e:
        raise HTTPException(status_code=400, detail="Invalid search query") from e
    except SolrUnavailableError as e:
        logger.error(f"Solr unavailable: {e}")
        raise HTTPException(status_code=503, detail="Search service unavailable") from e
    except Exception as e:
        logger.error(f"Unexpected search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e

@app.get("/suggest", response_model=SuggestResponse)
@limiter.limit("30/minute")
async def suggest(
    request: Request,
    q: str = Query(..., min_length=1, description="Terme à compléter"),
    service: SuggestService = Depends(get_suggest_service),
):
    """Endpoint d'autocomplétion — délègue au SuggestService (cache + Solr)."""
    return await service.fetch_autocomplete_suggestions(q)

@app.get("/cache/stats")
async def get_cache_stats():
    """ Endpoint pour récupérer les statistiques du cache Redis """
    return await cache_service.get_stats()

@app.delete("/cache/clear")
async def clear_cache(
    pattern: str = Query("*", description="Pattern des clés à supprimer (ex: search:*, suggest:*)")
):
    """ Endpoint pour vider le cache (dev/staging uniquement) """
    if settings.environment == "production":
        raise HTTPException(status_code=403, detail="Cache clearing is disabled in production")
    deleted_count = await cache_service.clear_pattern(pattern)
    return {
        "message": f"Cache cleared for pattern: {pattern}",
        "deleted_keys": deleted_count
    }

@app.get("/facets/config", response_model=FacetsConfigResponse)
async def get_facets_config():
    """Retourne la configuration complète des facettes + champs de recherche avancée."""
    from app.services.facet_config import FACET_CONFIG, SEARCH_FIELDS_MAPPING
    return {**FACET_CONFIG, "search_fields": list(SEARCH_FIELDS_MAPPING.keys())}

@app.get("/health")
async def health_check():
    """ Endpoint de santé incluant le statut Redis """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {
            "api": "healthy",
            "cache": "unknown"
        }
    }

    # Vérifier le statut du cache Redis
    try:
        cache_stats = await cache_service.get_stats()
        if cache_stats.get("enabled", False) and "error" not in cache_stats:
            health_status["services"]["cache"] = "healthy"
        elif not cache_stats.get("enabled", False):
            health_status["services"]["cache"] = "disabled"
        else:
            health_status["services"]["cache"] = "unhealthy"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["services"]["cache"] = "unhealthy"
        health_status["status"] = "degraded"
        logger.error(f"Health check failed for cache: {e}")

    return health_status

# --- Initialisation ---

if __name__ == "__main__":
    import uvicorn

    from app.settings import settings
    # Lancez l'application avec uvicorn: uvicorn app.main:app --reload
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )
