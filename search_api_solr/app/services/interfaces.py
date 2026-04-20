# app/services/interfaces.py
"""
Interfaces pour les services - Définition des contrats pour le découplage
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.models.search_models import SearchRequest


class ISearchService(ABC):
    """Interface pour le service de recherche"""

    @abstractmethod
    async def execute_cached_search(self, request: SearchRequest) -> dict[str, Any]:
        """Effectue une recherche avec cache"""
        pass


class ISolrClient(ABC):
    """Interface pour le client Solr"""

    @abstractmethod
    async def search(self, query: str) -> dict[str, Any]:
        """Exécute une requête Solr"""
        pass


class ISearchBuilder(ABC):
    """Interface pour le builder de requêtes Solr"""

    @abstractmethod
    def build_search_url(self, request: SearchRequest) -> str:
        """Construire une URL de recherche Solr à partir d'un SearchRequest typé"""
        pass

    @abstractmethod
    def build_suggest_url(self, query: str) -> str:
        """Construire une URL de suggestion Solr"""
        pass
