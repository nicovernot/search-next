# tests/test_env_validation.py
"""
Tests pour la validation secondaire d'environnement (app/core/env_validation.py).
Couvre FR-009 (rejet d'un ENVIRONMENT hors development/test/production) et
FR-014 (blocage si un secret de production reste au placeholder).
"""

import pytest

from app.core.env_validation import EnvironmentConfig

REQUIRED_FIELDS = {
    "solr_url": "http://solr:8983/solr",
    "solr_collection": "searchv2_test",
}


class TestEnvironmentFieldValidation:
    """FR-009 : ENVIRONMENT doit être development, test ou production"""

    @pytest.mark.parametrize("value", ["development", "test", "production"])
    def test_valid_environment_accepted(self, value):
        config = EnvironmentConfig(environment=value, disable_auth=True, **REQUIRED_FIELDS)
        assert config.environment == value

    @pytest.mark.parametrize("value", ["staging", "prod", "dev", "", "STAGING"])
    def test_invalid_environment_rejected(self, value):
        with pytest.raises(ValueError, match="ENVIRONMENT must be one of"):
            EnvironmentConfig(environment=value, disable_auth=True, **REQUIRED_FIELDS)

    def test_environment_value_is_normalized_to_lowercase(self):
        config = EnvironmentConfig(environment="PRODUCTION", disable_auth=True, secret_key="x", **REQUIRED_FIELDS)
        assert config.environment == "production"


class TestProductionPlaceholderSecretDetection:
    """FR-010 / FR-014 : blocage si un secret de production reste au placeholder committé"""

    @pytest.mark.parametrize("field", ["secret_key", "jwt_secret", "session_secret"])
    def test_placeholder_secret_blocks_production_startup(self, field):
        with pytest.raises(ValueError, match="change-me-in-production"):
            EnvironmentConfig(
                environment="production",
                disable_auth=True,
                **{field: "change-me-in-production"},
                **REQUIRED_FIELDS,
            )

    def test_real_secret_allows_production_startup(self):
        config = EnvironmentConfig(
            environment="production",
            disable_auth=True,
            secret_key="a-real-random-production-secret",
            **REQUIRED_FIELDS,
        )
        assert config.environment == "production"

    def test_placeholder_secret_allowed_outside_production(self):
        config = EnvironmentConfig(
            environment="development",
            disable_auth=True,
            secret_key="change-me-in-production",
            **REQUIRED_FIELDS,
        )
        assert config.environment == "development"
