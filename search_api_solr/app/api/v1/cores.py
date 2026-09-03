from fastapi import APIRouter, Depends

from app.api.dependencies import get_solr_core_registry
from app.models import SolrCoreInfo, SolrCoresResponse
from app.services.solr_core_registry import SolrCoreRegistry

router = APIRouter(tags=["cores"])


@router.get(
    "/cores",
    response_model=SolrCoresResponse,
    responses={200: {"description": "Cores Solr configurés et core par défaut"}},
)
async def get_cores(
    registry: SolrCoreRegistry = Depends(get_solr_core_registry),
) -> SolrCoresResponse:
    """Liste les cores Solr configurés et indique lequel est le core par défaut."""
    cores = [
        SolrCoreInfo(name=core.name, is_default=core.is_default)
        for core in sorted(registry.cores.values(), key=lambda c: c.name)
    ]
    return SolrCoresResponse(cores=cores, default_core=registry.default_core_name)
