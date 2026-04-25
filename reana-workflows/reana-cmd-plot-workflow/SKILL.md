---
name: reana-cmd-plot-workflow
description: REANA workflow that caches a large S3 Parquet dataset and plots bprp0 vs mg0 as a hex‑bin PNG.
author: Hermi (sorgenfresser)
date: 2026-04-04
---

## Overview
This skill automates the creation of a self‑contained REANA workflow for the ShBoost 2024 star dataset. It:
1. Sets up a folder `reana_cmd` with `plot_cmd.py` and `reana.yaml`.
2. `plot_cmd.py` pulls the public `shboost2024` Parquet dataset from S3 (anonymous access), caches it locally, samples ~200 k rows, and generates a 512 × 512 hex‑bin PNG of **bprp0** vs **mg0** (y‑axis inverted).
3. `reana.yaml` runs the script in a Python 3.12‑Slim container, installs the needed Python packages, and declares `cmd.png` as the workflow output.
4. Provides the exact REANA‑client commands to create, start, monitor, and retrieve the PNG.

## Files
### `plot_cmd.py`
```python
#!/usr/bin/env python3
"""Self‑contained script for REANA that:
* Accesses the public `shboost2024` Parquet dataset on S3 (anon).
* Writes a minimal local cache (`shboost_cache.parquet`).
* Samples ~200 k rows for fast plotting.
* Produces a 512 × 512 hex‑bin density plot of bprp0 (x) vs mg0 (y) with y‑axis inverted.
* Saves the image as `cmd.png`.
"""

import pathlib
import dask.dataframe as dd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl

# ------------------------------------------------------------------
# 1️⃣  S3 configuration (public bucket → anonymous access)
# ------------------------------------------------------------------
S3_ENDPOINT = "https://s3.data.aip.de:9000"
S3_BUCKET   = "shboost2024"
S3_PREFIX   = "shboost_08july2024_pub.parq/"

STORAGE_OPTS = {
    "use_ssl": True,
    "anon": True,
    "client_kwargs": {"endpoint_url": S3_ENDPOINT},
}

# ------------------------------------------------------------------
# 2️⃣  Local cache location (kept in the REANA workspace)
# ------------------------------------------------------------------
CACHE_PATH = pathlib.Path("shboost_cache.parquet")

# ------------------------------------------------------------------
# 3️⃣  Load (or create) the cache
# ------------------------------------------------------------------
def get_dataframe() -> dd.DataFrame:
    """Return a Dask dataframe with only the columns needed for the plot."""
    if CACHE_PATH.is_file():
        print(f"🔄 Loading cached parquet from {CACHE_PATH}")
        df = dd.read_parquet(CACHE_PATH)
    else:
        s3_glob = f"s3://{S3_BUCKET}/{S3_PREFIX}*.parquet"
        print("⏬ Pulling metadata from S3 …")
        df = dd.read_parquet(s3_glob, storage_options=STORAGE_OPTS)
        df = df[["bprp0", "mg0"]]
        total = df.shape[0].compute()
        print(f"Dataset size: {total:,} rows – writing cache …")
        df.to_parquet(CACHE_PATH, write_index=False)
        print(f"✅ Cache written to {CACHE_PATH}")
    return df

# ------------------------------------------------------------------
# 4️⃣  Plot the CMD (hex‑bin, 512×512, y‑axis inverted)
# ------------------------------------------------------------------
def make_cmd(df: dd.DataFrame, out_png: str = "cmd.png"):
    target = 200_000  # rows to sample – adjust for higher fidelity
    total = df.shape[0].compute()
    frac = min(target / total, 1.0)
    print(f"Sampling {frac:.6%} → ~{min(target, total):,} rows")
    if frac < 1.0:
        df = df.sample(frac=frac, random_state=42)
    pdf = df.compute()

    sns.set_style("whitegrid")
    mpl.rcParams.update({
        "font.size": 12,
        "axes.titlesize": 14,
        "axes.labelsize": 13,
        "figure.figsize": (8, 6),
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
    })
    plt.figure()
    sns.hexbin(
        x=pdf["bprp0"],
        y=pdf["mg0"],
        gridsize=512,
        cmap="viridis",
        mincnt=1,
        linewidths=0.2,
        reduce_C_function="count",
    )
    plt.xlabel("bprp0")
    plt.ylabel("mg0")
    plt.title("ShBoost 2024 – bprp0 vs mg0 (≈200 k stars)")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(out_png, dpi=300)
    plt.close()
    print(f"✅ Plot saved → {out_png}")

if __name__ == "__main__":
    df = get_dataframe()
    make_cmd(df)
```

### `reana.yaml`
```yaml
workflow:
  type: serial
  specification:
    - name: plot
      type: run
      image: python:3.12-slim
      command: bash -c "pip install --quiet dask[dataframe] s3fs matplotlib seaborn pyarrow && python plot_cmd.py"
      compute_backend: generic
      resources:
        memory: 8gb
        runtime: 02:00:00
      env:
        S3_ENDPOINT: https://s3.data.aip.de:9000
        S3_BUCKET: shboost2024
        S3_PREFIX: shboost_08july2024_pub.parq/
      outputs:
        - cmd.png
```

## Execution Steps
```bash
# 1️⃣  Create the folder and copy in the files (once)
mkdir -p reana_cmd && cd reana_cmd
# (copy the two files shown above into this directory)

# 2️⃣  Activate the REANA virtualenv that ships the client
source /home/hermes/reana_venv/bin/activate

# 3️⃣  Export REANA connection details (replace the token if it changes)
export REANA_SERVER_URL="https://reana-dev.kube.aip.de"
export REANA_ACCESS_TOKEN="_PByOFmu-I4ScnfzK95AGg"

# 4️⃣  Pick a workflow name (avoid collisions)
WF="shboost_plot_$(date +%s)"

# 5️⃣  Create the workflow – some REANA‑client versions raise a cryptic error.
#     If that happens, you can safely ignore it and go straight to `start`.
reana-client create -w $WF -f reana.yaml || echo "⚠️ create failed – proceeding to start"

# 6️⃣  Start (or re‑start) the workflow
reana-client start -w $WF

# 7️⃣  Poll until the workflow finishes (adjust the sleep interval if you like)
while true; do
    STATUS=$(reana-client status -w $WF | awk '/status/ {print $2}')
    echo "Current status: $STATUS"
    if [[ "$STATUS" == "finished" ]]; then
        echo "✅ Workflow finished – downloading output"
        reana-client download -w $WF -o .
        break
    elif [[ "$STATUS" == "failed" || "$STATUS" == "stopped" ]]; then
        echo "⚠️ Workflow ended with status $STATUS"
        break
    else
        sleep 30
    fi
done
```

## Pitfalls & Tips
* **`reana-client create` bug** – older client releases sometimes error with *list indices must be integers or slices, not str*. The workaround is to ignore the error and go straight to `reana-client start`; the workflow will be created on‑the‑fly.
* **Environment variable `REANA_WORKON`** – if set to another workflow, `reana-client create` may refuse. Unset it (`unset REANA_WORKON`) before running the script.
* **Large dataset** – the first run downloads ~200 GB of Parquet data. Subsequent runs are fast because the cache (`shboost_cache.parquet`) is reused.
* **Memory** – the container is allocated 8 GB; this is ample for the 200 k row sample. Increase if you raise the sample size.
* **Token expiry** – the access token may expire; regenerate it via the REANA UI if you see authentication errors.
```
---
*Skill created by Hermi (sorgenfresser) on 2026‑04‑04.*