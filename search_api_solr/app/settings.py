# app/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, model_validator
from typing import List, Union, Optional
import os
import json


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
        return ["http://localhost:8007", "http://localhost:3009", "http://127.0.0.1:3009", "http://127.0.0.1:8007"]
    else:  # development
        return ["http://localhost:3009", "http://localhost:3000", "http://127.0.0.1:3009", "http://127.0.0.1:3000", "http://0.0.0.0:3007", "http://0.0.0.0:3009", "http://localhost:3007", "http://127.0.0.1:3007"]


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
    cors_origins: Optional[Union[str, List[str]]] = None
    cors_allow_credentials: bool = True
    cors_allow_methods: Union[str, List[str]] = "GET,POST,PUT,DELETE,OPTIONS"
    cors_allow_headers: Union[str, List[str]] = "Accept,Accept-Language,Authorization,Content-Language,Content-Type,X-Requested-With,X-CSRF-Token"
    cors_expose_headers: Union[str, List[str]] = "X-Total-Count,X-Pagination"
    cors_max_age: int = 86400  # 24 heures en développement, sera ajusté par environnement
    
    # Configuration de logging
    log_level: Optional[str] = None
    
    # Configuration Redis
    redis_url: str = "redis://redis:6379/0"
    redis_enabled: bool = True
    redis_ttl_search: int = 300  # 5 minutes pour les recherches
    redis_ttl_suggest: int = 3600  # 1 heure pour les suggestions
    redis_ttl_permissions: int = 1800  # 30 minutes pour les permissions
    
    # Configuration Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_default_requests: int = 100
    rate_limit_default_window: int = 60
    rate_limit_burst_multiplier: float = 1.0
    
    # Endpoint-specific limits (JSON format)
    rate_limit_endpoints: str = ""
    
    # Client type limits
    rate_limit_authenticated_multiplier: float = 2.0
    rate_limit_ip_whitelist: Union[str, List[str]] = ""
    
    # Backend configuration
    rate_limit_backend: str = "redis"
    rate_limit_redis_key_prefix: str = "rate_limit:"
    
    # Monitoring
    rate_limit_log_violations: bool = True
    rate_limit_metrics_enabled: bool = True
    
    # Configuration Base de Données
    database_url: str = "postgresql://search_user:search_password@postgres:5432/search_db"
    
    # Configuration Authentification (JWT)
    secret_key: str = "your-secret-key-for-development" # À changer en production !
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    @model_validator(mode='after')
    def set_default_log_level(self):
        """Définit le niveau de log par défaut selon l'environnement"""
        if self.log_level is None:
            self.log_level = "INFO" if self.environment == "production" else "DEBUG"
        return self
    
    @model_validator(mode='after')
    def set_default_cors_origins(self):
        """Définit les origines CORS par défaut selon l'environnement si non spécifié"""
        if self.cors_origins is None:
            self.cors_origins = get_cors_origins(self.environment)
        return self
    
    # Configuration de sécurité
    enable_https_redirect: bool = False  # Sera ajusté par le validator
    trusted_hosts: Union[str, List[str]] = []
    
    @field_validator('types_needing_parents', 'default_fields', 'cors_origins', 'cors_allow_methods', 'cors_allow_headers', 'cors_expose_headers', 'trusted_hosts', 'rate_limit_ip_whitelist', mode='before')
    @classmethod
    def parse_list_from_string(cls, v: Union[str, List[str], None]) -> Union[List[str], None]:
        """Parse une liste depuis une string CSV ou JSON, ou retourne la liste telle quelle"""
        if v is None:
            return None
        if isinstance(v, str):
            # Essayer de parser comme JSON d'abord
            v = v.strip()
            if v.startswith('[') and v.endswith(']'):
                try:
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
    
    @field_validator('redis_ttl_search', 'redis_ttl_suggest', 'redis_ttl_permissions')
    @classmethod
    def adjust_redis_ttl_by_environment(cls, v: int, info) -> int:
        """Ajuste les TTL Redis selon l'environnement"""
        environment = info.data.get('environment', 'development')
        
        if environment == "test":
            return 60  # TTL courts en test (1 minute)
        elif environment == "production":
            # TTL plus longs en production
            if info.field_name == "redis_ttl_search":
                return 600  # 10 minutes pour les recherches
            elif info.field_name == "redis_ttl_suggest":
                return 7200  # 2 heures pour les suggestions
            elif info.field_name == "redis_ttl_permissions":
                return 3600  # 1 heure pour les permissions
        
        return v  # Valeurs par défaut pour development/staging
    
    @field_validator('rate_limit_default_requests')
    @classmethod
    def set_rate_limit_requests_by_environment(cls, v: int, info) -> int:
        """Ajuste les limites de requêtes selon l'environnement si non spécifié"""
        # Si la valeur a été explicitement définie via env var, la conserver
        if os.getenv('RATE_LIMIT_DEFAULT_REQUESTS'):
            return v
            
        environment = info.data.get('environment', 'development')
        
        if environment == "test":
            return 10  # Limite basse pour les tests
        elif environment == "production":
            return 100  # Limite de production
        elif environment == "development":
            return 1000  # Limite élevée pour le développement
        else:  # staging
            return 200  # Limite intermédiaire pour staging
        
        return v
    
    @field_validator('rate_limit_endpoints')
    @classmethod
    def set_default_endpoint_limits_by_environment(cls, v: str, info) -> str:
        """Définit les limites par endpoint selon l'environnement si non spécifié"""
        # Si explicitement configuré via env var, conserver la valeur
        if v.strip() or os.getenv('RATE_LIMIT_ENDPOINTS'):
            return v
            
        environment = info.data.get('environment', 'development')
        
        if environment == "production":
            return json.dumps({
                "search": {"requests": 50, "window": 60},
                "suggest": {"requests": 200, "window": 60}
            })
        elif environment == "test":
            return json.dumps({
                "search": {"requests": 5, "window": 60},
                "suggest": {"requests": 20, "window": 60}
            })
        elif environment == "development":
            return json.dumps({
                "search": {"requests": 500, "window": 60},
                "suggest": {"requests": 2000, "window": 60}
            })
        else:  # staging
            return json.dumps({
                "search": {"requests": 100, "window": 60},
                "suggest": {"requests": 400, "window": 60}
            })
    
    @field_validator('rate_limit_backend')
    @classmethod
    def validate_rate_limit_backend(cls, v: str) -> str:
        """Valide le backend de rate limiting"""
        if v not in ['redis', 'memory']:
            raise ValueError("rate_limit_backend must be 'redis' or 'memory'")
        return v
    
    @field_validator('rate_limit_default_requests', 'rate_limit_default_window')
    @classmethod
    def validate_positive_rate_limit_values(cls, v: int) -> int:
        """Valide que les valeurs de rate limiting sont positives"""
        if v <= 0:
            raise ValueError("Rate limit values must be positive")
        return v
    
    @field_validator('rate_limit_burst_multiplier', 'rate_limit_authenticated_multiplier')
    @classmethod
    def validate_rate_limit_multipliers(cls, v: float) -> float:
        """Valide que les multiplicateurs sont >= 1.0"""
        if v < 1.0:
            raise ValueError("Rate limit multipliers must be >= 1.0")
        return v
    
    def get_rate_limit_config(self):
        """Crée une configuration de rate limiting à partir des settings"""
        from .models.rate_limit_models import RateLimitConfig
        
        # Parse endpoint configuration
        endpoints = {}
        if self.rate_limit_endpoints.strip():
            try:
                endpoints_data = json.loads(self.rate_limit_endpoints)
                from .models.rate_limit_models import RateLimit
                
                for endpoint, config in endpoints_data.items():
                    endpoints[endpoint] = RateLimit(
                        requests=config['requests'],
                        window_seconds=config['window'],
                        burst_multiplier=config.get('burst_multiplier', 1.0)
                    )
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                # Log error but continue with empty endpoints
                print(f"Warning: Invalid rate limit endpoints configuration: {e}")
        
        # Parse IP whitelist
        ip_whitelist = self.rate_limit_ip_whitelist if isinstance(self.rate_limit_ip_whitelist, list) else []
        
        return RateLimitConfig(
            enabled=self.rate_limit_enabled,
            default_requests=self.rate_limit_default_requests,
            default_window=self.rate_limit_default_window,
            burst_multiplier=self.rate_limit_burst_multiplier,
            endpoints=endpoints,
            authenticated_multiplier=self.rate_limit_authenticated_multiplier,
            ip_whitelist=ip_whitelist,
            backend=self.rate_limit_backend,
            redis_key_prefix=self.rate_limit_redis_key_prefix,
            log_violations=self.rate_limit_log_violations,
            metrics_enabled=self.rate_limit_metrics_enabled
        )

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

