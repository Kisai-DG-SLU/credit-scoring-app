import pytest
import sqlite3
import pandas as pd
import numpy as np
from src.model.loader import ModelLoader


@pytest.fixture
def temp_db(tmp_path):
    """Crée une base SQLite temporaire pour les tests."""
    db_path = tmp_path / "test_db.sqlite"
    conn = sqlite3.connect(db_path)
    # Création d'une table clients minimale
    df = pd.DataFrame(
        {
            "SK_ID_CURR": [1, 2, 3],
            "TARGET": [0, 1, 0],
            "AMT_ANNUITY": [1000.0, None, 3000.0],  # Une valeur manquante
            "DAYS_BIRTH": [-10000, -15000, 5000],  # Une valeur aberrante (positive)
            "TEXT_COL": ["A", "B", "C"],  # Une colonne texte à convertir
        }
    )
    df.to_sql("clients", conn, index=False)
    conn.close()
    return str(db_path)


def test_loader_singleton():
    """Vérifie que le loader est bien un singleton."""
    l1 = ModelLoader()
    l2 = ModelLoader()
    assert l1 is l2


def test_get_client_data_success(temp_db):
    """Vérifie la récupération et conversion des données."""
    loader = ModelLoader()
    loader.db_path = temp_db  # On pointe vers la base de test

    # Test client 1 (nominal)
    df = loader.get_client_data(1)
    assert df is not None
    assert df.iloc[0]["SK_ID_CURR"] == 1
    assert df.iloc[0]["AMT_ANNUITY"] == 1000.0

    # Test client 2 (valeur manquante)
    df = loader.get_client_data(2)
    assert np.isnan(df.iloc[0]["AMT_ANNUITY"])

    # Test client 3 (valeur aberrante & conversion texte)
    df = loader.get_client_data(3)
    # TEXT_COL devrait devenir NaN car non numérique et errors='coerce'
    assert np.isnan(df.iloc[0]["TEXT_COL"])
    assert df.iloc[0]["DAYS_BIRTH"] == 5000


def test_get_client_data_not_found(temp_db):
    """Vérifie le cas d'un client absent."""
    loader = ModelLoader()
    loader.db_path = temp_db
    df = loader.get_client_data(999)
    assert df is None


def test_get_client_data_no_db():
    """Vérifie le comportement si la base n'existe pas."""
    loader = ModelLoader()
    loader.db_path = "non_existent.sqlite"
    df = loader.get_client_data(1)
    assert df is None
