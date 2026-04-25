---
name: dask-hvplot-datashader-scientific-plots
description: Build scalable scientific plots from large tabular datasets using Dask for processing, hvPlot for plotting, and Datashader for dense large-data rendering.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [python, dask, hvplot, datashader, plotting, visualization, large-data]
    related_skills: [dask-mcp-docs-first, pandas-datashader-mcp-docs-first, python-mcp-docs-first]
---

# Dask + hvPlot + Datashader Scientific Plots

Use this skill when a scientific plot must scale beyond comfortable eager pandas/matplotlib workflows, especially for large S3- or TAP-derived tabular datasets.

## Procedure
1. Start from a local cached tabular dataset.
2. Load with Dask when the working set is large.
3. Use hvPlot as the main plotting layer.
4. Use Datashader-backed rendering (`rasterize=True` or `datashade=True`) for dense plots.
5. Keep the pipeline reduction-first: prune columns, filter early, cache reduced results.
6. For huge datasets, keep Dask as the default processing engine and aim for an effective 32GB RAM footprint.

## Pitfalls
- Do not start plotting directly from remote S3/TAP sources without a local cache.
- Do not force raw scatter plots for dense tens-of-millions-row datasets.
- Do not eagerly convert large Dask frames to pandas just to plot them.
- **Datashader `tf.shade()` does NOT accept standard matplotlib colormaps** ('inferno', 'cividis', 'fire', 'plasma', 'magma', etc.) — it only accepts color lists like `['blue', 'red']` or colorcet strings with `::` prefix. If you need matplotlib colormaps + `LogNorm`, use datashader **only for aggregation** (`cvs.points()`) then render with `ax.imshow()` on the numpy array, which handles all standard colormaps.
- When filtering S3 Parquet data for CMDs, always clamp X/Y ranges (e.g. BP-RP −0.2→5.0, G −1→22) before computing canvas ranges — outliers will dominate the binning.

## Verification
- Data used for plotting comes from a local cached table.
- Dask remains the processing engine for large working sets.
- hvPlot is the primary plotting layer.
- Datashader-backed rendering is used when density or scale requires it.
