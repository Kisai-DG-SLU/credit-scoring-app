# Architecture : credit-scoring-app

## 1. Vue d'ensemble
L'application suit une architecture découplée avec un backend (API de scoring) et un frontend (Dashboard Streamlit).

```text
[ Sources de Données ] 
      │
      ▼
[ Pipeline Data ] (Notebooks/Scripts) ──> [ Modèle Sérialisé (.pkl/.joblib) ]
                                                │
                                                ▼
                                        [ API FastAPI ] 
                                                │
                                                ▼
                                       [ Dashboard Streamlit ]
```

## 2. Structure du Code Source
Conformément au plan standard :
- `src/model/` : Scripts d'entraînement et de prédiction.
- `src/api/` : Code de l'API FastAPI.
- `src/dashboard/` : Code de l'application Streamlit.
- `src/utils/` : Fonctions utilitaires partagées.

## 3. Stack Technique
- **Langage** : Python 3.10
- **Gestionnaire de dépendances** : Conda (environment.yml)
- **Framework API** : FastAPI
- **Interface Utilisateur** : Streamlit
- **ML Tracking** : MLflow (local ou distant)
- **Tests** : Pytest

## 4. Stratégie de Déploiement (SIMPLIFIÉE)

### 4.1. Environnement Unique (Démo)
- **Production/Démo** : Branche `main`.
- **Hébergement** : Hugging Face Space (Docker).
- **Objectif** : Une URL publique stable pour la soutenance.

### 4.2. Workflow Qualité
1.  **Développement** : Sur branches dédiées (`feat/...`, `fix/...`). Interdiction de push sur `main`.
2.  **Validation (CI)** : `ci.yml` exécuté sur chaque Pull Request (Linting + Tests).
3.  **Merge & Deploy** : Le merge vers `main` déclenche le déploiement automatique sur Hugging Face Space.

## 5. Stratégie de Données (Optimisation & Performance)
> **Décision (09/01/2026)** : Migration du stockage des données de CSV vers **SQLite**.

### Problème
Le chargement du dataset de référence (1.3 Go CSV) via Pandas nécessite ~5-10 Go de RAM, ce qui dépasse les quotas des environnements "Low Cost" (Hugging Face Spaces, Conteneurs standards) et ralentit le démarrage de l'API.

### Solution : SQLite
- **Type** : Base de données relationnelle fichier (Serverless).
- **Accès** : Lecture disque indexée (Index sur `SK_ID_CURR`).
- **Performance** : Temps d'accès < 10ms (vs scan mémoire).
- **Empreinte Mémoire** : Minime (~50 Mo vs 6 Go).
- **Déploiement Cloud** : Une version 'Lite' (`database_lite.sqlite`) est générée (<100 Mo) pour être incluse dans le repository Git et permettre le build Docker sur Hugging Face sans dépendance à un stockage externe lourd.
- **Flux** : 
  1. Conversion `csv` -> `sqlite` (Script utilitaire `src/data/convert_to_sqlite.py`).
  2. Génération d'un échantillon représentatif pour la version Lite.
  3. API charge uniquement la ligne demandée via SQL.
