import os
import sqlite3
import pytest
from src.database.db_utils import init_logs_db, log_prediction

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


def test_init_logs_db_already_exists():
    """Vérifie que init_logs_db gère le cas où la table et la colonne latency existent déjà."""
    init_logs_db(DB_PATH)
    # Deuxième appel ne doit pas crasher
    init_logs_db(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(prediction_logs)")
    cols = [c[1] for c in cursor.fetchall()]
    conn.close()
    assert "latency" in cols


def test_log_prediction_missing_features(db_connection):
    """Vérifie log_prediction avec des features manquantes ou invalides."""
    db_connection.close()
    init_logs_db(DB_PATH)

    # Dictionnaire vide
    log_prediction(DB_PATH, 124, 0.1, "Accordé", features={})

    # Avec des valeurs non numériques
    log_prediction(DB_PATH, 125, 0.1, "Accordé", features={"EXT_SOURCE_1": "invalid"})

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM prediction_logs WHERE client_id=125")
    row = cursor.fetchone()
    conn.close()
    assert row is not None
