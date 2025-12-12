# app/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Union, Optional
import os


def get_environment() -> str:
    """Détermine l'environnement actuel"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    return env if env in ["development", "production", "test", "staging"] else "development"


def get_cors_origins(environment: str) -> List[str]:
    """Récupère les origines CORS par défaut selon l'environnement"""
    cors_origins_env = os.getenv("CORS_ORIGINS", "")
    
    if cors_origins_env:
        return [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
    
    # Valeurs par défaut selon l'environnement
    if environment == "production":
        return ["https://search.openedition.org", "https://www.openedition.org"]
    elif environment == "staging":
        return ["https://staging.search.openedition.org", "https://search.openedition.org"]
    elif environment == "test":
        return ["http://localhost:8007"]
    else:  # development
        return ["http://localhost:3009", "http://localhost:3000", "http://127.0.0.1:3009"]


class Settings(BaseSettings):
    """Configuration de l'application chargée depuis les variables d'environnement"""
    
    # Environnement
    environment: str = get_environment()
    
    # Configuration Solr
    solr_base_url: str = "https://solrslave-sec.labocleo.org/solr/documents"
    
    # Types de documents nécessitant des parents
    types_needing_parents: Union[str, List[str]] = "article,chapter"
    
    # Champs par défaut à retourner
    default_fields: Union[str, List[str]] = "id,url,title,idparent,container_url"
    
    # Configuration de l'API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    
    # Auth API
    auth_api_url: str = "http://auth.openedition.org/auth_by_url/"
    
    # Dev mode
    dev: bool = False
    test_ip: str = "193.48.45.2"  # IP de test par défaut
    
    # Configuration CORS
    cors_origins: Union[str, List[str]] = get_cors_origins(environment)
    cors_allow_credentials: bool = True
    cors_allow_methods: Union[str, List[str]] = "GET,POST,PUT,DELETE,OPTIONS"
    cors_allow_headers: Union[str, List[str]] = "Accept,Authorization,Content-Type,X-Requested-With,X-CSRF-Token"
    cors_expose_headers: Union[str, List[str]] = "X-Total-Count,X-Pagination"
    cors_max_age: int = 86400  # 24 heures en développement, sera ajusté par environnement
    
    # Configuration de logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO" if environment == "production" else "DEBUG")
    
    # Configuration de sécurité
    enable_https_redirect: bool = False  # Sera ajusté par le validator
    trusted_hosts: Union[str, List[str]] = []
    
    @field_validator('types_needing_parents', 'default_fields', 'cors_origins', 'cors_allow_methods', 'cors_allow_headers', 'cors_expose_headers', 'trusted_hosts', mode='before')
    @classmethod
    def parse_list_from_string(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse une liste depuis une string CSV ou JSON, ou retourne la liste telle quelle"""
        if isinstance(v, str):
            # Essayer de parser comme JSON d'abord
            v = v.strip()
            if v.startswith('[') and v.endswith(']'):
                try:
                    import json
                    return json.loads(v)
                except:
                    pass
            # Sinon, parser comme CSV
            return [item.strip() for item in v.split(',') if item.strip()]
        return v if isinstance(v, list) else []
    
    @field_validator('environment')
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Valide que l'environnement est valide"""
        valid_envs = ["development", "production", "test", "staging"]
        if v not in valid_envs:
            raise ValueError(f"ENVIRONMENT must be one of: {', '.join(valid_envs)}")
        return v
    
    @field_validator('enable_https_redirect')
    @classmethod
    def set_https_redirect_by_environment(cls, v: bool, info) -> bool:
        """Active la redirection HTTPS uniquement en production"""
        environment = info.data.get('environment', 'development')
        return environment == "production"
    
    @field_validator('cors_max_age')
    @classmethod
    def set_cors_max_age_by_environment(cls, v: int, info) -> int:
        """Ajuste cors_max_age selon l'environnement"""
        environment = info.data.get('environment', 'development')
        
        if environment == "production":
            return 3600  # 1 heure en production
        elif environment == "test":
            return 60  # 1 minute en test
        else:
            return 86400  # 24 heures en développement/staging
    
    @field_validator('cors_allow_methods', 'cors_allow_headers')
    @classmethod
    def adjust_cors_for_production(cls, v: List[str], info) -> List[str]:
        """Ajuste les méthodes et headers CORS pour la production"""
        environment = info.data.get('environment', 'development')
        
        if environment == "production":
            if info.field_name == "cors_allow_methods":
                # En production, seulement les méthodes nécessaires
                return [method for method in v if method in ["GET", "POST", "OPTIONS"]]
            elif info.field_name == "cors_allow_headers":
                # En production, headers minimaux
                return [header for header in v if header in ["Accept", "Authorization", "Content-Type"]]
        
        return v
    
    @field_validator('trusted_hosts')
    @classmethod
    def set_trusted_hosts_by_environment(cls, v: List[str], info) -> List[str]:
        """Configure les hôtes de confiance selon l'environnement"""
        environment = info.data.get('environment', 'development')
        
        if not v:  # Si non configuré dans .env
            if environment == "production":
                return ["search.openedition.org", "www.openedition.org"]
            elif environment == "staging":
                return ["staging.search.openedition.org"]
        
        return v
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_parse_enums=None,  # Désactive le parsing automatique pour permettre au validator de gérer
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

