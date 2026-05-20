"""Tests pour les endpoints hypermedia (HTML) — spec 014."""
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_search_service
from app.main import app
from app.models.search_models import SearchResponse


def _mock_service(results=None, total=0):
    service = MagicMock()
    service.execute_cached_search = AsyncMock(
        return_value=SearchResponse(results=results or [], total=total, facets=None)
    )
    return service


@pytest.fixture()
def client():
    return TestClient(app, raise_server_exceptions=False)


class TestHypermediaHome:
    def test_home_returns_html(self, client):
        app.dependency_overrides[get_search_service] = lambda: _mock_service()
        response = client.get("/api/v1/hypermedia/")
        app.dependency_overrides.clear()
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_home_contains_search_form(self, client):
        app.dependency_overrides[get_search_service] = lambda: _mock_service()
        response = client.get("/api/v1/hypermedia/")
        app.dependency_overrides.clear()
        assert b"search-form" in response.content
        assert b"hx-get" in response.content


class TestHypermediaSearch:
    def test_search_page_returns_html(self, client):
        app.dependency_overrides[get_search_service] = lambda: _mock_service()
        response = client.get("/api/v1/hypermedia/search?q=histoire")
        app.dependency_overrides.clear()
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_search_page_empty_query_no_results(self, client):
        app.dependency_overrides[get_search_service] = lambda: _mock_service()
        response = client.get("/api/v1/hypermedia/search")
        app.dependency_overrides.clear()
        assert response.status_code == 200

    def test_search_page_not_json(self, client):
        app.dependency_overrides[get_search_service] = lambda: _mock_service()
        response = client.get("/api/v1/hypermedia/search?q=test")
        app.dependency_overrides.clear()
        assert "application/json" not in response.headers.get("content-type", "")


class TestHypermediaSearchResults:
    def test_results_fragment_returns_html(self, client):
        mock_doc = MagicMock()
        mock_doc.title = "Article test"
        mock_doc.url = "https://example.org"
        mock_doc.overview = "Un résumé."
        mock_doc.authors = ["Auteur A"]
        mock_doc.date = "2024"
        mock_doc.platformID = "OJ"
        app.dependency_overrides[get_search_service] = lambda: _mock_service(
            results=[mock_doc], total=1
        )
        response = client.get("/api/v1/hypermedia/search/results?q=histoire")
        app.dependency_overrides.clear()
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_results_fragment_no_full_page(self, client):
        """Le fragment ne doit pas contenir le layout complet."""
        app.dependency_overrides[get_search_service] = lambda: _mock_service()
        response = client.get("/api/v1/hypermedia/search/results?q=test")
        app.dependency_overrides.clear()
        assert b"<!DOCTYPE" not in response.content

    def test_results_fragment_error_display(self, client):
        """Une erreur Solr doit afficher un message d'erreur HTML, pas lever une 500."""
        from app.core.exceptions import SolrUnavailableError
        service = MagicMock()
        service.execute_cached_search = AsyncMock(side_effect=SolrUnavailableError("down"))
        app.dependency_overrides[get_search_service] = lambda: service
        response = client.get("/api/v1/hypermedia/search/results?q=test")
        app.dependency_overrides.clear()
        assert response.status_code == 200
        assert b"indisponible" in response.content

    def test_results_empty_query_returns_empty(self, client):
        app.dependency_overrides[get_search_service] = lambda: _mock_service()
        response = client.get("/api/v1/hypermedia/search/results")
        app.dependency_overrides.clear()
        assert response.status_code == 200

    def test_search_htmx_request_returns_fragment(self, client):
        """HX-Request: true → /search retourne le fragment, pas la page complète."""
        app.dependency_overrides[get_search_service] = lambda: _mock_service()
        response = client.get(
            "/api/v1/hypermedia/search?q=test",
            headers={"HX-Request": "true"},
        )
        app.dependency_overrides.clear()
        assert response.status_code == 200
        assert b"<!DOCTYPE" not in response.content

    def test_filter_param_forwarded(self, client):
        """Le param filter= est accepté sans erreur."""
        app.dependency_overrides[get_search_service] = lambda: _mock_service()
        response = client.get(
            "/api/v1/hypermedia/search/results?q=test&filter=platform:OJ"
        )
        app.dependency_overrides.clear()
        assert response.status_code == 200


class TestHypermediaAuthSession:
    def _make_token(self, user_id: int = 1) -> str:
        from jose import jwt
        from app.settings import settings
        return jwt.encode({"sub": str(user_id)}, settings.secret_key, algorithm=settings.algorithm)

    def test_post_session_no_token_returns_401(self, client):
        response = client.post("/api/v1/hypermedia/auth/session")
        assert response.status_code == 401

    def test_post_session_invalid_token_returns_401(self, client):
        response = client.post(
            "/api/v1/hypermedia/auth/session",
            headers={"Authorization": "Bearer notavalidtoken"},
        )
        assert response.status_code == 401

    def test_delete_session_clears_cookie(self, client):
        response = client.delete("/api/v1/hypermedia/auth/session")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Déconnecté".encode() in response.content

    def test_delete_session_returns_html_fragment(self, client):
        response = client.delete("/api/v1/hypermedia/auth/session")
        assert b"<!DOCTYPE" not in response.content
        assert b"session-status" in response.content


class TestHypermediaFacets:
    def test_facets_endpoint_returns_html(self, client):
        app.dependency_overrides[get_search_service] = lambda: _mock_service()
        response = client.get("/api/v1/hypermedia/search/facets?q=histoire")
        app.dependency_overrides.clear()
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_facets_fragment_no_full_layout(self, client):
        app.dependency_overrides[get_search_service] = lambda: _mock_service()
        response = client.get("/api/v1/hypermedia/search/facets?q=test")
        app.dependency_overrides.clear()
        assert b"<!DOCTYPE" not in response.content

    def test_results_oob_includes_facets_div(self, client):
        """Le fragment résultats inclut un div#facets OOB pour le swap."""
        app.dependency_overrides[get_search_service] = lambda: _mock_service()
        response = client.get("/api/v1/hypermedia/search/results?q=test")
        app.dependency_overrides.clear()
        assert b'id="facets"' in response.content
        assert b"hx-swap-oob" in response.content
