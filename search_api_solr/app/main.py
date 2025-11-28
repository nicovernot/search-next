# app/main.py
from fastapi import FastAPI, Depends, Query, Request, APIRouter
import httpx

from app.services.docs_permissions_client import DocsPermissionsClient, SolrClient
from app.services.search_builder import SearchBuilder
from app.models.search_models import SearchRequest
from app.settings import SOLR_CONFIG
from app.models import DocsPermissionsResponse

app = FastAPI()

router = APIRouter()
app.include_router(router)

# --- Injection de Dépendance ---

def get_solr_client() -> SolrClient:
    """ Fournit une instance du client Solr """
    return SolrClient(base_url=SOLR_CONFIG['base_url'])

def get_docs_permissions_client(
    solr_client: SolrClient = Depends(get_solr_client)
) -> DocsPermissionsClient:
    """ Fournit une instance du service de permissions """
    return DocsPermissionsClient(solr_client, settings=SOLR_CONFIG)

def get_search_builder() -> SearchBuilder:
    """ Fournit une instance du SearchBuilder """
    return SearchBuilder(solr_base_url=SOLR_CONFIG['base_url'])

# --- Endpoint ---

@app.get("/permissions")
async def get_document_permissions(
    request: Request,
    urls: str = Query(..., description="Liste des URLs de documents séparées par des virgules"),
    client: DocsPermissionsClient = Depends(get_docs_permissions_client)
) -> DocsPermissionsResponse:
    
    # Récupérer l'adresse IP distante du client (méthode standard dans FastAPI)
    remote_ip = request.client.host if request.client else None
    
    return await client.handle_query(urls, remote_ip)


@app.post("/search")
async def perform_search(
    request: SearchRequest, 
    builder: SearchBuilder = Depends(get_search_builder)
):
    # 1. Construction de la requête Solr
    solr_search_url = builder.build_search_url(request)
    
    # 2. Exécution (via un client HTTP)
    async with httpx.AsyncClient() as client:
        response = await client.get(solr_search_url, timeout=10.0)
        response.raise_for_status()
        solr_data = response.json()
    
    # 3. Post-traitement et retour à Searchkit
    # TODO: Implémenter format_response dans SearchBuilder
    return solr_data    

# --- Initialisation ---

if __name__ == "__main__":
    import uvicorn
    from app.settings import settings
    # Lancez l'application avec uvicorn: uvicorn app.main:app --reload
    uvicorn.run(
        "app.main:app", 
        host=settings.api_host, 
        port=settings.api_port, 
        reload=settings.api_reload
    )