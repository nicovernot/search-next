"""
Tests pour l'endpoint GET /search
"""
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_search_get_endpoint():
    """Vérifie que l'endpoint GET construit correctement la SearchRequest"""

    # On mocke _execute_search pour vérifier les arguments passés
    with patch("app.services.search_service.SearchService.execute_cached_search", new_callable=AsyncMock) as mock_execute:
        mock_execute.return_value = {"results": []}

        response = client.get(
            "/search",
            params={
                "q": "test",
                "filters": ["platform:OB", "type:livre"],
                "facets": ["platform", "author"],
                "page": 2,
                "size": 20
            }
        )

        assert response.status_code == 200

        # Vérifier que _execute_search a été appelé
        assert mock_execute.called

        # Récupérer l'objet SearchRequest passé
        call_args = mock_execute.call_args
        request = call_args[0][0] # Premier argument positionnel

        # Vérifier la construction de la requête
        assert request["query"] == "test"

        # Filtres
        assert len(request["filters"]) == 2
        assert request["filters"][0]["identifier"] == "platform"
        assert request["filters"][0]["value"] == "OB"
        assert request["filters"][1]["identifier"] == "type"
        assert request["filters"][1]["value"] == "livre"

        # Pagination (page 2, size 20 -> from 20)
        assert request["pagination"]["from"] == 20
        assert request["pagination"]["size"] == 20

        # Facettes
        assert len(request["facets"]) == 2
        assert request["facets"][0]["identifier"] == "platform"
        assert request["facets"][0]["type"] == "list"
        assert request["facets"][1]["identifier"] == "author"
