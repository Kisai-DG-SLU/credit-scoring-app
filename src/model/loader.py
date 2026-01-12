import joblib
import os
import logging
import sqlite3
import pandas as pd
import shap
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class ModelLoader:
    _instance = None
    _model = None
    _explainer = None
    _db_path = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
            cls._instance._detect_db()
        return cls._instance

    def _detect_db(self):
        """Détecte la meilleure base de données disponible."""
        # Chemins absolus pour éviter les surprises
        paths = [
            BASE_DIR / "data/database.sqlite",
            BASE_DIR / "data/database_lite.sqlite",
        ]

        for p in paths:
            if p.exists():
                self._db_path = str(p)
                logger.info(f"Base de données détectée : {self._db_path}")
                return

        # Défaut si rien n'est trouvé
        self._db_path = str(BASE_DIR / "data/database.sqlite")
        logger.warning(
            f"Aucune base de données trouvée, utilisation du chemin par défaut : {self._db_path}"
        )

    @property
    def db_path(self):
        return self._db_path

    def load_artifacts(self, model_path="src/model/model.joblib"):
        """Charge le modèle et l'explainer SHAP s'ils ne sont pas déjà chargés."""
        if self._model is None:
            if os.path.exists(model_path):
                logger.info(f"Chargement du modèle depuis {model_path}")
                try:
                    self._model = joblib.load(model_path)

                    # Extraction du classifieur du Pipeline pour SHAP
                    # Si c'est un Pipeline, on prend la dernière étape
                    if (
                        hasattr(self._model, "named_steps")
                        and "clf" in self._model.named_steps
                    ):
                        classifier = self._model.named_steps["clf"]
                        logger.info(
                            "Initialisation de SHAP TreeExplainer sur le classifieur..."
                        )
                        self._explainer = shap.TreeExplainer(classifier)
                    else:
                        logger.info("Initialisation de SHAP Explainer standard...")
                        self._explainer = shap.Explainer(self._model)
                except Exception as e:
                    logger.error(f"Erreur lors du chargement des artefacts : {e}")
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
            for col in df.columns:
                if col not in ["SK_ID_CURR", "TARGET"]:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            return df
        except Exception as e:
            logger.error(f"Erreur lors de la lecture de la base SQLite : {e}")
            return None

    def get_shap_values(self, features):
        """Calcule les valeurs SHAP pour un ensemble de features."""
        if self._explainer is None:
            self.load_artifacts()

        if self._explainer is not None:
            try:
                shap_values = self._explainer(features)
                return shap_values
            except Exception as e:
                logger.error(f"Erreur lors du calcul SHAP : {e}")
                return None
        return None

    @property
    def model(self):
        if self._model is None:
            self.load_artifacts()
        return self._model


# Instance globale pour accès facile
loader = ModelLoader()
