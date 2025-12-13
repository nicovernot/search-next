# app/services/solr_client.py
"""
Client Solr dédié - Implémentation de ISolrClient
"""
from app.services.interfaces import ISolrClient
import httpx
from typing import Dict, Any
import logging

from app.core.logging import get_logger

# logger = logging.getLogger(__name__)

class SolrClient(ISolrClient):
    """Client dédié pour les requêtes Solr"""
    
    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout
        self.logger = get_logger(__name__)
    
    async def search(self, query: str) -> Dict[str, Any]:
        """Exécute une requête Solr"""
        try:
            # Logging structuré de la requête Solr
            self.logger.debug(
                "Executing Solr query",
                extra={
                    "context": {
                        "query": query,
                        "timeout": self.timeout
                    }
                }
            )
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(query)
                response.raise_for_status()
                
                # Logging structuré de la réponse
                self.logger.debug(
                    "Solr query completed",
                    extra={
                        "context": {
                            "query": query,
                            "status_code": response.status_code,
                            "elapsed": response.elapsed.total_seconds()
                        }
                    }
                )
                
                return response.json()
        except httpx.ReadTimeout:
            self.logger.error(
                "Solr search timeout",
                extra={
                    "context": {
                        "query": query,
                        "timeout": self.timeout
                    }
                }
            )
            raise Exception("Solr search timeout")
        except httpx.HTTPStatusError as e:
            self.logger.error(
                "Solr HTTP error",
                extra={
                    "context": {
                        "query": query,
                        "status_code": e.response.status_code,
                        "error": str(e)
                    }
                }
            )
            if e.response.status_code == 400:
                raise Exception("Invalid search query")
            raise Exception("Solr service unavailable")
        except Exception as e:
            self.logger.error(
                "Unexpected Solr error",
                extra={
                    "context": {
                        "query": query,
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
                },
                exc_info=True
            )
            raise Exception("Internal server error")