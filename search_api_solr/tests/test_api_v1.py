from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.models.search_models import SearchRequest

client = TestClient(app)


def test_v1_search_and_root_alias_build_same_contract():
    with patch(
        "app.services.search_service.SearchService.execute_cached_search",
        new_callable=AsyncMock,
    ) as mock_execute:
        mock_execute.return_value = {"results": [], "total": 0, "facets": {}}

        payload = {
            "query": {"query": "history"},
            "filters": [],
            "pagination": {"from": 0, "size": 5},
            "facets": [],
        }

        v1_response = client.post("/api/v1/search", json=payload)
        root_response = client.post("/search", json=payload)

        assert v1_response.status_code == 200
        assert root_response.status_code == 200
        assert v1_response.json() == root_response.json()
        assert mock_execute.await_count == 2
        assert isinstance(mock_execute.call_args_list[0].args[0], SearchRequest)


def test_v1_get_search_builds_search_request():
    with patch(
        "app.services.search_service.SearchService.execute_cached_search",
        new_callable=AsyncMock,
    ) as mock_execute:
        mock_execute.return_value = {"results": [], "total": 0, "facets": {}}

        response = client.get(
            "/api/v1/search",
            params={
                "q": "test",
                "filters": ["platform:OB", "type:livre"],
                "facets": ["platform", "author"],
                "page": 2,
                "size": 20,
            },
        )

        assert response.status_code == 200
        search_request = mock_execute.call_args.args[0]
        assert search_request.query.query == "test"
        assert [filter_model.identifier for filter_model in search_request.filters] == [
            "platform",
            "type",
        ]
        assert search_request.pagination.from_ == 20
        assert search_request.pagination.size == 20
        assert [facet.identifier for facet in search_request.facets] == [
            "platform",
            "author",
        ]


def test_v1_openapi_exposes_versioned_public_routes():
    response = client.get("/api/v1/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/api/v1/search" in paths
    assert "/api/v1/suggest" in paths
    assert "/api/v1/facets/config" in paths
    assert "/api/v1/permissions" in paths
    assert "/search" not in paths
