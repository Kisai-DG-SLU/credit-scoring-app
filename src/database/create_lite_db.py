import pandas as pd
import sqlite3
import os
import time
from src.database.db_utils import init_logs_db


def create_lite_sqlite(csv_path, db_path, table_name="clients", sample_size=3000):
    """
    Crée une base SQLite très légère à partir d'un échantillon du CSV.
    Garantit l'inclusion des IDs de démo : 100004 et 100431.
    """
    if not os.path.exists(csv_path):
        print(f"Erreur : Le fichier {csv_path} n'existe pas.")
        return

    print(
        f"Création de la base Ultra-Lite ({sample_size} lignes) : {csv_path} -> {db_path}"
    )
    start_time = time.time()

    # Supprimer l'ancienne base pour garantir la taille
    if os.path.exists(db_path):
        os.remove(db_path)

    try:
        # 1. Identifier et charger les clients de démo
        # On lit par morceaux pour ne pas saturer la RAM (le CSV fait 1.3Go)
        demo_ids = [100004, 100431]
        demo_dfs = []

        print("Recherche des IDs de démo dans le dataset complet...")
        chunk_size = 50000
        found_ids = set()

        for chunk in pd.read_csv(csv_path, chunksize=chunk_size):
            matches = chunk[chunk["SK_ID_CURR"].isin(demo_ids)]
            if not matches.empty:
                demo_dfs.append(matches)
                found_ids.update(matches["SK_ID_CURR"].tolist())

            if len(found_ids) == len(demo_ids):
                break

        # 2. Charger le reste pour atteindre sample_size
        remaining_needed = sample_size - len(found_ids)
        print(f"Chargement de {remaining_needed} lignes complémentaires...")
        other_df = pd.read_csv(csv_path, nrows=sample_size + 100)  # Marge
        other_df = other_df[~other_df["SK_ID_CURR"].isin(demo_ids)].head(
            remaining_needed
        )

        # 3. Fusionner
        df = pd.concat(demo_dfs + [other_df]).drop_duplicates(subset=["SK_ID_CURR"])

        # Connexion à SQLite
        conn = sqlite3.connect(db_path)

        # Écriture dans la base
        df.to_sql(table_name, conn, if_exists="replace", index=False)

        print("Création de l'index sur SK_ID_CURR...")
        conn.execute(f"CREATE INDEX idx_sk_id_curr_lite ON {table_name} (SK_ID_CURR)")

        print("Optimisation de la base (VACUUM)...")
        conn.execute("VACUUM")

        conn.commit()
        conn.close()

        # Initialisation de la table des logs dans la même base
        print("Initialisation de la table des logs...")
        init_logs_db(db_path)

        end_time = time.time()
        print(f"Base Lite créée avec succès en {end_time - start_time:.2f} secondes.")
        file_size = os.path.getsize(db_path) / (1024 * 1024)
        print(f"Taille du fichier : {file_size:.2f} Mo")

        if file_size > 10:
            print("ATTENTION : Le fichier dépasse encore 10 Mo. Réduire sample_size.")

    except Exception as e:
        print(f"Erreur lors de la création : {e}")


if __name__ == "__main__":
    CSV_FILE = "data/final_dataset.csv"
    DB_LITE_FILE = "data/database_lite.sqlite"

    # S'assurer que le dossier data existe
    os.makedirs("data", exist_ok=True)

    create_lite_sqlite(CSV_FILE, DB_LITE_FILE)
