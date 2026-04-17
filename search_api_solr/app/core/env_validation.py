"""
Validation des variables d'environnement pour l'API SearchV2.
Utilise pydantic-settings pour la validation de configuration.
"""

from pydantic import BaseModel, field_validator, AnyHttpUrl, Field, ValidationInfo, model_validator
from pydantic_settings import BaseSettings
from typing import Optional, List
import os
import logging

logger = logging.getLogger(__name__)


class EnvironmentConfig(BaseSettings):
    """Configuration complète de l'environnement"""
    # Variables communes
    node_env: str = Field(default="development", description="Environnement (development, production, test)")
    
    # Configuration Solr
    solr_url: AnyHttpUrl = Field(description="URL du serveur Solr")
    solr_collection: str = Field(description="Collection Solr")
    
    # Configuration API
    api_base_url: str = Field(description="URL base publique de l'API")
    debug: bool = Field(default=False, description="Mode debug")
    auto_reload: bool = Field(default=False, description="Rechargement automatique")
    log_level: str = Field(default="info", description="Niveau de logging")
    
    # Configuration sécurité
    disable_auth: bool = Field(default=False, description="Désactiver l'authentification")
    jwt_secret: Optional[str] = Field(default=None, description="Secret JWT")
    secret_key: Optional[str] = Field(default=None, description="Secret JWT utilisé par l'application")
    session_secret: Optional[str] = Field(default=None, description="Secret de session")
    cors_origins: str = Field(default="", description="Origines CORS autorisées (séparées par des virgules)")
    
    # Autres variables
    frontend_url: Optional[str] = Field(default=None, description="URL du frontend")
    test_timeout: Optional[int] = Field(default=None, description="Timeout pour les tests")
    test_retries: Optional[int] = Field(default=None, description="Nombre de tentatives pour les tests")
    
    @field_validator('solr_url')
    def validate_solr_url(cls, v):
        if 'solr' not in v.path.lower():
            raise ValueError('Solr URL must contain "solr" in the path')
        return v
    
    @field_validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ['debug', 'info', 'warning', 'error', 'critical']
        if v.lower() not in valid_levels:
            raise ValueError(f'Log level must be one of: {valid_levels}')
        return v.lower()

    @field_validator('debug', 'auto_reload', mode='before')
    def parse_bool_env(cls, v):
        if isinstance(v, str):
            normalized = v.strip().lower()
            if normalized in {"1", "true", "yes", "on", "debug"}:
                return True
            if normalized in {"0", "false", "no", "off", "release", "production"}:
                return False
        return v
    
    @model_validator(mode='after')
    def validate_auth_secret(self):
        disable_auth = os.getenv('DISABLE_AUTH', 'false').lower() == 'true'
        if not disable_auth and not (self.secret_key or self.jwt_secret):
            if os.getenv('NODE_ENV', 'development') == 'development':
                self.secret_key = "default_secret_key_for_dev"
            else:
                raise ValueError('SECRET_KEY or JWT_SECRET is required when auth is enabled')
        return self
    
    class Config:
        env_file = ['.env.shared', '.env.local', '.env']
        env_file_encoding = 'utf-8'
        case_sensitive = False
        extra = 'allow'


def validate_environment():
    """
    Valide toutes les variables d'environnement nécessaires.
    À appeler au démarrage de l'application.
    """
    try:
        # Charger et valider la configuration
        config = EnvironmentConfig()
        
        logger.info(f"Environment validation successful: {config.node_env}")
        logger.info(f"Solr configuration: {config.solr_url}/{config.solr_collection}")
        logger.info(f"API base URL: {config.api_base_url}")
        logger.info(f"Log level: {config.log_level}")
        
        # Exporter les variables validées pour utilisation dans l'app
        os.environ['VALIDATED_SOLR_URL'] = str(config.solr_url)
        os.environ['VALIDATED_SOLR_COLLECTION'] = config.solr_collection
        
        return config
        
    except Exception as e:
        logger.error(f"Environment validation failed: {str(e)}")
        logger.error("Please check your .env files and ensure all required variables are set.")
        raise


# Exemple d'utilisation dans votre application principale
if __name__ == "__main__":
    # Cela sera appelé automatiquement au démarrage
    config = validate_environment()
    print("Environment validation completed successfully!")
    print(f"Node environment: {config.node_env}")
    print(f"Solr URL: {config.solr_url}")
    print(f"API Base URL: {config.api_base_url}")
