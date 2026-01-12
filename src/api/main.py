from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from src.model.loader import loader
from src.data.db_utils import init_logs_db, log_prediction
import os
import logging
import time
import pandas as pd

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("api.log"), logging.StreamHandler()],
)
logger = logging.getLogger("credit-scoring-api")

app = FastAPI(title="Credit Scoring API", version="1.0.0")


def clean_feature_names(df):
    """Nettoyage des noms de features (standard Projet 6)"""
    df.columns = [
        "".join(c if c.isalnum() else "_" for c in str(x)) for x in df.columns
    ]
    return df


@app.on_event("startup")
async def startup_event():
    logger.info("Démarrage de l'API - Initialisation des ressources...")
    init_logs_db(loader.db_path)
    # Préchauffage : charge le modèle et initialise SHAP TreeExplainer
    loader.load_artifacts()
    logger.info("Ressources initialisées avec succès.")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(
        f"Method: {request.method} Path: {request.url.path} Duration: {duration:.4f}s Status: {response.status_code}"
    )
    return response


class PredictionResponse(BaseModel):
    client_id: int
    score: float
    decision: str
    threshold: float
    shap_values: dict[str, float]
    base_value: float


# Seuil par défaut (issu du Projet 6)
DEFAULT_THRESHOLD = 0.49


@app.get("/health")
def health_check():
    model = loader.load_artifacts()
    db_exists = os.path.exists("data/database.sqlite")
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "database_available": db_exists,
    }


@app.get("/predict/{client_id}", response_model=PredictionResponse)
def predict(client_id: int):
    start_time = time.time()
    model = loader.model

    if model is None:
        raise HTTPException(status_code=500, detail="Modèle non disponible")

    # Récupération des données du client via SQLite
    client_data = loader.get_client_data(client_id)

    if client_data is None:
        raise HTTPException(status_code=404, detail=f"Client {client_id} non trouvé")

    # Préparation des features (on retire TARGET si présent et SK_ID_CURR)
    features = client_data.drop(columns=["TARGET", "SK_ID_CURR"], errors="ignore")
    features = clean_feature_names(features)

    # Prédiction de probabilité (classe 1 = défaut)
    try:
        # LightGBM/Scikit-learn predict_proba
        prob = model.predict_proba(features)[0][1]
    except Exception:
        # Fallback si le modèle n'a pas predict_proba ou autre erreur
        try:
            prob = model.predict(features)[0]
        except Exception as e2:
            raise HTTPException(status_code=500, detail=f"Erreur de prédiction : {e2}")

    # Calcul des valeurs SHAP
    shap_data = {}
    base_val = 0.0
    try:
        explanation = loader.get_shap_values(features)
        if explanation is not None:
            # On récupère les valeurs pour la classe 1 (défaut)
            vals = explanation.values[0]
            # base_values peut être un scalaire ou un tableau
            bv = explanation.base_values
            if isinstance(bv, (list, pd.Series, pd.Index)) or hasattr(bv, "__len__"):
                base_val = float(bv[0])
                if len(vals.shape) > 1:
                    vals = vals[:, 1]
                    base_val = float(bv[0][1])
            else:
                base_val = float(bv)

            # Création d'un dictionnaire feature: value
            feature_names = features.columns.tolist()
            full_shap = dict(zip(feature_names, vals))

            # On ne garde que les 10 plus importantes (en valeur absolue)
            sorted_shap = sorted(
                full_shap.items(), key=lambda x: abs(x[1]), reverse=True
            )[:10]
            shap_data = dict(sorted_shap)
    except Exception as e:
        logger.error(f"Erreur lors du calcul SHAP dans l'API : {e}")
        shap_data = {"error": 0.0}

    decision = "Refusé" if prob > DEFAULT_THRESHOLD else "Accordé"

    latency = time.time() - start_time

    try:
        log_prediction(
            loader.db_path,
            client_id,
            float(prob),
            decision,
            features.iloc[0],
            latency=latency,
        )
    except Exception as e:
        logger.error(f"Erreur lors du logging en base : {e}")

    logger.info(
        f"Prediction for Client {client_id}: Score={prob:.4f}, Decision={decision}"
    )

    return PredictionResponse(
        client_id=client_id,
        score=float(prob),
        decision=decision,
        threshold=DEFAULT_THRESHOLD,
        shap_values=shap_data,
        base_value=base_val,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
