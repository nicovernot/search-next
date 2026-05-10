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
from app.settings import SOLR_CONFIG


def get_solr_client() -> ISolrClient:
    """Fournit une instance du client Solr."""
    return SolrClient(base_url=SOLR_CONFIG["base_url"])


def get_search_builder() -> ISearchBuilder:
    """Fournit une instance du SearchBuilder."""
    return SearchBuilder(solr_base_url=SOLR_CONFIG["base_url"])


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
    solr_client: ISolrClient = Depends(get_solr_client),
) -> PermissionsService:
    """Fournit une instance du service de permissions."""
    return PermissionsService(solr_client)
