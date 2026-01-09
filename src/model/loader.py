import joblib
import os
import logging
import sqlite3
import pandas as pd

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelLoader:
    _instance = None
    _model = None
    _db_path = "data/database.sqlite"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
        return cls._instance

    def load_artifacts(self, model_path="src/model/model.joblib"):
        """Charge le modèle s'il n'est pas déjà chargé."""
        if self._model is None:
            if os.path.exists(model_path):
                logger.info(f"Chargement du modèle depuis {model_path}")
                try:
                    self._model = joblib.load(model_path)
                except Exception as e:
                    logger.error(f"Erreur lors du chargement du modèle : {e}")
            else:
                logger.warning(f"Fichier modèle non trouvé : {model_path}")

        return self._model

    def get_client_data(self, client_id):
        """Récupère les données d'un client spécifique depuis la base SQLite."""
        if not os.path.exists(self._db_path):
            logger.error(f"Base de données non trouvée : {self._db_path}")
            return None

        try:
            conn = sqlite3.connect(self._db_path)
            query = "SELECT * FROM clients WHERE SK_ID_CURR = ?"
            df = pd.read_sql_query(query, conn, params=(client_id,))
            conn.close()

            if df.empty:
                logger.warning(f"Client {client_id} non trouvé dans la base.")
                return None

            # Conversion des colonnes en numérique pour éviter les erreurs de type 'object'
            # (Certaines colonnes peuvent contenir des chaînes vides ou None converties en object par SQLite)
            for col in df.columns:
                if col not in ["SK_ID_CURR", "TARGET"]:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            return df
        except Exception as e:
            logger.error(f"Erreur lors de la lecture de la base SQLite : {e}")
            return None

    @property
    def model(self):
        if self._model is None:
            self.load_artifacts()
        return self._model


# Instance globale pour accès facile
loader = ModelLoader()
