import os
import sqlite3
import pytest
from src.data.db_utils import init_logs_db, log_prediction

DB_PATH = "test_logs.sqlite"


@pytest.fixture
def db_connection():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    yield conn
    conn.close()
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)


def test_init_logs_db(db_connection):
    """Vérifie que la table prediction_logs est bien créée."""
    # On ferme la connexion de fixture pour laisser init_logs_db gérer la sienne
    db_connection.close()

    init_logs_db(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='prediction_logs';"
    )
    table = cursor.fetchone()
    conn.close()

    assert table is not None
    assert table[0] == "prediction_logs"


def test_log_prediction(db_connection):
    """Vérifie l'insertion d'une prédiction."""
    db_connection.close()
    init_logs_db(DB_PATH)

    features = {
        "EXT_SOURCE_1": 0.5,
        "EXT_SOURCE_2": 0.6,
        "EXT_SOURCE_3": 0.7,
        "PAYMENT_RATE": 0.05,
        "DAYS_BIRTH": -10000,
        "DAYS_EMPLOYED": -2000,
        "AMT_ANNUITY": 50000.0,
        "AMT_CREDIT": 1000000.0,
        "AMT_INCOME_TOTAL": 200000.0,
        "DAYS_REGISTRATION": -500,
    }

    log_prediction(
        DB_PATH, client_id=123, score=0.85, decision="Refusé", features=features
    )

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM prediction_logs WHERE client_id=123")
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    # Vérification des colonnes principales (adapté selon le schéma créé)
    # On suppose l'ordre : id, client_id, score, decision, timestamp, ...features...
    assert row[1] == 123
    assert row[2] == 0.85
    assert row[3] == "Refusé"
    # Vérifie une feature
    # Il faudra ajuster l'index selon le schéma exact, mais pour l'instant on vérifie juste que ça a marché
