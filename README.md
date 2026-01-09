# Prêt à dépenser (Credit Scoring App)

![CI](https://github.com/Kisai-DG-SLU/credit-scoring-app/actions/workflows/ci.yml/badge.svg)
![Release](https://img.shields.io/github/v/release/Kisai-DG-SLU/credit-scoring-app)
![Python](https://img.shields.io/badge/python-3.10-blue)
![License](https://img.shields.io/github/license/Kisai-DG-SLU/credit-scoring-app)

Application d'évaluation du risque de crédit ("Credit Scoring") permettant de prédire la probabilité de faillite d'un client. Ce projet s'inscrit dans le cadre d'une démarche MLOps complète, intégrant le développement d'une API, d'un Dashboard interactif, et l'industrialisation via CI/CD.

## 🏗 Architecture

Le projet est structuré pour optimiser la performance et la maintenabilité :

- **Backend (API)** : Développé avec **FastAPI**, exposant un endpoint de prédiction.
- **Frontend (Dashboard)** : Interface interactive réalisée avec **Streamlit** (en cours de développement).
- **Données** : Migration des fichiers plats (CSV) vers **SQLite** pour réduire l'empreinte mémoire et accélérer les requêtes via indexation.
- **Environnement** : Gestion stricte des dépendances via **Conda**.

## 🚀 Installation

Ce projet nécessite **Python 3.10** et **Conda**.

1. **Cloner le dépôt** :
   ```bash
   git clone git@github.com:Kisai-DG-SLU/credit-scoring-app.git
   cd credit-scoring-app
   ```

2. **Créer l'environnement Conda** :
   L'environnement est défini dans `environment.yml`.
   ```bash
   make install
   # Ou manuellement : conda env update --file environment.yml --prune
   ```

3. **Activer l'environnement** :
   ```bash
   conda activate credit-scoring
   ```

## 🛠 Utilisation

### Démarrer l'API
L'API expose le modèle de scoring.

```bash
make run-api
```
L'API sera accessible sur `http://localhost:8000`.
Documentation interactive (Swagger UI) disponible sur `http://localhost:8000/docs`.

### Tests et Qualité

Le projet intègre une suite de tests et des outils de linting pour garantir la qualité du code.

- **Lancer les tests** (avec rapport de couverture) :
  ```bash
  make test
  ```

- **Vérifier le style (Linting)** :
  ```bash
  make lint
  ```

- **Formater le code** :
  ```bash
  make format
  ```

## ⚙️ CI/CD

Le workflow GitHub Actions (`ci.yml`) automatise :
1.  L'installation de l'environnement.
2.  Le linting (`ruff`, `black`).
3.  Les tests unitaires (`pytest`).
4.  La publication des releases (Semantic Release) lors des merges sur `main`.

## 📦 Structure du Projet

```
.
├── src/
│   ├── api/          # Application FastAPI
│   ├── data/         # Scripts de gestion des données (CSV -> SQLite)
│   ├── model/        # Chargement du modèle et feature engineering
│   └── dashboard/    # (À venir) Application Streamlit
├── tests/            # Tests unitaires et d'intégration
├── specs/            # Spécifications fonctionnelles et techniques
├── environment.yml   # Définition de l'environnement Conda
├── Makefile          # Commandes d'automatisation
└── README.md         # Documentation du projet
```

## 👤 Auteur

**Damien Guesdon**
Projet réalisé dans le cadre de la formation "Data Scientist" (OpenClassrooms - Projet 7/8).