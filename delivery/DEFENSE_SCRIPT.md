# 🎙️ Script de Soutenance : Projet Credit Scoring

## ⏱️ Timing Global (30 min)
- **15 min** : Présentation (Slides + Démo)
- **10 min** : Q&A (Chloé Dubois)
- **5 min** : Débrief

---

## 📅 Partie 1 : Présentation (15 min)

### 1. Introduction (2 min)
- **Le Contexte** : Besoin du département "Crédit Express" pour des réponses en quasi temps-réel.
- **La Mission** : Industrialiser le modèle de scoring (Inférence rapide, Conteneurisation, Monitoring).

### 2. Architecture & Industrialisation (4 min)
- **Choix Technique** : FastAPI pour la performance, Docker pour la portabilité.
- **Inférence ONNX** : Pourquoi ? (Standardisation, gain de latence).
- **Scalabilité** : Usage du Cache LRU pour SHAP (gain massif sur les calculs répétés).
- **Architecture Hybride** : Utilisation de SQLite pour le stockage local des logs, garantissant l'indépendance de l'API.

### 3. Démonstration de l'API (3 min)
- **Action** : Montrer un appel sur Hugging Face ou Localhost.
- **Points à souligner** : 
    - Rapidité de réponse (< 300ms avec SHAP).
    - Qualité de l'explication locale (Graphique Waterfall conforme P6).
    - Robustesse (Que se passe-t-il si j'entre un ID inconnu ? -> Erreur 404 propre).

### 4. Monitoring & Data Drift (4 min)
- **Le Concept** : Stockage automatique de 10 features clés dans `prediction_logs`.
- **Simulation** : Lancer le script de simulation (1000 samples) pour montrer un dashboard "vivant".
- **Détection de Drift** : Expliquer comment Evidently AI compare le "Current" au "Reference".
- **Gouvernance** : Mentionner l'indicateur de "Confiance Statistique" pour ne pas s'alarmer prématurément.

### 5. Pipeline CI/CD & Tests (2 min)
- **Automatisation** : Chaque commit déclenche Pytest (Tests unitaires et de robustesse).
- **Qualité** : Couverture > 70% et validation de non-régression.
- **Déploiement** : Merge automatique vers la production (Hugging Face).

---

## ❓ Partie 2 : Q&A - Les questions de Chloé

### Q1 : "Pourquoi utiliser ONNX alors que LightGBM est déjà rapide ?"
- **Réponse** : ONNX standardise le format d'échange. Cela permet de changer de modèle (ex: passer à XGBoost ou PyTorch) sans jamais modifier le code de l'API. C'est un gage de maintenance à long terme.

### Q2 : "Comment gérez-vous le drift si une feature change brutalement ?"
- **Réponse** : Le rapport Evidently identifie la feature en cause. Si le drift est majeur (> 50% des features impactées), cela déclenche une alerte (log/dashboard) et planifie un réentraînement du modèle sur les nouvelles données collectées.

### Q3 : "Votre API est-elle scalable ?"
- **Réponse** : Oui. Grâce au cache LRU, les requêtes répétées ne consomment plus de CPU. Grâce à Docker, on peut multiplier les instances de l'API derrière un Load Balancer.

---

## 🛠️ Cheat Sheet Démo (Commandes)

- **Lancer l'API** : `uvicorn src.api.main:app --reload`
- **Lancer le Dashboard** : `streamlit run src/api/dashboard.py`
- **Simuler 1000 clients (Baseline)** : `python src/database/simulation_cli.py baseline`
- **Simuler un Drift** : `python src/database/simulation_cli.py drift`
- **Reset logs** : `python src/database/simulation_cli.py reset`
