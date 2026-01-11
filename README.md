# Prêt à dépenser (Credit Scoring App)

![CI](https://github.com/Kisai-DG-SLU/credit-scoring-app/actions/workflows/ci.yml/badge.svg)
![Deploy](https://github.com/Kisai-DG-SLU/credit-scoring-app/actions/workflows/deploy-hf.yml/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-92%25-brightgreen)
![Release](https://img.shields.io/github/v/release/Kisai-DG-SLU/credit-scoring-app)
![Python](https://img.shields.io/badge/python-3.10-blue)
![License](https://img.shields.io/github/license/Kisai-DG-SLU/credit-scoring-app)

> **Projet 7/8 - Parcours Data Scientist OpenClassrooms**
>
> Application d'évaluation du risque de crédit ("Credit Scoring") permettant de prédire la probabilité de défaut de paiement d'un client. Ce projet implémente une approche **MLOps** rigoureuse, de l'optimisation des données au déploiement d'une API conteneurisée.

---

## ⚡ Points Forts Techniques

- **Performance Backend** : API développée avec **FastAPI** pour une exécution asynchrone et rapide.
- **Optimisation Données** : Migration des datasets CSV (> 1 Go) vers **SQLite** avec indexation, réduisant drastiquement l'empreinte mémoire lors de l'inférence.
- **Qualité Code** : Pipeline CI strict refusant tout code non formaté (Black/Ruff) ou sous 70% de couverture de tests.
- **Architecture Modulaire** : Séparation claire entre `Data`, `Model` et `API` (Clean Architecture simplifiée).

## 🏗 Architecture

Le projet est structuré selon les standards industriels :

```
.
├── src/
│   ├── api/          # Application FastAPI (Entrées/Sorties, Validation Pydantic)
│   ├── data/         # Gestion des données (Conversion CSV -> SQLite)
│   ├── model/        # Logique métier (Chargement modèle, Preprocessing, Prédiction)
│   └── dashboard/    # (À venir) Interface Streamlit
├── tests/            # Tests unitaires (Pytest) couvrant > 90% du code
├── specs/            # Documentation technique et fonctionnelle
└── .github/          # Workflows CI/CD (Tests, Release)
```

## 🚀 Installation

Pré-requis : **Conda** (Miniconda recommandé).

1. **Cloner le dépôt**
   ```bash
   git clone git@github.com:Kisai-DG-SLU/credit-scoring-app.git
   cd credit-scoring-app
   ```

2. **Installer l'environnement**
   L'environnement est strictement défini dans `environment.yml`.
   ```bash
   make install
   ```
   *Cela créera l'environnement `credit-scoring-app` et installera toutes les dépendances.*

3. **Activer l'environnement**
   ```bash
   conda activate credit-scoring-app
   ```

4. **Configurer les Hooks Git (Qualité)**
   Pour garantir la qualité avant chaque commit :
   ```bash
   pre-commit install
   ```

## 🛠 Utilisation

### Démarrer l'API
Le serveur de développement se lance avec rechargement automatique :

```bash
make run-api
```
- **API Root** : `http://localhost:8000`
- **Documentation Swagger** : `http://localhost:8000/docs`

### Déploiement Cloud (Hugging Face)

Le projet est automatiquement déployé sur Hugging Face Spaces via GitHub Actions à chaque mise à jour de la branche `main`.

- **URL de Production** : [https://huggingface.co/spaces/damienguesdon/credit-scoring-app](https://huggingface.co/spaces/damienguesdon/credit-scoring-app)

### Commandes de Développement (Makefile)

Un `Makefile` est à votre disposition pour automatiser les tâches courantes :

| Commande | Description |
| :--- | :--- |
| `make test` | Lance la suite de tests avec rapport de couverture |
| `make lint` | Vérifie le style du code (Ruff, Black) |
| `make format` | Reformate automatiquement le code |
| `make install` | Met à jour l'environnement Conda |
| `clean` | Nettoie les fichiers temporaires et caches |

## 🧪 Tests & Qualité

La qualité est au cœur de ce projet. Une couverture de code minimale de **70%** est imposée par la CI.

Actuellement, le projet atteint : **92% de couverture**.

Pour générer le rapport localement :
```bash
make test
# Ouvrir htmlcov/index.html pour le détail
```

## 👤 Auteur

**Damien Guesdon**
*Projet réalisé dans le cadre de la formation OpenClassrooms.*
