import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np

from src.model.loader import loader
from src.api.main import app


@pytest.fixture(autouse=True)
def reset_loader():
    """Réinitialise le singleton loader avant chaque test."""
    loader._reset()
    yield
    loader._reset()


@pytest.fixture
def client():
    """Fixture pour le client de test FastAPI."""
    return TestClient(app)


@pytest.fixture
def mock_loader():
    """Fixture pour mocker le ModelLoader avec comportements par défaut."""
    with patch("src.api.main.loader") as mock:
        # Mock SHAP par défaut pour éviter les crashes dans predict()
        shap_mock = MagicMock()
        # On simule un tableau (1, N) pour 1 sample
        shap_mock.values = np.array([[0.01] * 200])
        shap_mock.base_values = np.array([0.5])
        mock.get_shap_values_cached.return_value = shap_mock
        yield mock


@pytest.fixture(autouse=True)
def mock_log_prediction():
    """Fixture automatique pour mocker log_prediction (évite l'accès SQLite)."""
    with patch("src.api.main.log_prediction") as mock:
        yield mock


@pytest.fixture
def mock_model():
    """Fixture pour simuler le modèle LightGBM."""
    model = MagicMock()
    # Simule predict_proba qui renvoie [prob_classe_0, prob_classe_1]
    model.predict_proba.return_value = np.array([[0.3, 0.7]])
    return model


def create_client_features(overrides=None):
    """
    Data Factory pour générer des features client.
    Inspiré du fragment 'data-factories.md'.
    """
    defaults = {
        "SK_ID_CURR": 100002,
        "TARGET": 0,
        "NAME_CONTRACT_TYPE": "Cash loans",
        "CODE_GENDER": "M",
        "FLAG_OWN_CAR": "N",
        "FLAG_OWN_REALTY": "Y",
        "CNT_CHILDREN": 0,
        "AMT_INCOME_TOTAL": 202500.0,
        "AMT_CREDIT": 406597.5,
        "AMT_ANNUITY": 24700.5,
        "DAYS_BIRTH": -9461,  # ~25 ans
        "DAYS_EMPLOYED": -637,
        "REGION_RATING_CLIENT": 2,
        # Ajoutez ici d'autres colonnes si nécessaire
    }
    if overrides:
        defaults.update(overrides)

    return pd.DataFrame([defaults])
