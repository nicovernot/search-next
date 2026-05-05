# app/main.py
# ruff: noqa: E402
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.logging import get_logger, setup_logging
from app.core.rate_limit import limiter
from app.settings import settings

# Point d'initialisation unique du logging — avant tout autre import applicatif
setup_logging(settings.log_level)
logger = get_logger(__name__)

from app.api.auth import router as auth_router
from app.api.v1.facets import router as facets_router
from app.api.v1.openapi import router as openapi_router
from app.api.v1.permissions import router as permissions_router
from app.api.v1.saved_searches import router as saved_searches_router
from app.api.v1.search import router as search_router
from app.api.v1.suggest import router as suggest_router
from app.core.env_validation import validate_environment
from app.services.cache_service import cache_service

# Validation de l'environnement au démarrage
try:
    env_config = validate_environment()
    logger.info("Environment validation completed successfully")
except Exception as e:
    logger.critical(f"Environment validation failed: {e}")
    raise

app = FastAPI()

# Rate limiting
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
for public_router in (search_router, suggest_router, facets_router, permissions_router):
    app.include_router(public_router, prefix="/api/v1")
    app.include_router(public_router, include_in_schema=False)

app.include_router(saved_searches_router, prefix="/api/v1")
app.include_router(saved_searches_router, include_in_schema=False)
app.include_router(openapi_router, prefix="/api/v1")

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
