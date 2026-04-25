---
name: shboost-public-s3-cmd-plot
description: Plot a colour-magnitude diagram from the public SHBoost 2024 S3 parquet dataset using the notebook-backed access pattern and a REANA-friendly serial workflow.
author: Hermi (sorgenfresser)
---

## Purpose
Use the public SHBoost 2024 parquet dataset exactly the way shown in the reference notebook:
- S3 path: `s3://shboost2024/shboost_08july2024_pub.parq/*.parquet`
- endpoint: `https://s3.data.aip.de:9000`
- anonymous SSL access
- sample before plotting
- produce a CMD with `x=bprp0`, `y=mg0`, inverted y-axis, and log-scaled hexbin density

This skill is intended for both local runs and REANA serial workflows.

## Notebook reference
Reference notebook: `https://github.com/arm2arm/starhorse_db/blob/master/shboost2024_plot_cmd.ipynb`

Key pattern from the notebook:
```python
df = dd.read_parquet(
    "s3://shboost2024/shboost_08july2024_pub.parq/*.parquet",
    storage_options={
        'use_ssl': True,
        'anon': True,
        'client_kwargs': dict(endpoint_url='https://s3.data.aip.de:9000')
    }
)
```

The notebook reports about 217,974,770 rows and uses a 1% sample for plotting.

## Recommended memory
For CMD plotting with only the needed columns (`xg`, `yg`, `bprp0`, `mg0`) and a 1% sample:
- 32 GB RAM is the safe default and matches the user policy.
- This is more than enough for a few million sampled rows and plotting.

## Preferred plotting conventions
- Cache processed data locally as Parquet
- PNG output
- original axes: `x=bprp0`, `y=mg0`
- invert y-axis only
- number-density hexbin plot
- `gridsize=512`

## Minimal Python workflow
```python
import dask.dataframe as dd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LogNorm

S3_PARQUET_GLOB = "s3://shboost2024/shboost_08july2024_pub.parq/*.parquet"
STORAGE_OPTS = {
    "use_ssl": True,
    "anon": True,
    "client_kwargs": {"endpoint_url": "https://s3.data.aip.de:9000"},
}
REQUIRED_COLUMNS = ["xg", "yg", "bprp0", "mg0"]


ddf = dd.read_parquet(
    S3_PARQUET_GLOB,
    columns=REQUIRED_COLUMNS,
    storage_options=STORAGE_OPTS,
)

sampled = ddf.sample(frac=0.01, random_state=42).compute()
sel = (
    np.isfinite(sampled["xg"])
    & np.isfinite(sampled["yg"])
    & np.isfinite(sampled["bprp0"])
    & np.isfinite(sampled["mg0"])
    & (np.abs(sampled["xg"] + 8.2) < 10)
    & (np.abs(sampled["yg"]) < 10)
)
plot_df = sampled.loc[sel, ["bprp0", "mg0", "xg", "yg"]].copy()
plot_df.to_parquet("shboost_cache.parquet", index=False)

fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
hb = ax.hexbin(
    plot_df["bprp0"],
    plot_df["mg0"],
    gridsize=512,
    cmap="viridis",
    mincnt=1,
    norm=LogNorm(),
)
ax.invert_yaxis()
ax.set_xlabel("bprp0")
ax.set_ylabel("mg0")
cb = fig.colorbar(hb, ax=ax)
cb.set_label("Number density")
plt.tight_layout()
plt.savefig("shboost_cmd.png", dpi=300)
```

## REANA serial workflow template
Use an approved environment and valid serial syntax:
```yaml
inputs:
  files:
    - plot_shboost_remote_sample.py

workflow:
  type: serial
  specification:
    steps:
      - name: build-plot
        environment: gitlab-p4n.aip.de:5005/p4nreana/reana-env:py311-astro-ml.2891a60c
        kubernetes_memory_limit: "32Gi"
        kubernetes_job_timeout: 7200
        commands:
          - python3 plot_shboost_remote_sample.py --force-refresh --sample-frac 0.01
          - ls -lh shboost_cmd.png shboost_cache.parquet summary.json

outputs:
  files:
    - shboost_cmd.png
    - shboost_cache.parquet
    - summary.json
```

## Running with dockerized REANA client
Important: when using the Dockerized REANA client with a local workflow directory, mount the directory and set the container working directory to `/workspace`:
```bash
sg docker -c "docker run --rm -i \
  -w /workspace \
  -e REANA_SERVER_URL=$REANA_SERVER_URL \
  -e REANA_ACCESS_TOKEN=$REANA_ACCESS_TOKEN \
  -v $(pwd):/workspace \
  reanahub/reana-client:0.95.0-alpha.3 \
  run -w my-workflow"
```

## Common pitfalls
- Wrong S3 path: use `s3://shboost2024/shboost_08july2024_pub.parq/*.parquet`, not the older public-bucket glob.
- Missing endpoint URL: include `client_kwargs.endpoint_url=https://s3.data.aip.de:9000`.
- Missing columns: use `xg`, `yg`, `bprp0`, `mg0` from the notebook-backed dataset.
- REANA upload issues with Dockerized client: set `-w /workspace` inside the container.
- Old serial syntax warnings: use `kubernetes_memory_limit` and `kubernetes_job_timeout`, with outputs declared at top level.
