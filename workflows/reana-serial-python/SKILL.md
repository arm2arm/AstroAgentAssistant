---
name: reana-serial-python
description: Reusable template for REANA serial workflows that run a Python analysis script on remote data, cache processed results locally as Parquet, and produce PNG outputs. Designed for SHBoost-like analyses where only the script, selected columns, and output names change.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [reana, workflow, serial, python, parquet, analysis, reproducibility]
    category: workflows
    related_skills: [reana-aip, reana-shboost24, s3-parquet-sampling, cmd-plotting]
---

# REANA Serial Python Analysis Template

## When to Use
Use this skill when creating a REANA workflow that: (1) reads remote data (S3, HTTP, TAP), (2) processes it in Python, (3) caches intermediate results as Parquet, and (4) produces PNG outputs. All AIP REANA workflows use this pattern.

## Procedure

### 1. Create a dedicated workflow directory
```bash
mkdir -p workflows/my-analysis && cd workflows/my-analysis
```

### 2. Write `reana.yaml`
```yaml
version: 0.9.0
inputs:
  - name: script
    path: script.py
outputs:
  - name: plot
    path: output.png
  - name: cache
    path: cache.parquet
command: python3 script.py
environment: docker://gitlab-p4n.aip.de/punch_public/reana/environments/conda_python312:latest
resources:
  memory: 32G
```

### 3. Write `script.py`
```python
import pandas as pd, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

# 1. Load / fetch remote data (or use cached Parquet)
df = pd.read_parquet('cache.parquet')  # if cached
# OR fetch from remote:
# import pyarrow.parquet as pq
# dataset = pq.ParquetDataset('s3://bucket/path/')
# df = dataset.read().to_pandas()

# 2. Analysis / plotting
fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(df['column'], bins=50)
fig.savefig('output.png')
df[['col_a', 'col_b']].to_parquet('cache.parquet', index=False)
```

### 4. Run via reana-client
```bash
reana-client run -w my-analysis
# or via Docker:
docker run -it --rm \
  -v $(pwd):/workdir \
  -w /workdir \
  ghcr.io/reana/reana-client:latest \
  run -w my-analysis
```

### 5. Monitor
```bash
reana-client status -w my-analysis
reana-client download -w my-analysis
```

## AIP Conventions
- Use approved environments from `https://gitlab-p4n.aip.de/punch_public/reana/environments`.
- Set memory to 32GB unless explicitly overridden.
- Include all Python scripts as workflow inputs (do not inline scripts in `reana.yaml`).
- Prefer `reana-client run -w <name>` over `reana-client upload + start`.

## Common Remote Data Patterns

| Source | Library | Example |
|---|---|---|
| S3 bucket | `pyarrow` | `pq.ParquetDataset('s3://bucket/path/')` |
| TAP service | `pyvo` | `tap.run_sync("SELECT ...")` |
| HTTP URL | `pandas` | `pd.read_csv('https://...')` |

## Pitfalls
- Do NOT invent custom environments — use only AIP-approved ones.
- Do NOT omit scripts from workflow inputs — they must be referenced in `inputs:`.
- Do NOT set memory below 8GB for large-parquet workflows — parquet loading is memory-intensive.
- Do NOT use `reana-client upload` alone — prefer `run` which handles context correctly.

## Verification
- `reana.yaml` references an approved environment.
- `reana-client status -w <name>` reaches `succeeded`.
- Output files exist and are PNG (unless PDF explicitly requested).
- Cached Parquet is saved in the workflow directory.