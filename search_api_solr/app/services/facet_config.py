import json
from pathlib import Path

def load_facet_configs() -> dict:
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

FACET_CONFIG = load_facet_configs()

# Mapping des noms de facettes conviviales vers les champs Solr
COMMON_FACETS_MAPPING = {
    'author': 'contributeurFacetR_auteur',
    'publisher': 'editeurFacetR',
    'language': 'langueFacetR',
    'type': 'typeFacetR',
    'platform': 'platformeFacetR',
    'collection': 'collectionFacetR',
    'year': 'anneeFacetR',
}

# Facettes spécifiques par plateforme
PLATFORM_SPECIFIC_FACETS = {
    'openedition-books': ['editeurFacetR', 'collectionFacetR'],
    'openedition-journals': ['revueFacetR'],
    'hypotheses': ['blogFacetR'],
    'calenda': ['categorieCalendaFacetR'],
}
