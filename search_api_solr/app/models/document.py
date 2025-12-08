# models/document.py
from typing import Literal, Optional, List, Union
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from datetime import date

PlatformID = Literal["OJ", "OB", "HO", "CO"]
AccessType = Literal["openaccess", "restricted", "exclusive", "embargo", None]

class DocumentBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    type: Literal["article", "book", "chapter", "blogpost", "event", "other"]
    url: str = Field(..., description="URL canonique du document")
    platformID: PlatformID

    title: str
    subtitle: Optional[str] = None
    overview: Optional[str] = Field(None, max_length=500)

    authors: List[str] = Field(default_factory=list)
    first_author: Optional[str] = None

    date: str = Field(..., description="Année ou date formatée JJ-MM-AAAA")
    access_type: Optional[AccessType] = None
    access: Optional[bool] = None  # legacy, à supprimer plus tard

    site_title: Optional[str] = None  # revue OU éditeur
    datemisenligne: Optional[str] = None  # ISO date brute (optionnel)


class JournalArticle(DocumentBase):
    type: Literal["article"] = "article"
    platformID: Literal["OJ"] = "OJ"
    site_title: Optional[str] = Field(None, description="Nom de la revue")


class Book(DocumentBase):
    type: Literal["book"] = "book"
    platformID: Literal["OB"] = "OB"
    site_title: Optional[str] = Field(None, description="Nom de l'éditeur")

    isbn_print: Optional[str] = Field(None, alias="ep_isbnprint")
    isbn_electronic: Optional[str] = Field(None, alias="ep_isbnelec")


class BookChapter(DocumentBase):
    type: Literal["chapter"] = "chapter"
    platformID: Literal["OB"] = "OB"
    site_title: Optional[str] = Field(None, description="Nom de l'éditeur")
    book_title: Optional[str] = None

    isbn_print: Optional[str] = Field(None, alias="ep_isbnprint")
    isbn_electronic: Optional[str] = Field(None, alias="ep_isbnelec")


class BlogPost(DocumentBase):
    type: Literal["blogpost"] = "blogpost"
    platformID: Literal["HO"] = "HO"


class Event(DocumentBase):
    type: Literal["event"] = "event"
    platformID: Literal["CO"] = "CO"


# Union finale pour FastAPI
DocumentResponse = Union[
    JournalArticle,
    Book,
    BookChapter,
    BlogPost,
    Event,
    DocumentBase  # fallback
]