import pandas as pd
import sqlite3
import os
import time


def convert_csv_to_sqlite(csv_path, db_path, table_name="clients", chunksize=50000):
    """
    Convertit un fichier CSV lourd en base SQLite avec indexation.
    """
    if not os.path.exists(csv_path):
        print(f"Erreur : Le fichier {csv_path} n'existe pas.")
        return

    # Connexion à SQLite
    conn = sqlite3.connect(db_path)

    print(f"Début de la conversion : {csv_path} -> {db_path}")
    start_time = time.time()

    try:
        # Lecture et écriture par morceaux (chunks) pour gérer la RAM
        first_chunk = True
        for chunk in pd.read_csv(csv_path, chunksize=chunksize):
            # Pour le premier chunk, on remplace la table si elle existe
            # Pour les suivants, on ajoute les données
            if first_chunk:
                chunk.to_sql(table_name, conn, if_exists="replace", index=False)
                first_chunk = False
            else:
                chunk.to_sql(table_name, conn, if_exists="append", index=False)

            print(".", end="", flush=True)

        print("\nCréation de l'index sur SK_ID_CURR...")
        conn.execute(f"CREATE INDEX idx_sk_id_curr ON {table_name} (SK_ID_CURR)")

        conn.commit()
        end_time = time.time()
        print(f"Conversion terminée en {end_time - start_time:.2f} secondes.")

    except Exception as e:
        print(f"\nErreur lors de la conversion : {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    CSV_FILE = "data/final_dataset.csv"
    DB_FILE = "data/database.sqlite"

    # S'assurer que le dossier data existe
    os.makedirs("data", exist_ok=True)

    convert_csv_to_sqlite(CSV_FILE, DB_FILE)
