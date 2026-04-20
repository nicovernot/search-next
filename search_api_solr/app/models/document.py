# models/document.py
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PlatformID = Literal["OJ", "OB", "HO", "CO"]
AccessType = Literal["openaccess", "restricted", "exclusive", "embargo", None]

class DocumentBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    type: Literal["article", "book", "chapter", "blogpost", "event", "other"]
    url: str = Field(..., description="URL canonique du document")
    platformID: PlatformID

    title: str
    subtitle: str | None = None
    overview: str | None = Field(None, max_length=500)

    authors: list[str] = Field(default_factory=list)
    first_author: str | None = None

    date: str = Field(..., description="Année ou date formatée JJ-MM-AAAA")
    access_type: AccessType | None = None
    access: bool | None = None  # legacy, à supprimer plus tard

    site_title: str | None = None  # revue OU éditeur
    datemisenligne: str | None = None  # ISO date brute (optionnel)


class JournalArticle(DocumentBase):
    type: Literal["article"] = "article"
    platformID: Literal["OJ"] = "OJ"
    site_title: str | None = Field(None, description="Nom de la revue")


class Book(DocumentBase):
    type: Literal["book"] = "book"
    platformID: Literal["OB"] = "OB"
    site_title: str | None = Field(None, description="Nom de l'éditeur")

    isbn_print: str | None = Field(None, alias="ep_isbnprint")
    isbn_electronic: str | None = Field(None, alias="ep_isbnelec")


class BookChapter(DocumentBase):
    type: Literal["chapter"] = "chapter"
    platformID: Literal["OB"] = "OB"
    site_title: str | None = Field(None, description="Nom de l'éditeur")
    book_title: str | None = None

    isbn_print: str | None = Field(None, alias="ep_isbnprint")
    isbn_electronic: str | None = Field(None, alias="ep_isbnelec")


class BlogPost(DocumentBase):
    type: Literal["blogpost"] = "blogpost"
    platformID: Literal["HO"] = "HO"


class Event(DocumentBase):
    type: Literal["event"] = "event"
    platformID: Literal["CO"] = "CO"


# Union finale pour FastAPI
DocumentResponse = JournalArticle | Book | BookChapter | BlogPost | Event | DocumentBase
