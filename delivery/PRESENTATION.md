---
marp: true
theme: gaia
paginate: true
backgroundImage: url('images/background.png')
color: #333
style: |
  section {
    justify-content: center;
    padding: 70px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 28px;
  }
  section::before {
    content: ' ';
    position: absolute;
    top: 20px;
    left: 20px;
    width: 80px;
    height: 80px;
    background-image: url('images/logo_projet.png');
    background-size: contain;
    background-repeat: no-repeat;
  }
  footer {
    position: absolute;
    bottom: 20px;
    right: 20px;
    font-size: 0.8em;
    color: #7f8c8d;
  }
  section:not(.lead) h1 {
    margin-top: 1.0em; 
    color: #2c3e50;
    border-bottom: 2px solid #e74c3c;
  }
  section.lead h1 {
    font-size: 2.2em;
    color: #2c3e50;
    margin-bottom: 0.2em;
  }
  section.lead h2 {
    font-size: 1.4em;
    color: #7f8c8d;
    margin-top: 0;
  }
  .catchphrase {
    color: #e74c3c;
    font-size: 1.3em;
    font-weight: bold;
    margin-top: 10px;
    display: inline-block;
    transform: rotate(-2deg);
    text-shadow: 1px 1px 1px rgba(0,0,0,0.1);
  }
  code {
    background-color: #f4f4f4;
    color: #e74c3c;
    padding: 2px 4px;
    border-radius: 4px;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
  }
  th {
    background-color: #2c3e50;
    color: white;
    padding: 10px;
  }
  td {
    padding: 10px;
    border-bottom: 1px solid #ddd;
  }
  .highlight {
    color: #e67e22;
    font-weight: bold;
  }
---

<!-- _class: lead -->

# **Scoring & Monitoring Industriel**
## Projet 8 : MLOps & Déploiement

<span class="catchphrase">"De l'expérimentation à la production résiliente"</span>

**Damien Guesdon** | Janvier 2026

<!-- 
NOTES :
Bonjour Chloé. Ravi de te présenter l'aboutissement de ma mission. 
L'objectif aujourd'hui est de te prouver que notre modèle de scoring n'est plus un prototype de labo, mais un service de production industriel, rapide et surtout sous contrôle statistique.

TIMING : 15 min max.
STRUCTURE : 
1. Architecture & Dépôt (2 min)
2. Optimisation & Performance (4 min)
3. Démo API & Dashboard (3 min)
4. Monitoring & Data Drift (4 min)
5. CI/CD & Démo Pipeline (2 min)
-->

---

# Architecture & Structure du Projet

### Organisation du Dépôt (Livrables 1-5)
- `src/` : Coeur métier (API FastAPI, Logique ONNX).
- `tests/` : Suite Pytest (Robustesse & Unitaire).
- `.github/workflows/` : Pipeline CI/CD (Automatisation).
- `Dockerfile` : Standardisation de l'environnement.

### Le Choix de l'Architecture Hybride
- **Migration SQLite** : Passage de 6 Go à **50 Mo de RAM**.
- **Indépendance** : Données de référence indexées pour un accès < 5ms.

<!-- 
NOTES :
[ACTION : Préparez votre fenêtre VS Code / GitHub]
Commençons par l'Architecture Hybride. Chloé, c'est ma réponse au problème de scalabilité.
Le problème : Charger 1.3Go de CSV avec Pandas consomme ~6Go de RAM. C'est impossible sur les instances Cloud standards gratuites ou low-cost.
Ma solution : J'ai migré les données vers SQLite avec un INDEX sur l'ID client. 
L'impact : On passe d'une consommation RAM de 6 Go pour la donnée à une empreinte quasi-nulle (quelques Mo de buffer SQL).
En incluant l'API et le modèle ONNX, l'application totale ne consomme que 300 Mo de RAM. C'est un gain d'un facteur 20.
[DÉMONSTRATION RAPIDE] : Montrez le fichier Dockerfile et expliquez que cela permet de faire tourner l'application sur n'importe quel serveur CPU léger.
-->

---

# Optimisations de Performance (Livrable 5)

| Métrique | Joblib (Baseline) | **ONNX (Optimisé)** | Gain |
| :--- | :--- | :--- | :--- |
| **Temps d'inférence** | 3.39 ms | **0.03 ms** | **x113** |
| **Throughput** | 294 req/s | **32 000 req/s** | **x108** |
| **Démarrage API** | ~45 sec | **~2 sec** | **x22** |

- **Goulot identifié** : Chargement lourd de Scikit-Learn & Overhead Pandas.
- **Solution** : Inférence via **ONNX Runtime** + Cache LRU pour SHAP.

<!-- 
NOTES :
Chloé, tu m'avais demandé de réduire le temps de réponse. Après profiling, j'ai identifié que l'overhead de Pandas et Scikit-learn était notre frein.
En convertissant en ONNX, l'inférence brute passe à 0.03ms. 
Attention à la nuance : sur le dashboard, on voit environ 300ms de latence globale car cela inclut SHAP.
[ACTION : Si Chloé demande une preuve du 0.03ms]
"Chloé, si tu veux voir la performance brute du moteur ONNX, je peux te lancer mon script de benchmark."
[ACTION TERMINAL : python scripts/benchmark_resources.py]
"On voit ici qu'on est bien à 0.03 ms en moyenne. C'est cette réserve de puissance qui nous permet d'absorber des pics de charge massifs sans GPU."

--- 💡 ANTISÈCHE EXPERT (En langage simple) ---
- Pourquoi ONNX ? On passe d'une traduction "mot à mot" (Python) à un texte lu directement par l'ordinateur. C'est plus rapide car on supprime les intermédiaires.
- Pourquoi 300ms sur le Dashboard ? 0.03ms c'est le score seul. 300ms c'est le temps de chercher le dossier client et surtout de rédiger la "lettre d'explication" (SHAP).
- Le script est-il dans la CI ? Le benchmark est un "check-up complet" (Audit). La CI est un "coup de thermomètre" (Test perf_test.py) : si on dépasse 100ms, on bloque tout.
- Warmup ? Comme un moteur d'avion, on attend qu'il soit chaud (10 tours à blanc) avant de mesurer sa vitesse réelle.
- Percentiles (P95/P99) ? La moyenne est un piège. Le P99 garantit que même le client "le moins chanceux" a une réponse ultra-rapide.
-->

---

# Démonstration : API & Dashboard

### 1. L'API de Production (FastAPI)
- Documentation interactive (Swagger).
- Validation stricte des types via Pydantic.

### 2. Le Dashboard (Streamlit)
- Visualisation du score et de la décision.
- **Explicabilité Locale** : Pourquoi ce client a-t-il ce score ?

<!-- 
NOTES :
[ACTION : Ouvrez le navigateur sur l'interface Swagger /docs]
Faisons une démonstration. J'envoie une requête pour l'ID 100001. 
[ACTION : 'Try it out' dans Swagger, entrez l'ID, montrez le JSON de réponse].
On voit le score et la recommandation immédiate. 
[ACTION : Passez sur le Dashboard Streamlit]
Ici, c'est l'outil pour les chargés de clientèle. On entre l'ID, et on obtient non seulement la jauge de risque, mais aussi le graphique Waterfall de SHAP. C'est la transparence RGPD que nous visions.
-->

---

# Monitoring & Data Drift (Livrable 4 & 6)

- **Collecte** : Table `prediction_logs` après chaque prédiction.
- **Analyse** : Rapport **Evidently AI** (Drift Detected).
- **Indicateur** : Jensen-Shannon sur le Top-10 features.

<span class="highlight">Gouvernance</span> : Alerte automatique si dérive statistique majeure.

<!-- 
NOTES :
Un modèle peut dériver si le profil des clients change. 
[ACTION : Montrez le rapport HTML drift_report.html]

[PRÉPARATION (Avant soutenance) : python src/database/simulation_cli.py reset && python src/database/simulation_cli.py baseline]
[ACTION LIVE : python src/database/simulation_cli.py drift]
[EXPLICATION DRIFT : Ma simulation altère 3 features clés :
1. EXT_SOURCE_2 : divisé par 2 (chute de fiabilité d'une source externe).
2. AMT_INCOME_TOTAL : multiplié par 2 (hausse suspecte des revenus déclarés).
3. DAYS_BIRTH : population artificiellement vieillie de ~13 ans.
Cela permet de démontrer la capacité du système à détecter des changements comportementaux ou démographiques.]

J'ai configuré le monitoring sur notre Top-10 Features. Le rapport montre par exemple que EXT_SOURCE_1 a dérivé.
C'est notre signal pour un réentraînement. 
J'ai mis un verrou de "Confiance Statistique" : pas d'alerte avant 500 nouveaux profils pour éviter les faux positifs.

--- 💡 ANTISÈCHE ÉVIDENTLY (Le moteur) ---
- Comment ça marche ? Comparaison "Reference" (Entraînement) vs "Current" (Production).
- Seuil Individuel ? P-Value < 0.05. Si p < 0.05, on est sûr à 95% que la différence n'est pas un hasard.
- Seuil Global (0.3) ? C'est ma config `drift_share=0.3`. Si 3 variables sur 10 dérivent, le modèle global est considéré en drift.
- Quel test ? Jensen-Shannon ici car nos 10 features sont numériques. Le Chi-2 serait utilisé pour des catégories.

--- 🎯 PUNCHLINES & ESQUIVES (En cas de question "piège") ---
- "La P-Value, c'est mon filtre anti-hasard : elle me certifie que le changement est réel."
- "Jensen-Shannon mesure l'Entropie (le désordre) : on regarde si le mélange entre passé et présent crée une 'surprise' statistique."
- "J'ai choisi JS car c'est une mesure symétrique et borné (entre 0 et 1), ce qui la rend plus stable que d'autres tests pour du monitoring."
- "Le Chi-2 (si demandé), c'est pour comparer des fréquences : est-ce que j'ai toujours la même proportion de types de contrats qu'avant ?"
-->

---

# CI/CD & Robustesse (Livrable 3 & 4)

- **Workflow** : GitHub Actions (`ci.yml`).
- **Tests de Robustesse** : IDs inconnus, types erronés, limites.

### **Démonstration Directe**
1. Modification mineure du code.
2. `git commit` & `git push`.
3. Observation du déclenchement du Pipeline.

<!-- 
NOTES :
La sécurité de notre prod repose sur le CI/CD. 
[ACTION : Ouvrez votre terminal]
Je vais simuler une mise à jour mineure. 
[ACTION : Modifiez un commentaire dans README.md ou un print mineur dans src/api/main.py]
`git add . && git commit -m "docs: minor update for demo" && git push`
[ACTION : Allez sur l'onglet 'Actions' de votre dépôt GitHub]
On voit le workflow se lancer. Il va tester le code, vérifier la couverture, et si tout est vert, il déploiera la nouvelle image sur Hugging Face automatiquement. C'est l'assurance qu'aucun code cassé ne part en prod.
-->

---

<!-- _class: lead -->

# Conclusion & Discussion

- ✅ **API Industrielle** (FastAPI/Docker).
- ✅ **Optimisation ONNX** (x100 vitesse).
- ✅ **Monitoring Actif** (Evidently AI).

### **Questions ? (Chloé)**

<!-- 
NOTES :
En résumé, Chloé, nous avons une solution robuste, monitorée et scalable. 
L'architecture est optimisée pour le coût et la performance. 
Je suis prêt pour tes questions sur la robustesse ou la maintenance à long terme.

--- 💾 ANTISÈCHE STOCKAGE (Monitoring) ---
- Pourquoi des screenshots de stockage ? C'est la preuve que notre API a de la mémoire. Sans logs persistants (SQLite), pas de monitoring possible.
- Utilité métier : On peut rejouer une décision passée, auditer un refus ou prouver la non-dérive à un régulateur.
- Action Preuve BDD : sqlite3 data/database.sqlite "SELECT * FROM prediction_logs ORDER BY id DESC LIMIT 5;"

--- 🛡️ ANTISÈCHE TESTS & QUALITÉ (Garantie industrielle) ---
- Stratégie : 3 niveaux (Unitaires sur le modèle, Intégration sur l'API, Performance sur la latence).
- Coverage : > 70% (exigence Chloé). On teste les cas "passants" ET les cas "limites".
- Exemples de Robustesse (test_api.py) : 
    - Ligne 45 : Gestion des NaN/Inf -> LightGBM les gère nativement en les orientant vers la branche la plus logique de l'arbre.
    - Ligne 98 : On teste les "Types Invalides" (ID = "abc"). L'API renvoie une 422 (Unprocessable Entity) grâce à Pydantic.
- Performance (perf_test.py) : 
    - cProfile : Outil Python qui compte chaque appel de fonction et sa durée pour identifier précisément les goulots d'étranglement.
    - Cache LRU (Least Recently Used) : Mémoire vive qui stocke les 128 derniers résultats pour servir SHAP instantanément.
- Pourquoi Pytest ? Pour l'automatisation dans la CI. Si un test échoue, le déploiement sur Hugging Face est bloqué.

--- 💻 ANTISÈCHE CODE (API & Dashboard) ---
- FastAPI (src/api/main.py) :
    - Ligne 30 : `startup_event` -> On charge le modèle ONNX et l'explainer SHAP une seule fois au démarrage (Gain de perf).
    - Ligne 43 : `middleware` -> On calcule automatiquement la durée de chaque requête HTTP pour le monitoring de latence.
    - Ligne 77 : `predict` -> Le coeur de l'API. Utilise le `loader` pour l'inférence ONNX et le cache LRU.
    - Ligne 134 : `log_prediction` -> Enregistrement asynchrone dans SQLite pour ne pas ralentir la réponse client.
- Dashboard (src/api/dashboard.py) :
    - Ligne 42 : `@st.cache_data` -> On évite de refaire des requêtes API inutiles si on change juste un paramètre visuel.
    - Lignes 93-100 : Intégration de `shap.plots.waterfall` -> On utilise l'objet 'Explanation' pour avoir le même rendu que dans le Projet 6.
    - Ligne 145 : Lecture SQLite -> Le dashboard interroge directement les logs pour afficher les stats de prod en temps réel.
    - Ligne 190 : `generate_drift_report` -> On lance l'analyse Evidently AI d'un clic et on affiche le HTML interactif dans un 'iframe'.
-->












