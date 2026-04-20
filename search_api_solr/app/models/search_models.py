from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from app.models.logical_query import QueryGroup


class SearchQuery(BaseModel):
    q: str
    filters: list[str] | None = None
    page: int = 1
    page_size: int = 10


class SearchResponse(BaseModel):
    results: list[Any]
    total: int
    facets: Any | None = None


class SuggestResponse(BaseModel):
    suggestions: list[str]


class FacetsConfigResponse(BaseModel):
    facets: list[Any]
    search_fields: list[str]

    model_config = {"extra": "allow"}


# Modèles pour Searchkit (utilisés par SearchBuilder)
class QueryModel(BaseModel):
    query: str = Field(
        ..., description="Terme de recherche principal", example="histoire"
    )

    @field_validator("query")
    @classmethod
    def sanitize_query(cls, v: str) -> str:
        # Échappement des caractères spéciaux Solr
        dangerous_chars = [':', 'AND', 'OR', 'NOT', '(', ')', '[', ']', '{', '}']
        for char in dangerous_chars:
            if char in v:
                v = v.replace(char, f"\\{char}")
        return v


class FilterModel(BaseModel):
    identifier: str = Field(
        ...,
        description="Identifiant du filtre (ex: platform, type, author)",
        example="platform",
    )
    value: str = Field(..., description="Valeur du filtre", example="OB")


class PaginationModel(BaseModel):
    from_: int = Field(
        0, alias="from", description="Index de départ (offset)", example=0
    )
    size: int = Field(10, description="Nombre de résultats par page", example=10)

    model_config = {"populate_by_name": True}


class FacetModel(BaseModel):
    identifier: str = Field(
        ..., description="Identifiant de la facette", example="platform"
    )
    type: Literal["list", "query"] = Field(
        "list",
        description="Type de facette: 'list' (champ) ou 'query' (requête)",
        example="list",
    )
    value: str | None = Field(
        None,
        description="Valeur pour le type 'query' (ex: subscribers:amu)",
        example=None,
    )
    label: str | None = Field(
        None, description="Libellé de la facette", example="Plateforme"
    )
    size: int | None = Field(
        5, description="Nombre de valeurs à retourner", example=5
    )


class SearchRequest(BaseModel):
    """Modèle de requête compatible avec Searchkit et SearchBuilder"""

    query: QueryModel
    logical_query: QueryGroup | None = Field(
        None, description="Requête logique complexe (AND/OR/NOT récursif)"
    )
    filters: list[FilterModel] = Field(
        default=[], description="Liste des filtres actifs"
    )
    pagination: PaginationModel = Field(
        default_factory=PaginationModel, description="Paramètres de pagination"
    )
    facets: list[FacetModel] = Field(
        default=[], description="Liste des facettes demandées"
    )
    sort: str | None = Field(
        None, description="Critères de tri (ex: date desc)", example="date desc"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": {"query": "révolution"},
                "filters": [
                    {"identifier": "platform", "value": "OB"},
                    {"identifier": "type", "value": "livre"},
                ],
                "pagination": {"from": 0, "size": 20},
                "facets": [
                    {"identifier": "platform", "type": "list"},
                    {
                        "identifier": "subscribers_amu",
                        "type": "query",
                        "value": "subscribers:amu",
                    },
                ],
            }
        }
    }
