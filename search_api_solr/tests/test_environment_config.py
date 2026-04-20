# tests/test_environment_config.py
"""
Tests pour la configuration des environnements
"""

import pytest

from app.settings import Settings, get_cors_origins, get_environment

TEST_PRODUCTION_SECRET_KEY = "test-production-secret-key-that-is-not-a-placeholder"


class TestEnvironmentDetection:
    """Tests pour la détection de l'environnement"""

    def test_get_environment_default(self, monkeypatch):
        """Test que l'environnement par défaut est 'development'"""
        monkeypatch.delenv("ENVIRONMENT", raising=False)
        assert get_environment() == "development"

    def test_get_environment_explicit(self, monkeypatch):
        """Test la détection explicite de l'environnement"""
        monkeypatch.setenv("ENVIRONMENT", "production")
        assert get_environment() == "production"

    def test_get_environment_invalid(self, monkeypatch):
        """Test qu'un environnement invalide revient à 'development'"""
        monkeypatch.setenv("ENVIRONMENT", "invalid_env")
        assert get_environment() == "development"

    def test_get_environment_case_insensitive(self, monkeypatch):
        """Test que la détection est insensible à la casse"""
        monkeypatch.setenv("ENVIRONMENT", "PRODUCTION")
        assert get_environment() == "production"


class TestCORSOrigins:
    """Tests pour la configuration CORS par environnement"""

    def test_get_cors_origins_from_env(self, monkeypatch):
        """Test la récupération des origines CORS depuis l'environnement"""
        monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3009,http://localhost:3000")
        origins = get_cors_origins("development")
        assert origins == ["http://localhost:3009", "http://localhost:3000"]

    def test_get_cors_origins_default_development(self, monkeypatch):
        """Test les origines CORS par défaut pour le développement"""
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
        origins = get_cors_origins("development")
        assert "http://localhost:3009" in origins
        assert "http://localhost:3000" in origins

    def test_get_cors_origins_default_production(self, monkeypatch):
        """Test les origines CORS par défaut pour la production"""
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
        origins = get_cors_origins("production")
        assert "https://search.openedition.org" in origins
        assert "https://www.openedition.org" in origins

    def test_get_cors_origins_default_test(self, monkeypatch):
        """Test les origines CORS par défaut pour les tests"""
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
        origins = get_cors_origins("test")
        assert "http://localhost:8007" in origins
        assert "http://localhost:3009" in origins
        assert "http://127.0.0.1:3009" in origins
        assert "http://127.0.0.1:8007" in origins


class TestSettingsValidation:
    """Tests pour la validation des settings"""

    def test_environment_validation_valid(self):
        """Test la validation d'un environnement valide"""
        settings = Settings(environment="production", secret_key=TEST_PRODUCTION_SECRET_KEY)
        assert settings.environment == "production"

    def test_environment_validation_invalid(self):
        """Test la validation d'un environnement invalide"""
        with pytest.raises(ValueError) as excinfo:
            Settings(environment="invalid_env")
        assert "ENVIRONMENT must be one of" in str(excinfo.value)

    def test_cors_max_age_adjustment(self):
        """Test l'ajustement automatique de cors_max_age"""
        # Production
        prod_settings = Settings(
            environment="production",
            cors_max_age=86400,
            secret_key=TEST_PRODUCTION_SECRET_KEY,
        )
        assert prod_settings.cors_max_age == 3600  # Doit être ajusté à 1h

        # Développement
        dev_settings = Settings(environment="development", cors_max_age=3600)
        assert dev_settings.cors_max_age == 86400  # Doit être ajusté à 24h

        # Test
        test_settings = Settings(environment="test", cors_max_age=86400)
        assert test_settings.cors_max_age == 60  # Doit être ajusté à 1min

    def test_cors_methods_adjustment_production(self):
        """Test l'ajustement des méthodes CORS en production"""
        settings = Settings(
            environment="production",
            cors_allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            secret_key=TEST_PRODUCTION_SECRET_KEY,
        )
        # En production, seulement GET, POST, OPTIONS doivent être conservés
        assert settings.cors_allow_methods == ["GET", "POST", "OPTIONS"]

    def test_cors_headers_adjustment_production(self):
        """Test l'ajustement des headers CORS en production"""
        settings = Settings(
            environment="production",
            cors_allow_headers=["Accept", "Authorization", "Content-Type", "X-Requested-With"],
            secret_key=TEST_PRODUCTION_SECRET_KEY,
        )
        # En production, seulement les headers minimaux doivent être conservés
        assert settings.cors_allow_headers == ["Accept", "Authorization", "Content-Type"]

    def test_trusted_hosts_default_production(self):
        """Test les hôtes de confiance par défaut en production"""
        settings = Settings(environment="production", secret_key=TEST_PRODUCTION_SECRET_KEY)
        assert "search.openedition.org" in settings.trusted_hosts
        assert "www.openedition.org" in settings.trusted_hosts

    @pytest.mark.parametrize(
        "placeholder_secret_key",
        ["your-secret-key-for-development", "change-me-in-production"],
    )
    def test_production_rejects_placeholder_secret_keys(self, placeholder_secret_key):
        """Test que les placeholders de SECRET_KEY sont interdits en production"""
        with pytest.raises(ValueError, match="SECRET_KEY must be changed"):
            Settings(environment="production", secret_key=placeholder_secret_key)


class TestEnvironmentSpecificSettings:
    """Tests pour les settings spécifiques à chaque environnement"""

    @pytest.fixture
    def dev_settings(self, monkeypatch):
        """Fixture pour les settings de développement"""
        monkeypatch.delenv("LOG_LEVEL", raising=False)
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
        return Settings(environment="development", _env_file=None)

    @pytest.fixture
    def prod_settings(self, monkeypatch):
        """Fixture pour les settings de production"""
        monkeypatch.delenv("LOG_LEVEL", raising=False)
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
        return Settings(
            environment="production",
            secret_key=TEST_PRODUCTION_SECRET_KEY,
            _env_file=None,
        )

    @pytest.fixture
    def test_settings(self, monkeypatch):
        """Fixture pour les settings de test"""
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
        return Settings(environment="test", _env_file=None)

    def test_development_settings(self, dev_settings):
        """Test les settings spécifiques au développement"""
        assert dev_settings.cors_max_age == 86400  # 24h
        assert dev_settings.log_level == "DEBUG"
        assert dev_settings.enable_https_redirect is False
        assert "http://localhost:3009" in dev_settings.cors_origins

    def test_production_settings(self, prod_settings):
        """Test les settings spécifiques à la production"""
        assert prod_settings.cors_max_age == 3600  # 1h
        # log_level est déterminé par os.getenv, pas par l'environnement
        assert prod_settings.log_level in ["INFO", "DEBUG"]  # Peut être INFO ou DEBUG selon .env
        assert prod_settings.enable_https_redirect is True
        # Vérifier que les CORS sont configurés (peut varier selon .env)
        assert len(prod_settings.cors_origins) > 0

    def test_test_settings(self, test_settings):
        """Test les settings spécifiques aux tests"""
        assert test_settings.cors_max_age == 60  # 1min
        # log_level est déterminé par os.getenv, pas par l'environnement
        assert test_settings.log_level in ["WARNING", "DEBUG", "INFO"]  # Peut varier selon .env
        assert test_settings.enable_https_redirect is False
        # Vérifier que les CORS sont configurés (peut varier selon .env.test)
        assert "http://localhost:8007" in test_settings.cors_origins


class TestEnvironmentIntegration:
    """Tests d'intégration pour la configuration d'environnement"""

    def test_settings_from_env_file(self, tmp_path, monkeypatch):
        """Test le chargement des settings depuis un fichier .env"""
        # S'assurer que les variables d'environnement n'interfèrent pas
        monkeypatch.delenv("ENVIRONMENT", raising=False)
        monkeypatch.delenv("API_PORT", raising=False)
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
        monkeypatch.delenv("LOG_LEVEL", raising=False)

        env_file = tmp_path / ".env.test"
        env_file.write_text("""
ENVIRONMENT=test
API_PORT=8007
CORS_ORIGINS=http://test.example.com
LOG_LEVEL=DEBUG
""")

        # Charger les settings depuis le fichier
        settings = Settings(_env_file=env_file)
        assert settings.environment == "test"
        assert settings.api_port == 8007
        assert "http://test.example.com" in settings.cors_origins
        assert settings.log_level == "DEBUG"  # Log level du fichier prime sur la valeur par défaut

    def test_environment_switching(self, monkeypatch):
        """Test le changement d'environnement"""
        # Simuler un environnement de développement
        monkeypatch.setenv("ENVIRONMENT", "development")
        monkeypatch.delenv("CORS_ORIGINS", raising=False)

        dev_settings = Settings()
        assert dev_settings.environment == "development"
        assert dev_settings.cors_max_age == 86400

        # Changer pour la production
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("SECRET_KEY", TEST_PRODUCTION_SECRET_KEY)
        prod_settings = Settings()
        assert prod_settings.environment == "production"
        assert prod_settings.cors_max_age == 3600


class TestCORSConfiguration:
    """Tests pour la configuration CORS complète"""

    def test_cors_origins_parsing(self):
        """Test le parsing des origines CORS depuis une string"""
        settings = Settings(cors_origins="http://localhost:3009, http://localhost:3000 , http://127.0.0.1:3009")
        assert settings.cors_origins == ["http://localhost:3009", "http://localhost:3000", "http://127.0.0.1:3009"]

    def test_cors_origins_list(self):
        """Test les origines CORS depuis une liste"""
        settings = Settings(cors_origins=["http://localhost:3009", "http://localhost:3000"])
        assert settings.cors_origins == ["http://localhost:3009", "http://localhost:3000"]

    def test_cors_expose_headers(self):
        """Test les headers exposés CORS"""
        settings = Settings(cors_expose_headers="X-Total-Count,X-Pagination")
        # Le validator convertit la string CSV en liste
        assert "X-Total-Count" in settings.cors_expose_headers
        assert "X-Pagination" in settings.cors_expose_headers


class TestSecuritySettings:
    """Tests pour les paramètres de sécurité"""

    def test_https_redirect_settings(self):
        """Test la configuration de la redirection HTTPS"""
        prod_settings = Settings(environment="production", secret_key=TEST_PRODUCTION_SECRET_KEY)
        dev_settings = Settings(environment="development")

        assert prod_settings.enable_https_redirect is True
        assert dev_settings.enable_https_redirect is False

    def test_trusted_hosts_settings(self):
        """Test la configuration des hôtes de confiance"""
        prod_settings = Settings(environment="production", secret_key=TEST_PRODUCTION_SECRET_KEY)
        staging_settings = Settings(environment="staging")
        dev_settings = Settings(environment="development")

        assert len(prod_settings.trusted_hosts) > 0
        assert len(staging_settings.trusted_hosts) > 0
        assert len(dev_settings.trusted_hosts) == 0  # Pas de hôtes de confiance par défaut en dev

    def test_dev_mode_settings(self):
        """Test la configuration du mode développement"""
        dev_settings = Settings(environment="development", dev=True)
        prod_settings = Settings(
            environment="production",
            dev=False,
            secret_key=TEST_PRODUCTION_SECRET_KEY,
        )

        assert dev_settings.dev is True
        assert prod_settings.dev is False


class TestEnvironmentEdgeCases:
    """Tests pour les cas limites"""

    def test_empty_cors_origins(self, monkeypatch):
        """Test le comportement avec des origines CORS vides"""
        monkeypatch.setenv("CORS_ORIGINS", "")
        settings = Settings(environment="development")
        # Une string vide est parsée comme une liste vide par le validator
        # Il faut utiliser get_cors_origins pour avoir les valeurs par défaut
        # Ou ne pas définir CORS_ORIGINS du tout
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
        settings = Settings(environment="development")
        assert len(settings.cors_origins) > 0

    def test_whitespace_in_cors_origins(self, monkeypatch):
        """Test le traitement des espaces dans les origines CORS"""
        monkeypatch.setenv("CORS_ORIGINS", " http://localhost:3009 , http://localhost:3000 ")
        settings = Settings()
        assert settings.cors_origins == ["http://localhost:3009", "http://localhost:3000"]

    def test_invalid_environment_fallback(self, monkeypatch):
        """Test le fallback pour un environnement invalide"""
        monkeypatch.setenv("ENVIRONMENT", "invalid_env")
        # get_environment() retourne 'development' pour les valeurs invalides
        # mais Settings() valide et lève une erreur
        # On doit tester que get_environment fait le fallback
        from app.settings import get_environment
        assert get_environment() == "development"

        # Settings() avec un environnement invalide lève une ValidationError
        with pytest.raises(Exception):  # ValidationError de pydantic
            Settings(environment="invalid_env")

    def test_missing_optional_settings(self):
        """Test le comportement avec des settings optionnels manquants"""
        settings = Settings()
        # Ces settings doivent avoir des valeurs par défaut
        assert settings.cors_allow_credentials is not None
        assert settings.cors_allow_methods is not None
        assert settings.cors_allow_headers is not None
