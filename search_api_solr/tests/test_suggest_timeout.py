"""
Test du comportement de l'endpoint /suggest en cas de timeout
"""
import pytest
from unittest.mock import patch, AsyncMock
from httpx import ReadTimeout
from fastapi.testclient import TestClient
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
        assert "suggest" in data
        assert "default" in data["suggest"]
        assert "test" in data["suggest"]["default"]
        assert data["suggest"]["default"]["test"]["numFound"] == 0
        assert data["suggest"]["default"]["test"]["suggestions"] == []
