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
[![Coverage](https://img.shields.io/badge/coverage-79%25-brightgreen)](https://kisai-dg-slu.github.io/credit-scoring-app/)
![Version](https://img.shields.io/github/v/tag/Kisai-DG-SLU/credit-scoring-app?label=version)
![Python](https://img.shields.io/badge/python-3.10-blue)
![License](https://img.shields.io/github/license/Kisai-DG-SLU/credit-scoring-app)

> **Projet 8 - Parcours Data Scientist OpenClassrooms**
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

2.  **Stratégie d'Hybridation des Données**
    *   **Mode Local (Full)** : Utilise `data/database.sqlite` (850 Mo) pour un accès à l'intégralité des 307 511 clients.
    *   **Mode Cloud (Lite)** : Utilise `data/database_lite.sqlite` (< 10 Mo) incluse dans le repository pour garantir un build Docker rapide et stable sur Hugging Face Spaces. L'API bascule automatiquement sur la base disponible au démarrage.

3.  **Optimisation de l'Image Docker**
    *   *Problème* : Image initiale > 4 Go incluant les datasets d'entraînement.
    *   *Solution* : Image multi-stage optimisée à **~500 Mo** (Python Slim + SQLite Lite).

4.  **Réduction de la Latence (Warmup)**
    *   Le système effectue une prédiction "à vide" au démarrage de l'API (Warmup) pour pré-charger les modèles en cache. Latence moyenne observée : **~270ms**.

## 📊 Monitoring & Data Drift

Le système implémente une surveillance continue de la qualité des données (MLOps) :
- **Traçabilité** : Chaque appel API est logué dans une table SQLite `prediction_logs` (Date, ID, Score, Décision).
- **Analyse du Drift** : Un notebook dédié (`notebooks/data_drift_analysis.ipynb`) utilise **Evidently AI** pour comparer les données de production aux données de référence (Training).
- **Indicateurs Clés** : Surveillance prioritaire sur le Top-10 des features (EXT_SOURCES, DAYS_BIRTH, etc.).

## 🛡️ Robustesse & Erreurs

- **Validation des Entrées** : Utilisation de modèles Pydantic pour interdire les requêtes malformées.
- **Gestion des Cas Limites** :
    *   **Client Inconnu** : Retourne un code `404 Not Found` propre avec message pédagogique.
    *   **Données Manquantes** : Le pipeline de preprocessing gère l'imputation automatique des valeurs manquantes via le modèle pré-entraîné.
    *   **Sécurité** : Logs anonymisés (pas de données personnelles sensibles hors ID technique).


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