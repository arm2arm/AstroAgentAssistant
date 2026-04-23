---
name: dask-hvplot-datashader-scientific-plots
description: Build scalable scientific plots from large tabular datasets using Dask for processing, hvPlot for plotting, and Datashader for dense large-data rendering.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [python, dask, hvplot, datashader, plotting, visualization, large-data]
    category: python
    related_skills: [dask-mcp-docs-first, pandas-datashader-mcp-docs-first, s3-parquet-sampling, shboost24-cmd]
---

# Dask + hvPlot + Datashader Scientific Plots

## When to Use
Use this skill when a scientific plot must scale beyond comfortable eager pandas/matplotlib workflows, especially for large S3- or TAP-derived tabular datasets.

## Procedure

### 1. Start from a local cached tabular dataset
If the source is S3 or TAP, reduce first and cache locally as Parquet.

### 2. Load with Dask when the working set is large
```python
import dask.dataframe as dd
import hvplot.dask  # noqa

ddf = dd.read_parquet('./cache/data.parquet')
```

### 3. Use hvPlot as the plotting layer
For moderate size:
```python
plot = ddf.hvplot.scatter(x='x', y='y', alpha=0.2)
```

### 4. Use Datashader-backed rendering for dense plots
Preferred options:
```python
plot = ddf.hvplot.scatter(x='x', y='y', rasterize=True, cnorm='eq_hist')
# or
plot = ddf.hvplot.scatter(x='x', y='y', datashade=True)
```

### 5. Keep the pipeline reduction-first
Before plotting:
- prune columns
- filter rows early
- cache reusable reduced results
- avoid eager `.compute()` unless needed for a small final product

### 6. Default performance stance
For huge datasets, keep Dask as the default processing engine and aim for an effective working footprint around **32GB RAM**.

### 7. Output choices
- use `hvplot` for nice scientific interactive plots
- use `rasterize=True` / `datashade=True` when density hides structure or raw plotting becomes slow
- export static outputs only after the plotting representation is settled

## Pitfalls
- Do not start plotting directly from remote S3/TAP sources without a local cache.
- Do not force raw scatter plots for dense tens-of-millions-row datasets.
- Do not eagerly convert large Dask frames to pandas just to plot them.
- Do not skip Datashader when overplotting makes the science unreadable.

## Verification
- Data used for plotting comes from a local cached table.
- Dask remains the processing engine for large working sets.
- hvPlot is the primary plotting layer.
- Datashader-backed rendering is used when density or scale requires it.
