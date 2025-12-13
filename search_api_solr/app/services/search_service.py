# app/services/search_service.py
"""
Service de recherche - Encapsulation de la logique métier
"""
from app.services.interfaces import ISearchService, ISearchBuilder, ISolrClient
from app.models.search_models import SearchRequest
from typing import Dict, Any
import logging

from app.core.logging import get_logger

# logger = logging.getLogger(__name__)

class SearchService(ISearchService):
    """Service de recherche implémentant ISearchService"""
    
    def __init__(self, builder: ISearchBuilder, solr_client: ISolrClient):
        self.builder = builder
        self.solr_client = solr_client
        self.logger = get_logger(__name__)
    
    async def perform_search(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Effectue une recherche complète"""
        try:
            # Construire l'URL de recherche
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
            
            # Exécuter la recherche via le client Solr
            result = await self.solr_client.search(search_url)
            
            # Logging structuré des résultats
            self.logger.info(
                "Search completed successfully",
                extra={
                    "context": {
                        "query": request.get("query"),
                        "num_found": result.get('response', {}).get('numFound', 0),
                        "processing_time": result.get('responseHeader', {}).get('QTime', 0)
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
    """Service de permissions"""
    
    def __init__(self, solr_client: ISolrClient):
        self.solr_client = solr_client
        self.logger = get_logger(__name__)
    
    async def get_document_permissions(self, urls: str, ip: str) -> Dict[str, Any]:
        """Récupère les permissions pour des documents"""
        try:
            # Logique pour récupérer les permissions
            # (À implémenter selon la logique existante)
            return {"data": {"organization": None, "docs": None}, "info": {"status": "ok"}}
        except Exception as e:
            self.logger.error(f"Permissions check failed: {e}")
            return {"data": {"organization": None, "docs": None}, "info": {"error": str(e)}}