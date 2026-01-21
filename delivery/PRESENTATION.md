---
marp: true
theme: default
size: 16:9
paginate: true
---

<!-- _class: lead -->

# **Confirmez vos compétences en MLOps**
## Projet 8 : Scoring & Monitoring
**Damien Guesdon**

---

## Slide 2: Le Contexte & La Mission

- **Besoin Client ("Prêt à dépenser")**:
  - Obtenir un score de crédit fiable et **rapide**.
  - Aider les chargés de clientèle à **expliquer les décisions**.

- **Notre Mission**:
  1.  **Industrialiser** le modèle de scoring existant.
  2.  **Monitorer** sa performance et la qualité des données en production.
  3.  **Garantir** une API robuste, scalable et maintenable.

---

## Slide 3: Architecture & Choix Techniques

- **Frameworks**:
  - **FastAPI**: Pour une API haute performance.
  - **Streamlit**: Pour un dashboard de monitoring interactif.
  - **Docker**: Pour conteneuriser l'application et garantir la portabilité.

- **Décision Clé 1 : Architecture Hybride SQLite**
  - **Problème**: Le dataset de 1.3Go consommait ~6Go de RAM.
  - **Solution**: Stockage des données de référence et des logs dans une base **SQLite**.
  - **Résultat**: Consommation RAM réduite à **~50Mo**. Démarrage 10x plus rapide.

---
<!-- header: Architecture Diagram -->

## Schéma d'Architecture

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
**Flux de données optimisé avec SQLite pour un accès performant et une faible empreinte mémoire.**

---

## Slide 5: Optimisation de l'Inférence (ONNX & Caching)

- **Décision Clé 2 : Standardisation avec ONNX**
  - **Problème**: Dépendance forte à la version de `lightgbm`.
  - **Solution**: Conversion du modèle au format standard **ONNX**.
  - **Résultat**: **Inférence 100x plus rapide** (de 3.39ms à 0.03ms).

- **Décision Clé 3 : Caching des calculs SHAP**
  - **Problème**: Le calcul de l'explicabilité (SHAP) est coûteux (~250ms).
  - **Solution**: Mise en place d'un **cache LRU**.
  - **Résultat**: Les requêtes répétées pour un même client sont **instantanées** (0.001ms).

---

## Slide 6: Rapport de Performance

| Opération | Méthode | Temps Moyen | Gain (Speedup) |
|-----------|---------|-------------|----------------|
| Inférence | Joblib    | 3.39 ms     | 1x (Baseline)  |
| Inférence | ONNX      | **0.03 ms** | **~100x**      |

**L'architecture "CPU-only" est validée pour la production (coût minimal pour une performance maximale).**

---

## Slide 7: Démonstration Live

1.  **Lancer l'application conteneurisée**:
    ```bash
    make docker-run
    ```

2.  **Ouvrir le Dashboard Streamlit** (`http://localhost:8501`):
    - Entrer un ID client (ex: `100001`).
    - Montrer la jauge, le graphique SHAP, et la comparaison client.

3.  **Montrer la robustesse**:
    - Entrer un ID invalide (`999999`) et observer l'erreur 404 propre.

---

## Slide 8: Monitoring du Data Drift

- **Stratégie**:
  - **Collecte**: Chaque appel API enregistre les 10 features clés dans `prediction_logs`.
  - **Analyse**: Un notebook utilise **Evidently AI** pour comparer les distributions.

- **Décision Clé 4 : Indicateur de Confiance Statistique**
  - **Problème**: Risque de fausses alertes de drift avec peu de données.
  - **Solution**: Le dashboard n'affiche l'analyse que si le volume de données est suffisant (N > 500).

- **Démo Monitoring**:
  1.  Simuler un drift: `python src/database/simulation_cli.py drift 500`
  2.  Lancer le notebook et montrer le rapport HTML généré.

---

## Slide 9: Qualité & Automatisation (CI/CD)

- **Pipeline GitHub Actions**:
  - **Qualité du code**: `black` et `ruff` à chaque commit.
  - **Tests automatisés**: `pytest` sur chaque Pull Request (> 70% de couverture).
  - **Déploiement Continu**: Merge sur `main` déclenche le déploiement sur Hugging Face.

**Garantie de non-régression et de maintenabilité du projet.**

---

<!-- _class: lead -->

# Conclusion & Questions

- ✅ API **robuste** et **performante**.
- ✅ Application **conteneurisée** et **déployable**.
- ✅ Système de **monitoring de data drift**.
- ✅ Pipeline **CI/CD complet**.

**Prêt pour vos questions.**
