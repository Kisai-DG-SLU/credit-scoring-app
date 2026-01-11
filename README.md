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

## 🚀 Installation & Lancement Rapide

### Option 1 : Docker (Recommandé)
Le projet est entièrement conteneurisé.

```bash
# Build de l'image
docker build -t credit-scoring-app .

# Lancement du conteneur (API + Dashboard)
docker run -p 8000:8000 -p 8501:8501 credit-scoring-app
```

### Option 2 : Installation Locale (Conda)
Pré-requis : **Conda** (Miniconda recommandé).

1. **Installer l'environnement**
   ```bash
   make install
   conda activate credit-scoring-app
   ```

2. **Démarrer les services**
   *   **API** : `make run-api` (Port 8000)
   *   **Dashboard** : `streamlit run src/api/dashboard.py` (Port 8501)

## 📊 Monitoring & Data Drift

Le système inclut un module de monitoring basé sur **Evidently AI**.
- **Logs** : Chaque prédiction est enregistrée dans une table SQLite structurée.
- **Analyse de dérive** : Le dashboard permet de générer un rapport de Data Drift comparant les données de production aux données de référence.

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