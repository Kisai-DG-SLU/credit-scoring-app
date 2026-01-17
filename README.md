---
title: Credit Scoring App
emoji: 🏦
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8501
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
    *   *Problème* : Le dataset original (CSV) pesait **1.4 Go**, saturant la RAM des petits conteneurs.
    *   *Solution* : Conversion vers **SQLite** indexé. Chargement sélectif des clients (< 10ms). Usage RAM < 100 Mo.

2.  **Stratégie d'Hybridation des Données**
    *   **Mode Local (Full)** : Utilise `data/database.sqlite` (**~900 Mo**) pour un accès à l'intégralité des 307 511 clients. Idéal pour le développement et la simulation massive.
    *   **Mode Cloud (Lite)** : Utilise `data/database_lite.sqlite` (**~8 Mo**) incluse dans le repository pour garantir un build Docker rapide et stable sur Hugging Face Spaces. L'API bascule automatiquement sur la base disponible au démarrage.

3.  **Optimisation de l'Image Docker**
    *   *Problème* : Image initiale > 4 Go incluant les datasets d'entraînement.
    *   *Solution* : Image multi-stage optimisée à **~500 Mo** (Python Slim + SQLite Lite).

4.  **Réduction de la Latence (Warmup)**
    *   Le système effectue une prédiction "à vide" au démarrage de l'API (Warmup) pour pré-charger les modèles en cache. Latence moyenne observée : **~270ms**.

## 🏗️ Architecture & Industrialisation

### Inférence & Optimisation (Étape 4)
- **Format ONNX** : Le modèle est converti en format ONNX (`model.onnx`) pour une inférence standardisée et performante (**~100x plus rapide** que Scikit-Learn).
- **Cache LRU** : Un mécanisme de cache (Least Recently Used) est implémenté pour mémoriser les résultats SHAP et les scores, réduisant la latence à **0.001ms** pour les requêtes répétées.
- **Warmup** : L'API effectue une prédiction "à blanc" au démarrage pour initialiser les ressources (Explainer SHAP) et éviter la latence du premier appel utilisateur.

### Stratégie de Données Hybride (SQLite)
Pour concilier les limites de stockage de Git/HuggingFace et le besoin de monitoring :
1. **`database_lite.sqlite` (~8 Mo)** : Contient un échantillon représentatif de 1000 clients. Inclus dans le repository pour permettre un build Docker autonome.
2. **`database.sqlite` (Production/Local)** : Utilisée pour stocker les logs d'appels réels. C'est sur cette base que s'effectue l'analyse de Data Drift.

## 📊 Guide d'Interprétation du Monitoring (Étape 3)

Le suivi de la performance du modèle en production repose sur l'outil **Evidently AI**.

### 1. Qu'est-ce que le Data Drift ?
Le "Data Drift" (ou dérive des données) survient lorsque les données reçues en production ("Current") diffèrent statistiquement des données sur lesquelles le modèle a été entraîné ("Reference"). Cela peut dégrader la performance du modèle sans qu'aucune erreur technique ne soit levée.

### 2. Comment fonctionne Evidently AI dans ce projet ?
Nous utilisons le `DataDriftPreset` d'Evidently qui compare deux jeux de données :
- **Reference Dataset** : Un échantillon statique de la base d'entraînement (stocké dans `database_lite.sqlite`).
- **Current Dataset** : Les logs réels des prédictions, stockés au fil de l'eau dans la table `prediction_logs` de la base SQLite.

Pour chaque variable clé (Top 10 Feature Importance), Evidently applique des tests statistiques (ex: Test de Kolmogorov-Smirnov pour les données numériques) pour déterminer si la distribution a changé de manière significative (p-value < 0.05).

### 3. Interpréter le Rapport
Le Dashboard génère un rapport HTML interactif (`drift_report.html`) accessible via l'interface.
- **Colonne "Drift Detected"** :
    - 🔴 **Drift détecté** : La distribution a changé. Alerte ! Il faut investiguer (changement de population ? erreur de collecte ?).
    - 🟢 **Pas de drift** : Le modèle opère dans son domaine de validité connu.
- **Visualisation** : En cliquant sur une feature, vous pouvez voir l'histogramme comparatif (Reference vs Current) pour comprendre la nature du changement.

**Seuil de Confiance** : L'analyse statistique n'est fiable qu'avec un volume suffisant de données. Le dashboard affiche un indicateur de confiance (Vert > 500 échantillons, Orange < 500).

## ✅ Conformité & Robustesse (Points de Vigilance)

L'application répond aux exigences critiques de la mission :
- **Chargement Unique** : Le modèle et les artefacts SHAP sont chargés via un **Singleton Pattern** au démarrage de l'API (`on_event("startup")`). Aucun rechargement n'est effectué lors des appels.
- **Gestion des Erreurs** :
    - **Données manquantes** : L'API convertit automatiquement les NaNs en types compatibles et retourne une prédiction robuste.
    - **Identifiants invalides** : Gestion propre des erreurs 404.
    - **Validation types** : Validation stricte des schémas d'entrée via Pydantic.
- **Sécurité** : Configuration par variables d'environnement (`.env`).

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