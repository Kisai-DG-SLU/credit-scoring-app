import requests
import time
import numpy as np

API_URL = "http://localhost:8000"
CLIENT_ID = 100001


def benchmark_api(n_requests=50):
    # Warmup
    print("Warming up...")
    requests.get(f"{API_URL}/predict/{CLIENT_ID}")

    times = []
    print(f"Benchmarking {n_requests} requests...")

    for i in range(n_requests):
        start = time.time()
        resp = requests.get(f"{API_URL}/predict/{CLIENT_ID}")
        end = time.time()

        if resp.status_code == 200:
            times.append(end - start)
        else:
            print(f"Request failed: {resp.status_code}")

    avg_time = np.mean(times)
    p95_time = np.percentile(times, 95)

    print(f"Average time: {avg_time*1000:.2f} ms")
    print(f"95th percentile: {p95_time*1000:.2f} ms")
    print(f"Min time: {np.min(times)*1000:.2f} ms")
    print(f"Max time: {np.max(times)*1000:.2f} ms")


if __name__ == "__main__":
    # Attente que l'API soit up
    time.sleep(5)
    try:
        benchmark_api()
    except Exception as e:
        print(f"Benchmark error: {e}")
