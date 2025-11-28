# app/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Union


class Settings(BaseSettings):
    """Configuration de l'application chargée depuis les variables d'environnement"""
    
    # Configuration Solr
    solr_base_url: str = "https://solrslave-sec.labocleo.org/:8983/solr/documents"
    
    # Types de documents nécessitant des parents
    types_needing_parents: List[str] = ["article", "chapter"]
    
    # Champs par défaut à retourner
    default_fields: List[str] = ["id", "url", "title", "idparent", "container_url"]
    
    # Configuration de l'API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    
    # Auth API
    auth_api_url: str = "http://auth.openedition.org/auth_by_url/"
    
    @field_validator('types_needing_parents', 'default_fields', mode='before')
    @classmethod
    def parse_list_from_string(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse une liste depuis une string CSV ou retourne la liste telle quelle"""
        if isinstance(v, str):
            return [item.strip() for item in v.split(',') if item.strip()]
        return v
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Instance globale des settings
settings = Settings()

# Pour compatibilité avec le code existant
SOLR_CONFIG = {
    'base_url': settings.solr_base_url,
    'types_needing_parents': settings.types_needing_parents,
    'fl': settings.default_fields,
}

# Constantes pour les filtres Solr (FQ)
FQ_IDS_ARE = 'id:(%s)'
FQ_SUBSCRIBERS_IS = 'subscribers:%s'
FQ_TYPE_IS = 'type:(%s)'
SOLR_QUERY = '*:*'

