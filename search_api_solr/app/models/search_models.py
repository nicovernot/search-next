from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict, Union, Literal

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
    query: str = Field(..., description="Terme de recherche principal", example="histoire")

class FilterModel(BaseModel):
    identifier: str = Field(..., description="Identifiant du filtre (ex: platform, type, author)", example="platform")
    value: str = Field(..., description="Valeur du filtre", example="OB")

class PaginationModel(BaseModel):
    from_: int = Field(0, alias="from", description="Index de départ (offset)", example=0)
    size: int = Field(10, description="Nombre de résultats par page", example=10)
    
    model_config = {"populate_by_name": True}

class FacetModel(BaseModel):
    identifier: str = Field(..., description="Identifiant de la facette", example="platform")
    type: Literal["list", "query"] = Field("list", description="Type de facette: 'list' (champ) ou 'query' (requête)", example="list")
    value: Optional[str] = Field(None, description="Valeur pour le type 'query' (ex: subscribers:amu)", example=None)
    label: Optional[str] = Field(None, description="Libellé de la facette", example="Plateforme")
    size: Optional[int] = Field(5, description="Nombre de valeurs à retourner", example=5)

class SearchRequest(BaseModel):
    """Modèle de requête compatible avec Searchkit et SearchBuilder"""
    query: QueryModel
    filters: List[FilterModel] = Field(default=[], description="Liste des filtres actifs")
    pagination: PaginationModel = Field(default_factory=PaginationModel, description="Paramètres de pagination")
    facets: List[FacetModel] = Field(default=[], description="Liste des facettes demandées")

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": {"query": "révolution"},
                "filters": [
                    {"identifier": "platform", "value": "OB"},
                    {"identifier": "type", "value": "livre"}
                ],
                "pagination": {"from": 0, "size": 20},
                "facets": [
                    {"identifier": "platform", "type": "list"},
                    {"identifier": "subscribers_amu", "type": "query", "value": "subscribers:amu"}
                ]
            }
        }
    }

