from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Organization(BaseModel):
    name: Optional[str] = None
    shortname: Optional[str] = None
    longname: Optional[str] = None
    logoUrl: Optional[str] = None
    formats: Optional[List[str]] = None
    purchased: bool = False

class DocsPermissionsResponse(BaseModel):
    data: Dict[str, Any]
    info: Dict[str, Any] = {}
