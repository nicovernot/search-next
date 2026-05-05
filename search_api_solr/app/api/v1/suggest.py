from typing import Any

from fastapi import APIRouter, Depends, Query, Request

from app.api.dependencies import get_suggest_service
from app.core.rate_limit import limiter
from app.models.search_models import SuggestResponse
from app.services.search_service import SuggestService

router = APIRouter(tags=["suggest"])


@router.get("/suggest", response_model=SuggestResponse)
@limiter.limit("30/minute")
async def suggest(
    request: Request,
    q: str = Query(..., min_length=1, description="Terme à compléter"),
    service: SuggestService = Depends(get_suggest_service),
) -> dict[str, Any]:
    """Endpoint d'autocomplétion — délègue au SuggestService."""
    return await service.fetch_autocomplete_suggestions(q)
