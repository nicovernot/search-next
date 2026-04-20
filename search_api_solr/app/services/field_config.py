import json
from pathlib import Path


def load_field_configs() -> dict:
    config_dir = Path(__file__).parent / "fields_json"
    configs = {}
    if config_dir.exists():
        for file_path in config_dir.glob("*.json"):
            try:
                with open(file_path, encoding="utf-8") as f:
                    configs[file_path.stem] = json.load(f)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
    return configs

FIELD_CONFIG = load_field_configs()

def get_default_fields() -> list[str]:
    """
    Retourne la liste des champs par défaut à récupérer (fl).
    """
    common = FIELD_CONFIG.get('common', {})
    default = common.get('default', {})
    return default.get('fl', [])

def get_default_search_field() -> str:
    """
    Retourne le champ de recherche par défaut (df).
    """
    common = FIELD_CONFIG.get('common', {})
    default = common.get('default', {})
    return default.get('df', 'text_recherche')

def get_highlight_fields() -> list[str]:
    """
    Retourne la liste des champs à surligner (hl.fl).
    """
    common = FIELD_CONFIG.get('common', {})
    default = common.get('default', {})
    return default.get('hl_fl', [])

def get_qf_params() -> str:
    """Retourne la chaîne de paramètres `qf` formatée pour Solr.
    Le JSON stocke les boosts sous forme d'un dictionnaire `qf` où la clé
    est le nom du champ et la valeur est le facteur de boost (float).
    Cette fonction construit la chaîne "field1^boost1 field2^boost2 …".
    """
    common = FIELD_CONFIG.get('common', {})
    default = common.get('default', {})
    qf_dict = default.get('qf', {})
    # Convert dict to "field^boost" strings, preserving order if possible
    parts = [f"{field}^{boost}" for field, boost in qf_dict.items()]
    return " ".join(parts)

def get_extended_search_params() -> str:
    """Return the additional query‑string fragment defined in the JSON config.
    The fragment includes extra `fl` fields, `defType`, `stopwords`,
    `lowercaseOperators`, `preferLocalShards` and the `qf` boost list.
    """
    common = FIELD_CONFIG.get('common', {})
    default = common.get('default', {})
    return default.get('extended_params', '')
