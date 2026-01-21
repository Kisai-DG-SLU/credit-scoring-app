import pandas as pd
import sqlite3
import os
import logging
from evidently import Report
from evidently.presets import DataDriftPreset

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
    if features is None:
        features = DEFAULT_FEATURES

    try:
        conn = sqlite3.connect(db_path)
        ref_df = pd.read_sql_query("SELECT * FROM clients LIMIT 10000", conn)
        curr_df = pd.read_sql_query("SELECT * FROM prediction_logs", conn)
        conn.close()
    except Exception as e:
        logger.error(f"Erreur lecture BDD : {e}")
        return None

    if curr_df.empty:
        return None

    available_features = [
        f for f in features if f in ref_df.columns and f in curr_df.columns
    ]
    ref_data = ref_df[available_features].copy().reset_index(drop=True)
    curr_data = curr_df[available_features].copy().reset_index(drop=True)

    try:
        # Initialisation de la configuration
        report_config = Report(metrics=[DataDriftPreset(drift_share=0.3)])

        # GÉNÉRATION : On récupère l'objet résultat (comme dans ton notebook)
        actual_report = report_config.run(
            reference_data=ref_data, current_data=curr_data
        )

        # SAUVEGARDE : Sur l'objet résultat
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        actual_report.save_html(output_path)

        logger.info(f"✅ Rapport généré avec succès : {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"❌ Erreur lors de la génération du rapport : {e}")
        return None
