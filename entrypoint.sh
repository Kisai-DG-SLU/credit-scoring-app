#!/bin/bash
set -e

# S'assurer que le répertoire racine est dans le PYTHONPATH
export PYTHONPATH=$PYTHONPATH:/app

echo "🚀 Démarrage de l'API FastAPI..."
# On utilise src.database au lieu de src.data
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &

# Attendre que l'API soit prête
sleep 10

echo "📊 Démarrage du Dashboard Streamlit..."
streamlit run src/api/dashboard.py --server.port 8501 --server.address 0.0.0.0