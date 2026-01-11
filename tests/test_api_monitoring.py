import os
import sqlite3
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import pandas as pd

# On doit définir les variables d'env AVANT d'importer l'app si elles sont utilisées au niveau module
# Mais ici DB_FILE est défini dans le module. On va le patcher.

from src.api.main import app
from src.data.db_utils import init_logs_db

TEST_DB_FILE = "test_api_logs.sqlite"


@pytest.fixture
def client():
    # Setup : Patcher DB_FILE dans main et initialiser la DB de test
    with patch("src.api.main.DB_FILE", TEST_DB_FILE):
        if os.path.exists(TEST_DB_FILE):
            os.remove(TEST_DB_FILE)

        # On force l'init de la DB car le startup event peut ne pas être déclenché par TestClient de la même façon
        # ou on veut être sûr de l'état
        init_logs_db(TEST_DB_FILE)

        with TestClient(app) as c:
            yield c

    # Teardown
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)


@pytest.fixture
def mock_loader():
    with patch("src.api.main.loader") as mock:
        # Mock du modèle
        mock_model = MagicMock()
        mock_model.predict_proba.return_value = [
            [0.8, 0.2]
        ]  # Prob défaut = 0.2 -> Accordé
        mock.model = mock_model

        # Mock des données client
        # On doit retourner un DataFrame avec les colonnes attendues
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
        mock.get_client_data.return_value = pd.DataFrame(features_data)

        yield mock


def test_predict_logs_to_db(client, mock_loader):
    """Vérifie que l'appel à /predict enregistre bien dans la BDD."""

    response = client.get("/predict/123")
    assert response.status_code == 200

    # Vérification BDD
    conn = sqlite3.connect(TEST_DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM prediction_logs WHERE client_id=123")
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    # row[2] = score (0.2), row[3] = decision ("Accordé")
    assert abs(row[2] - 0.2) < 0.001
    assert row[3] == "Accordé"
    # Vérif feature EXT_SOURCE_1 (colonne 5 normalement, après id, client_id, score, decision, timestamp)
    # Les colonnes sont id, client_id, score, decision, timestamp, EXT1, EXT2...
    # Donc EXT1 est à l'index 5
    assert abs(row[5] - 0.5) < 0.001
