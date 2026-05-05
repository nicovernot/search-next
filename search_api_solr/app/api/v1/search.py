from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.api.dependencies import get_search_service
from app.core.exceptions import (
    SolrInvalidQueryError,
    SolrTimeoutError,
    SolrUnavailableError,
)
from app.core.logging import get_logger
from app.core.rate_limit import limiter
from app.models.search_models import (
    FacetModel,
    FilterModel,
    PaginationModel,
    QueryModel,
    SearchRequest,
    SearchResponse,
)
from app.services.interfaces import ISearchService

router = APIRouter(tags=["search"])
logger = get_logger(__name__)


def _raise_public_search_error(error: Exception) -> None:
    if isinstance(error, SolrTimeoutError):
        raise HTTPException(
            status_code=503, detail="Search service unavailable (timeout)"
        ) from error
    if isinstance(error, SolrInvalidQueryError):
        raise HTTPException(status_code=400, detail="Invalid search query") from error
    if isinstance(error, SolrUnavailableError):
        logger.error("Solr unavailable", extra={"context": {"error": str(error)}})
        raise HTTPException(
            status_code=503, detail="Search service unavailable"
        ) from error

    logger.error(
        "Unexpected search error",
        extra={"context": {"error": str(error)}},
        exc_info=True,
    )
    raise HTTPException(status_code=500, detail="Internal server error") from error


@router.post(
    "/search",
    response_model=SearchResponse,
    responses={
        400: {"description": "Invalid search query"},
        422: {"description": "Invalid request payload"},
        503: {"description": "Search service unavailable"},
    },
)
@limiter.limit("120/minute")
async def perform_search(
    request: Request,
    search_request: SearchRequest,
    service: ISearchService = Depends(get_search_service),
):
    """Endpoint de recherche POST — délègue au SearchService."""
    try:
        return await service.execute_cached_search(search_request)
    except HTTPException:
        raise
    except Exception as error:
        _raise_public_search_error(error)


@router.get(
    "/search",
    response_model=SearchResponse,
    responses={
        400: {"description": "Invalid search query"},
        422: {"description": "Invalid query parameters"},
        503: {"description": "Search service unavailable"},
    },
)
@limiter.limit("120/minute")
async def search_via_get(
    request: Request,
    q: str = Query(..., description="Terme de recherche"),
    filters: list[str] = Query(
        [], description="Filtres 'identifier:value' (ex: platform:OB)"
    ),
    facets: list[str] = Query([], description="Facettes à récupérer (ex: platform)"),
    page: int = Query(1, ge=1, description="Numéro de page"),
    size: int = Query(10, ge=1, le=100, description="Nombre de résultats par page"),
    service: ISearchService = Depends(get_search_service),
):
    """Recherche via paramètres URL — construit un SearchRequest."""
    filter_models = [
        FilterModel(identifier=identifier, value=value)
        for raw_filter in filters
        if ":" in raw_filter
        for identifier, value in [raw_filter.split(":", 1)]
    ]
    facet_models = [FacetModel(identifier=facet, type="list") for facet in facets]
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
    except Exception as error:
        _raise_public_search_error(error)
