# 📊 Rapport d'Optimisation & Performance

## ⏱️ Résultats du Benchmark (Audit Final - Phase 17)

Mesures réalisées sur environnement local (Mac, CPU) via script de benchmark dédié (`scripts/benchmark_resources.py`).

| Opération | Méthode | Temps Moyen | Gain (Speedup) |
|-----------|---------|-------------|----------------|
| **Inférence** | Joblib (Baseline) | 3.39 ms | 1x (Baseline) |
| **Inférence** | ONNX (Optimisé) | **0.03 ms** | **~100x** plus rapide |
| **Inférence** | Cached (LRU) | ~0.001 ms | Instantané |

> **Note** : Le temps d'inférence ONNX est extrêmement faible (0.03ms), démontrant l'efficacité de la compilation du graphe pour des prédictions unitaires.

## 💾 Analyse des Ressources (CPU/RAM)
| Métrique | Joblib | ONNX | Observation |
|----------|--------|------|-------------|
| **Utilisation RAM** | ~288 MB | ~311 MB | ONNX consomme légèrement plus (+8%) dû au chargement du runtime. |
| **Utilisation CPU** | Négligeable | Négligeable | Le modèle est très léger, l'inférence ne sature pas le CPU. |
| **Throughput** | ~294 req/s | **~32,000 req/s** | Capacité de traitement massivement augmentée. |

## 🚀 Analyse Technique & Justifications
- **ONNX Runtime** : Le passage à ONNX offre un gain de performance spectaculaire (x100) sur ce modèle tabulaire. Cela s'explique par l'optimisation bas niveau du graphe de calcul et l'absence de l'overhead Python/Pandas inhérent à Scikit-Learn lors des appels `predict`.
- **Cache LRU** : Maintenu pour éliminer totalement le coût pour les requêtes répétées (UX Dashboard).
- **Architecture CPU** : Les résultats (0.03ms) confirment que l'usage d'un GPU est **inutile** et serait même contre-productif (latence de transfert RAM-VRAM > temps de calcul). L'architecture "CPU-only" est validée pour la production (coût minimal).

## 🛠️ Configuration d'Optimisation
- **Format** : ONNX Opset 12
- **Moteur** : ONNX Runtime CPU (optimisé osx-64/linux-64)
- **Cache** : LRU (Least Recently Used) - Taille 128 entrées