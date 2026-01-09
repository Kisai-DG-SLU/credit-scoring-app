import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np

# On patche le loader AVANT d'importer l'app pour éviter les effets de bord
with patch("src.model.loader.loader.load_artifacts"):
    from src.api.main import app


@pytest.fixture
def client():
    """Fixture pour le client de test FastAPI."""
    return TestClient(app)


@pytest.fixture
def mock_loader():
    """Fixture pour mocker le ModelLoader."""
    with patch("src.api.main.loader") as mock:
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
