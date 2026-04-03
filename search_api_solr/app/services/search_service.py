# app/services/search_service.py
"""
Service de recherche - Encapsulation de la logique métier avec cache Redis
"""
from app.services.interfaces import ISearchService, ISearchBuilder, ISolrClient
from app.models.search_models import SearchRequest
from typing import Dict, Any
import logging

from app.core.logging import get_logger

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
    
    async def perform_search(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Effectue une recherche complète avec cache"""
        try:
            # Import local pour éviter les imports circulaires
            from app.services.cache_service import cache_service
            
            # 1. Vérifier le cache d'abord
            cached_result = await cache_service.get_search_cache(request)
            if cached_result:
                self.logger.debug(
                    "Returning cached search results",
                    extra={"context": {"query": request.get("query")}}
                )
                return cached_result
            
            # 2. Construire l'URL de recherche
            search_url = self.builder.build_search_url(request)
            
            # Logging structuré avec contexte
            self.logger.info(
                "Starting search request",
                extra={
                    "context": {
                        "query": request.get("query"),
                        "filters": [f["identifier"] for f in request.get("filters", [])],
                        "pagination": request.get("pagination")
                    }
                }
            )
            
            # 3. Exécuter la recherche via le client Solr
            solr_data = await self.solr_client.search(search_url)
            
            # 4. Normaliser le résultat pour le frontend
            raw_facets = solr_data.get("facet_counts", {}).get("facet_fields", {})
            normalized_facets = self._normalize_facets(raw_facets)
            
            result = {
                "results": solr_data.get("response", {}).get("docs", []),
                "total": solr_data.get("response", {}).get("numFound", 0),
                "facets": normalized_facets,
                "highlighting": solr_data.get("highlighting", {})
            }
            
            # 5. Mettre en cache le résultat
            await cache_service.set_search_cache(request, result)
            
            # Logging structuré des résultats
            self.logger.info(
                "Search completed successfully",
                extra={
                    "context": {
                        "query": request.get("query"),
                        "num_found": result.get("total"),
                        "processing_time": solr_data.get('responseHeader', {}).get('QTime', 0)
                    }
                }
            )
            
            return result
            
        except Exception as e:
            # Logging structuré des erreurs
            self.logger.error(
                "Search failed",
                extra={
                    "context": {
                        "query": request.get("query"),
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
                },
                exc_info=True
            )
            raise

class SuggestService:
    """Service de suggestion"""
    
    def __init__(self, builder: ISearchBuilder, solr_client: ISolrClient):
        self.builder = builder
        self.solr_client = solr_client
        self.logger = get_logger(__name__)
    
    async def suggest(self, query: str) -> Dict[str, Any]:
        """Effectue une suggestion"""
        try:
            # Construire l'URL de suggestion
            suggest_url = self.builder.build_suggest_url(query)
            self.logger.debug(f"Suggest URL: {suggest_url}")
            
            # Exécuter la suggestion via le client Solr
            result = await self.solr_client.search(suggest_url)
            
            self.logger.info(f"Suggest completed for query: {query}")
            return result
            
        except Exception as e:
            self.logger.error(f"Suggest failed: {e}")
            # Retourner une réponse vide en cas d'erreur pour ne pas bloquer l'UI
            return {"suggest": {"default": {query: {"numFound": 0, "suggestions": []}}}}

class PermissionsService:
    """Service de permissions avec cache"""
    
    def __init__(self, solr_client: ISolrClient):
        self.solr_client = solr_client
        self.logger = get_logger(__name__)
    
    async def get_document_permissions(self, urls: str, ip: str) -> Dict[str, Any]:
        """Récupère les permissions pour des documents avec cache"""
        try:
            # Import local pour éviter les imports circulaires
            from app.services.cache_service import cache_service
            
            # 1. Vérifier le cache d'abord
            cached_result = await cache_service.get_permissions_cache(urls, ip)
            if cached_result:
                self.logger.debug(f"Returning cached permissions for URLs: {urls}")
                return cached_result
            
            # 2. Logique pour récupérer les permissions
            # (À implémenter selon la logique existante)
            result = {"data": {"organization": None, "docs": None}, "info": {"status": "ok"}}
            
            # 3. Mettre en cache le résultat
            await cache_service.set_permissions_cache(urls, result, ip)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Permissions check failed: {e}")
            return {"data": {"organization": None, "docs": None}, "info": {"error": str(e)}}