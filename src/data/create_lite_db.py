import pandas as pd
import sqlite3
import os
import time
from src.data.db_utils import init_logs_db


def create_lite_sqlite(csv_path, db_path, table_name="clients", sample_size=10000):
    """
    Crée une base SQLite légère à partir d'un échantillon du CSV.
    """
    if not os.path.exists(csv_path):
        print(f"Erreur : Le fichier {csv_path} n'existe pas.")
        return

    print(f"Création de la base Lite ({sample_size} lignes) : {csv_path} -> {db_path}")
    start_time = time.time()

    try:
        # Lecture d'un échantillon
        # On lit les premières lignes ou on échantillonne si le fichier n'est pas trop gros
        # Vu que final_dataset.csv fait 1.3Go, on va lire les N premières lignes pour la rapidité
        # ou utiliser skip-rows aléatoires. Pour une démo, les N premières suffisent souvent
        # car elles sont déjà mélangées dans beaucoup de datasets Kaggle.

        df = pd.read_csv(csv_path, nrows=sample_size)

        # Connexion à SQLite
        conn = sqlite3.connect(db_path)

        # Écriture dans la base
        df.to_sql(table_name, conn, if_exists="replace", index=False)

        print("Création de l'index sur SK_ID_CURR...")
        conn.execute(f"CREATE INDEX idx_sk_id_curr_lite ON {table_name} (SK_ID_CURR)")

        conn.commit()
        conn.close()

        # Initialisation de la table des logs dans la même base
        print("Initialisation de la table des logs...")
        init_logs_db(db_path)

        end_time = time.time()
        print(f"Base Lite créée avec succès en {end_time - start_time:.2f} secondes.")
        print(f"Taille du fichier : {os.path.getsize(db_path) / (1024*1024):.2f} Mo")

    except Exception as e:
        print(f"Erreur lors de la création : {e}")


if __name__ == "__main__":
    CSV_FILE = "data/final_dataset.csv"
    DB_LITE_FILE = "data/database_lite.sqlite"

    # S'assurer que le dossier data existe
    os.makedirs("data", exist_ok=True)

    create_lite_sqlite(CSV_FILE, DB_LITE_FILE)
