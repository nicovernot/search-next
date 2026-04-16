# app/services/interfaces.py
"""
Interfaces pour les services - Définition des contrats pour le découplage
"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class ISearchService(ABC):
    """Interface pour le service de recherche"""
    
    @abstractmethod
    async def execute_cached_search(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Effectue une recherche avec cache"""
        pass

class ISolrClient(ABC):
    """Interface pour le client Solr"""
    
    @abstractmethod
    async def search(self, query: str) -> Dict[str, Any]:
        """Exécute une requête Solr"""
        pass

class ISearchBuilder(ABC):
    """Interface pour le builder de requêtes Solr"""
    
    @abstractmethod
    def build_search_url(self, request: Dict[str, Any]) -> str:
        """Construire une URL de recherche Solr"""
        pass
    
    @abstractmethod
    def build_suggest_url(self, query: str) -> str:
        """Construire une URL de suggestion Solr"""
        pass