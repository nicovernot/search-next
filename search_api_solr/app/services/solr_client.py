# app/services/solr_client.py
"""
Client Solr dédié - Implémentation de ISolrClient
"""
from app.services.interfaces import ISolrClient
import httpx
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class SolrClient(ISolrClient):
    """Client dédié pour les requêtes Solr"""
    
    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout
    
    async def search(self, query: str) -> Dict[str, Any]:
        """Exécute une requête Solr"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(query)
                response.raise_for_status()
                return response.json()
        except httpx.ReadTimeout:
            logger.error(f"Solr search timeout: {query}")
            raise Exception("Solr search timeout")
        except httpx.HTTPStatusError as e:
            logger.error(f"Solr HTTP error: {e}")
            if e.response.status_code == 400:
                raise Exception("Invalid search query")
            raise Exception("Solr service unavailable")
        except Exception as e:
            logger.error(f"Unexpected Solr error: {e}")
            raise Exception("Internal server error")