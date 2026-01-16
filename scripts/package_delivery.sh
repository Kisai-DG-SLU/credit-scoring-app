#!/bin/bash

# Configuration
NOM="Guesdon"
PRENOM="Damien"
PROJET="Projet_8_Scoring_Credit"
DATE=$(date +%Y-%m-%d)
ZIP_NAME="${PROJET}_${NOM}_${PRENOM}.zip"

echo "📦 Préparation du packaging final..."

# Création d'un dossier temporaire de livraison
mkdir -p delivery/final_package

# Liste des livrables selon la mission Chloé Dubois
# 1. Historique des versions (PDF de l'historique git ou lien)
git log --oneline --graph --all > "delivery/final_package/${NOM}_${PRENOM}_1_historique_git_${DATE}.txt"

# 2. Scripts API
cp src/api/main.py "delivery/final_package/${NOM}_${PRENOM}_2_api_fastapi_${DATE}.py"

# 3. Dockerfile
cp Dockerfile "delivery/final_package/${NOM}_${PRENOM}_3_dockerfile_${DATE}"

# 4. Scripts de tests automatisés
zip -r "delivery/final_package/${NOM}_${PRENOM}_4_tests_pytest_${DATE}.zip" tests/

# 5. Pipeline CI/CD (YAML)
cp .github/workflows/ci.yml "delivery/final_package/${NOM}_${PRENOM}_5_ci_cd_workflow_${DATE}.yml"

# 6. Analyse du Data Drift (Notebook)
cp notebooks/data_drift_analysis.ipynb "delivery/final_package/${NOM}_${PRENOM}_6_data_drift_analysis_${DATE}.ipynb"

# 7. Screenshots de la solution de stockage
# Note: Ces fichiers doivent être mis manuellement dans delivery/proof/ par l'Owner
if [ -d "delivery/proof" ]; then
    zip -r "delivery/final_package/${NOM}_${PRENOM}_7_screenshots_storage_${DATE}.zip" delivery/proof/
else
    echo "⚠️ Attention: Dossier delivery/proof/ absent. Screenshots non inclus."
fi

# Création du ZIP final
cd delivery/final_package
zip -r "../../${ZIP_NAME}" .
cd ../..

echo "✅ Succès ! Fichier prêt : ${ZIP_NAME}"
echo "N'oubliez pas de vérifier le contenu du ZIP avant l'envoi."
