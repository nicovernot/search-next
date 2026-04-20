# app/services/search_service.py
"""
Service de recherche - Encapsulation de la logique métier avec cache Redis
"""
from typing import Any

from app.core.logging import get_logger
from app.models.search_models import SearchRequest
from app.services.interfaces import ISearchBuilder, ISearchService, ISolrClient


class SearchService(ISearchService):
    """Service de recherche implémentant ISearchService avec cache Redis"""

    def __init__(self, builder: ISearchBuilder, solr_client: ISolrClient):
        self.builder = builder
        self.solr_client = solr_client
        self.logger = get_logger(__name__)

        # Reverse mapping: Solr field name -> frontend identifier
        from app.services.facet_config import COMMON_FACETS_MAPPING
        self._solr_to_identifier = {v: k for k, v in COMMON_FACETS_MAPPING.items()}

    def _normalize_facets(self, raw_facets: dict) -> dict:
        """
        Normalise les facettes Solr brutes en format frontend.

        Solr renvoie:  {"platformID": ["OJ", 206225, "OB", 173423, ...]}
        Frontend attend: {"platform": {"buckets": [{"key": "OJ", "doc_count": 206225}, ...]}}
        """
        normalized = {}
        for solr_field, values in raw_facets.items():
            # Mapper le nom Solr vers l'identifiant frontend
            identifier = self._solr_to_identifier.get(solr_field, solr_field)

            if isinstance(values, list):
                # Convertir la liste alternée [key, count, key, count, ...] en buckets
                buckets = []
                for i in range(0, len(values), 2):
                    if i + 1 < len(values) and values[i + 1] > 0:
                        buckets.append({
                            "key": str(values[i]),
                            "doc_count": values[i + 1]
                        })
                normalized[identifier] = {"buckets": buckets}
            elif isinstance(values, dict):
                # Déjà au bon format (JSON Facet API)
                normalized[identifier] = values

        return normalized

    async def execute_cached_search(self, request: SearchRequest) -> dict[str, Any]:
        """Effectue une recherche complète avec cache."""
        from app.services.cache_service import cache_service

        # Cache key uses the serialised request
        request_dict = request.model_dump(by_alias=True)

        cached_result = await cache_service.get_search_cache(request_dict)
        if cached_result:
            self.logger.debug(
                "Returning cached search results",
                extra={"context": {"query": request.query.query}},
            )
            return cached_result

        search_url = self.builder.build_search_url(request)

        self.logger.info(
            "Starting search request",
            extra={
                "context": {
                    "query": request.query.query,
                    "filters": [f.identifier for f in request.filters],
                    "pagination": request_dict.get("pagination"),
                }
            },
        )

        try:
            solr_data = await self.solr_client.search(search_url)
        except Exception as e:
            self.logger.error(
                "Search failed",
                extra={"context": {"query": request.query.query, "error": str(e)}},
                exc_info=True,
            )
            raise

        solr_raw_facets = solr_data.get("facet_counts", {}).get("facet_fields", {})
        search_result: dict[str, Any] = {
            "results": solr_data.get("response", {}).get("docs", []),
            "total": solr_data.get("response", {}).get("numFound", 0),
            "facets": self._normalize_facets(solr_raw_facets),
        }

        await cache_service.set_search_cache(request_dict, search_result)

        self.logger.info(
            "Search completed successfully",
            extra={
                "context": {
                    "query": request.query.query,
                    "num_found": search_result["total"],
                    "processing_time": solr_data.get("responseHeader", {}).get("QTime", 0),
                }
            },
        )

        return search_result

class SuggestService:
    """Service d'autocomplétion : cache, appel Solr, parsing de la réponse."""

    def __init__(self, builder: ISearchBuilder, solr_client: ISolrClient):
        self.builder = builder
        self.solr_client = solr_client
        self.logger = get_logger(__name__)

    def _parse_solr_suggestions(self, solr_data: dict[str, Any], query: str) -> list:
        """Extrait la liste de termes depuis la réponse Solr Suggester."""
        try:
            suggest_block = solr_data.get("suggest", {}).get("default", {})
            if query in suggest_block:
                raw = suggest_block[query].get("suggestions", [])
            elif suggest_block:
                first_term = next(iter(suggest_block))
                raw = suggest_block[first_term].get("suggestions", [])
            else:
                return []
            return [s.get("term") for s in raw if s.get("term")]
        except Exception as parse_error:
            self.logger.error(f"Error parsing Solr suggest response: {parse_error}")
            return []

    async def fetch_autocomplete_suggestions(self, query: str) -> dict[str, Any]:
        """Retourne les suggestions d'autocomplétion avec cache Redis."""
        from app.services.cache_service import cache_service

        cached = await cache_service.get_suggest_cache(query)
        if cached:
            self.logger.debug(f"Returning cached suggestions for query: {query}")
            return cached

        suggest_url = self.builder.build_suggest_url(query)
        self.logger.debug(f"Suggest URL: {suggest_url}")

        try:
            solr_data = await self.solr_client.search(suggest_url)
        except Exception as e:
            self.logger.error(f"Suggest Solr call failed: {e}")
            return {"suggestions": []}

        suggestions = self._parse_solr_suggestions(solr_data, query)
        result: dict[str, Any] = {"suggestions": suggestions}

        await cache_service.set_suggest_cache(query, result)
        self.logger.info(f"Suggest completed for query: {query} ({len(suggestions)} results)")
        return result

class PermissionsService:
    """Service de permissions avec cache"""

    def __init__(self, solr_client: ISolrClient):
        self.solr_client = solr_client
        self.logger = get_logger(__name__)

    async def get_document_permissions(self, urls: str, ip: str) -> dict[str, Any]:
        """Récupère les permissions pour des documents avec cache"""
        try:
            from app.services.cache_service import cache_service
            from app.services.docs_permissions_client import DocsPermissionsClient
            from app.services.docs_permissions_client import SolrClient as PermSolrClient
            from app.settings import SOLR_CONFIG

            # 1. Vérifier le cache d'abord
            cached_result = await cache_service.get_permissions_cache(urls, ip)
            if cached_result:
                self.logger.debug(f"Returning cached permissions for URLs: {urls}")
                return cached_result

            # 2. Appel réel via DocsPermissionsClient
            perm_client = DocsPermissionsClient(
                solr_client=PermSolrClient(base_url=SOLR_CONFIG["base_url"]),
                settings=SOLR_CONFIG,
            )
            response = await perm_client.handle_query(urls, ip)
            result = response.dict() if hasattr(response, "dict") else dict(response)

            # 3. Mettre en cache le résultat
            await cache_service.set_permissions_cache(urls, result, ip)

            return result

        except Exception as e:
            self.logger.error(f"Permissions check failed: {e}")
            return {"data": {"organization": None, "docs": None}, "info": {"error": str(e)}}
