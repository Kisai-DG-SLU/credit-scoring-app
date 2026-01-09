from unittest.mock import MagicMock
import numpy as np
from tests.conftest import create_client_features


def test_health_check(client, mock_loader):
    """Vérifie que l'endpoint health répond correctement."""
    mock_loader.load_artifacts.return_value = MagicMock()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_predict_valid_client(client, mock_loader, mock_model):
    """Cas nominal : client existant et données complètes."""
    # Setup mock
    mock_loader.model = mock_model
    mock_loader.get_client_data.return_value = create_client_features(
        {"SK_ID_CURR": 123}
    )

    response = client.get("/predict/123")

    assert response.status_code == 200
    data = response.json()
    assert data["client_id"] == 123
    assert data["score"] == 0.7
    assert data["decision"] == "Refusé"  # car 0.7 > 0.5


def test_predict_client_not_found(client, mock_loader):
    """Cas : client inexistant dans la base SQLite."""
    mock_loader.get_client_data.return_value = None

    response = client.get("/predict/999")
    assert response.status_code == 404
    assert "non trouvé" in response.json()["detail"]


def test_predict_missing_values(client, mock_loader, mock_model):
    """T005 : Test avec valeurs manquantes (AMT_ANNUITY est NULL)."""
    mock_loader.model = mock_model
    # Simulation d'une valeur manquante qui devient NaN après conversion numérique
    features = create_client_features({"AMT_ANNUITY": np.nan})
    mock_loader.get_client_data.return_value = features

    response = client.get("/predict/123")

    assert response.status_code == 200
    # On vérifie que l'API ne crashe pas et renvoie bien une prédiction
    assert "score" in response.json()


def test_predict_aberrant_values(client, mock_loader, mock_model):
    """T005 : Test avec valeurs aberrantes (DAYS_BIRTH > 0)."""
    mock_loader.model = mock_model
    # Un âge positif en jours est aberrant dans ce dataset (attendu négatif)
    features = create_client_features({"DAYS_BIRTH": 1000})
    mock_loader.get_client_data.return_value = features

    response = client.get("/predict/123")

    assert response.status_code == 200
    assert "score" in response.json()


def test_predict_model_error(client, mock_loader, mock_model):
    """Vérifie la gestion d'erreur si le modèle échoue."""
    mock_loader.model = mock_model
    mock_model.predict_proba.side_effect = Exception("Model inference failed")
    mock_model.predict.side_effect = Exception("Model inference failed")

    mock_loader.get_client_data.return_value = create_client_features()

    response = client.get("/predict/123")
    assert response.status_code == 500
    assert "Erreur de prédiction" in response.json()["detail"]


def test_predict_no_model(client, mock_loader):
    """Vérifie l'erreur si le modèle n'est pas chargé."""
    # Forcer loader.model à être None
    # Note: On doit mocker la propriété. C'est plus simple de mocker ModelLoader.model directement.
    type(mock_loader).model = property(lambda x: None)

    response = client.get("/predict/123")
    assert response.status_code == 500
    assert "Modèle non disponible" in response.json()["detail"]
