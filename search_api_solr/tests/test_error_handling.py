"""
Tests de la gestion des erreurs pour les endpoints /search et /permissions
"""
import pytest
from unittest.mock import patch
from httpx import ReadTimeout, HTTPStatusError, Response as HttpxResponse
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestSearchErrorHandling:
    """Tests de gestion d'erreur pour /search"""
    
    def test_search_timeout(self):
        """Vérifie que le timeout retourne 503"""
        with patch("httpx.AsyncClient.get", side_effect=ReadTimeout("Timeout simulé", request=None)):
            response = client.post(
                "/search",
                json={
                    "query": {"query": "test"},
                    "filters": [],
                    "pagination": {"from": 0, "size": 10},
                    "facets": []
                }
            )
            assert response.status_code == 503
            assert response.json()["detail"] == "Search service unavailable (timeout)"

    def test_search_solr_error_500(self):
        """Vérifie qu'une erreur 500 de Solr retourne 503"""
        mock_response = HttpxResponse(500, request=None)
        error = HTTPStatusError("Solr Error", request=None, response=mock_response)
        
        with patch("httpx.AsyncClient.get", side_effect=error):
            response = client.post(
                "/search",
                json={
                    "query": {"query": "test"},
                    "filters": [],
                    "pagination": {"from": 0, "size": 10},
                    "facets": []
                }
            )
            assert response.status_code == 503
            assert response.json()["detail"] == "Search service unavailable"

    def test_search_solr_error_400(self):
        """Vérifie qu'une erreur 400 de Solr retourne 400"""
        mock_response = HttpxResponse(400, request=None)
        error = HTTPStatusError("Bad Request", request=None, response=mock_response)
        
        with patch("httpx.AsyncClient.get", side_effect=error):
            response = client.post(
                "/search",
                json={
                    "query": {"query": "test"},
                    "filters": [],
                    "pagination": {"from": 0, "size": 10},
                    "facets": []
                }
            )
            assert response.status_code == 400
            assert response.json()["detail"] == "Invalid search query"


class TestPermissionsErrorHandling:
    """Tests de gestion d'erreur pour /permissions"""
    
    def test_permissions_exception(self):
        """Vérifie qu'une exception non gérée retourne une réponse vide avec info d'erreur"""
        # On mocke get_document_permissions pour lever une exception générique
        with patch("app.services.search_service.PermissionsService.get_document_permissions", side_effect=Exception("Erreur inattendue")):
            response = client.get("/permissions?urls=http://test.com")
            
            assert response.status_code == 200 # On ne veut pas casser le front
            data = response.json()
            
            assert data["data"]["organization"] is None
            assert data["data"]["docs"] is None
            assert "error" in data["info"]
            assert "Erreur inattendue" in data["info"]["error"]
