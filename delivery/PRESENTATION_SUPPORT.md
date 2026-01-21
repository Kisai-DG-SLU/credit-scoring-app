# Support de Présentation : Scoring & Monitoring

---

## Slide 1: Titre

- **Confirmez vos compétences en MLOps**
- **Projet 8 : Scoring & Monitoring**
- Damien Guesdon

---

## Slide 2: Le Contexte & La Mission (2 min)

- **Besoin Client ("Prêt à dépenser")**:
  - Obtenir un score de crédit fiable et **rapide**.
  - Aider les chargés de clientèle à **expliquer les décisions**.

- **Notre Mission**:
  1.  **Industrialiser** le modèle de scoring existant.
  2.  **Monitorer** sa performance et la qualité des données en production.
  3.  **Garantir** une API robuste, scalable et maintenable.

---

## Slide 3: Architecture & Choix Techniques (4 min)

- **Frameworks**:
  - **FastAPI**: Pour une API haute performance et asynchrone.
  - **Streamlit**: Pour un dashboard de monitoring interactif et simple à développer.
  - **Docker**: Pour conteneuriser l'application et garantir la portabilité.

- **Décision Clé 1 : Architecture Hybride SQLite**
  - **Problème**: Le dataset de 1.3Go consommait ~6Go de RAM, incompatible avec des déploiements "low-cost".
  - **Solution**: Stockage des données de référence et des logs de prédiction dans une base **SQLite**.
  - **Résultat**: Consommation RAM réduite à **~50Mo**. Démarrage 10x plus rapide.

- _(Afficher le schéma d'architecture de `specs/02_ARCHITECTURE.md`)_

---

## Slide 4: Optimisation de l'Inférence (ONNX & Caching)

- **Décision Clé 2 : Standardisation avec ONNX**
  - **Problème**: Dépendance forte à la version de `lightgbm` et `scikit-learn`.
  - **Solution**: Conversion du modèle au format standard **ONNX**.
  - **Résultat**: **Inférence 100x plus rapide** (de 3.39ms à 0.03ms). L'API est agnostique au framework d'entraînement.

- **Décision Clé 3 : Caching des calculs SHAP**
  - **Problème**: Le calcul de l'explicabilité (SHAP) est coûteux en CPU (~250ms).
  - **Solution**: Mise en place d'un **cache LRU** sur les prédictions et les valeurs SHAP.
  - **Résultat**: Les requêtes répétées pour un même client sont **instantanées** (0.001ms).

- _(Montrer le tableau du `PERFORMANCE_REPORT.md`)_

| Opération | Méthode | Temps Moyen | Gain (Speedup) |
|-----------|---------|-------------|----------------|
| Inférence | Joblib    | 3.39 ms     | 1x (Baseline)  |
| Inférence | ONNX      | **0.03 ms** | **~100x**      |

---

## Slide 5: Démonstration Live (3 min)

1.  **Lancer l'application conteneurisée**:
    - `make docker-run`

2.  **Ouvrir le Dashboard Streamlit** (`http://localhost:8501`):
    - Entrer un ID client (ex: `100001`).
    - **Montrer**:
      - La jauge de score claire (Accepté/Refusé).
      - Le graphique "waterfall" SHAP qui explique la décision.
      - La comparaison du client aux statistiques globales.

3.  **Montrer la robustesse**:
    - Entrer un ID invalide (`999999`).
    - **Constater**: L'API répond une erreur 404 propre sans crasher.

---

## Slide 6: Monitoring du Data Drift (4 min)

- **Stratégie**:
  - **Collecte**: Chaque appel à l'API enregistre les 10 features les plus importantes dans une table `prediction_logs` (SQLite).
  - **Analyse**: Un notebook (`data_drift_analysis.ipynb`) utilise **Evidently AI** pour comparer la distribution des données de production ("Current") à celles de l'entraînement ("Reference").

- **Décision Clé 4 : Indicateur de Confiance Statistique**
  - **Problème**: Risque de fausses alertes de drift avec peu de données.
  - **Solution**: Le dashboard affiche un indicateur de "confiance" et ne montre l'analyse de drift que si le volume de données est suffisant (N > 500).

- **Démo Monitoring**:
  1.  Simuler un baseline: `python src/database/simulation_cli.py baseline 500`
  2.  Simuler un drift: `python src/database/simulation_cli.py drift 500`
  3.  Relancer le notebook d'analyse et montrer le rapport HTML généré avec les dérives détectées (graphiques rouges).

---

## Slide 7: Qualité & Automatisation (CI/CD) (2 min)

- **Pipeline GitHub Actions**:
  - **Qualité du code**: `black` et `ruff` s'exécutent à chaque commit.
  - **Tests automatisés**: `pytest` est lancé sur chaque Pull Request, avec une couverture de code > 70%.
  - **Déploiement Continu**: Le merge sur `main` déclenche automatiquement le déploiement sur Hugging Face Spaces.

- **Garantie de non-régression** et de maintenabilité du projet.

---

## Slide 8: Conclusion & Questions

- **Ce qui a été fait**:
  - ✅ API de scoring **robuste** et **performante**.
  - ✅ Application **conteneurisée** et facilement **déployable**.
  - ✅ Système de **monitoring de data drift** avec gouvernance.
  - ✅ Pipeline **CI/CD complet** garantissant la qualité.

- **Prêt pour vos questions.**
