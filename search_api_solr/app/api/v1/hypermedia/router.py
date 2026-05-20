from pathlib import Path

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.api.dependencies import get_search_service
from app.core.exceptions import (
    SolrInvalidQueryError,
    SolrTimeoutError,
    SolrUnavailableError,
)
from app.core.logging import get_logger
from app.models.search_models import (
    FacetModel,
    FilterModel,
    PaginationModel,
    QueryModel,
    SearchRequest,
)
from app.services.interfaces import ISearchService
from app.settings import settings

TEMPLATES_DIR = Path(__file__).parent.parent.parent.parent / "templates" / "hypermedia"
STATIC_DIR = Path(__file__).parent.parent.parent.parent / "static" / "hypermedia"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter(tags=["hypermedia"])
logger = get_logger(__name__)

_PAGE_SIZE = 10
_FACETS = [
    FacetModel(identifier="platform", type="list", size=10),
    FacetModel(identifier="type", type="list", size=10),
]


def _parse_filters(raw_filters: list[str]) -> list[FilterModel]:
    """Parse 'identifier:value' strings into FilterModel list."""
    result = []
    for raw in raw_filters:
        if ":" in raw:
            identifier, value = raw.split(":", 1)
            result.append(FilterModel(identifier=identifier, value=value))
    return result


def _build_search_request(q: str, page: int, filters: list[FilterModel]) -> SearchRequest:
    return SearchRequest(
        query=QueryModel(query=q),
        filters=filters,
        pagination=PaginationModel(from_=(page - 1) * _PAGE_SIZE, size=_PAGE_SIZE),
        facets=_FACETS,
    )


async def _execute_search(
    q: str, page: int, filters: list[FilterModel], service: ISearchService
) -> dict:
    try:
        result = await service.execute_cached_search(_build_search_request(q, page, filters))
        return {"results": result.get("results", []), "total": result.get("total", 0), "facets": result.get("facets")}
    except SolrTimeoutError:
        return {"error": "Le moteur de recherche ne répond pas (timeout).", "results": [], "total": 0, "facets": None}
    except SolrInvalidQueryError:
        return {"error": "Requête invalide.", "results": [], "total": 0, "facets": None}
    except SolrUnavailableError:
        logger.error("Solr unavailable during hypermedia search")
        return {"error": "Service de recherche indisponible.", "results": [], "total": 0, "facets": None}
    except Exception:
        logger.error("Unexpected hypermedia search error", exc_info=True)
        return {"error": "Erreur interne.", "results": [], "total": 0, "facets": None}


def _is_htmx(request: Request) -> bool:
    return request.headers.get("HX-Request") == "true"


@router.get("/", response_class=HTMLResponse)
async def hypermedia_home(request: Request):
    """Page d'accueil du frontend hypermedia."""
    return templates.TemplateResponse(
        "pages/search.j2",
        {"request": request, "results": [], "total": 0, "q": "", "page": 1,
         "filters": [], "facets": None, "debug": settings.environment != "production"},
    )


@router.get("/search", response_class=HTMLResponse)
async def hypermedia_search(
    request: Request,
    q: str = Query("", description="Terme de recherche"),
    page: int = Query(1, ge=1, description="Numéro de page"),
    filter: list[str] = Query([], description="Filtres actifs 'identifier:value'"),
    service: ISearchService = Depends(get_search_service),
):
    """Page de recherche — rendu SSR complet ou fragment si requête HTMX."""
    active_filters = _parse_filters(filter)
    data = (
        await _execute_search(q, page, active_filters, service)
        if q
        else {"results": [], "total": 0, "facets": None}
    )
    ctx = {
        "request": request, "q": q, "page": page, "filters": active_filters,
        "debug": settings.environment != "production", **data,
    }
    # Réponse HTMX : fragment résultats + facettes OOB
    if _is_htmx(request):
        return templates.TemplateResponse("fragments/results.j2", ctx)
    return templates.TemplateResponse("pages/search.j2", ctx)


@router.get("/search/results", response_class=HTMLResponse)
async def hypermedia_search_results(
    request: Request,
    q: str = Query("", description="Terme de recherche"),
    page: int = Query(1, ge=1, description="Numéro de page"),
    filter: list[str] = Query([], description="Filtres actifs 'identifier:value'"),
    service: ISearchService = Depends(get_search_service),
):
    """Fragment résultats + facettes OOB — réponse aux requêtes HTMX directes."""
    active_filters = _parse_filters(filter)
    data = (
        await _execute_search(q, page, active_filters, service)
        if q
        else {"results": [], "total": 0, "facets": None}
    )
    return templates.TemplateResponse(
        "fragments/results.j2",
        {"request": request, "q": q, "page": page, "filters": active_filters, **data},
    )


@router.get("/search/facets", response_class=HTMLResponse)
async def hypermedia_search_facets(
    request: Request,
    q: str = Query("", description="Terme de recherche"),
    filter: list[str] = Query([], description="Filtres actifs 'identifier:value'"),
    service: ISearchService = Depends(get_search_service),
):
    """Fragment facettes seul."""
    active_filters = _parse_filters(filter)
    data = (
        await _execute_search(q, 1, active_filters, service)
        if q
        else {"results": [], "total": 0, "facets": None}
    )
    return templates.TemplateResponse(
        "fragments/facets.j2",
        {"request": request, "q": q, "filters": active_filters, "facets": data.get("facets")},
    )
