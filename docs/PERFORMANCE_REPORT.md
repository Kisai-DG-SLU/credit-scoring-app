# 📊 Rapport de Performance API Scoring

## ⏱️ Mesures de Latence (Baseline)
- **Latence Moyenne (API + SHAP)** : ~269 ms
- **Latence P95** : ~324 ms
- **Temps d'inférence Modèle (pur)** : < 15 ms

## 🔍 Analyse du Profilage (Goulots d'étranglement)
Le profilage via `cProfile` a révélé les points suivants :
1. **Chargement Initial (Cold Start)** : 1.08s lors du premier appel.
   - Cause : Initialisation de `shap.TreeExplainer` qui nécessite un dump JSON du modèle LightGBM.
2. **Impact de SHAP** : Le calcul des SHAP values représente ~90% du temps de traitement de la requête.
3. **Optimisation appliquée** : Mise en place d'un mécanisme de **Warmup** au démarrage de l'API (`on_event("startup")`).

## 🚀 Améliorations & Scalabilité
- **Warmup** : Réduit la latence du premier appel de 1200ms à 270ms.
- **Conformité P6** : L'usage de `shap.plots.waterfall` avec un échantillonnage Top 15 assure un bon compromis entre explicabilité et rapidité.
- **Docker** : L'encapsulation dans Docker n'ajoute qu'une latence réseau négligeable (< 5ms).

## 💡 Recommandations (Futur)
1. **Mise en cache** : Les résultats SHAP pour les clients fréquents pourraient être mis en cache (Redis/LRU).
2. **Conversion ONNX** : À explorer pour une production à très haute fréquence, bien que le gain soit marginal face au coût de SHAP.
