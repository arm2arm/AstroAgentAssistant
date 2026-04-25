---
name: shboost-cmd-plot
title: Plot CMD from shboost2024 S3 dataset with local Parquet cache
description: |
  Generates a colour‑magnitude diagram (CMD) for ~100 k stars from the public shboost2024 S3 bucket.
  The script caches the sampled data locally as a Parquet file for fast repeat runs and outputs a high‑resolution PNG (300 dpi).
requirements:
  - Python 3.12+ (or compatible)
  - dask[dataframe]
  - s3fs
  - pandas
  - matplotlib
  - seaborn
steps:
  - "Create an isolated virtual environment and install dependencies: `python3 -m venv ~/shboost-env && source ~/shboost-env/bin/activate && pip install --quiet dask[dataframe] s3fs pandas matplotlib seaborn`"
  - "Save the provided `shboost_plot_cached.py` script (full source below) to your working directory."
  - "Run the script: `~/shboost-env/bin/python shboost_plot_cached.py`. The first run downloads metadata, samples ~100 k rows, writes `shboost_cache.parquet`, and produces `shboost_cmd.png`."
  - "For a fresh sample, rerun with `--force-refresh`."
  - "Axis customisation is built‑in: x‑axis limits [-2, 6], y‑axis limits [6, -4] (inverted). Adjust the `plt.xlim`/`plt.ylim` lines in the script if needed."
---
```python
#!/usr/bin/env python3
"""
Paper‑ready CMD (colour‑magnitude diagram) for ~100 k stars from the shboost2024 S3 bucket.
The script caches the sampled data locally as Parquet for fast repeat runs.
It outputs a high‑resolution PNG (300 dpi) suitable for publications.
"""

import argparse
import os
import dask.dataframe as dd
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------------  Config --------------------------- #
S3_ENDPOINT = "https://s3.data.aip.de:9000"
S3_PARQUET_GLOB = "s3://shboost2024/shboost_08july2024_pub.parq/*.parquet"
STORAGE_OPTS = {
    "use_ssl": True,
    "anon": True,
    "client_kwargs": {"endpoint_url": S3_ENDPOINT},
}
CACHE_PATH = "shboost_cache.parquet"   # local parquet cache
TARGET_ROWS = 100_000                  # desired number of stars for the plot
# ------------------------------------------------------------- #

def load_or_fetch(force_refresh: bool) -> pd.DataFrame:
    """Return a pandas DataFrame with ~TARGET_ROWS rows.
    Uses a local Parquet cache if present, otherwise samples from S3 and writes the cache.
    """
    if os.path.isfile(CACHE_PATH) and not force_refresh:
        print(f"🔄 Loading cached data from {CACHE_PATH}")
        return pd.read_parquet(CACHE_PATH)

    # No cache or refresh requested: fetch from S3
    print("⏬ Reading metadata from S3 …")
    df = dd.read_parquet(S3_PARQUET_GLOB, storage_options=STORAGE_OPTS)
    total_rows = df.shape[0].compute()
    frac = min(TARGET_ROWS / total_rows, 1.0)
    print(f"Dataset size: {total_rows:,} rows")
    print(f"Sampling fraction: {frac:.6%} → ~{TARGET_ROWS:,} rows")

    sample = df.sample(frac=frac, random_state=42).persist()
    pdf = sample.compute()
    print(f"Sampled rows: {len(pdf):,}")

    print(f"💾 Writing cache to {CACHE_PATH}")
    pdf.to_parquet(CACHE_PATH, index=False)
    print("Cache saved.")
    return pdf


def plot_cmd(df: pd.DataFrame, png_path: str = "shboost_cmd.png"):
    """Create a paper‑ready CMD and save as a high‑resolution PNG (300 dpi)."""
    sns.set_style("whitegrid")
    plt.rcParams.update({
        "font.size": 12,
        "axes.titlesize": 14,
        "axes.labelsize": 13,
        "legend.fontsize": 11,
        "figure.figsize": (8, 6),
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
    })
    plt.figure()
    sns.scatterplot(
        data=df,
        x="mg0",   # swapped as requested
        y="bprp0",
        s=8,
        alpha=0.6,
        linewidth=0,
        edgecolor=None,
        color="#1b9e77",
    )
    plt.title("ShBoost 2024 Colour‑Magnitude Diagram (≈100 k stars)")
    plt.xlabel("mg0")
    plt.ylabel("bprp0")
    plt.xlim(-2, 6)   # user‑requested X range
    plt.ylim(6, -4)   # Y inverted as requested
    plt.tight_layout()
    plt.savefig(png_path, dpi=300)
    plt.close()
    print(f"✅ Saved PNG -> {png_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Ignore existing parquet cache and re‑sample from S3.",
    )
    args = parser.parse_args()
    df = load_or_fetch(force_refresh=args.force_refresh)
    plot_cmd(df)

if __name__ == "__main__":
    main()
```
