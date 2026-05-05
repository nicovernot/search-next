from fastapi import APIRouter

from app.models.search_models import FacetsConfigResponse
from app.services.facet_config import FACET_CONFIG, SEARCH_FIELDS_MAPPING

router = APIRouter(tags=["facets"])


@router.get(
    "/facets/config",
    response_model=FacetsConfigResponse,
    responses={200: {"description": "Facet and advanced-search field configuration"}},
)
async def get_facets_config() -> dict:
    """Retourne la configuration complète des facettes et champs avancés."""
    return {**FACET_CONFIG, "search_fields": list(SEARCH_FIELDS_MAPPING.keys())}
