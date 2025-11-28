# app/services/search_builder.py (Début du fichier)

from typing import Dict, List, Any
from urllib.parse import urlencode, quote_plus

# Importez vos configurations (simulées ici)
from app.services.facet_config import COMMON_FACETS_MAPPING, PLATFORM_SPECIFIC_FACETS
from app.models.search_models import SearchRequest # Le modèle Pydantic de Searchkit

# Constantes Solr
SOLR_BASE_HANDLER = "/base_search"
SOLR_QUERY_HANDLER = "/select" # Pour les recherches standard et MLT
SOLR_SUGGEST_HANDLER = "/suggest" # Pour l'autocomplétion

# app/services/search_builder.py (Suite)

class SearchBuilder:
    def __init__(self, solr_base_url: str):
        self.solr_base_url = solr_base_url

    # --- A. Construction de la Recherche et des Filtres (q et fq) ---

    def _build_filter_queries(self, filters: List[Dict[str, Any]]) -> List[str]:
        """ Traduit les filtres Searchkit en paramètres Solr fq """
        fq_list = []
        
        # 1. Filtre Permanent (Exemple de sécurité)
        fq_list.append("document_statut:ACTIF")

        # 2. Filtres Dynamiques de l'utilisateur
        for f in filters:
            # Traduire le nom convivial (ex: 'author') en champ Solr (ex: 'contributeurFacetR_auteur')
            solr_field = COMMON_FACETS_MAPPING.get(f['identifier'], f['identifier'])
            value = f['value']
            
            # Simple échappement (doit être plus robuste)
            escaped_value = quote_plus(value) 
            
            fq_list.append(f'{solr_field}:"{escaped_value}"')
            
        return fq_list

    # --- B. Construction des Facettes (facet.field) ---

    def _build_facet_params(self, request: SearchRequest, active_platform: str) -> Dict[str, Any]:
        """ Construit les paramètres facet.field incluant la logique conditionnelle """
        
        facet_params = {}
        # Les facettes communes sont déjà dans le requestHandler de Solr (solrconfig.xml),
        # mais nous les listons ici pour les facettes dynamiques ou spécifiques
        
        facettes_a_demander = []
        
        # 1. Ajout des facettes demandées par Searchkit
        for f in request.facets:
            solr_field = COMMON_FACETS_MAPPING.get(f['identifier'], f['identifier'])
            facettes_a_demander.append(solr_field)
            
        # 2. Ajout des facettes spécifiques si un filtre de plateforme est actif
        if active_platform in PLATFORM_SPECIFIC_FACETS:
            facettes_a_demander.extend(PLATFORM_SPECIFIC_FACETS[active_platform])

        # Construction des paramètres Solr (peut être plus complexe avec JSON Facet API)
        if facettes_a_demander:
            # S'assure qu'on envoie facet=true même si c'est dans solrconfig
            facet_params['facet'] = 'true' 
            # Solr accepte des paramètres multiples pour facet.field
            facet_params['facet.field'] = facettes_a_demander 
            
        return facet_params
        
    # --- C. Autocomplétion (Suggester) ---

    def build_suggest_url(self, query_term: str) -> str:
        """ Construit l'URL pour l'autocomplétion (Suggester) """
        params = {
            'q': query_term,
            'wt': 'json',
            'suggest.q': query_term # Si vous utilisez le composant Suggester standard
        }
        # Utilise le Request Handler dédié (ex: /suggest)
        return f"{self.solr_base_url}{SOLR_SUGGEST_HANDLER}?{urlencode(params)}"
        
    # --- D. More Like This (MLT) ---
    
    def build_mlt_url(self, doc_id: str, limit: int = 5) -> str:
        """ Construit l'URL pour la recherche MLT sur un document donné """
        params = {
            'q': f'id:{doc_id}', # MLT utilise un document source
            'mlt': 'true',       # Active le composant MLT
            'mlt.fl': 'text_recherche', # Champs à utiliser pour la comparaison
            'mlt.mindf': 1,      # Fréquence minimale du terme
            'mlt.count': limit,
            'wt': 'json'
        }
        # Souvent le même handler que la recherche standard ou /mlt
        return f"{self.solr_base_url}{SOLR_QUERY_HANDLER}?{urlencode(params)}"

    # --- E. La Requête de Recherche Principale ---

    def build_search_url(self, request: SearchRequest) -> str:
        """ Construit l'URL complète pour la recherche, facettes, et highlighting """
        
        # 1. Identifier la plateforme active pour la logique conditionnelle des facettes
        active_platform = next(
            (f['value'] for f in request.filters if f['identifier'] == 'platform'), 
            None
        )
        
        # 2. Construction des blocs de la requête
        query_params = {
            'q': request.query.query, # La requête en texte libre (q)
            'df': 'text_recherche',     # Champ par défaut pour le q
            'start': request.pagination.get('from', 0),
            'rows': request.pagination.get('size', 10),
            'wt': 'json'
        }
        
        # 3. Ajouter les Filtres (fq)
        query_params['fq'] = self._build_filter_queries(request.filters)

        # 4. Ajouter les Facettes et le Highlighting
        facet_params = self._build_facet_params(request, active_platform)
        
        highlight_params = {
            'hl': 'true',             # Activation du highlighting
            'hl.fl': 'titre,resume',  # Champs à surligner
            'hl.simple.pre': '<b>',
            'hl.simple.post': '</b>',
        }
        
        # Fusionner tous les paramètres
        all_params = {**query_params, **facet_params, **highlight_params}
        
        # Solr accepte des listes pour 'fq' et 'facet.field', urlencode gère ça
        return f"{self.solr_base_url}{SOLR_BASE_HANDLER}?{urlencode(all_params, doseq=True)}"

    # --- F. Post-traitement ---
    
    # Méthode pour appeler Solr et formater le JSON pour Searchkit...
    # (Dépend de la classe SolrConnector)
    # async def execute_query_and_format(self, url: str) -> Dict[str, Any]: 
    #   ...
