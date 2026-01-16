import sqlite3
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Ajouter le chemin racine pour les imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.model.loader import loader  # noqa: E402
from src.database.db_utils import log_prediction  # noqa: E402


def get_db_path():
    return loader.db_path


def reset_logs():
    """Supprime toutes les entrées de la table prediction_logs."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM prediction_logs")
    conn.commit()
    conn.close()
    print("Logs réinitialisés.")


def simulate_production(n_samples=1000, drift_mode=False):
    """
    Simule n_samples appels API.
    Si drift_mode est True, on altère les données pour créer un drift visible.
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)

    # Récupérer des clients aléatoires depuis la base
    print(f"Chargement de {n_samples} clients de référence...")
    query = f"SELECT * FROM clients ORDER BY RANDOM() LIMIT {n_samples}"
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        print("Erreur: La table clients est vide.")
        return

    print(f"Simulation en cours (Mode drift: {drift_mode})...")

    # Chargement du modèle
    loader.load_artifacts()

    count = 0
    for _, row in df.iterrows():
        client_id = int(row["SK_ID_CURR"])

        # Préparation des features
        features = row.copy()

        # Injection de DRIFT si demandé
        if drift_mode:
            # On altère artificiellement les features les plus importantes
            if "EXT_SOURCE_2" in features:
                features["EXT_SOURCE_2"] = (
                    features["EXT_SOURCE_2"] * 0.5
                )  # Chute de la fiabilité source 2
            if "AMT_INCOME_TOTAL" in features:
                features["AMT_INCOME_TOTAL"] = (
                    features["AMT_INCOME_TOTAL"] * 2.0
                )  # Hausse soudaine des revenus
            if "DAYS_BIRTH" in features:
                features["DAYS_BIRTH"] = (
                    features["DAYS_BIRTH"] - 5000
                )  # Population plus âgée

        # Calcul du score
        # On utilise une version simplifiée de l'inférence pour la simulation
        score = loader.predict_proba(client_id)
        if score is None:
            continue

        decision = "Accepté" if score < 0.5 else "Refusé"
        latency = np.random.uniform(0.05, 0.3)  # Simulation latence

        # Enregistrement
        log_prediction(
            db_path=db_path,
            client_id=client_id,
            score=float(score),
            decision=decision,
            features=features,
            latency=latency,
        )
        count += 1
        if count % 100 == 0:
            print(f"Injecté {count}/{n_samples}...")

    print(f"Succès: {count} logs injectés.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/database/simulation_cli.py [baseline|drift|reset]")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "reset":
        reset_logs()
    elif cmd == "baseline":
        simulate_production(n_samples=1000, drift_mode=False)
    elif cmd == "drift":
        simulate_production(n_samples=500, drift_mode=True)
    else:
        print(f"Commande inconnue: {cmd}")
