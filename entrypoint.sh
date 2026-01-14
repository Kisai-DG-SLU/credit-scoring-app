#!/bin/bash
set -e

export PYTHONPATH=$PYTHONPATH:/app

echo "🔍 DIAGNOSTIC COMPLET :"
echo "Utilisateur actuel : $(whoami)"
echo "Répertoire courant (CWD) : $(pwd)"
echo "Contenu de /app :"
ls -R /app

# Vérifier spécifiquement src/data
if [ -d "/app/src/data" ]; then
    echo "✅ /app/src/data existe"
else
    echo "❌ /app/src/data est INTROUVABLE"
fi

# Créer __init__.py si manquant (sécurité)
mkdir -p /app/src/data
touch /app/src/data/__init__.py

echo "🚀 Démarrage de l'API FastAPI..."
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &

sleep 10

echo "📊 Démarrage du Dashboard Streamlit..."
streamlit run src/api/dashboard.py --server.port 8501 --server.address 0.0.0.0
