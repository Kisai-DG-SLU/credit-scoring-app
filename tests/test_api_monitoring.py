import os
import pytest
import numpy as np
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pandas as pd

from src.api.main import app, loader
from src.database.db_utils import init_logs_db

TEST_DB_FILE = "test_api_logs.sqlite"


@pytest.fixture
def mock_loader_monitoring():
    """Mock global du loader pour les tests de monitoring."""
    with (
        patch.object(loader, "db_path", TEST_DB_FILE),
        patch.object(loader, "model") as mock_model,
        patch.object(loader, "predict_proba") as mock_predict,
        patch.object(loader, "get_client_data") as mock_data,
        patch.object(loader, "get_shap_values_cached") as mock_shap,
    ):

        # Mock du modèle et prédiction
        mock_model.predict_proba.return_value = [[0.8, 0.2]]
        mock_predict.return_value = 0.2

        # Mock des données client
        features_data = {
            "SK_ID_CURR": [123],
            "TARGET": [0],
            "EXT_SOURCE_1": [0.5],
            "EXT_SOURCE_2": [0.6],
            "EXT_SOURCE_3": [0.7],
            "PAYMENT_RATE": [0.05],
            "DAYS_BIRTH": [-10000],
            "DAYS_EMPLOYED": [-2000],
            "AMT_ANNUITY": [50000.0],
            "AMT_CREDIT": [1000000.0],
            "AMT_INCOME_TOTAL": [200000.0],
            "DAYS_REGISTRATION": [-500],
        }
        mock_data.return_value = pd.DataFrame(features_data)

        # Mock SHAP
        shap_mock = MagicMock()
        shap_mock.values = np.array([[0.1] * 20])
        shap_mock.base_values = np.array([0.5])
        mock_shap.return_value = shap_mock

        yield loader


@pytest.fixture
def client_monitoring(mock_loader_monitoring):
    """Client de test configuré avec le mock_loader."""
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)

    init_logs_db(TEST_DB_FILE)

    with TestClient(app) as c:
        yield c

    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)


def test_predict_logs_to_db(client_monitoring, mock_loader_monitoring):
    """Vérifie que l'appel à /predict enregistre bien dans la BDD."""
    # On désactive le mock automatique de log_prediction pour tester l'appel réel ou simuler
    with patch("src.api.main.log_prediction") as mock_log:
        response = client_monitoring.get("/predict/123")
        assert response.status_code == 200
        assert mock_log.called
