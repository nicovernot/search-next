from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.interfaces import ISearchBuilder, ISearchService, ISolrClient
from app.services.search_builder import SearchBuilder
from app.services.search_service import (
    PermissionsService,
    SearchService,
    SuggestService,
)
from app.services.solr_client import SolrClient
from app.services.solr_core_registry import SolrCoreRegistry

# Chargé et validé une fois au démarrage (import de ce module) — voir FR-007.
_solr_core_registry = SolrCoreRegistry()


def get_solr_core_registry() -> SolrCoreRegistry:
    """Fournit le registre des cores Solr configurés (singleton partagé)."""
    return _solr_core_registry


def get_solr_client() -> ISolrClient:
    """Fournit une instance du client Solr."""
    return SolrClient(base_url=_solr_core_registry.resolve(None).base_url)


def get_search_builder(
    registry: SolrCoreRegistry = Depends(get_solr_core_registry),
) -> ISearchBuilder:
    """Fournit une instance du SearchBuilder."""
    return SearchBuilder(core_registry=registry)


def get_search_service(
    builder: ISearchBuilder = Depends(get_search_builder),
    solr_client: ISolrClient = Depends(get_solr_client),
    db: Session = Depends(get_db),
) -> ISearchService:
    """Fournit une instance du service de recherche."""
    return SearchService(builder, solr_client, db)


def get_suggest_service(
    builder: ISearchBuilder = Depends(get_search_builder),
    solr_client: ISolrClient = Depends(get_solr_client),
) -> SuggestService:
    """Fournit une instance du service de suggestion."""
    return SuggestService(builder, solr_client)


def get_permissions_service(
    registry: SolrCoreRegistry = Depends(get_solr_core_registry),
) -> PermissionsService:
    """Fournit une instance du service de permissions."""
    return PermissionsService(registry)
