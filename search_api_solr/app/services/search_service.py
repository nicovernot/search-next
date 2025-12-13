# app/services/search_service.py
"""
Service de recherche - Encapsulation de la logique métier
"""
from app.services.interfaces import ISearchService, ISearchBuilder, ISolrClient
from app.models.search_models import SearchRequest
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class SearchService(ISearchService):
    """Service de recherche implémentant ISearchService"""
    
    def __init__(self, builder: ISearchBuilder, solr_client: ISolrClient):
        self.builder = builder
        self.solr_client = solr_client
    
    async def perform_search(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Effectue une recherche complète"""
        try:
            # Construire l'URL de recherche
            search_url = self.builder.build_search_url(request)
            logger.debug(f"Search URL: {search_url}")
            
            # Exécuter la recherche via le client Solr
            result = await self.solr_client.search(search_url)
            
            logger.info(f"Search completed: {result.get('response', {}).get('numFound', 0)} results")
            return result
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise

class SuggestService:
    """Service de suggestion"""
    
    def __init__(self, builder: ISearchBuilder, solr_client: ISolrClient):
        self.builder = builder
        self.solr_client = solr_client
    
    async def suggest(self, query: str) -> Dict[str, Any]:
        """Effectue une suggestion"""
        try:
            # Construire l'URL de suggestion
            suggest_url = self.builder.build_suggest_url(query)
            logger.debug(f"Suggest URL: {suggest_url}")
            
            # Exécuter la suggestion via le client Solr
            result = await self.solr_client.search(suggest_url)
            
            logger.info(f"Suggest completed for query: {query}")
            return result
            
        except Exception as e:
            logger.error(f"Suggest failed: {e}")
            # Retourner une réponse vide en cas d'erreur pour ne pas bloquer l'UI
            return {"suggest": {"default": {query: {"numFound": 0, "suggestions": []}}}}

class PermissionsService:
    """Service de permissions"""
    
    def __init__(self, solr_client: ISolrClient):
        self.solr_client = solr_client
    
    async def get_document_permissions(self, urls: str, ip: str) -> Dict[str, Any]:
        """Récupère les permissions pour des documents"""
        try:
            # Logique pour récupérer les permissions
            # (À implémenter selon la logique existante)
            return {"data": {"organization": None, "docs": None}, "info": {"status": "ok"}}
        except Exception as e:
            logger.error(f"Permissions check failed: {e}")
            return {"data": {"organization": None, "docs": None}, "info": {"error": str(e)}}