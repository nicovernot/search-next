"""
Tests d'intégration US2 — cohérence du ciblage de core sur /search, /suggest, /permissions.

Cibler un core inconnu échoue avant tout appel Solr (résolution dans le registre),
donc ces tests n'ont pas besoin de mocker httpx : la requête doit être rejetée en 404
sans jamais atteindre le réseau.
"""
import inspect

from fastapi.testclient import TestClient

from app.main import app
from app.services.search_service import PermissionsService

client = TestClient(app)


class TestUnknownCoreReturns404:
    """FR-004/FR-010 — un core inconnu échoue explicitement, de façon cohérente."""

    def test_search_post_unknown_core_returns_404(self):
        response = client.post(
            "/api/v1/search",
            json={
                "query": {"query": "test"},
                "core": "core-inconnu",
                "filters": [],
                "pagination": {"from": 0, "size": 10},
                "facets": [],
            },
        )
        assert response.status_code == 404

    def test_search_get_unknown_core_returns_404(self):
        response = client.get("/api/v1/search?q=test&core=core-inconnu")
        assert response.status_code == 404

    def test_suggest_unknown_core_returns_404(self):
        response = client.get("/api/v1/suggest?q=hist&core=core-inconnu")
        assert response.status_code == 404

    def test_permissions_unknown_core_returns_404(self):
        response = client.get(
            "/api/v1/permissions?urls=https://example.org/doc&core=core-inconnu"
        )
        assert response.status_code == 404


class TestDefaultCoreFallback:
    """FR-003/US3 — omettre `core` cible le core par défaut, sans erreur de résolution."""

    def test_search_get_without_core_does_not_404(self):
        response = client.get("/api/v1/search?q=test")
        assert response.status_code != 404

    def test_search_get_with_explicit_default_core_does_not_404(self):
        response = client.get("/api/v1/search?q=test&core=documents")
        assert response.status_code != 404

    def test_suggest_without_core_does_not_404(self):
        response = client.get("/api/v1/suggest?q=test")
        assert response.status_code != 404

    def test_permissions_without_core_does_not_404(self):
        response = client.get("/api/v1/permissions?urls=https://example.org/doc")
        assert response.status_code != 404


class TestPermissionsServiceUsesInjectedRegistry:
    """FR-006 — PermissionsService ne contourne plus la DI pour résoudre le core."""

    def test_constructor_takes_a_core_registry(self):
        params = inspect.signature(PermissionsService.__init__).parameters
        assert "core_registry" in params

    def test_get_document_permissions_source_does_not_read_solr_config_base_url(self):
        source = inspect.getsource(PermissionsService.get_document_permissions)
        assert 'SOLR_CONFIG["base_url"]' not in source
