from unittest.mock import MagicMock
import numpy as np
import pandas as pd
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
    mock_loader.predict_proba.return_value = 0.7
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
    mock_loader.predict_proba.return_value = 0.3
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
    mock_loader.predict_proba.return_value = 0.8
    # Un âge positif en jours est aberrant dans ce dataset (attendu négatif)
    features = create_client_features({"DAYS_BIRTH": 1000})
    mock_loader.get_client_data.return_value = features

    response = client.get("/predict/123")

    assert response.status_code == 200
    assert "score" in response.json()


def test_predict_model_error(client, mock_loader, mock_model):
    """Vérifie la gestion d'erreur si le modèle échoue."""
    mock_loader.model = mock_model
    mock_loader.predict_proba.side_effect = Exception("Model inference failed")

    mock_loader.get_client_data.return_value = create_client_features()

    response = client.get("/predict/123")
    assert response.status_code == 500
    assert "Erreur de prédiction" in response.json()["detail"]


def test_predict_no_model(client, mock_loader):
    """Vérifie l'erreur si le modèle n'est pas chargé."""
    mock_loader.predict_proba.return_value = None

    response = client.get("/predict/123")
    assert response.status_code == 500
    assert "Modèle non disponible" in response.json()["detail"]


def test_predict_invalid_type(client):
    """T046 : Vérifie que l'API rejette un ID de type chaîne de caractères."""
    response = client.get("/predict/abc")
    assert response.status_code == 422


def test_predict_float_id(client):
    """T046 : Vérifie que l'API rejette un ID de type flottant."""
    response = client.get("/predict/123.45")
    assert response.status_code == 422


def test_predict_negative_id(client, mock_loader):
    """T046 : Vérifie le comportement avec un ID négatif (hors plage logique)."""
    mock_loader.get_client_data.return_value = None
    response = client.get("/predict/-1")
    # FastAPI accepte l'entier négatif, mais le loader ne le trouvera pas
    assert response.status_code == 404


def test_predict_very_large_id(client, mock_loader):
    """T046 : Vérifie le comportement avec un ID très grand."""
    mock_loader.get_client_data.return_value = None
    # Test avec un ID dépassant les entiers standards
    response = client.get("/predict/999999999999999999")
    assert response.status_code == 404


def test_predict_zero_id(client, mock_loader):
    """T046 : Vérifie le comportement avec un ID égal à zéro."""
    mock_loader.get_client_data.return_value = None
    response = client.get("/predict/0")
    assert response.status_code == 404


def test_predict_infinite_feature(client, mock_loader, mock_model):
    """T046 : Vérifie que l'API gère les valeurs infinies dans les features."""
    mock_loader.model = mock_model
    mock_loader.predict_proba.return_value = 0.5
    # Simulation d'une valeur infinie (hors plage standard)
    features = create_client_features({"AMT_INCOME_TOTAL": np.inf})
    mock_loader.get_client_data.return_value = features

    response = client.get("/predict/123")
    assert response.status_code == 200
    assert "score" in response.json()


def test_clean_feature_names():
    """Vérifie le nettoyage des noms de colonnes."""
    from src.api.main import clean_feature_names

    df = pd.DataFrame({"Feature (Name)!": [1]})
    df_clean = clean_feature_names(df)
    assert "Feature__Name__" in df_clean.columns
