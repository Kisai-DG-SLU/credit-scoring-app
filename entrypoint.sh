#!/bin/bash

# Activer le "mode strict" de bash pour arrêter le script en cas d'erreur
set -e

# S'assurer que le répertoire racine est dans le PYTHONPATH
export PYTHONPATH=$PYTHONPATH:/app

# Diagnostic pour les logs Hugging Face
echo "🔍 Diagnostic de l'environnement :"
echo "CWD: $(pwd)"
echo "PYTHONPATH: $PYTHONPATH"
echo "Contenu de src/data :"
ls -la src/data/

# Vérifier la présence du fichier __init__.py crucial
if [ ! -f "src/data/__init__.py" ]; then
    echo "⚠️ src/data/__init__.py manquant ! Création..."
    touch src/data/__init__.py
fi

# Lancer l'API FastAPI en arrière-plan avec python -m pour garantir le path
echo "🚀 Démarrage de l'API FastAPI..."
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &

# Attendre quelques secondes que l'API soit prête
sleep 10

# Lancer le Dashboard Streamlit au premier plan
echo "📊 Démarrage du Dashboard Streamlit..."
streamlit run src/api/dashboard.py --server.port 8501 --server.address 0.0.0.0
