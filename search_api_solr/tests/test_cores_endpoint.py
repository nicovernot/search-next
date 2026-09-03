from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_cores_lists_configured_cores_and_default():
    response = client.get("/api/v1/cores")

    assert response.status_code == 200
    body = response.json()
    names = {core["name"] for core in body["cores"]}
    assert "documents" in names
    assert body["default_core"] == "documents"
    documents_entry = next(core for core in body["cores"] if core["name"] == "documents")
    assert documents_entry["is_default"] is True


def test_get_cores_response_never_exposes_base_url():
    response = client.get("/api/v1/cores")

    assert response.status_code == 200
    assert "base_url" not in response.text


def test_v1_openapi_exposes_cores_route():
    response = client.get("/api/v1/openapi.json")

    assert response.status_code == 200
    assert "/api/v1/cores" in response.json()["paths"]


def test_get_cores_lists_calenda_as_non_default():
    response = client.get("/api/v1/cores")

    assert response.status_code == 200
    body = response.json()
    calenda_entry = next(core for core in body["cores"] if core["name"] == "calenda")
    assert calenda_entry["is_default"] is False
    assert body["default_core"] == "documents"
