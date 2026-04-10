"""
Tests d'intégration pour les endpoints de l'API
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestSearchEndpoint:
    """Tests pour l'endpoint /search"""
    
    def test_search_basic(self):
        """Test de recherche basique"""
        response = client.post(
            "/search",
            json={
                "query": {"query": "history"},
                "filters": [],
                "pagination": {"from": 0, "size": 5},
                "facets": []
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'results' in data
        assert 'total' in data
    
    def test_search_with_platform_filter(self):
        """Test de recherche avec filtre platform"""
        response = client.post(
            "/search",
            json={
                "query": {"query": "science"},
                "filters": [
                    {"identifier": "platform", "value": "OB"}
                ],
                "pagination": {"from": 0, "size": 5},
                "facets": []
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'results' in data
    
    def test_search_with_type_subcategory(self):
        """Test de recherche avec sous-catégorie de type"""
        response = client.post(
            "/search",
            json={
                "query": {"query": "literature"},
                "filters": [
                    {"identifier": "type", "value": "article"}
                ],
                "pagination": {"from": 0, "size": 5},
                "facets": []
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'results' in data
    
    def test_search_with_multiple_filters(self):
        """Test de recherche avec plusieurs filtres"""
        response = client.post(
            "/search",
            json={
                "query": {"query": "philosophy"},
                "filters": [
                    {"identifier": "platform", "value": "OB"},
                    {"identifier": "type", "value": "livre"}
                ],
                "pagination": {"from": 0, "size": 5},
                "facets": []
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'results' in data


class TestPermissionsEndpoint:
    """Tests pour l'endpoint /permissions"""
    
    def test_permissions_basic(self):
        """Test basique de l'endpoint permissions"""
        response = client.get(
            "/permissions",
            params={"urls": "https://books.openedition.org/pur/30504"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'data' in data
        assert 'organization' in data['data']
        assert 'docs' in data['data']
    
    def test_permissions_dev_mode(self):
        """Test que le mode DEV utilise TEST_IP"""
        from app.settings import settings
        
        if settings.dev:
            response = client.get(
                "/permissions",
                params={"urls": "https://books.openedition.org/pur/30504"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # En mode DEV avec TEST_IP, on devrait avoir une organisation
            if data['data']['organization']:
                assert 'name' in data['data']['organization']
    
    def test_permissions_with_ip_parameter(self):
        """Test que le paramètre ip surcharge l'IP détectée"""
        # Test avec une IP locale (devrait retourner null/anonymous)
        response = client.get(
            "/permissions",
            params={
                "urls": "https://books.openedition.org/pur/30504",
                "ip": "127.0.0.1"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Avec 127.0.0.1, on ne devrait pas avoir d'organisation (ou organisation vide)
        assert data['data']['organization'] is None
        
        # Test avec l'IP AMU (devrait retourner AMU)
        # Note: Cela dépend de l'API externe, mais on peut tester que le paramètre est pris en compte
        # Si DEV=True, l'appel sans IP utiliserait TEST_IP. Avec IP explicite, on surcharge.

