# Implementation Plan: MLOps Industrialization

**Goal**: Déployer une API de scoring crédit robuste, conteneurisée et monitorée.

## Architecture Cible
- **Modèle** : LightGBM/XGBoost (importé du P6).
- **Backend** : FastAPI (Sert le modèle).
- **Frontend** : Streamlit (Consomme l'API).
- **Monitoring** : Evidently AI + Logs locaux/Cloud.
- **Infrastructure** : Docker sur Hugging Face Spaces.

## Flux de Données
1.  **Utilisateur** (Streamlit) -> Envoie données client.
2.  **API** (FastAPI) :
    *   Reçoit et valide (Pydantic).
    *   Pré-traite (Preprocessor P6).
    *   Predit (Modèle P6).
    *   Loggue (Pour monitoring Drift).
    *   Retourne Score + Feature Importance (SHAP).
3.  **Monitoring** (Batch) :
    *   Analyse les logs vs Reference Dataset.
    *   Génère rapport html (Evidently).

## Stratégie de Test
- **Unitaires** : Validation des entrées API, chargement du modèle.
- **Intégration** : Test de bout en bout (API -> Modèle).
- **Performance** : Mesure du temps d'inférence (< 200ms).