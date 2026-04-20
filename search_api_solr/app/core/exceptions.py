# app/core/exceptions.py
"""Exceptions métier de l'API — codes HTTP stables et compréhensibles."""


class SolrTimeoutError(Exception):
    """Solr n'a pas répondu dans le délai imparti (→ HTTP 503)."""


class SolrInvalidQueryError(Exception):
    """La requête envoyée à Solr est invalide (→ HTTP 400)."""


class SolrUnavailableError(Exception):
    """Solr est injoignable ou renvoie une erreur inattendue (→ HTTP 503)."""
