# PRD : Système de Scoring de Crédit

## 1. Vision du Produit
Offrir aux chargés de clientèle de "Prêt à dépenser" un outil d'aide à la décision rapide, fiable et explicable pour l'octroi de crédits.

## 2. Personas
- **Chargé de Clientèle** : Utilise le dashboard pour visualiser le score d'un client et comprendre les raisons du refus ou de l'acceptation.
- **Data Scientist** : Développe, entraîne et déploie le modèle de scoring.

## 3. Parcours Utilisateur (User Stories)
- **US1 (Score)** : En tant que chargé de clientèle, je veux saisir l'identifiant d'un client pour obtenir instantanément son score de crédit.
- **US2 (Explication)** : En tant que chargé de clientèle, je veux voir les facteurs principaux qui ont influencé le score du client.
- **US3 (Comparaison)** : En tant que chargé de clientèle, je veux comparer les informations du client actuel à l'ensemble de la base clients.
- **US4 (Simulation)** : En tant que chargé de clientèle, je veux pouvoir modifier certaines variables du client pour voir l'impact sur son score (optionnel).

## 4. Exigences Techniques
- **Backend** : Python 3.10, FastAPI (ou Flask).
- **Modélisation** : Scikit-learn, XGBoost/LightGBM, SHAP (pour l'explicabilité).
- **Frontend** : Streamlit.
- **Qualité** : 70% de couverture de tests minimum (règle projet).
- **CI/CD** : GitHub Actions pour le déploiement et les tests.

## 5. Critères d'Acceptation
- Le modèle doit avoir une performance supérieure à un baseline simple (ex: Dummy Classifier).
- L'API doit répondre en moins de 500ms pour une prédiction.
- Le dashboard doit afficher clairement le score, le seuil de décision et l'interprétabilité locale.
