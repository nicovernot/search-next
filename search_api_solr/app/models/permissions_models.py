from typing import Any

from pydantic import BaseModel


class Organization(BaseModel):
    name: str | None = None
    shortname: str | None = None
    longname: str | None = None
    logoUrl: str | None = None
    formats: list[str] | None = None
    purchased: bool = False

class DocsPermissionsResponse(BaseModel):
    data: dict[str, Any]
    info: dict[str, Any] = {}
