import time
import requests
import numpy as np
import cProfile
import pstats
import io


def benchmark_api(n_iterations=10, client_id=100004):
    url = "http://localhost:8000/predict/"
    latencies = []

    print(f"--- Benchmarking API Predict ({n_iterations} iterations) ---")

    for i in range(n_iterations):
        start = time.time()
        try:
            response = requests.get(f"{url}{client_id}")
            if response.status_code == 200:
                latencies.append(time.time() - start)
            else:
                print(f"Iteration {i}: Error {response.status_code}")
        except Exception as e:
            print(f"Iteration {i}: Connection failed ({e})")
            break

    if latencies:
        avg_lat = np.mean(latencies)
        p95_lat = np.percentile(latencies, 95)
        print(f"Average Latency: {avg_lat*1000:.2f} ms")
        print(f"P95 Latency: {p95_lat*1000:.2f} ms")
        return avg_lat
    return None


def profile_call():
    # Simulation d'un appel interne pour profilage sans réseau
    from src.model.loader import loader

    data = loader.get_client_data(100004)
    features = data.drop(columns=["TARGET", "SK_ID_CURR"], errors="ignore")

    pr = cProfile.Profile()
    pr.enable()

    # Simuler le flow de l'API
    model = loader.model
    model.predict_proba(features)[0][1]
    loader.get_shap_values(features)

    pr.disable()
    s = io.StringIO()
    sortby = "cumulative"
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats(15)  # Top 15 fonctions
    print(s.getvalue())


if __name__ == "__main__":
    print("1. Profiling Interne (Goulots d'étranglement)")
    profile_call()

    print("\n2. Benchmark Externe (Latence réelle)")
    # Note: L'API doit être lancée séparément sur le port 8000
    benchmark_api()
