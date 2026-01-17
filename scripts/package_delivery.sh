#!/bin/bash

# -----------------------------------------------------------------------------
# Script de Packaging - Mise en conformité stricte
# Format Archive : Titre_du_projet_nom_prenom.zip
# Format Fichier : Nom_Prenom_n°_NomLivrable_mmaaaa
# -----------------------------------------------------------------------------

NOM="Guesdon"
PRENOM="Damien"
DATE_SUFFIX="012026" # Format mmaaaa fixé

# Titre du projet normalisé (sans accents, sans espaces, sans apostrophes)
# Titre original : "Confirmez vos compétences en MLOps (Partie 2)"
TITRE_PROJET="Confirmez_vos_competences_en_MLOps_Partie_2"

FOLDER_NAME="${TITRE_PROJET}_${NOM}_${PRENOM}"
OUTPUT_DIR="delivery/${FOLDER_NAME}"

echo "📦 Démarrage du packaging conforme..."
echo "📂 Dossier cible : ${OUTPUT_DIR}"

# 1. Nettoyage et Création
rm -rf "${OUTPUT_DIR}"
rm -f "delivery/${FOLDER_NAME}.zip"
mkdir -p "${OUTPUT_DIR}"

# 2. Copie et Renommage des Livrables

# Livrable 1 : Historique des versions
echo "Lien vers le repository GitHub : https://github.com/Kisai-DG-SLU/credit-scoring-app" > "${OUTPUT_DIR}/${NOM}_${PRENOM}_1_Historique_${DATE_SUFFIX}.txt"
git log --oneline --graph --all >> "${OUTPUT_DIR}/${NOM}_${PRENOM}_1_Historique_${DATE_SUFFIX}.txt"

# Livrable 2 : Scripts API et Dockerfile (Code Source)
# On zippe le code source pour n'avoir qu'un seul fichier pour le livrable 2
mkdir -p "${OUTPUT_DIR}/Source"
cp -r src "${OUTPUT_DIR}/Source/"
cp Dockerfile "${OUTPUT_DIR}/Source/${NOM}_${PRENOM}_2_Dockerfile_${DATE_SUFFIX}"
cp requirements.txt "${OUTPUT_DIR}/Source/"
cp environment.yml "${OUTPUT_DIR}/Source/"
cd "${OUTPUT_DIR}"
zip -r "${NOM}_${PRENOM}_2_Scripts_${DATE_SUFFIX}.zip" Source
rm -rf Source
cd ../..

# Livrable 3 : Tests et Pipeline CI/CD
mkdir -p "${OUTPUT_DIR}/Tests"
cp -r tests "${OUTPUT_DIR}/Tests/"
cp .github/workflows/ci.yml "${OUTPUT_DIR}/Tests/${NOM}_${PRENOM}_3_Pipeline_${DATE_SUFFIX}.yml"
cd "${OUTPUT_DIR}"
zip -r "${NOM}_${PRENOM}_3_Tests_${DATE_SUFFIX}.zip" Tests
rm -rf Tests
cd ../..

# Livrable 4 : Analyse Data Drift (Notebook + Rapport)
mkdir -p "${OUTPUT_DIR}/Drift"
cp notebooks/data_drift_analysis.ipynb "${OUTPUT_DIR}/Drift/${NOM}_${PRENOM}_4_Notebook_${DATE_SUFFIX}.ipynb"
if [ -f "data/drift_report.html" ]; then
    cp data/drift_report.html "${OUTPUT_DIR}/Drift/${NOM}_${PRENOM}_4_Rapport_${DATE_SUFFIX}.html"
fi
# Inclusion des preuves de stockage (Screenshots T047)
if [ -d "delivery/proof/screenshots" ]; then
    mkdir -p "${OUTPUT_DIR}/Drift/Preuves"
    cp -r delivery/proof/screenshots/* "${OUTPUT_DIR}/Drift/Preuves/"
    cp delivery/proof/logs_sample.txt "${OUTPUT_DIR}/Drift/Preuves/Logs_${DATE_SUFFIX}.txt"
fi
cd "${OUTPUT_DIR}"
zip -r "${NOM}_${PRENOM}_4_Drift_${DATE_SUFFIX}.zip" Drift
rm -rf Drift
cd ../..

# Livrable 5 : Rapport d'Optimisation (T051)
cp delivery/PERFORMANCE_REPORT.md "${OUTPUT_DIR}/${NOM}_${PRENOM}_5_Optimisation_${DATE_SUFFIX}.md"
if [ -f "delivery/proof/resource_usage.txt" ]; then
    cp delivery/proof/resource_usage.txt "${OUTPUT_DIR}/${NOM}_${PRENOM}_5_Benchmark_${DATE_SUFFIX}.txt"
fi

# Livrable 6 : Documentation & Présentation
cp delivery/README.md "${OUTPUT_DIR}/${NOM}_${PRENOM}_6_Documentation_${DATE_SUFFIX}.md"
cp delivery/DEMO_GUIDE.md "${OUTPUT_DIR}/${NOM}_${PRENOM}_6_Presentation_${DATE_SUFFIX}.md"
cp delivery/TECHNICAL_STORYTELLING.md "${OUTPUT_DIR}/${NOM}_${PRENOM}_6_Storytelling_${DATE_SUFFIX}.md"

# 3. Zippage Final de l'archive principale
echo "🤐 Compression de l'archive finale..."
cd delivery
zip -r "${FOLDER_NAME}.zip" "${FOLDER_NAME}"
rm -rf "${FOLDER_NAME}" # Nettoyage du dossier décompressé

echo "✅ TERMINÉ !"
echo "📁 Archive prête : delivery/${FOLDER_NAME}.zip"
