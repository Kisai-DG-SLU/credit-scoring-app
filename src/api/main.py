from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from src.model.loader import loader
from src.database.db_utils import init_logs_db, log_prediction
import os
import logging
import time

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
async def predict(client_id: int):
    """Calcule le score de crédit pour un client (avec cache LRU)."""
    start_time = time.time()
    try:
        # 1. Récupération des données (via loader qui gère SQLite)
        client_data = loader.get_client_data(client_id)
        if client_data is None:
            raise HTTPException(
                status_code=404, detail=f"Client {client_id} non trouvé dans la base."
            )

        # 2. Prédiction (via loader qui gère ONNX + Cache)
        score = loader.predict_proba(client_id)
        if score is None:
            raise HTTPException(status_code=500, detail="Modèle non disponible")

        # Seuil de décision (Standard Projet 7)
        threshold = 0.5
        decision = "Accepté" if score < threshold else "Refusé"

        # 3. Explicabilité SHAP (via loader qui gère Cache)
        shap_values = loader.get_shap_values_cached(client_id)

        # Extraction des features importance locales
        features_list = client_data.drop(
            columns=["TARGET", "SK_ID_CURR"], errors="ignore"
        ).columns.tolist()

        # Formater les SHAP values pour le dashboard
        # On prend les 10 plus importantes (valeur absolue)
        importances = []
        if shap_values is not None:
            # shap_values.values est un array (n_samples, n_features) ou (n_samples, n_features, n_classes)
            # Pour TreeExplainer sur LGBMBinary, c'est souvent (n_features,) pour un sample
            vals = (
                shap_values.values[0]
                if len(shap_values.values.shape) > 1
                else shap_values.values
            )

            for i, feat in enumerate(features_list):
                importances.append({"feature": feat, "shap_value": float(vals[i])})

            # Trier par importance absolue
            importances = sorted(
                importances, key=lambda x: abs(x["shap_value"]), reverse=True
            )[:15]

        execution_time = time.time() - start_time

        # 4. Logging en base SQLite pour monitoring
        log_prediction(
            db_path=loader.db_path,
            client_id=client_id,
            score=float(score),
            decision=decision,
            features=client_data.iloc[0].to_dict(),
            latency=execution_time,
        )

        return {
            "client_id": client_id,
            "score": float(score),
            "decision": decision,
            "threshold": threshold,
            "shap_values": {imp["feature"]: imp["shap_value"] for imp in importances},
            "base_value": (
                float(shap_values.base_values[0]) if shap_values is not None else 0.0
            ),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur de prédiction pour client {client_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
