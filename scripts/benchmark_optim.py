import time
import sys
from pathlib import Path

# Ajouter le chemin racine pour les imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.model.loader import loader  # noqa: E402


def run_benchmark():
    print("--- Benchmark Optimisation MLOps ---")

    # 1. Mesure du Cold Start (Chargement)
    start = time.time()
    loader.load_artifacts()
    load_time = time.time() - start
    print(f"Cold Start (Chargement artefacts) : {load_time:.4f}s")

    client_id = 100004

    # 2. Inférence Standard (Joblib) - On désactive ONNX temporairement pour le test
    orig_session = loader.onnx_session
    loader.onnx_session = None
    loader.predict_proba.cache_clear()

    start = time.time()
    loader.predict_proba(client_id)
    joblib_time = time.time() - start
    print(f"Inférence Joblib (Premier appel) : {joblib_time*1000:.2f}ms")

    # 3. Inférence ONNX
    loader.onnx_session = orig_session
    loader.predict_proba.cache_clear()

    start = time.time()
    loader.predict_proba(client_id)
    onnx_time = time.time() - start
    print(f"Inférence ONNX (Premier appel) : {onnx_time*1000:.2f}ms")

    # 4. Inférence avec Cache LRU
    start = time.time()
    loader.predict_proba(client_id)
    cached_time = time.time() - start
    print(f"Inférence Cached (Second appel) : {cached_time*1000:.4f}ms")

    # 5. Calcul SHAP
    loader.get_shap_values_cached.cache_clear()
    start = time.time()
    loader.get_shap_values_cached(client_id)
    shap_time = time.time() - start
    print(f"Calcul SHAP (Premier appel) : {shap_time*1000:.2f}ms")

    start = time.time()
    loader.get_shap_values_cached(client_id)
    shap_cached_time = time.time() - start
    print(f"Calcul SHAP (Cached) : {shap_cached_time*1000:.4f}ms")

    # Création du rapport
    report = f"""# 📊 Rapport d'Optimisation & Performance

## ⏱️ Résultats du Benchmark
| Opération | Méthode | Temps | Gain |
|-----------|---------|-------|------|
| **Chargement** | Cold Start | {load_time:.2f}s | Baseline |
| **Inférence** | Joblib | {joblib_time*1000:.2f}ms | Baseline |
| **Inférence** | ONNX | {onnx_time*1000:.2f}ms | {((joblib_time/onnx_time)-1)*100:.0f}% plus rapide |
| **Inférence** | **Cached** | **{cached_time*1000:.4f}ms** | **~{joblib_time/cached_time:,.0f}x** plus rapide |
| **SHAP** | Standard | {shap_time*1000:.2f}ms | Baseline |
| **SHAP** | **Cached** | **{shap_cached_time*1000:.4f}ms** | **~{shap_time/shap_cached_time:,.0f}x** plus rapide |

## 🚀 Analyse Technique
- **ONNX Runtime** : Standardise l'inférence et réduit la latence CPU. Très utile pour la scalabilité.
- **Cache LRU** : Élimine totalement le coût de calcul pour les requêtes répétées (ex: dashboard rafraîchi par l'utilisateur). C'est l'optimisation la plus impactante pour l'UX.
- **Inférence pure** : Réduite de {joblib_time*1000:.1f}ms à {onnx_time*1000:.1f}ms.

## 🛠️ Configuration d'Optimisation
- **Format** : ONNX Opset 12
- **Moteur** : ONNX Runtime CPU (optimisé osx-64/linux-64)
- **Cache** : LRU (Least Recently Used) - Taille 128 entrées
"""

    with open("delivery/PERFORMANCE_REPORT.md", "w") as f:
        f.write(report)
    print("\nRapport généré : delivery/PERFORMANCE_REPORT.md")


if __name__ == "__main__":
    run_benchmark()
