from fastapi.testclient import TestClient
from src.api.main import app
import pytest

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_predict_valid_client():
    # Le client 100002 est présent dans les premières lignes du CSV
    response = client.get("/predict/100002")
    assert response.status_code == 200
    data = response.json()
    assert data["client_id"] == 100002
    assert "score" in data
    assert "decision" in data

def test_predict_invalid_client():
    response = client.get("/predict/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Client 999999 non trouvé"

def test_predict_bad_input():
    response = client.get("/predict/not-an-id")
    assert response.status_code == 422 # Validation error
