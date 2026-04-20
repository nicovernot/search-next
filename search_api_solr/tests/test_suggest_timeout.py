"""
Test du comportement de l'endpoint /suggest en cas de timeout
"""
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from httpx import ReadTimeout

from app.main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_suggest_timeout_handling():
    """Vérifie que l'endpoint retourne une réponse vide en cas de timeout Solr"""

    # Mocker httpx.AsyncClient.get pour lever une ReadTimeout
    with patch("httpx.AsyncClient.get", side_effect=ReadTimeout("Timeout simulé", request=None)) as mock_get:
        response = client.get("/suggest?q=test")

        # On s'attend à un code 200 (gestion gracieuse)
        assert response.status_code == 200

        data = response.json()
        # Vérifier la structure de réponse vide
        assert "suggestions" in data
        assert data["suggestions"] == []
