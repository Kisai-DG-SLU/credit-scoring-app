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
1. Saisir l'ID d'un client avec un bon score (ex: `100004`).
2. Montrer le score vert, le positionnement par rapport au seuil de décision.
3. Expliquer les facteurs positifs (ex: Revenu élevé, ratio d'endettement faible).

### Scénario "Client Refusé"
1. Saisir l'ID d'un client avec un risque élevé (ex: `100431`).
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

## 💡 Points Clés pour la Discussion Technique

### 1. Continuité Métier (Héritage P6)
- **Pourquoi ce seuil (0.49) ?** : Issu de l'étude de la fonction de coût métier visant à minimiser les pertes bancaires (FN > FP).
- **Stabilité des Features** : Utilisation du pipeline `clean_feature_names` pour garantir que le modèle en production reçoit exactement le même format de données qu'à l'entraînement.
- **Transparence (SHAP)** : Le choix du visuel Waterfall plot répond au besoin d'explicabilité locale immédiate pour le conseiller lors d'un entretien client.

### 2. Choix Technologiques (P8)
... (existant)

## 7. Cheat Sheet Technique : Réponses aux Questions Critiques

| Thème | Question probable | Argumentaire à tenir (Punchlines) |
| :--- | :--- | :--- |
| **Données** | Pourquoi SQLite plutôt que du CSV ? | "Pour l'efficience. Le CSV imposait un scan total de 1.3 Go en RAM à chaque appel. SQLite indexé permet un accès direct disque en < 10ms, divisant l'usage RAM par 50." |
| **Performance** | Votre API est rapide, comment avez-vous optimisé ? | "Nous avons implémenté un **Warmup** au démarrage pour pré-charger le modèle en cache et migré vers une base de données indexée. Latence stabilisée à ~270ms." |
| **Monitoring** | Comment détectez-vous qu'un modèle devient obsolète ? | "Grâce au monitoring de **Data Drift** (Evidently AI). Nous comparons périodiquement les distributions des features de prod (logs) aux données d'entraînement." |
| **Sécurité** | Comment gérez-vous les données sensibles ? | "Architecture par ID technique uniquement. Aucune donnée nominative (nom, prénom) n'est stockée ni traitée, assurant une conformité **RGPD 'by design'**." |
| **DevOps** | Pourquoi Docker et GitHub Actions ? | "Pour la reproductibilité totale (principe 'Build once, run anywhere') et la garantie d'une qualité constante via la CI/CD (Coverage > 70% requis)." |
| **Métier** | Pourquoi un seuil à 0.49 et pas 0.50 ? | "C'est une décision métier basée sur une **fonction de coût asymétrique** : un faux négatif (client insolvable accepté) coûte 10x plus cher à la banque qu'un faux positif." |

## 8. Récit d'Ingénierie (Storytelling)
*À utiliser pour répondre aux questions "Quelles difficultés avez-vous rencontrées ?"*

### 🧱 Obstacle 1 : "Memory Leak" & Coûts Cloud
- **Situation** : Le dataset CSV faisait 1.3 Go. Charger Pandas demandait 4 à 6 Go de RAM.
- **Impact** : Impossible de déployer sur Hugging Face (limite RAM) ou sur des serveurs low-cost.
- **Résolution** : Migration vers **SQLite**.
- **Gain** : On ne charge en mémoire QUE le client demandé. Empreinte RAM divisée par 50 (Passage de 6 Go à < 100 Mo).

### 🐳 Obstacle 2 : L'Enfer du Build Docker
- **Situation** : Les premières images Docker pesaient 4.5 Go et faisaient planter le build (disque saturé).
- **Cause** : Le contexte Docker embarquait le CSV d'entraînement et la base complète inutilement.
- **Résolution** :
    1. Mise en place stricte du `.dockerignore`.
    2. Stratégie d'**Hybridation** : Utilisation d'une Base Lite (< 10 Mo) pour la démo Cloud.
- **Gain** : Image finale allégée (~500 Mo) et déploiement ultra-rapide sur Hugging Face.

### ☁️ Obstacle 3 : Déploiement "All-in-One"
- **Situation** : Hugging Face Spaces n'attend qu'un seul service, mais j'avais une API (Backend) et un Dashboard (Frontend).
- **Résolution** : Développement d'un script d'orchestration (`entrypoint.sh`) qui lance FastAPI en arrière-plan et Streamlit au premier plan dans le même conteneur via un monitoring de processus.

---

### Commandes Utiles pour la démo :
- **Lancer TOUT via Docker (Recommandé)** : `make docker-build && make docker-run`
- **Lancer l'API (Local)** : `make run-api`
- **Lancer le Dashboard (Local)** : `streamlit run src/api/dashboard.py`
- **Accès Swagger** : `http://localhost:8000/docs`
- **Accès Dashboard** : `http://localhost:8501`
