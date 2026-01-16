import os
import sqlite3
import pandas as pd
from src.database.create_lite_db import create_lite_sqlite


def test_create_lite_sqlite(tmp_path):
    # Setup : Création d'un CSV factice
    csv_path = tmp_path / "mock_data.csv"
    db_path = tmp_path / "mock_lite.sqlite"

    df = pd.DataFrame(
        {
            "SK_ID_CURR": [1, 2, 3, 4, 5],
            "TARGET": [0, 1, 0, 1, 0],
            "EXT_SOURCE_1": [0.1, 0.2, 0.3, 0.4, 0.5],
        }
    )
    df.to_csv(csv_path, index=False)

    # Exécution
    create_lite_sqlite(str(csv_path), str(db_path), sample_size=3)

    # Vérifications
    assert os.path.exists(db_path)

    conn = sqlite3.connect(db_path)
    df_res = pd.read_sql_query("SELECT * FROM clients", conn)
    conn.close()

    assert len(df_res) == 3
    assert "SK_ID_CURR" in df_res.columns
    assert (
        "prediction_logs"
        in pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table'",
            sqlite3.connect(db_path),
        ).values
    )


def test_create_lite_sqlite_missing_file():
    # Vérifie que le script gère l'absence de fichier CSV sans crasher
    create_lite_sqlite("non_existent.csv", "wont_be_created.sqlite")
    assert not os.path.exists("wont_be_created.sqlite")


def test_create_lite_sqlite_full_flow(tmp_path):
    # Test avec un petit fichier réel pour couvrir la logique de lecture chunk
    csv_path = tmp_path / "full.csv"
    db_path = tmp_path / "full.sqlite"
    df = pd.DataFrame({"SK_ID_CURR": range(10), "TARGET": [0] * 10})
    df.to_csv(csv_path, index=False)

    # Appel avec un sample_size plus grand que le fichier
    create_lite_sqlite(str(csv_path), str(db_path), sample_size=100)
    assert os.path.exists(db_path)
