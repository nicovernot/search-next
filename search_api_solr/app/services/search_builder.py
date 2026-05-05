from typing import Any
from urllib.parse import urlencode

from app.core.logging import get_logger
from app.models.search_models import SearchRequest

logger = get_logger(__name__)
from app.services.facet_config import (
    COMMON_FACETS_MAPPING,
    PLATFORM_SPECIFIC_FACETS,
    get_filter_values,
)
from app.services.field_config import (
    get_default_fields,
    get_default_search_field,
    get_qf_params,
)
from app.services.interfaces import ISearchBuilder
from app.services.query_logic_parser import QueryLogicParser

SOLR_BASE_HANDLER = "/select"
SOLR_QUERY_HANDLER = "/select"
SOLR_SUGGEST_HANDLER = "/suggest"


class SearchBuilder(ISearchBuilder):
    def __init__(self, solr_base_url: str):
        self.solr_base_url = solr_base_url

    # --- A. Construction de la Recherche et des Filtres (q et fq) ---

    def _escape_solr_value(self, value: str) -> str:
        """Escape special characters for Solr phrase query (inside quotes)"""
        # We only need to escape " and \ when the value is inside quotes
        return value.replace("\\", "\\\\").replace('"', '\\"')

    def _build_filter_queries(self, filters: list[Any]) -> list[str]:
        """Traduit les filtres en paramètres Solr fq"""
        fq_list = []
        for f in filters:
            # Traduire le nom convivial (ex: 'author') en champ Solr (ex: 'contributeurFacetR_auteur')
            # f est un FilterModel, donc on utilise l'accès par attribut
            identifier = (
                f.identifier if hasattr(f, "identifier") else f.get("identifier")
            )
            value = f.value if hasattr(f, "value") else f.get("value")

            solr_field = COMMON_FACETS_MAPPING.get(identifier, identifier)

            # Obtenir les valeurs Solr (avec expansion des sous-catégories si applicable)
            solr_values = get_filter_values(identifier, value)

            # Construire le filtre
            if len(solr_values) == 1:
                # Une seule valeur: échappement Solr standard (pas URL encode)
                escaped_value = self._escape_solr_value(solr_values[0])
                fq_list.append(f'{solr_field}:"{escaped_value}"')
            else:
                # Plusieurs valeurs: utiliser OR
                # type:(article OR articlepdf)
                # Note: ici on suppose que les sous-catégories sont "safe" ou on les échappe aussi
                escaped_values = [self._escape_solr_value(v) for v in solr_values]
                values_str = '" OR "'.join(escaped_values)
                # On met des guillemets autour de chaque valeur pour être sûr
                fq_list.append(f'{solr_field}:("{values_str}")')

        return fq_list

    # --- B. Construction des Facettes (facet.field) ---

    def _build_facet_params(
        self, request: SearchRequest, active_platform: str
    ) -> dict[str, Any]:
        """Construit les paramètres facet.field incluant la logique conditionnelle"""

        facet_params = {}
        # Les facettes communes sont déjà dans le requestHandler de Solr (solrconfig.xml),
        # mais nous les listons ici pour les facettes dynamiques ou spécifiques

        facettes_a_demander = []
        facettes_query = []

        # 1. Ajout des facettes demandées par Searchkit
        for f in request.facets:
            # Vérifier le type de facette (support dict et Pydantic)
            if isinstance(f, dict):
                facet_type = f.get("type")
                identifier = f.get("identifier")
                value = f.get("value")
            else:
                facet_type = getattr(f, "type", None)
                identifier = getattr(f, "identifier", None)
                value = getattr(f, "value", None)

            if facet_type == "query":
                # Facette par requête (ex: subscribers:amu)
                if value:
                    facettes_query.append(value)
            else:
                # Facette standard (champ)
                solr_field = COMMON_FACETS_MAPPING.get(identifier, identifier)
                facettes_a_demander.append(solr_field)

        # 2. Ajout des facettes spécifiques si un filtre de plateforme est actif
        if active_platform in PLATFORM_SPECIFIC_FACETS:
            facettes_a_demander.extend(PLATFORM_SPECIFIC_FACETS[active_platform])

        # Construction des paramètres Solr (peut être plus complexe avec JSON Facet API)
        if facettes_a_demander or facettes_query:
            # S'assure qu'on envoie facet=true même si c'est dans solrconfig
            facet_params["facet"] = "true"

            if facettes_a_demander:
                # Solr accepte des paramètres multiples pour facet.field
                facet_params["facet.field"] = facettes_a_demander

            if facettes_query:
                # Solr accepte des paramètres multiples pour facet.query
                facet_params["facet.query"] = facettes_query

            # Paramètres de sécurité pour les facettes
            facet_params["facet.mincount"] = 1
            facet_params["facet.limit"] = 50  # Évite les explosions de mémoire côté client

        return facet_params

    # --- C. Autocomplétion (Suggester) ---

    def build_suggest_url(self, query_term: str) -> str:
        """Construit l'URL pour l'autocomplétion (Suggester)"""
        params = {
            "q": query_term,
            "wt": "json",
            "suggest.q": query_term,  # Si vous utilisez le composant Suggester standard
        }
        # Utilise le Request Handler dédié (ex: /suggest)
        return f"{self.solr_base_url}{SOLR_SUGGEST_HANDLER}?{urlencode(params)}"

    # --- D. More Like This (MLT) ---

    def build_mlt_url(self, doc_id: str, limit: int = 5) -> str:
        """Construit l'URL pour la recherche MLT sur un document donné"""
        params = {
            "q": f"id:{doc_id}",  # MLT utilise un document source
            "mlt": "true",  # Active le composant MLT
            "mlt.fl": "text_recherche",  # Champs à utiliser pour la comparaison
            "mlt.mindf": 1,  # Fréquence minimale du terme
            "mlt.count": limit,
            "wt": "json",
        }
        # Souvent le même handler que la recherche standard ou /mlt
        return f"{self.solr_base_url}{SOLR_QUERY_HANDLER}?{urlencode(params)}"

    # --- E. La Requête de Recherche Principale ---

    def build_search_url(self, request: SearchRequest) -> str:
        """Construit l'URL complète pour la recherche et les facettes."""
        # 1. Plateforme active pour la logique conditionnelle des facettes
        active_platform = next(
            (f.value for f in request.filters if f.identifier == "platform"), None
        )

        # 2. Pagination
        start = request.pagination.from_
        rows = request.pagination.size

        query_params = {
            "q": request.query.query or "*:*",  # Défaut à *:* si vide (Recherche Avancée seule)
            "defType": "edismax",  # Requis pour utiliser qf (Query Fields)
            "df": get_default_search_field(),  # Champ par défaut pour le q
            "fl": get_default_fields(),  # Champs à retourner
            "qf": get_qf_params(),  # Paramètres de boost (Query Fields)
            "start": start,
            "rows": rows,
            "wt": "json",
        }

        if request.sort:
            query_params["sort"] = request.sort

        # 3. Ajouter les Filtres (fq)
        fq_list = self._build_filter_queries(request.filters)

        if request.logical_query:
            try:
                logical_fq = QueryLogicParser.convert_to_solr_query_string(request.logical_query)
                if logical_fq:
                    fq_list.append(logical_fq)
            except Exception as e:
                logger.error("Error parsing logical query: %s", e)

        query_params["fq"] = fq_list

        # 4. Ajouter les Facettes
        facet_params = self._build_facet_params(request, active_platform)

        # Fusionner tous les paramètres
        all_params = {**query_params, **facet_params}

        # Solr accepte des listes pour 'fq' et 'facet.field', urlencode gère ça
        return f"{self.solr_base_url}{SOLR_BASE_HANDLER}?{urlencode(all_params, doseq=True)}"
