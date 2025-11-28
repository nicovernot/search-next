import httpx
from app.core.config import settings

class SolrConnector:
    def __init__(self):
        self.base_url = settings.SOLR_BASE_URL
        self.core = settings.SOLR_CORE_NAME

    async def search(self, params: dict):
        url = f"{self.base_url}/{self.core}/select"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
