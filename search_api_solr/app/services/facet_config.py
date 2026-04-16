import json
from pathlib import Path

def load_facet_config_from_json() -> dict:
    config_dir = Path(__file__).parent / "facets_json"
    configs = {}
    if config_dir.exists():
        for file_path in config_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    configs[file_path.stem] = json.load(f)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
    return configs

FACET_CONFIG = load_facet_config_from_json()

def build_solr_to_frontend_facet_mapping() -> dict:
    """
    Construit le mapping des facettes à partir de common.json.
    Utilise le paramètre 'list' qui contient le nom du champ Solr.
    Gère les facettes qui n'ont pas de clé par défaut '' (ex: date avec clés OB/OJ/HO/CO).
    """
    solr_to_frontend_mapping = {}
    common_config = FACET_CONFIG.get('common', {})

    for facet_name, facet_data in common_config.items():
        # Récupérer la configuration par défaut (clé vide "")
        default_facet_config = facet_data.get('', {})
        if default_facet_config and 'list' in default_facet_config:
            # Le champ Solr est le premier élément de la liste
            solr_field_name = default_facet_config['list'][0]
            solr_to_frontend_mapping[facet_name] = solr_field_name
        else:
            # Fallback: prendre la première config disponible (ex: date avec clés OB/OJ/HO/CO)
            for key, config in facet_data.items():
                if isinstance(config, dict) and 'list' in config:
                    solr_field_name = config['list'][0]
                    solr_to_frontend_mapping[facet_name] = solr_field_name
                    break

    return solr_to_frontend_mapping

def build_facet_subcategories() -> dict:
    """
    Construit le mapping des sous-catégories de facettes.
    Par exemple, pour 'type': {'livre': ['livre'], 'article': ['article', 'articlepdf'], ...}
    """
    subcategories = {}
    common_config = FACET_CONFIG.get('common', {})
    
    for facet_name, facet_data in common_config.items():
        default_config = facet_data.get('', {})
        
        # Vérifier s'il y a des options (sous-catégories)
        if default_config and 'options' in default_config:
            facet_subcats = {}
            
            for option_name, option_data in default_config['options'].items():
                if 'list' in option_data:
                    # Stocker la liste des valeurs pour cette sous-catégorie
                    facet_subcats[option_name] = option_data['list']
            
            if facet_subcats:
                subcategories[facet_name] = facet_subcats
    
    return subcategories

# Mapping des noms de facettes conviviales vers les champs Solr
# Chargé dynamiquement depuis common.json
COMMON_FACETS_MAPPING = build_solr_to_frontend_facet_mapping()

# Mapping des sous-catégories de facettes
# Par exemple: {'type': {'livre': ['livre'], 'article': ['article', 'articlepdf'], ...}}
FACET_SUBCATEGORIES = build_facet_subcategories()

def get_filter_values(facet_name: str, filter_value: str) -> list:
    """
    Retourne les valeurs Solr pour un filtre donné.
    Si le filtre correspond à une sous-catégorie, retourne toutes les valeurs associées.
    Sinon, retourne la valeur telle quelle.
    
    Exemple:
        get_filter_values('type', 'article') -> ['article', 'articlepdf']
        get_filter_values('type', 'livre') -> ['livre']
        get_filter_values('platform', 'OB') -> ['OB']
    """
    # Vérifier si cette facette a des sous-catégories
    if facet_name in FACET_SUBCATEGORIES:
        subcats = FACET_SUBCATEGORIES[facet_name]
        
        # Vérifier si la valeur correspond à une sous-catégorie
        if filter_value in subcats:
            return subcats[filter_value]
    
    # Sinon, retourner la valeur telle quelle
    return [filter_value]

def build_platform_specific_facets() -> dict:
    """
    Construit le mapping des facettes spécifiques par plateforme.
    Extrait les facettes de chaque fichier JSON de plateforme (books, journals, hypotheses, calenda).
    
    Returns:
        Dict avec le mapping platformID -> liste de champs Solr spécifiques
        Exemple: {'OB': ['site_title'], 'OJ': ['site_title'], ...}
    """
    platform_facets = {}
    
    # Mapping des noms de fichiers vers les platformID
    platform_mapping = {
        'books': 'OB',
        'journals': 'OJ', 
        'hypotheses': 'HO',
        'calenda': 'CO'
    }
    
    for config_name, platform_id in platform_mapping.items():
        if config_name not in FACET_CONFIG:
            continue
            
        platform_config = FACET_CONFIG[config_name]
        specific_fields = []
        
        # Parcourir toutes les facettes de cette plateforme
        for facet_name, facet_data in platform_config.items():
            default_config = facet_data.get('', {})
            
            if default_config and 'list' in default_config:
                solr_field = default_config['list'][0]
                
                # Ajouter uniquement les facettes spécifiques à cette plateforme
                # (celles qui ne sont pas dans common.json)
                if facet_name not in FACET_CONFIG.get('common', {}):
                    specific_fields.append(solr_field)
        
        if specific_fields:
            platform_facets[platform_id] = specific_fields
    
    return platform_facets

PLATFORM_SPECIFIC_FACETS = build_platform_specific_facets()

# Mapping des champs de recherche (Advanced Query Builder)
# Frontend ID -> Champ Solr indexé (tokenisé de préférence)
SEARCH_FIELDS_MAPPING = {
    "titre": "naked_titre",
    "author": "contributeur_auteur",
    "naked_texte": "naked_texte",
    "disciplinary_field": "platformIndex_*"
}
