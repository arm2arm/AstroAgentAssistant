#!/usr/bin/env python3
"""Generate 8-panel dashboard for a single DBBench model result.

Usage:
    python3 generate_dbbench_plot.py <results_json_path> [output_png_path]

For multi-model comparison plots, see SKILL.md for inline template.
"""

import json
import sys
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def make_plot(data, output_path):
    results = sorted(data["results"], key=lambda r: r["index"])
    model = data["model"]
    sql_rate = data["sql_rate"]
    avg_time = data["avg_time_sec"]
    elapsed = data["elapsed_seconds"]
    error_count = data["error_count"]

    times = [r["time_sec"] for r in results if r["status"] == "COMPLETED"]
    indices = list(range(len(times)))

    fig, axes = plt.subplots(2, 4, figsize=(22, 10))
    fig.suptitle(f"AgentBench DBBench — {model}", fontsize=16, fontweight="bold", y=0.98)
    fig.text(0.5, 0.94,
             f"SQL Rate: {sql_rate:.1f}% | Avg Time: {avg_time:.1f}s | Total: {elapsed/60:.1f}min | Errors: {error_count}",
             ha="center", fontsize=11, style="italic", color="#555")

    # Panel 1: Per-sample time (line)
    ax1 = axes[0, 0]
    ax1.plot(indices, times, color="#2563eb", linewidth=0.5, alpha=0.8)
    ax1.axhline(y=np.mean(times), color="#dc2626", linestyle="--", linewidth=1, label=f"Mean={np.mean(times):.1f}s")
    ax1.set_xlabel("Sample"); ax1.set_ylabel("Time (s)")
    ax1.set_title("Per-Sample Latency", fontweight="bold")
    ax1.legend(fontsize=8); ax1.grid(True, alpha=0.2)

    # Panel 2: Histogram
    ax2 = axes[0, 1]
    bins = np.linspace(0, min(max(times) * 1.05, max(times) + 5), 50)
    ax2.hist(times, bins=bins, color="#2563eb", edgecolor="#1e40af", alpha=0.8, linewidth=0.3)
    ax2.axvline(x=np.mean(times), color="#dc2626", linestyle="--", linewidth=1.5, label=f"Mean={np.mean(times):.1f}s")
    ax2.axvline(x=np.median(times), color="#f59e0b", linestyle="--", linewidth=1.5, label=f"Median={np.median(times):.1f}s")
    ax2.set_xlabel("Time (s)"); ax2.set_ylabel("Count")
    ax2.set_title("Latency Distribution", fontweight="bold")
    ax2.legend(fontsize=8); ax2.grid(True, alpha=0.2)

    # Panel 3: Cumulative SQL rate
    ax3 = axes[0, 2]
    cumulative_sql = []; sql_count = 0; completed_count = 0
    for r in results:
        if r["status"] == "COMPLETED":
            completed_count += 1
            if r.get("has_sql"): sql_count += 1
            cumulative_sql.append(sql_count / completed_count * 100)
    ax3.plot(range(len(cumulative_sql)), cumulative_sql, color="#10b981", linewidth=1.2)
    ax3.axhline(y=sql_rate, color="#dc2626", linestyle="--", linewidth=1, label=f"Final={sql_rate:.1f}%")
    ax3.set_xlabel("Sample"); ax3.set_ylabel("Cumulative SQL Rate (%)")
    ax3.set_title("Cumulative SQL Rate", fontweight="bold")
    ax3.set_ylim(0, 105); ax3.legend(fontsize=8); ax3.grid(True, alpha=0.2)

    # Panel 4: SQL vs Non-SQL bar
    ax4 = axes[0, 3]
    has_sql_count = sum(1 for r in results if r.get("has_sql"))
    no_sql_count = sum(1 for r in results if r["status"] == "COMPLETED" and not r.get("has_sql"))
    err_count = sum(1 for r in results if r["status"] == "ERROR")
    bars = ax4.bar(["SQL", "No SQL", "Errors"], [has_sql_count, no_sql_count, err_count],
                   color=["#10b981", "#ef4444", "#f59e0b"], width=0.5)
    ax4.set_ylabel("Count")
    ax4.set_title(f"SQL: {has_sql_count} | No SQL: {no_sql_count} | Errors: {err_count}", fontweight="bold")
    for bar in bars:
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                 f"{int(bar.get_height())}", ha="center", va="bottom", fontsize=12, fontweight="bold")
    ax4.grid(True, alpha=0.2, axis="y")

    # Panel 5: Status pie
    ax5 = axes[1, 0]
    statuses = {}
    for r in results:
        s = r["status"]
        statuses[s] = statuses.get(s, 0) + 1
    labels_pie = list(statuses.keys()); vals = list(statuses.values())
    colors_pie = ["#10b981", "#ef4444", "#f59e0b"]
    ax5.pie(vals, labels=labels_pie, autopct="%1.0f%%", colors=colors_pie[:len(labels_pie)], textprops={"fontsize": 10})
    ax5.set_title("Response Status", fontweight="bold")

    # Panel 6: Boxplot SQL vs non-SQL
    ax6 = axes[1, 1]
    sql_times_d = [r["time_sec"] for r in results if r.get("has_sql")]
    nosql_times_d = [r["time_sec"] for r in results if not r.get("has_sql") and r["status"] == "COMPLETED"]
    if sql_times_d and nosql_times_d:
        bp = ax6.boxplot([sql_times_d, nosql_times_d], tick_labels=["SQL", "No SQL"], patch_artist=True, showfliers=True)
        for patch, color in zip(bp["boxes"], ["#10b981", "#ef4444"]):
            patch.set_facecolor(color); patch.set_alpha(0.6)
        ax6.set_ylabel("Time (s)"); ax6.set_title("Latency by SQL Output", fontweight="bold")
    ax6.grid(True, alpha=0.2)

    # Panel 7: Stats table
    ax7 = axes[1, 2]
    ax7.axis("off")
    stats = [
        ("Min", f"{np.min(times):.2f}s"), ("Max", f"{np.max(times):.2f}s"),
        ("Median", f"{np.median(times):.2f}s"), ("Mean", f"{np.mean(times):.2f}s"),
        ("P90", f"{np.percentile(times, 90):.2f}s"), ("P95", f"{np.percentile(times, 95):.2f}s"),
        ("SQL Rate", f"{sql_rate:.1f}%"), ("Total Time", f"{elapsed/60:.1f}min"),
    ]
    table = ax7.table(cellText=stats, colLabels=["Metric", "Value"], cellLoc="left", loc="center", bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False); table.set_fontsize(10); table.scale(1.2, 1.8)
    for j in range(2):
        table[0, j].set_facecolor("#2563eb")
        table[0, j].set_text_props(color="white", fontweight="bold")
    for i in range(1, len(stats)):
        table[i, 0].set_facecolor("#f3f4f6")
    ax7.set_title("Summary Statistics", fontweight="bold", pad=20)

    # Panel 8: Percentiles
    ax8 = axes[1, 3]
    percentiles = [50, 75, 90, 95, 99, 100]
    pvals = [np.percentile(times, p) for p in percentiles]
    ax8.plot(percentiles, pvals, "o-", color="#2563eb", linewidth=2, markersize=8)
    ax8.fill_between(percentiles, pvals, alpha=0.2, color="#2563eb")
    for p, v in zip(percentiles, pvals):
        ax8.annotate(f"{v:.1f}s", (p, v), textcoords="offset points", xytext=(0, 8), fontsize=8, ha="center")
    ax8.set_xlabel("Percentile"); ax8.set_ylabel("Latency (s)")
    ax8.set_title("Latency Percentiles", fontweight="bold")
    ax8.set_xticks(percentiles); ax8.grid(True, alpha=0.2)

    plt.tight_layout(rect=[0, 0, 1, 0.92])
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Saved dashboard: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 generate_dbbench_plot.py <results_json_path> [output_png_path]")
        print("For multi-model comparison, see SKILL.md for inline template.")
        sys.exit(1)

    json_path = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else json_path.replace(".json", ".png")
    with open(json_path) as f:
        data = json.load(f)
    make_plot(data, output)