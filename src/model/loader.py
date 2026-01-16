import joblib
import os
import logging
import sqlite3
import pandas as pd
import shap
import numpy as np
import onnxruntime as ort
from pathlib import Path
from functools import lru_cache

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class ModelLoader:
    _instance = None
    _model = None
    _onnx_session = None
    _explainer = None
    _db_path = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
            cls._instance.model = None
            cls._instance.onnx_session = None
            cls._instance.explainer = None
            cls._instance.db_path = None
            cls._instance._detect_db()
        return cls._instance

    def _detect_db(self):
        """Détecte la meilleure base de données disponible."""
        paths = [
            BASE_DIR / "data/database.sqlite",
            BASE_DIR / "data/database_lite.sqlite",
        ]

        for p in paths:
            if p.exists():
                self.db_path = str(p)
                logger.info(f"Base de données détectée : {self.db_path}")
                return

        self.db_path = str(BASE_DIR / "data/database.sqlite")
        logger.warning(
            f"Aucune base de données trouvée, utilisation du chemin par défaut : {self.db_path}"
        )

    def load_artifacts(
        self, model_path="src/model/model.joblib", onnx_path="src/model/model.onnx"
    ):
        """Charge le modèle (ONNX prioritaire) et l'explainer SHAP."""
        # 1. Chargement ONNX pour l'inférence rapide
        if self.onnx_session is None and os.path.exists(onnx_path):
            logger.info(f"Chargement de la session ONNX depuis {onnx_path}")
            try:
                self.onnx_session = ort.InferenceSession(onnx_path)
            except Exception as e:
                logger.error(f"Erreur chargement ONNX : {e}")

        # 2. Chargement Joblib pour SHAP (qui a besoin de l'objet LightGBM)
        if self.model is None:
            if os.path.exists(model_path):
                logger.info(f"Chargement du modèle Joblib depuis {model_path}")
                try:
                    self.model = joblib.load(model_path)

                    # Extraction du classifieur pour SHAP
                    if (
                        hasattr(self.model, "named_steps")
                        and "clf" in self.model.named_steps
                    ):
                        classifier = self.model.named_steps["clf"]
                    else:
                        classifier = self.model

                    logger.info("Initialisation de SHAP TreeExplainer...")
                    self.explainer = shap.TreeExplainer(classifier)
                except Exception as e:
                    logger.error(f"Erreur chargement Joblib/SHAP : {e}")
            else:
                logger.warning(f"Fichier modèle non trouvé : {model_path}")

        return self.model

    @lru_cache(maxsize=128)
    def predict_proba(self, client_id):
        """Prédit la probabilité avec ONNX (si dispo) et met en cache."""
        data = self.get_client_data(client_id)
        if data is None:
            return None

        features = data.drop(columns=["TARGET", "SK_ID_CURR"], errors="ignore")

        # Inférence ONNX (Prioritaire car ultra rapide)
        if self.onnx_session is not None:
            try:
                # Préparation de l'input (doit être float32)
                inputs = {
                    self.onnx_session.get_inputs()[0].name: features.values.astype(
                        np.float32
                    )
                }
                # ONNX retourne [label, probabilités]
                # probas est une liste de dict ou un array selon le converter
                outputs = self.onnx_session.run(None, inputs)

                # Typiquement : [array([label]), [ {0: p0, 1: p1} ]]
                # Ou si c'est un array direct :
                if isinstance(outputs[1], list):
                    return outputs[1][0][1]  # proba de la classe 1
                return outputs[1][0, 1]
            except Exception as e:
                logger.error(f"Erreur inférence ONNX : {e}, fallback sur Joblib")

        # Fallback Joblib
        if self.model is not None:
            return self.model.predict_proba(features)[0, 1]

        return None

    def get_client_data(self, client_id):
        """Récupère les données d'un client spécifique depuis la base SQLite."""
        if not self.db_path or not os.path.exists(self.db_path):
            return None

        try:
            conn = sqlite3.connect(self.db_path)
            query = "SELECT * FROM clients WHERE SK_ID_CURR = ?"
            df = pd.read_sql_query(query, conn, params=(client_id,))
            conn.close()

            if df.empty:
                return None

            for col in df.columns:
                if col not in ["SK_ID_CURR", "TARGET"]:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            return df
        except Exception as e:
            logger.error(f"Erreur lecture SQLite : {e}")
            return None

    @lru_cache(maxsize=128)
    def get_shap_values_cached(self, client_id):
        """Calcule les valeurs SHAP pour un client et met en cache."""
        data = self.get_client_data(client_id)
        if data is None:
            return None

        features = data.drop(columns=["TARGET", "SK_ID_CURR"], errors="ignore")

        if self.explainer is None:
            self.load_artifacts()

        if self.explainer is not None:
            try:
                shap_values = self.explainer(features)
                return shap_values
            except Exception as e:
                logger.error(f"Erreur calcul SHAP : {e}")
                return None
        return None

    def _reset(self):
        """Réinitialise l'instance (usage interne pour les tests)."""
        self.model = None
        self.onnx_session = None
        self.explainer = None
        self.predict_proba.cache_clear()
        self.get_shap_values_cached.cache_clear()
        self._detect_db()


# Instance globale pour accès facile
loader = ModelLoader()
