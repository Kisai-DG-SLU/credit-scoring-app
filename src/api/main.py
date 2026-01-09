from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.model.loader import loader
import pandas as pd
import numpy as np
import os

app = FastAPI(title="Credit Scoring API", version="1.0.0")

class PredictionResponse(BaseModel):
    client_id: int
    score: float
    decision: str
    threshold: float

# Seuil par défaut (peut être ajusté ou chargé depuis un fichier)
DEFAULT_THRESHOLD = 0.5

@app.get("/health")
def health_check():
    model = loader.load_artifacts()
    db_exists = os.path.exists("data/database.sqlite")
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "database_available": db_exists
    }

@app.get("/predict/{client_id}", response_model=PredictionResponse)
def predict(client_id: int):
    model = loader.model
    
    if model is None:
        raise HTTPException(status_code=500, detail="Modèle non disponible")

    # Récupération des données du client via SQLite
    client_data = loader.get_client_data(client_id)
    
    if client_data is None:
        raise HTTPException(status_code=404, detail=f"Client {client_id} non trouvé")

    # Préparation des features (on retire TARGET si présent et SK_ID_CURR)
    features = client_data.drop(columns=['TARGET', 'SK_ID_CURR'], errors='ignore')
    
    # Prédiction de probabilité (classe 1 = défaut)
    try:
        # LightGBM/Scikit-learn predict_proba
        prob = model.predict_proba(features)[0][1]
    except Exception as e:
        # Fallback si le modèle n'a pas predict_proba ou autre erreur
        try:
            prob = model.predict(features)[0]
        except Exception as e2:
            raise HTTPException(status_code=500, detail=f"Erreur de prédiction : {e2}")

    decision = "Refusé" if prob > DEFAULT_THRESHOLD else "Accordé"

    return PredictionResponse(
        client_id=client_id,
        score=float(prob),
        decision=decision,
        threshold=DEFAULT_THRESHOLD
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
