from pydantic import BaseModel


class SolrCoreInfo(BaseModel):
    name: str
    is_default: bool


class SolrCoresResponse(BaseModel):
    cores: list[SolrCoreInfo]
    default_core: str
