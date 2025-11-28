from fastapi import APIRouter, Depends
from app.models.search_models import SearchQuery, SearchResponse
from app.services.search_builder import SearchBuilder
from app.services.solr_connector import SolrConnector

router = APIRouter()

@router.post("/search", response_model=SearchResponse)
async def search(
    query: SearchQuery,
    builder: SearchBuilder = Depends(SearchBuilder),
    connector: SolrConnector = Depends(SolrConnector)
):
    solr_params = builder.build_query(query)
    solr_response = await connector.search(solr_params)
    
    # Basic mapping - needs to be adapted based on actual Solr response structure
    return SearchResponse(
        results=solr_response.get("response", {}).get("docs", []),
        total=solr_response.get("response", {}).get("numFound", 0),
        facets=solr_response.get("facet_counts", {})
    )
