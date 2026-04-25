---
name: reana-serial-python-analysis-template
description: Reusable template for REANA serial workflows that run a Python analysis script on remote data, cache processed results locally as Parquet, and produce PNG outputs. Designed for SHBoost-like analyses where only the script, selected columns, and output names change.
author: Hermi (sorgenfresser)
---

## Purpose
Use this template whenever the analysis pattern is the same:
- one Python script does the analysis
- data are read remotely at runtime (for example from S3)
- only selected columns or filtering logic change
- processed/sample data are cached locally as Parquet
- final outputs are PNG and optional JSON summaries
- execution happens in a REANA serial workflow

This template is intentionally generic so it can be reused for CMDs, alternative column projections, density plots, selections, and similar analyses.

## Key rules
1. Use `reana-client run -w <workflow-name>` whenever possible.
2. If using the Dockerized REANA client, always mount the local workflow directory and set the container working directory to `/workspace`.
3. Keep all edits in the same project folder and rerun from there.
4. Use an approved REANA environment only.
5. Default memory is 32 GB.
6. Cache processed data locally as Parquet.
7. Prefer PNG outputs.

## Project layout
Example local project directory:
```text
my_analysis/
  reana.yaml
  analysis.py
```

## Generic Python script template
Replace placeholders such as S3 path, selected columns, filters, and plot logic:
```python
import argparse
import json
import os

import dask.dataframe as dd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LogNorm

S3_PARQUET_GLOB = "s3://YOUR-BUCKET/YOUR-PREFIX/*.parquet"
STORAGE_OPTS = {
    "use_ssl": True,
    "anon": True,
    "client_kwargs": {"endpoint_url": "https://YOUR-ENDPOINT"},
}
REQUIRED_COLUMNS = ["col_x", "col_y"]
CACHE_PATH = "analysis_cache.parquet"
PNG_PATH = "plot.png"
SUMMARY_PATH = "summary.json"
DEFAULT_SAMPLE_FRAC = 0.01


def build_selection_mask(df: pd.DataFrame) -> pd.Series:
    return np.isfinite(df["col_x"]) & np.isfinite(df["col_y"])


def load_or_fetch(sample_frac: float, force_refresh: bool = False) -> pd.DataFrame:
    if os.path.exists(CACHE_PATH) and not force_refresh:
        return pd.read_parquet(CACHE_PATH)

    ddf = dd.read_parquet(
        S3_PARQUET_GLOB,
        columns=REQUIRED_COLUMNS,
        storage_options=STORAGE_OPTS,
    )
    sampled_df = ddf.sample(frac=sample_frac, random_state=42).compute()
    selected_df = sampled_df.loc[build_selection_mask(sampled_df), REQUIRED_COLUMNS].copy()
    if selected_df.empty:
        raise RuntimeError("Selected dataframe is empty after filtering.")
    selected_df.to_parquet(CACHE_PATH, index=False)
    return selected_df


def make_plot(df: pd.DataFrame, png_path: str = PNG_PATH) -> str:
    fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
    hb = ax.hexbin(
        df["col_x"],
        df["col_y"],
        gridsize=512,
        cmap="viridis",
        mincnt=1,
        norm=LogNorm(),
    )
    ax.set_xlabel("col_x")
    ax.set_ylabel("col_y")
    cb = fig.colorbar(hb, ax=ax)
    cb.set_label("Number density")
    plt.tight_layout()
    plt.savefig(png_path, dpi=300)
    plt.close(fig)
    return png_path


def write_summary(df: pd.DataFrame, sample_frac: float, path: str = SUMMARY_PATH) -> str:
    summary = {
        "sample_fraction": sample_frac,
        "selected_rows": int(len(df)),
        "columns": list(df.columns),
        "outputs": {"png": PNG_PATH, "cache": CACHE_PATH},
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force-refresh", action="store_true")
    parser.add_argument("--sample-frac", type=float, default=DEFAULT_SAMPLE_FRAC)
    args = parser.parse_args()
    if not (0 < args.sample_frac <= 1.0):
        raise ValueError("--sample-frac must be in the interval (0, 1].")
    df = load_or_fetch(sample_frac=args.sample_frac, force_refresh=args.force_refresh)
    make_plot(df)
    write_summary(df, args.sample_frac)


if __name__ == "__main__":
    main()
```

## Generic REANA workflow template
```yaml
inputs:
  files:
    - analysis.py

workflow:
  type: serial
  specification:
    steps:
      - name: run-analysis
        environment: gitlab-p4n.aip.de:5005/p4nreana/reana-env:py311-astro-ml.2891a60c
        kubernetes_memory_limit: "32Gi"
        kubernetes_job_timeout: 7200
        commands:
          - python3 analysis.py --force-refresh --sample-frac 0.01
          - ls -lh plot.png analysis_cache.parquet summary.json

outputs:
  files:
    - plot.png
    - analysis_cache.parquet
    - summary.json
```

## How to adapt it
For a new analysis, usually only these parts change:
- `S3_PARQUET_GLOB`
- `STORAGE_OPTS`
- `REQUIRED_COLUMNS`
- `build_selection_mask()`
- `make_plot()`
- output filenames in both the Python script and `reana.yaml`
- CLI options if needed

Examples:
- CMD: `col_x=bprp0`, `col_y=mg0`, invert y-axis
- Galactic map: `col_x=xg`, `col_y=yg`
- Alternative density plot: swap in other astrophysical parameters

## Dockerized REANA client pattern
Run from inside the project directory:
```bash
export REANA_SERVER_URL="https://reana-dev.kube.aip.de"
export REANA_ACCESS_TOKEN="<token>"
sg docker -c "docker run -i --rm \
  -w /workspace \
  -e REANA_SERVER_URL=$REANA_SERVER_URL \
  -e REANA_ACCESS_TOKEN=$REANA_ACCESS_TOKEN \
  -v $(pwd):/workspace \
  reanahub/reana-client:0.95.0-alpha.3 \
  run -w my_analysis"
```

## Critical pitfall
If you forget `-w /workspace` on the Docker container, `reana-client run` may upload `reana.yaml` but fail to upload or resolve the analysis script correctly.

## SHBoost-specific note
For the public SHBoost 2024 dataset, use the notebook-backed access pattern:
- S3 path: `s3://shboost2024/shboost_08july2024_pub.parq/*.parquet`
- endpoint: `https://s3.data.aip.de:9000`
- anonymous SSL access

## When to use this skill
Use this for any similar REANA workflow where the structure is unchanged and only:
- the selected columns differ
- the filter differs
- the plotting logic differs
- the output names differ
