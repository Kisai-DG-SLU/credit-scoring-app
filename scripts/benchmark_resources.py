import time
import psutil
import pandas as pd
import numpy as np
import sqlite3
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.model.loader import loader  # noqa: E402


def measure_resources():
    process = psutil.Process(os.getpid())
    cpu_percent = process.cpu_percent(interval=None)
    memory_info = process.memory_info()
    return cpu_percent, memory_info.rss / 1024 / 1024  # MB


def benchmark_inference(model_type="onnx", n_iterations=1000, batch_size=1):
    print(
        f"--- Benchmarking {model_type.upper()} Model (n={n_iterations}, batch={batch_size}) ---"
    )

    # 1. Load Data
    conn = sqlite3.connect("data/database_lite.sqlite")
    # Exclude SK_ID_CURR and TARGET if present
    query = "SELECT * FROM clients LIMIT 100"
    df_sample = pd.read_sql(query, conn)
    conn.close()

    if "SK_ID_CURR" in df_sample.columns:
        df_sample = df_sample.drop(columns=["SK_ID_CURR"])
    if "TARGET" in df_sample.columns:
        df_sample = df_sample.drop(columns=["TARGET"])

    # Take one row and replicate it to simulate a request
    X_input = df_sample.iloc[0:1]  # Keep DataFrame format

    # 2. Load Model
    start_load = time.time()
    loader.load_artifacts()
    if model_type == "onnx":
        sess = loader.onnx_session
        if sess is None:
            raise ValueError("ONNX session not loaded. Check model path.")
        input_name = sess.get_inputs()[0].name
        # Prepare input for ONNX (numpy float32)
        X_onnx = X_input.values.astype(np.float32)
    else:
        model = loader.model
        if model is None:
            raise ValueError("Joblib model not loaded. Check model path.")
    load_time = time.time() - start_load
    print(f"Model Load Time: {load_time:.4f}s")

    # 3. Warmup
    print("Warming up...")
    for _ in range(10):
        if model_type == "onnx":
            sess.run(None, {input_name: X_onnx})
        else:
            model.predict_proba(X_input)

    # 4. Measure Loop
    print("Starting measurement loop...")
    latencies = []
    cpu_usages = []
    mem_usages = []

    # Initial Baseline
    base_cpu, base_mem = measure_resources()

    start_bench = time.time()

    for i in range(n_iterations):
        # Resource snapshot every 100 iters to avoid overhead
        if i % 100 == 0:
            c, m = measure_resources()
            cpu_usages.append(c)
            mem_usages.append(m)

        t0 = time.time()
        if model_type == "onnx":
            sess.run(None, {input_name: X_onnx})
        else:
            model.predict_proba(X_input)
        latencies.append((time.time() - t0) * 1000)  # ms

    total_time = time.time() - start_bench

    # Final stats
    avg_latency = np.mean(latencies)
    p95_latency = np.percentile(latencies, 95)
    p99_latency = np.percentile(latencies, 99)
    throughput = n_iterations / total_time

    avg_cpu = np.mean(cpu_usages) if cpu_usages else 0
    max_mem = np.max(mem_usages) if mem_usages else 0

    results = {
        "model": model_type,
        "avg_latency_ms": avg_latency,
        "p95_latency_ms": p95_latency,
        "p99_latency_ms": p99_latency,
        "throughput_req_sec": throughput,
        "avg_cpu_percent": avg_cpu,
        "peak_memory_mb": max_mem,
        "baseline_memory_mb": base_mem,
    }

    print("\nResults:")
    for k, v in results.items():
        if isinstance(v, float):
            print(f"{k}: {v:.4f}")
        else:
            print(f"{k}: {v}")

    return results


if __name__ == "__main__":
    # Benchmark ONNX
    results_onnx = benchmark_inference("onnx", n_iterations=1000)

    print("\n" + "=" * 30 + "\n")

    # Benchmark Joblib (Classic) for comparison
    results_joblib = benchmark_inference("joblib", n_iterations=1000)

    # Write report
    report_path = "delivery/proof/resource_usage.txt"
    with open(report_path, "w") as f:
        f.write("BENCHMARK REPORT: RESOURCE USAGE & INFERENCE TIME\n")
        f.write("=================================================\n\n")

        f.write("SCENARIO A: ONNX (Optimized)\n")
        f.write(f"Average Latency: {results_onnx['avg_latency_ms']:.2f} ms\n")
        f.write(f"P95 Latency:     {results_onnx['p95_latency_ms']:.2f} ms\n")
        f.write(f"Throughput:      {results_onnx['throughput_req_sec']:.2f} req/sec\n")
        f.write(f"Avg CPU Usage:   {results_onnx['avg_cpu_percent']:.1f}%\n")
        f.write(f"Peak RAM Usage:  {results_onnx['peak_memory_mb']:.1f} MB\n\n")

        f.write("SCENARIO B: JOBLIB (Baseline)\n")
        f.write(f"Average Latency: {results_joblib['avg_latency_ms']:.2f} ms\n")
        f.write(f"P95 Latency:     {results_joblib['p95_latency_ms']:.2f} ms\n")
        f.write(
            f"Throughput:      {results_joblib['throughput_req_sec']:.2f} req/sec\n"
        )
        f.write(f"Avg CPU Usage:   {results_joblib['avg_cpu_percent']:.1f}%\n")
        f.write(f"Peak RAM Usage:  {results_joblib['peak_memory_mb']:.1f} MB\n\n")

        speedup = results_joblib["avg_latency_ms"] / results_onnx["avg_latency_ms"]
        f.write(f"CONCLUSION: ONNX is {speedup:.1f}x faster than standard Joblib.\n")
        f.write(
            "Note: GPU usage is 0% as inference runs on CPU (optimized for low-cost env).\n"
        )

    print(f"\nReport written to {report_path}")
