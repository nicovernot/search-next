"""
Tests de non-régression US3 — omettre `core` doit produire un comportement
strictement identique à `core=documents` explicite, sur les 3 endpoints.

Ces tests comparent deux appels réels entre eux plutôt que d'affirmer un statut
fixe : quel que soit l'état du Solr distant au moment du test (joignable ou non),
les deux appels doivent se comporter de façon identique — c'est ce que FR-005
garantit, indépendamment de la disponibilité réseau du Solr de test.
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestDefaultCoreEquivalence:
    def test_search_get_omitted_vs_explicit_default_core(self):
        without_core = client.get("/api/v1/search?q=test")
        with_default_core = client.get("/api/v1/search?q=test&core=documents")

        assert without_core.status_code == with_default_core.status_code
        assert without_core.json() == with_default_core.json()

    def test_search_post_omitted_vs_explicit_default_core(self):
        payload = {
            "query": {"query": "test"},
            "filters": [],
            "pagination": {"from": 0, "size": 10},
            "facets": [],
        }
        without_core = client.post("/api/v1/search", json=payload)
        with_default_core = client.post(
            "/api/v1/search", json={**payload, "core": "documents"}
        )

        assert without_core.status_code == with_default_core.status_code
        assert without_core.json() == with_default_core.json()

    def test_suggest_omitted_vs_explicit_default_core(self):
        without_core = client.get("/api/v1/suggest?q=hist")
        with_default_core = client.get("/api/v1/suggest?q=hist&core=documents")

        assert without_core.status_code == with_default_core.status_code
        assert without_core.json() == with_default_core.json()

    def test_permissions_omitted_vs_explicit_default_core(self):
        url = "https://example.org/example-document"
        without_core = client.get(f"/api/v1/permissions?urls={url}")
        with_default_core = client.get(f"/api/v1/permissions?urls={url}&core=documents")

        assert without_core.status_code == with_default_core.status_code
        assert without_core.json() == with_default_core.json()

    def test_omitted_core_still_targets_documents_after_calenda_registered(self):
        """Feature 017 — l'ajout du core `calenda` ne change pas le core par défaut."""
        without_core = client.get("/api/v1/suggest?q=hist")
        explicit_documents = client.get("/api/v1/suggest?q=hist&core=documents")

        assert without_core.status_code == explicit_documents.status_code
        assert without_core.json() == explicit_documents.json()

        explicit_calenda = client.get("/api/v1/suggest?q=hist&core=calenda")
        assert explicit_calenda.status_code != 404
