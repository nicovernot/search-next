# app/services/solr_client.py
"""
Client Solr dédié - Implémentation de ISolrClient
"""
from typing import Any

import httpx

from app.core.exceptions import SolrInvalidQueryError, SolrTimeoutError, SolrUnavailableError
from app.core.logging import get_logger
from app.services.interfaces import ISolrClient

# Singleton pour le HTTP Client afin d'éviter d'ouvrir une connexion TCP à chaque requête
# Note: On crée un client par Event Loop pour éviter les erreurs dans le cadre de tests (TestClient)

class SolrClient(ISolrClient):
    """Client dédié pour les requêtes Solr"""

    def __init__(self, base_url: str, timeout: float = 10.0):
        self.base_url = base_url
        self.timeout = timeout
        self.logger = get_logger(__name__)
        # Initialisé au premier appel pour être lié à la bonne loop
        self._client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                limits=httpx.Limits(max_keepalive_connections=50, max_connections=100),
                timeout=self.timeout
            )
        return self._client

    async def search(self, query: str, timeout: float = None) -> dict[str, Any]:
        """Exécute une requête Solr"""
        eff_timeout = timeout if timeout is not None else self.timeout
        client = self._get_client()
        try:
            # Logging structuré de la requête Solr
            self.logger.debug(
                "Executing Solr query",
                extra={
                    "context": {
                        "query": query,
                        "timeout": eff_timeout
                    }
                }
            )

            response = await client.get(query, timeout=eff_timeout)
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
        except httpx.ReadTimeout as e:
            self.logger.error(
                "Solr search timeout",
                extra={"context": {"query": query, "timeout": self.timeout}},
            )
            raise SolrTimeoutError(f"Solr did not respond within {eff_timeout}s") from e
        except httpx.HTTPStatusError as e:
            self.logger.error(
                "Solr HTTP error",
                extra={
                    "context": {
                        "query": query,
                        "status_code": e.response.status_code,
                        "error": str(e),
                    }
                },
            )
            if e.response.status_code == 400:
                raise SolrInvalidQueryError("Solr rejected the query (400)") from e
            raise SolrUnavailableError(f"Solr HTTP {e.response.status_code}") from e
        except (SolrTimeoutError, SolrInvalidQueryError, SolrUnavailableError):
            raise
        except Exception as e:
            self.logger.error(
                "Unexpected Solr error",
                extra={"context": {"query": query, "error": str(e), "type": type(e).__name__}},
                exc_info=True,
            )
            raise SolrUnavailableError(f"Unexpected error: {type(e).__name__}") from e
