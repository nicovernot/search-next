
import asyncio
from app.services.search_builder import SearchBuilder
from app.models.search_models import SearchRequest, QueryModel, PaginationModel
from app.models.logical_query import QueryGroup, QueryRule
import httpx
import json

async def debug_search():
    builder = SearchBuilder(solr_base_url="https://solrslave-sec.labocleo.org/solr/documents")
    
    # Simuler la requête qui échoue (deux règles)
    logical_query = QueryGroup(
        combinator="and",
        rules=[
            QueryRule(field="titre", operator="contains", value="marseille"),
            QueryRule(field="text_recherche", operator="contains", value="marseille")
        ]
    )
    
    request = SearchRequest(
        query=QueryModel(query="histoire"),
        logical_query=logical_query,
        filters=[],
        pagination=PaginationModel(from_=0, size=10),
        facets=[]
    )
    
    url = builder.build_search_url(request)
    print(f"Generated URL: {url}")
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url)
            print(f"Status: {resp.status_code}")
            if resp.status_code != 200:
                print(f"Response Error Body: {resp.text}")
            else:
                data = resp.json()
                print(f"Success! NumFound: {data.get('response', {}).get('numFound')}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(debug_search())
