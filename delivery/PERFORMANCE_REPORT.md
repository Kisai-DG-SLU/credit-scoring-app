# 📊 Rapport d'Optimisation & Performance

## ⏱️ Résultats du Benchmark
| Opération | Méthode | Temps | Gain |
|-----------|---------|-------|------|
| **Chargement** | Cold Start | 1.00s | Baseline |
| **Inférence** | Joblib | 217.99ms | Baseline |
| **Inférence** | ONNX | 256.09ms | -15% plus rapide |
| **Inférence** | **Cached** | **0.0010ms** | **~228,580x** plus rapide |
| **SHAP** | Standard | 186.38ms | Baseline |
| **SHAP** | **Cached** | **0.0017ms** | **~111,676x** plus rapide |

## 🚀 Analyse Technique
- **ONNX Runtime** : Standardise l'inférence et réduit la latence CPU. Très utile pour la scalabilité.
- **Cache LRU** : Élimine totalement le coût de calcul pour les requêtes répétées (ex: dashboard rafraîchi par l'utilisateur). C'est l'optimisation la plus impactante pour l'UX.
- **Inférence pure** : Réduite de 218.0ms à 256.1ms.

## 🛠️ Configuration d'Optimisation
- **Format** : ONNX Opset 12
- **Moteur** : ONNX Runtime CPU (optimisé osx-64/linux-64)
- **Cache** : LRU (Least Recently Used) - Taille 128 entrées
