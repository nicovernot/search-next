# app/core/exceptions.py
"""Exceptions métier de l'API — codes HTTP stables et compréhensibles."""


class SolrTimeoutError(Exception):
    """Solr n'a pas répondu dans le délai imparti (→ HTTP 503)."""


class SolrInvalidQueryError(Exception):
    """La requête envoyée à Solr est invalide (→ HTTP 400)."""


class SolrUnavailableError(Exception):
    """Solr est injoignable ou renvoie une erreur inattendue (→ HTTP 503)."""


class SolrCoreNotFoundError(Exception):
    """Le core Solr demandé n'existe pas dans la configuration (→ HTTP 404)."""

    core_name: str

    def __init__(self, core_name: str):
        self.core_name = core_name
        super().__init__(f"Unknown Solr core: '{core_name}'")
