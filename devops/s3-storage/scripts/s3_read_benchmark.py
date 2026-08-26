#!/usr/bin/env python3
"""S3 read speed benchmark with visualization.

Usage: python3 s3_read_benchmark.py

Edit ENDPOINTS dict to target your S3-compatible endpoints.
Edit REPEATS and CONCURRENT_LEVELS to adjust test configuration.
"""

import boto3
import time
import os
import json
from datetime import datetime
from botocore.config import Config
from concurrent.futures import ThreadPoolExecutor, as_completed
from statistics import mean, stdev

# === CONFIGURATION ===
ENDPOINTS = {
    "rustfs (9000)": {
        "url": "http://141.33.4.155:9000",
        "key": "rustfsadmin2026",
        "secret": "rustfsadmin2026",
        "bucket": "dbbench-benchmarks",
    },
    "versitygw (7070)": {
        "url": "http://141.33.4.155:7070",
        "key": "versitygwadmin2026",
        "secret": "versitygwadmin2026",
        "bucket": "dbbench-benchmarks",
    },
}

REPEATS = 20
CONCURRENT_LEVELS = [1, 4, 8, 16]


def make_client(ep):
    return boto3.client(
        "s3",
        endpoint_url=ep["url"],
        aws_access_key_id=ep["key"],
        aws_secret_access_key=ep["secret"],
        config=Config(
            retries={"max_attempts": 3},
            signature_version="s3v4",
            connect_timeout=10,
            read_timeout=30,
        ),
    )


def main():
    print("\n" + "=" * 60)
    print("  S3 READ SPEED BENCHMARK")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    clients = {name: make_client(ep) for name, ep in ENDPOINTS.items()}
    bucket = list(ENDPOINTS.values())[0]["bucket"]

    for name, s3 in clients.items():
        print(f"\n✓ {name} connected")

    results = {}

    # Test 1: Single small object latency
    print("\n── Test 1: Single Small Object ──")
    results["single_obj"] = {}
    for name, s3 in clients.items():
        print(f"  {name}...")
        objects = s3.list_objects_v2(Bucket=bucket)["Contents"]
        small_key = objects[0]["Key"]
        times = []
        for _ in range(REPEATS):
            start = time.perf_counter()
            s3.get_object(Bucket=bucket, Key=small_key)["Body"].read()
            times.append((time.perf_counter() - start) * 1000)
        results["single_obj"][name] = {
            "times": times,
            "mean": mean(times),
            "p50": sorted(times)[REPEATS // 2],
            "stdev": stdev(times) if len(times) > 1 else 0,
        }
        print(f"    Mean: {mean(times):.1f} ms (p50: {sorted(times)[REPEATS//2]:.1f})")

    # Test 2: Sequential full read
    print("\n── Test 2: Sequential Full Dataset ──")
    results["sequential"] = {}
    for name, s3 in clients.items():
        print(f"  {name}...")
        objects = s3.list_objects_v2(Bucket=bucket)["Contents"]
        total_bytes = sum(o["Size"] for o in objects)
        times = []
        for _ in range(REPEATS):
            start = time.perf_counter()
            for obj in objects:
                s3.get_object(Bucket=bucket, Key=obj["Key"])["Body"].read()
            elapsed = time.perf_counter() - start
            times.append(elapsed)
        avg = mean(times)
        results["sequential"][name] = {
            "total_bytes": total_bytes,
            "mean_time": avg,
            "mean_throughput_mbps": total_bytes / avg / 1_000_000,
            "stdev": stdev(times) if len(times) > 1 else 0,
        }
        print(f"    {total_bytes / avg / 1_000_000:.1f} MB/s ({avg*1000:.0f} ms)")

    # Test 3: Parallel reads at various concurrency levels
    print("\n── Test 3: Parallel Reads ──")
    results["parallel"] = {}
    for name, s3 in clients.items():
        print(f"  {name}...")
        objects = s3.list_objects_v2(Bucket=bucket)["Contents"]
        total_bytes = sum(o["Size"] for o in objects)
        results["parallel"][name] = {}
        for n_workers in CONCURRENT_LEVELS:
            times = []
            for _ in range(REPEATS):
                start = time.perf_counter()

                def read_one(obj):
                    s3.get_object(Bucket=bucket, Key=obj["Key"])["Body"].read()

                with ThreadPoolExecutor(max_workers=n_workers) as pool:
                    list(pool.map(read_one, objects))

                elapsed = time.perf_counter() - start
                times.append(total_bytes / elapsed / 1_000_000)

            results["parallel"][name][n_workers] = {
                "throughputs": times,
                "mean": mean(times),
            }
            print(f"    {n_workers} workers: {mean(times):.1f} MB/s")

    # Generate plot and save raw data
    print("\nGenerating plot...")
    plot_path = os.path.expanduser("~/projects/s3-benchmark-results/s3_read_benchmark.png")
    os.makedirs(os.path.dirname(plot_path), exist_ok=True)
    _make_plot(results, plot_path)

    data_path = os.path.expanduser("~/projects/s3-benchmark-results/s3_read_benchmark.json")
    with open(data_path, "w") as f:
        json.dump(_serialize(results), f, indent=2)
    print(f"Saved data: {data_path}")

    # Print summary table
    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    header = f"{'Metric':<45} {'RustFS (9000)':>15} {'VersityGW (7070)':>15} {'Winner':>10}"
    print(header)
    print("-" * 90)

    # Sequential throughput
    seq_r = results["sequential"]["rustfs (9000)"]["mean_throughput_mbps"]
    seq_v = results["sequential"]["versitygw (7070)"]["mean_throughput_mbps"]
    w = "RustFS" if seq_r > seq_v else "VersityGW"
    print(f"{'Sequential full read (MB/s)':<45} {seq_r:>15.1f} {seq_v:>15.1f} {w:>10}")

    # Small object latency
    lat_r = results["single_obj"]["rustfs (9000)"]["mean"]
    lat_v = results["single_obj"]["versitygw (7070)"]["mean"]
    w = "RustFS" if lat_r < lat_v else "VersityGW"
    print(f"{'Small object read (ms)':<45} {lat_r:>15.1f} {lat_v:>15.1f} {w:>10}")

    # Parallel at each level
    for n in CONCURRENT_LEVELS:
        r_avg = mean(results["parallel"]["rustfs (9000)"][n]["throughputs"])
        v_avg = mean(results["parallel"]["versitygw (7070)"][n]["throughputs"])
        w = "RustFS" if r_avg > v_avg else "VersityGW"
        print(f"{'Parallel ' + str(n) + ' workers (MB/s)':<45} {r_avg:>15.1f} {v_avg:>15.1f} {w:>10}")

    print(f"\n✅ Benchmark complete — {REPEATS} repeats per test")


def _serialize(obj):
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_serialize(v) for v in obj]
    elif isinstance(obj, (int, float)):
        return float(obj)
    return obj


def _make_plot(results_data, output_path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    colors = {"rustfs (9000)": "#2563eb", "versitygw (7070)": "#dc2626"}
    labels = {"rustfs (9000)": "RustFS (9000)", "versitygw (7070)": "VersityGW (7070)"}

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(
        "S3 Endpoint Read Performance Benchmark",
        fontsize=15, fontweight="bold", y=0.98,
    )

    # Subplot 1: Single object latency (box plot)
    ax1 = axes[0, 0]
    all_times = []
    legend_handles = []
    for i, (name, ep_data) in enumerate(results_data["single_obj"].items()):
        times = ep_data["times"]
        all_times.extend(times)
        bp = ax1.boxplot(times, positions=[i], widths=0.3,
                       patch_artist=True, boxprops=dict(facecolor=colors[name], alpha=0.3),
                       medianprops=dict(color="black", linewidth=1.5),
                       whiskerprops=dict(color=colors[name], linewidth=1.2),
                       capprops=dict(color=colors[name], linewidth=1.2))
        ax1.scatter([i], [mean(times)], color=colors[name], s=50,
                   marker="D", edgecolor="white", linewidth=1, zorder=5)
        legend_handles.append(plt.Line2D([0], [0], marker='D', color='w', markerfacecolor=colors[name],
                                        markersize=8, label=labels[name]))

    ax1.set_xticks(range(len(results_data["single_obj"])))
    ax1.set_xticklabels(labels.keys())
    ax1.set_ylabel("Latency (ms)")
    ax1.set_title("Single Small Object Read")
    ax1.legend(handles=legend_handles, loc="upper right", fontsize=8)
    if all_times:
        ax1.set_ylim(0, max(all_times) * 1.1)

    # Subplot 2: Sequential full read throughput
    ax2 = axes[0, 1]
    sorted_names = sorted(results_data["sequential"].keys(),
                         key=lambda x: results_data["sequential"][x]["mean_throughput_mbps"])
    for i, name in enumerate(sorted_names):
        data = results_data["sequential"][name]
        if "mean_throughput_mbps" in data:
            val = data["mean_throughput_mbps"]
            err = data["stdev"] if data["stdev"] > 0 else 0
            y_pos = i
            ax2.barh([y_pos], [val], xerr=[err], color=colors[name],
                    alpha=0.75, edgecolor=colors[name], linewidth=1.2, height=0.5)
            ax2.text(val + err + 0.5, y_pos, f"{val:.1f} MB/s",
                    va="center", fontsize=10, fontweight="bold",
                    color=colors[name])
    ax2.set_yticks(range(len(sorted_names)))
    ax2.set_yticklabels([labels[n] for n in sorted_names])
    ax2.set_xlabel("Throughput (MB/s)")
    ax2.set_title("Sequential Full Dataset Read")
    ax2.set_xlim(0)
    ax2.spines['left'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    # Subplot 3: Parallel read throughput (bar comparison)
    ax3 = axes[1, 0]
    worker_counts = CONCURRENT_LEVELS
    bar_width = 0.35
    x_pos = range(len(worker_counts))
    ep_names = list(results_data["parallel"].keys())
    for i, name in enumerate(ep_names):
        data_list = results_data["parallel"][name]
        avg_throughputs = [mean(data_list[w]["throughputs"]) for w in worker_counts]
        ax3.bar(
            [p + i * bar_width for p in x_pos], avg_throughputs,
            bar_width, label=labels[name],
            color=colors[name], alpha=0.8, edgecolor=colors[name], linewidth=1,
        )
    ax3.set_xticks([p + bar_width / 2 for p in x_pos])
    ax3.set_xticklabels(worker_counts)
    ax3.set_ylabel("Throughput (MB/s)")
    ax3.set_title("Concurrent Read Throughput by Workers")
    ax3.legend(fontsize=8)

    # Value labels on bars
    for name in ep_names:
        data_list = results_data["parallel"][name]
        for i, w in enumerate(worker_counts):
            avg_t = mean(data_list[w]["throughputs"])
            ax3.text(i + ep_names.index(name) * bar_width,
                    avg_t + 0.3, f"{avg_t:.0f}",
                    ha="center", fontsize=7, color="black", fontweight="bold")

    # Subplot 4: Scaling curve (mean throughput vs workers)
    ax4 = axes[1, 1]
    markers = {"rustfs (9000)": "o", "versitygw (7070)": "s"}
    for name in ep_names:
        data_list = results_data["parallel"][name]
        avg_ts = [mean(data_list[w]["throughputs"]) for w in worker_counts]
        min_ts = [min(data_list[w]["throughputs"]) for w in worker_counts]
        max_ts = [max(data_list[w]["throughputs"]) for w in worker_counts]
        ax4.plot(worker_counts, avg_ts, marker=markers[name],
                color=colors[name], linewidth=2, markersize=8,
                label=labels[name], zorder=3)
        ax4.fill_between(worker_counts, min_ts, max_ts,
                        color=colors[name], alpha=0.1)

    ax4.set_xlabel("Concurrent Workers")
    ax4.set_ylabel("Throughput (MB/s)")
    ax4.set_title("Scaling Curve")
    ax4.set_xticks(worker_counts)
    ax4.legend(fontsize=8)
    ax4.grid(True, alpha=0.2)
    ax4.set_xlim(0, max(worker_counts) + 2)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(output_path, dpi=150, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close()
    print(f"Saved plot: {output_path}")


if __name__ == "__main__":
    main()
