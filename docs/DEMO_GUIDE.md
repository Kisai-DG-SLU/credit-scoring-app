# Guide de Soutenance - Credit Scoring App

Ce guide détaille le scénario de démonstration pour la présentation du projet "Prêt à dépenser".

## 1. Introduction & Contexte (2 min)
- **Problématique** : "Prêt à dépenser" souhaite automatiser l'octroi de crédits tout en garantissant la transparence des décisions pour les chargés de clientèle.
- **Solution** : Une plateforme MLOps intégrée comprenant une API de scoring, un dashboard interactif et un système de monitoring de dérive des données.
- **Valeur Ajoutée** : Rapidité de réponse (FastAPI + SQLite) et Explicabilité (Feature Importance).

## 2. Démonstration Technique : Le Socle (3 min)
### L'API (Backend)
- Montrer la documentation Swagger (`/docs`).
- **Point clé** : Validation stricte des données avec Pydantic.
- **Test rapide** : Envoyer une requête de prédiction via Swagger pour montrer le temps de réponse ultra-court (< 200ms).

### L'Optimisation SQLite
- Expliquer pourquoi nous sommes passés du CSV (1.3 Go) à SQLite.
- **Argument** : Réduction de l'usage RAM de 6 Go à moins de 100 Mo, permettant un déploiement sur des infrastructures légères (Hugging Face Free Tier).

## 3. Démonstration Métier : Le Dashboard (5 min)
*Lancer le dashboard Streamlit.*

### Scénario "Client Accepté"
1. Saisir l'ID d'un client avec un bon score (ex: `100001`).
2. Montrer le score vert, le positionnement par rapport au seuil de décision.
3. Expliquer les facteurs positifs (ex: Revenu élevé, ratio d'endettement faible).

### Scénario "Client Refusé"
1. Saisir un ID client avec un risque élevé.
2. Montrer le score rouge.
3. Utiliser les graphiques de **Feature Importance** pour expliquer au client pourquoi son prêt a été refusé (transparence RGPD).

## 4. MLOps & Monitoring (3 min)
- Montrer l'onglet **Monitoring** dans le Dashboard.
- Expliquer le concept de **Data Drift** (dérive des données).
- Lancer (ou montrer un résultat) du rapport **Evidently AI**.
- **Message** : "Nous ne nous contentons pas de déployer un modèle, nous surveillons sa validité dans le temps."

## 5. Industrialisation & CI/CD (2 min)
- Montrer les **GitHub Actions**.
- Expliquer que chaque modification passe par des tests unitaires (92% de coverage) et un linting automatique.
- Montrer le déploiement continu vers **Hugging Face Spaces**.

## 6. Conclusion
- Le projet répond aux exigences de performance, de qualité logicielle et d'éthique (explicabilité).
- Prêt pour une mise en production réelle.

---

### Commandes Utiles pour la démo :
- **Lancer l'API** : `make run-api`
- **Lancer le Dashboard** : `streamlit run src/api/dashboard.py`
- **Accès Swagger** : `http://localhost:8000/docs`
- **Accès Dashboard** : `http://localhost:8501`
