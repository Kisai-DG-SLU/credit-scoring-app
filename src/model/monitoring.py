import pandas as pd
import sqlite3
import os
import logging
from evidently import Report
from evidently.presets.drift import DataDriftPreset

# Configuration logging si non déjà faite par l'appelant
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_FEATURES = [
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


def generate_drift_report(db_path, output_path="drift_report.html", features=None):
    """
    Génère un rapport de Data Drift Evidently.

    Args:
        db_path (str): Chemin BDD.
        output_path (str): Chemin sortie HTML.
        features (list): Liste des features à surveiller. Si None, utilise DEFAULT_FEATURES.
    """
    if features is None:
        features = DEFAULT_FEATURES

    if not os.path.exists(db_path):
        logger.error(f"Base de données non trouvée : {db_path}")
        return None

    conn = sqlite3.connect(db_path)

    # Chargement Reference (Table clients)
    # On limite à 10000 comme demandé dans la spec
    try:
        ref_df = pd.read_sql_query("SELECT * FROM clients LIMIT 10000", conn)
    except Exception as e:
        logger.error(f"Erreur lecture reference (table clients) : {e}")
        conn.close()
        return None

    # Chargement Current (Table prediction_logs)
    try:
        curr_df = pd.read_sql_query("SELECT * FROM prediction_logs", conn)
    except Exception as e:
        logger.error(f"Erreur lecture logs (table prediction_logs) : {e}")
        conn.close()
        return None

    conn.close()

    if curr_df.empty:
        logger.warning("Pas de données de production (logs) pour le monitoring.")
        # On peut retourner None ou générer un rapport vide, ici None signale l'absence d'action
        return None

    # Filtrage des colonnes communes et présentes dans la liste features
    # On assure aussi que les types sont compatibles (numériques)
    available_features = []
    for f in features:
        if f in ref_df.columns and f in curr_df.columns:
            # Vérification sommaire si numérique (Evidently gère, mais mieux vaut être sûr)
            available_features.append(f)

    if not available_features:
        logger.error("Aucune feature commune valide trouvée entre reference et logs.")
        return None

    # Préparation des datasets réduits
    # On utilise .copy() pour éviter les warnings SettingWithCopy
    ref_data = ref_df[available_features].copy()
    curr_data = curr_df[available_features].copy()

    # Nettoyage basique des NaN si nécessaire (Evidently gère, mais parfois warning)
    # On laisse Evidently gérer.

    # Génération rapport
    logger.info(
        f"Génération du rapport de drift sur {len(available_features)} features..."
    )

    report = Report(metrics=[DataDriftPreset()])

    try:
        snapshot = report.run(reference_data=ref_data, current_data=curr_data)

        # Création du dossier parent si besoin
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        snapshot.save_html(output_path)
        logger.info(f"Rapport sauvegardé : {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Erreur exécution Evidently : {e}")
        return None
