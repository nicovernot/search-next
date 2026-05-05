from fastapi import APIRouter, Depends, Query, Request

from app.api.dependencies import get_permissions_service
from app.core.logging import get_logger
from app.core.rate_limit import limiter
from app.models import DocsPermissionsResponse
from app.services.search_service import PermissionsService
from app.settings import settings

router = APIRouter(tags=["permissions"])
logger = get_logger(__name__)


def _resolve_user_ip(request: Request, explicit_ip: str | None) -> str | None:
    forwarded_for_header = request.headers.get("x-forwarded-for")
    forwarded_user_ip = (
        forwarded_for_header.split(",")[0].strip() if forwarded_for_header else None
    )

    remote_ip = request.client.host if request.client else None
    if explicit_ip:
        return explicit_ip
    if forwarded_user_ip:
        logger.debug("IP resolved from X-Forwarded-For header")
        return forwarded_user_ip
    if settings.dev and settings.test_ip:
        logger.debug("[DEV] Using TEST_IP override")
        return settings.test_ip
    return remote_ip


@router.get(
    "/permissions",
    response_model=DocsPermissionsResponse,
    responses={422: {"description": "Invalid permissions query"}},
)
@limiter.limit("15/minute")
async def get_document_permissions(
    request: Request,
    urls: str = Query(
        ..., description="Liste des URLs de documents séparées par des virgules"
    ),
    ip: str | None = Query(None, description="Adresse IP à vérifier (optionnel)"),
    service: PermissionsService = Depends(get_permissions_service),
) -> DocsPermissionsResponse:
    """Endpoint de permissions découplé."""
    remote_ip = _resolve_user_ip(request, ip)
    try:
        return await service.get_document_permissions(urls, remote_ip)
    except Exception as error:
        logger.error(
            "Error in permissions endpoint",
            extra={"context": {"error": str(error)}},
        )
        return DocsPermissionsResponse(
            data={"organization": None, "docs": None},
            info={"error": str(error)},
        )
