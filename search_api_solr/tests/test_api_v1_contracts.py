"""
Tests de contrat pour les endpoints /api/v1/* — spec 012 Phase 1.
Vérifie la structure des réponses, les codes HTTP stables et les alias racine.
"""
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

SEARCH_PAYLOAD = {
    "query": {"query": "histoire"},
    "filters": [],
    "pagination": {"from": 0, "size": 5},
    "facets": [],
}

MOCK_SEARCH_RESULT = {"results": [], "total": 0, "facets": {}}


# ---------------------------------------------------------------------------
# /api/v1/search
# ---------------------------------------------------------------------------
class TestV1SearchContract:
    def test_post_returns_search_response_shape(self):
        with patch(
            "app.services.search_service.SearchService.execute_cached_search",
            new_callable=AsyncMock,
            return_value=MOCK_SEARCH_RESULT,
        ):
            resp = client.post("/api/v1/search", json=SEARCH_PAYLOAD)
        assert resp.status_code == 200
        body = resp.json()
        assert "results" in body
        assert "total" in body
        assert isinstance(body["results"], list)
        assert isinstance(body["total"], int)

    def test_get_returns_search_response_shape(self):
        with patch(
            "app.services.search_service.SearchService.execute_cached_search",
            new_callable=AsyncMock,
            return_value=MOCK_SEARCH_RESULT,
        ):
            resp = client.get("/api/v1/search", params={"q": "histoire"})
        assert resp.status_code == 200
        assert "results" in resp.json()

    def test_invalid_query_returns_422(self):
        resp = client.post("/api/v1/search", json={"query": "not_a_dict"})
        assert resp.status_code == 422

    def test_root_alias_returns_same_contract(self):
        with patch(
            "app.services.search_service.SearchService.execute_cached_search",
            new_callable=AsyncMock,
            return_value=MOCK_SEARCH_RESULT,
        ):
            v1 = client.post("/api/v1/search", json=SEARCH_PAYLOAD)
            root = client.post("/search", json=SEARCH_PAYLOAD)
        assert v1.status_code == root.status_code == 200
        assert v1.json().keys() == root.json().keys()

    def test_content_type_is_json(self):
        with patch(
            "app.services.search_service.SearchService.execute_cached_search",
            new_callable=AsyncMock,
            return_value=MOCK_SEARCH_RESULT,
        ):
            resp = client.post("/api/v1/search", json=SEARCH_PAYLOAD)
        assert "application/json" in resp.headers["content-type"]


# ---------------------------------------------------------------------------
# /api/v1/suggest
# ---------------------------------------------------------------------------
class TestV1SuggestContract:
    def test_returns_suggestions_list(self):
        with patch(
            "app.services.search_service.SuggestService.fetch_autocomplete_suggestions",
            new_callable=AsyncMock,
            return_value={"suggestions": ["histoire", "historique"]},
        ):
            resp = client.get("/api/v1/suggest", params={"q": "hist"})
        assert resp.status_code == 200
        body = resp.json()
        assert "suggestions" in body
        assert isinstance(body["suggestions"], list)

    def test_missing_q_returns_422(self):
        resp = client.get("/api/v1/suggest")
        assert resp.status_code == 422

    def test_root_alias_returns_same_contract(self):
        with patch(
            "app.services.search_service.SuggestService.fetch_autocomplete_suggestions",
            new_callable=AsyncMock,
            return_value={"suggestions": []},
        ):
            v1 = client.get("/api/v1/suggest", params={"q": "test"})
            root = client.get("/suggest", params={"q": "test"})
        assert v1.status_code == root.status_code == 200
        assert v1.json().keys() == root.json().keys()


# ---------------------------------------------------------------------------
# /api/v1/facets/config
# ---------------------------------------------------------------------------
class TestV1FacetsConfigContract:
    def test_returns_search_fields(self):
        resp = client.get("/api/v1/facets/config")
        assert resp.status_code == 200
        body = resp.json()
        assert "search_fields" in body
        assert isinstance(body["search_fields"], list)

    def test_root_alias_returns_same_contract(self):
        v1 = client.get("/api/v1/facets/config")
        root = client.get("/facets/config")
        assert v1.status_code == root.status_code == 200
        assert v1.json() == root.json()


# ---------------------------------------------------------------------------
# /api/v1/permissions
# ---------------------------------------------------------------------------
class TestV1PermissionsContract:
    def test_returns_permissions_object(self):
        with patch(
            "app.services.search_service.PermissionsService.get_document_permissions",
            new_callable=AsyncMock,
            return_value={"data": {"organization": None, "docs": None}, "info": {}},
        ):
            resp = client.get("/api/v1/permissions", params={"urls": "https://example.org/doc", "ip": "127.0.0.1"})
        assert resp.status_code == 200

    def test_root_alias_reachable(self):
        with patch(
            "app.services.search_service.PermissionsService.get_document_permissions",
            new_callable=AsyncMock,
            return_value={"data": {"organization": None, "docs": None}, "info": {}},
        ):
            resp = client.get("/permissions", params={"urls": "https://example.org/doc", "ip": "127.0.0.1"})
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# /api/v1/openapi.json
# ---------------------------------------------------------------------------
class TestV1OpenAPIContract:
    def test_openapi_lists_all_public_routes(self):
        resp = client.get("/api/v1/openapi.json")
        assert resp.status_code == 200
        paths = resp.json()["paths"]
        for expected in ("/api/v1/search", "/api/v1/suggest", "/api/v1/facets/config", "/api/v1/permissions"):
            assert expected in paths, f"Route manquante dans OpenAPI : {expected}"

    def test_root_aliases_absent_from_openapi(self):
        resp = client.get("/api/v1/openapi.json")
        paths = resp.json()["paths"]
        for alias in ("/search", "/suggest", "/facets/config", "/permissions"):
            assert alias not in paths, f"Alias racine ne devrait pas être dans OpenAPI : {alias}"

    def test_search_response_model_exposes_results_and_total(self):
        resp = client.get("/api/v1/openapi.json")
        schema = resp.json()
        search_schema = schema.get("components", {}).get("schemas", {}).get("SearchResponse", {})
        props = search_schema.get("properties", {})
        assert "results" in props
        assert "total" in props
