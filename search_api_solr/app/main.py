# app/main.py
from fastapi import FastAPI, Depends, Query, Request, APIRouter, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from typing import Dict, Any, List
import httpx
import logging
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.logging import get_logger
from app.core.env_validation import validate_environment
from app.services.interfaces import ISearchService, ISearchBuilder, ISolrClient
from app.services.search_service import SearchService, SuggestService, PermissionsService
from app.services.solr_client import SolrClient
from app.services.search_builder import SearchBuilder
from app.models.search_models import SearchRequest
from app.settings import settings, SOLR_CONFIG
from app.models import DocsPermissionsResponse

# Configuration du logging structuré
logger = get_logger(__name__)

# Validation de l'environnement au démarrage
try:
    env_config = validate_environment()
    logger.info("Environment validation completed successfully")
except Exception as e:
    logger.critical(f"Environment validation failed: {e}")
    raise

app = FastAPI()

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
    
    logger.info(f"CORS configured for environment '{settings.environment}': {settings.cors_origins}")
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

# router = APIRouter()
# app.include_router(router)

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
async def get_document_permissions(
    request: Request,
    urls: str = Query(..., description="Liste des URLs de documents séparées par des virgules"),
    ip: str = Query(None, description="Adresse IP à vérifier (optionnel)"),
    service: PermissionsService = Depends(get_permissions_service)
) -> DocsPermissionsResponse:
    """ Endpoint de permissions decouple """
    remote_ip = request.client.host if request.client else None
    if ip:
        remote_ip = ip
    try:
        return await service.get_document_permissions(urls, remote_ip)
    except Exception as e:
        return DocsPermissionsResponse(
            data={"organization": None, "docs": None},
            info={"error": str(e)}
        )
    try:
        return await service.get_document_permissions(urls, remote_ip)
    except Exception as e:
        logger.error(f"Error in permissions endpoint: {e}")
        return DocsPermissionsResponse(
            data={"organization": None, "docs": None},
            info={"error": str(e)}
        )


async def _execute_search(request: SearchRequest, builder: SearchBuilder) -> Dict[str, Any]:
    """ Logique commune pour exécuter la recherche Solr """
    # 1. Construction de la requête Solr
    try:
        solr_search_url = builder.build_search_url(request)
    except Exception as e:
        logger.error(f"Error building search URL: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid search request: {str(e)}")
    
    # 2. Exécution (via un client HTTP)
    async with httpx.AsyncClient() as client:
        try:
            # Timeout un peu plus long pour la recherche principale
            solr_response = await client.get(solr_search_url, timeout=10.0)
            solr_response.raise_for_status()
            return solr_response.json()
            
        except httpx.ReadTimeout:
            logger.error("Solr search timeout")
            raise HTTPException(status_code=503, detail="Search service unavailable (timeout)")
        except httpx.HTTPStatusError as e:
            logger.error(f"Solr search HTTP error: {e}")
            # Si Solr renvoie une 400, c'est probablement une mauvaise requête client
            if e.response.status_code == 400:
                raise HTTPException(status_code=400, detail="Invalid search query")
            raise HTTPException(status_code=503, detail="Search service unavailable")
        except Exception as e:
            logger.error(f"Unexpected error in search endpoint: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/search")
async def perform_search(
    request: SearchRequest, 
    service: ISearchService = Depends(get_search_service),
    response: Response = None
):
    """ Endpoint de recherche découplé """
    try:
        # Convertir la requête SearchRequest en dictionnaire pour le service
        request_dict = {
            "query": request.query.query,
            "filters": [{"identifier": f.identifier, "value": f.value} for f in request.filters],
            "pagination": {"from": request.pagination.from_, "size": request.pagination.size},
            "facets": [{"identifier": f.identifier, "type": f.type} for f in request.facets]
        }
        return await service.perform_search(request_dict)
    except Exception as e:
        logger.error(f"Search failed: {e}")
        error_msg = str(e)
        if "timeout" in error_msg.lower():
             raise HTTPException(status_code=503, detail="Search service unavailable (timeout)")
        elif "invalid search query" in error_msg.lower() or "bad request" in error_msg.lower():
             raise HTTPException(status_code=400, detail="Invalid search query")
        else:
             raise HTTPException(status_code=503, detail="Search service unavailable")

@app.get("/search")
async def search_via_get(
    q: str = Query(..., description="Terme de recherche"),
    filters: List[str] = Query([], description="Filtres au format 'identifier:value' (ex: platform:OB)"),
    facets: List[str] = Query([], description="Facettes à récupérer (ex: platform)"),
    page: int = Query(1, ge=1, description="Numéro de page"),
    size: int = Query(10, ge=1, le=100, description="Nombre de résultats par page"),
    service: ISearchService = Depends(get_search_service)
):
    """ Recherche via paramètres URL (GET) - Version découplée """
    try:
        # Conversion des filtres
        filter_list = []
        for f in filters:
            if ':' in f:
                identifier, value = f.split(":", 1)
                filter_list.append({"identifier": identifier, "value": value})
        
        # Conversion des facettes
        facet_list = []
        for f in facets:
            facet_list.append({"identifier": f, "type": "list"})
        
        # Construction de la requête pour le service
        request_dict = {
            "query": q,
            "filters": filter_list,
            "pagination": {"from": (page-1)*size, "size": size},
            "facets": facet_list
        }
        
        return await service.perform_search(request_dict)
    except Exception as e:
        logger.error(f"Search via GET failed: {e}")
        error_msg = str(e)
        if "timeout" in error_msg.lower():
             raise HTTPException(status_code=503, detail="Search service unavailable (timeout)")
        elif "invalid search query" in error_msg.lower() or "bad request" in error_msg.lower():
             raise HTTPException(status_code=400, detail="Invalid search query")
        else:
             raise HTTPException(status_code=503, detail="Search service unavailable")
@app.get("/suggest")
async def suggest(
    q: str = Query(..., min_length=1, description="Terme à compléter"),
    builder: SearchBuilder = Depends(get_search_builder)
):
    """ Endpoint d'autocomplétion """
    # 1. Construction de l'URL
    solr_suggest_url = builder.build_suggest_url(q)
    
    # 2. Exécution avec gestion d'erreurs
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(solr_suggest_url, timeout=2.0) # Timeout court pour l'autocomplétion
            response.raise_for_status()
            return response.json()
        except httpx.ReadTimeout:
            logger.warning(f"Solr suggest timeout for query: {q}")
            # Retourner une structure vide ou une erreur gérée
            return {"suggest": {"default": {q: {"numFound": 0, "suggestions": []}}}}
        except httpx.HTTPError as e:
            logger.error(f"Solr suggest error: {e}")
            return {"suggest": {"default": {q: {"numFound": 0, "suggestions": []}}}}

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