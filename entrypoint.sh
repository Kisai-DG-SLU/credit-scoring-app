#!/bin/bash

# Activer le "mode strict" de bash pour arrêter le script en cas d'erreur
set -e

# Lancer l'API FastAPI en arrière-plan
echo "🚀 Démarrage de l'API FastAPI..."
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &

# Attendre quelques secondes que l'API soit prête (optionnel mais recommandé)
sleep 5

# Lancer le Dashboard Streamlit au premier plan
echo "📊 Démarrage du Dashboard Streamlit..."
streamlit run src/api/dashboard.py --server.port 8501 --server.address 0.0.0.0
