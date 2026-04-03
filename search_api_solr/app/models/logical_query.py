from pydantic import BaseModel, Field
from typing import List, Union, Literal, Optional

class QueryRule(BaseModel):
    field: str = Field(..., description="Le champ Solr à interroger")
    operator: str = Field(..., description="L'opérateur (ex: '=', 'contains', 'begins_with')")
    value: str = Field(..., description="La valeur recherchée")

class QueryGroup(BaseModel):
    combinator: Literal["and", "or"] = Field("and", description="L'opérateur logique entre les règles")
    not_: bool = Field(False, alias="not", description="Si vrai, inverse la logique du groupe")
    rules: List[Union[QueryRule, "QueryGroup"]] = Field(..., description="Liste de règles ou sous-groupes")

# Pour permettre la récursion dans Pydantic v2
QueryGroup.model_rebuild()
