from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class SearchQuery(BaseModel):
    q: str
    filters: Optional[List[str]] = None
    page: int = 1
    page_size: int = 10

class SearchResponse(BaseModel):
    results: List[Any]
    total: int
    facets: Optional[Any] = None

# Modèles pour Searchkit (utilisés par SearchBuilder)
class QueryModel(BaseModel):
    query: str

class FilterModel(BaseModel):
    identifier: str
    value: str

class SearchRequest(BaseModel):
    """Modèle de requête compatible avec Searchkit et SearchBuilder"""
    query: QueryModel
    filters: List[FilterModel] = []
    pagination: Dict[str, int] = {'from': 0, 'size': 10}
    facets: List[Dict[str, Any]] = []

