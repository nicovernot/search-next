import json
from pathlib import Path
from typing import Dict, List, Optional

def load_field_configs() -> dict:
    config_dir = Path(__file__).parent / "fields_json"
    configs = {}
    if config_dir.exists():
        for file_path in config_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    configs[file_path.stem] = json.load(f)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
    return configs

FIELD_CONFIG = load_field_configs()

def get_default_fields() -> List[str]:
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

def get_highlight_fields() -> List[str]:
    """
    Retourne la liste des champs à surligner (hl.fl).
    """
    common = FIELD_CONFIG.get('common', {})
    default = common.get('default', {})
    return default.get('hl_fl', [])
