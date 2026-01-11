import os
import sqlite3
import pytest
from src.model.monitoring import generate_drift_report

TEST_DB = "test_monitoring.sqlite"
REPORT_PATH = "test_drift_report.html"


@pytest.fixture
def monitoring_db():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    conn = sqlite3.connect(TEST_DB)

    # Création table reference (clients)
    # On met quelques colonnes clés
    conn.execute(
        """
    CREATE TABLE clients (
        SK_ID_CURR INTEGER PRIMARY KEY,
        EXT_SOURCE_1 REAL,
        AMT_INCOME_TOTAL REAL
    )
    """
    )

    # Insertion données reference
    conn.execute("INSERT INTO clients VALUES (1, 0.5, 50000)")
    conn.execute("INSERT INTO clients VALUES (2, 0.6, 60000)")

    # Création table current (prediction_logs)
    conn.execute(
        """
    CREATE TABLE prediction_logs (
        id INTEGER PRIMARY KEY,
        client_id INTEGER,
        score REAL,
        decision TEXT,
        timestamp DATETIME,
        EXT_SOURCE_1 REAL,
        AMT_INCOME_TOTAL REAL
    )
    """
    )

    # Insertion données current (légèrement différentes pour tester drift potentiel ou juste fonctionnement)
    conn.execute(
        "INSERT INTO prediction_logs VALUES (1, 101, 0.1, 'Accordé', '2026-01-01', 0.1, 100000)"
    )
    conn.execute(
        "INSERT INTO prediction_logs VALUES (2, 102, 0.9, 'Refusé', '2026-01-02', 0.9, 120000)"
    )

    conn.commit()
    conn.close()

    yield TEST_DB

    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    if os.path.exists(REPORT_PATH):
        os.remove(REPORT_PATH)


def test_generate_drift_report(monitoring_db):
    """Test de la génération du rapport HTML."""

    # On appelle la fonction
    output_path = generate_drift_report(db_path=monitoring_db, output_path=REPORT_PATH)

    assert os.path.exists(output_path)
    # Vérification basique que le fichier n'est pas vide
    assert os.path.getsize(output_path) > 0

    # Nettoyage
    if os.path.exists(output_path):
        os.remove(output_path)
