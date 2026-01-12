---
title: Credit Scoring App
emoji: 🏦
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# Prêt à dépenser (Credit Scoring App)

![CI](https://github.com/Kisai-DG-SLU/credit-scoring-app/actions/workflows/ci.yml/badge.svg)
![Deploy](https://github.com/Kisai-DG-SLU/credit-scoring-app/actions/workflows/deploy-hf.yml/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-92%25-brightgreen)
![Release](https://img.shields.io/github/v/release/Kisai-DG-SLU/credit-scoring-app)
![Python](https://img.shields.io/badge/python-3.10-blue)
![License](https://img.shields.io/github/license/Kisai-DG-SLU/credit-scoring-app)

> **Projet 7/8 - Parcours Data Scientist OpenClassrooms**
>
> Application d'évaluation du risque de crédit permettant de prédire la probabilité de défaut de paiement d'un client. Ce projet implémente une approche **MLOps** complète, de l'optimisation des données au monitoring de la dérive (Data Drift) en production.

---

## ⚡ Points Forts Techniques

- **Performance Backend** : API développée avec **FastAPI** pour une exécution asynchrone et une validation stricte des données (Pydantic).
- **Optimisation Données** : Migration des datasets CSV (> 1 Go) vers **SQLite** indexé, permettant des requêtes ultra-rapides (< 10ms) avec une empreinte RAM minimale (< 100 Mo).
- **Dashboard Interactif** : Interface **Streamlit** intégrée permettant la visualisation des scores et l'explicabilité locale (Feature Importance).
- **Monitoring MLOps** : Détection automatique du **Data Drift** via **Evidently AI**, avec stockage structuré des logs de prédiction.
- **Conteneurisation** : Image Docker optimisée (multi-stage build) pour un déploiement agnostique de l'infrastructure.

## 🏗 Architecture

Le projet suit une architecture découplée et industrialisée :

```
.
├── src/
│   ├── api/          # Application FastAPI & Dashboard Streamlit
│   ├── data/         # Gestion des données (Conversion SQLite, Logs)
│   ├── model/        # Logique métier (Chargement, Inférence, Monitoring)
│   └── utils/        # Fonctions utilitaires partagées
├── tests/            # Tests unitaires et d'intégration (Coverage > 90%)
├── specs/            # Spécifications techniques et fonctionnelles (PRD, Archi)
└── .github/          # Workflows CI/CD (Tests, Déploiement Cloud)
```

## ⚙️ Optimisations & Performance

Pour répondre aux contraintes de production (Cloud Free Tier, Latence faible), plusieurs défis d'ingénierie ont été relevés :

1.  **Réduction de l'Empreinte Mémoire (RAM)**
    *   *Problème* : Le dataset original (CSV) pesait 1.3 Go, saturant la RAM des petits conteneurs.
    *   *Solution* : Conversion vers **SQLite** indexé. Chargement sélectif des clients (< 10ms). Usage RAM < 100 Mo.

2.  **Optimisation de l'Image Docker**
    *   *Problème* : Image initiale > 4 Go incluant les datasets d'entraînement.
    *   *Solution* : Exclusion des fichiers lourds (`.dockerignore`) et création d'une **Base Lite** (24 Mo) dédiée à la démo/prod.

3.  **Architecture "All-in-One"**
    *   *Solution* : Orchestration unique via `entrypoint.sh` permettant de servir l'API et le Dashboard dans un seul conteneur, simplifiant le déploiement sur les PaaS (Hugging Face Spaces).

## 🎯 Objectifs du Projet
... (existant)

## 🏗️ Héritage et Continuité (Projet 6)
Ce projet industrialise les résultats validés lors du **Projet 6 (Scoring Crédit)** :
- **Modèle** : LGBMClassifier optimisé (AUC ~0.78).
- **Seuil Décisionnel** : Fixé à **0.49** (optimisation du coût métier : 10x plus de poids sur les Faux Négatifs).
- **Feature Engineering** : Pipeline complet de 795 features (aggrégations Bureau, Prev, POS, Installments).
- **Explicabilité** : Standardisation du rendu **SHAP Waterfall** (Top 15 features) pour les conseillers.

## 🚀 Installation & Usage
... (suite)

### Option 1 : Docker (Recommandé - Démo All-in-One)
Le projet est entièrement conteneurisé. L'image lance automatiquement l'API et le Dashboard.

```bash
# Build de l'image (optimisée avec base SQLite Lite)
make docker-build

# Lancement du conteneur (API:8000 + Dashboard:8501)
make docker-run
```

### Option 2 : Installation Locale (Conda)
Pré-requis : **Conda** (Miniconda recommandé).

1. **Installer l'environnement**
   ```bash
   make install
   conda activate credit-scoring-app
   ```

2. **Démarrer les services séparément**
   *   **API** : `make run-api` (Port 8000)
   *   **Dashboard** : `streamlit run src/api/dashboard.py` (Port 8501)

## 📊 Monitoring & Data Drift

Le système inclut un module de monitoring basé sur **Evidently AI**.
- **Base Lite** : Utilise `data/database_lite.sqlite` (24 Mo) pour des performances optimales en démo.
- **Logs** : Chaque prédiction est enregistrée dans une table SQLite structurée.


## 🛠 Commandes Makefile

| Commande | Description |
| :--- | :--- |
| `make test` | Lance la suite de tests avec rapport de couverture |
| `make lint` | Vérifie le style du code (Ruff, Black) |
| `make format` | Reformate automatiquement le code |
| `make install` | Initialise l'environnement Conda |
| `make run-api` | Lance le serveur FastAPI |

## 🧪 Qualité

- **Couverture de tests** : 92% (Pytest).
- **CI/CD** : GitHub Actions automatise les tests et le déploiement sur **Hugging Face Spaces**.
- **URL de Production** : [Accéder à la démo](https://huggingface.co/spaces/damienguesdon/credit-scoring-app)

## 👤 Auteur

**Damien Guesdon**
*Projet réalisé dans le cadre de la formation Data Scientist.*