import sqlite3
import datetime

# Liste des features à logger (Top 10)
LOG_FEATURES = [
    "EXT_SOURCE_1",
    "EXT_SOURCE_2",
    "EXT_SOURCE_3",
    "PAYMENT_RATE",
    "DAYS_BIRTH",
    "DAYS_EMPLOYED",
    "AMT_ANNUITY",
    "AMT_CREDIT",
    "AMT_INCOME_TOTAL",
    "DAYS_REGISTRATION",
]


def init_logs_db(db_path="data/database.sqlite"):
    """
    Initialise la table des logs de prédiction si elle n'existe pas.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Construction de la requête de création
    # On ajoute les colonnes dynamiquement basées sur LOG_FEATURES
    cols = ", ".join([f"{feat} REAL" for feat in LOG_FEATURES])

    create_query = f"""
    CREATE TABLE IF NOT EXISTS prediction_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        score REAL,
        decision TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        {cols}
    )
    """

    cursor.execute(create_query)

    # Création d'index pour optimiser les requêtes par date
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_timestamp ON prediction_logs (timestamp)"
    )

    conn.commit()
    conn.close()


def log_prediction(db_path, client_id, score, decision, features):
    """
    Enregistre une prédiction et les features associées.

    Args:
        db_path (str): Chemin vers la BDD SQLite.
        client_id (int): ID du client.
        score (float): Score de probabilité.
        decision (str): Décision (Accordé/Refusé).
        features (dict): Dictionnaire contenant les valeurs des features.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Préparation des valeurs pour les features
    # On utilise features.get(feat, None) pour gérer les cas manquants
    # Attention: features peut être un DataFrame row (Series) ou un dict
    # On va gérer les deux cas

    feature_values = []
    for feat in LOG_FEATURES:
        val = None
        if hasattr(features, "get"):
            val = features.get(feat, None)
        elif hasattr(features, "__getitem__"):  # Pandas Series support
            try:
                val = features[feat]
            except KeyError:
                val = None

        # Conversion float simple pour éviter les types numpy
        if val is not None:
            try:
                val = float(val)
            except (ValueError, TypeError):
                val = None
        feature_values.append(val)

    # Construction de la requête
    placeholders = ", ".join(["?" for _ in LOG_FEATURES])
    insert_query = f"""
    INSERT INTO prediction_logs (client_id, score, decision, timestamp, {', '.join(LOG_FEATURES)})
    VALUES (?, ?, ?, ?, {placeholders})
    """

    # Date actuelle explicite
    timestamp = datetime.datetime.now().isoformat()

    params = [client_id, score, decision, timestamp] + feature_values

    cursor.execute(insert_query, params)
    conn.commit()
    conn.close()
