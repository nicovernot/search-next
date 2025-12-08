# services/document_mapper.py
from models.document import (
    JournalArticle, Book, BookChapter, BlogPost, Event, DocumentBase
)

TYPE_NORMALIZATION = {
    "article": "article",
    "review": "article",
    "compte-rendu": "article",
    "livre": "book",           # ← ici !
    "ouvrage": "book",
    "monographie": "book",
    "chapitre": "chapter",
    "billet": "blogpost",
    "événement": "event",
    "colloque": "event",
}

class DocumentMapper:
    @staticmethod
    def from_solr(raw: dict) -> DocumentResponse:
        platform = raw.get("platformID")
        raw_type = str(raw.get("type_s", "")).lower()

        normalized_type = TYPE_NORMALIZATION.get(raw_type, "other")

        authors = raw.get("authFullName_s") or []
        if isinstance(authors, str):
            authors = [authors]

        common = {
            "type": normalized_type,
            "url": raw.get("uri") or raw.get("url", ""),
            "platformID": platform,
            "title": raw.get("naked_titre") or raw.get("title_display", ""),
            "subtitle": raw.get("soustitre_s"),
            "overview": raw.get("overview"),
            "authors": authors,
            "first_author": authors[0] if authors else None,
            "access_type": raw.get("via"),
            "access": raw.get("access", False),
            "site_title": raw.get("journalTitle_s") or raw.get("site_title"),
            "datemisenligne": raw.get("producedDate_tdate"),
            "date": raw.get("anneedatepubli") or raw.get("producedDateY_i", "") or "Inconnue",
        }

        if platform == "OJ":
            return JournalArticle(**common)

        elif platform == "OB":
            if normalized_type == "book":
                return Book(
                    **common,
                    isbn_print=raw.get("ep_isbnprint"),
                    isbn_electronic=raw.get("ep_isbnelec")
                )
            else:
                return BookChapter(
                    **common,
                    book_title=raw.get("inBook_s"),
                    isbn_print=raw.get("ep_isbnprint"),
                    isbn_electronic=raw.get("ep_isbnelec")
                )

        elif platform == "HO":
            return BlogPost(**common)

        elif platform == "CO":
            return Event(**common)

        return DocumentBase(**common)