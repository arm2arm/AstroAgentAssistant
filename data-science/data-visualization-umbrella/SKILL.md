---
name: data-visualization-umbrella
description: Umbrella for large-data visualization, Datashader, Dask, Matplotlib patterns, and reproducible plotting workflows. Consolidates shboost, datashader, dask-large-parquet-joins, matplotlib-figs, and related plotting tips.
version: 1.0.0
author: Hermes Curator
license: MIT
---

# Data Visualization & Large-Data Plotting (Umbrella)

Purpose: centralize workflows and pitfalls for Datashader + Dask, large Parquet joins, CMD plotting, and animation pipelines. Reference session-specific scripts and templates under `references/` and `scripts`.

## SH26 dist50 EDA recipe (added Jun 13, 2026)
Use this subsection when producing quality diagnostics for SH26 dist50 (and SH21 comparisons). Key points and reproducible steps learned from recent sessions:

- Data locations and conventions
  - Typical SH26 cache path used here: /home/hermes/projects/SH26/data/sh26_cache_200k.parq/ (Parquet partitioned).
  - Standard image output dir: /home/hermes/projects/SH26/img/; create it if missing.

- Column discovery heuristics
  - Search for columns by lowercased keywords: 'dist50', 'dist50_sh21', 'dist50_err', 'parallax', 'phot_g'.
  - If 'dist5' is requested but missing, prefer using 'dist50' as the inner-region proxy after confirming with the user.

- Filtering and matching
  - Inner-most region: user asked for dist5<6; when no dist5 exists, use dist50 < 6 kpc (document the substitution explicitly in outputs).
  - Prefer in-place columns (dist50 and dist50_sh21 present in same row). If only separate catalogs exist, match by source_id or position with a small tolerance (0.5 arcsec) — see references/sh26_dist50_eda.md and scripts/eda_sh26.py for examples.

- Parallax handling
  - For quick checks, invert positive parallaxes: d_parallax_kpc = 1.0/(parallax_mas/1000.0). Only use this for parallax > 0 and high SNR. Document where inversion was used.
  - For robust comparisons, run a probabilistic parallax-to-distance method (Bailer-Jones or similar). Add this as an optional pipeline step.

- Recommended diagnostic plots (filenames used by convention)
  - dist50_histograms.png: linear + log histograms (clipped & full-range).
  - dist50_sh26_vs_sh21_full.png: hexbin comparison (full sample).
  - dist50_inner_dist50lt6_sh26_vs_sh21.png: inner-region hexbin (dist50 < 6 kpc).
  - residual_vs_distance_binned.png: residual (SH26-SH21) vs distance with binned medians.
  - residual_vs_gmag_binned.png and binned_median_residual_vs_gmag.png: residual vs G magnitude diagnostics.
  - residual_vs_parallax_snr.png: residual vs parallax SNR (log x-scale).
  - dist50_vs_parallax_distance.png: hexbin of parallax distance vs dist50.
  - sky_abs_resid_dist50.png: sky map (l,b) of median absolute residuals per tile.
  - cdf_abs_residuals.png: CDF of absolute residuals.
  - binned_bias_vs_distance.csv: numeric summary for downstream analysis.

- Plotting & style pitfalls
  - Colormap availability: some envs may not have aliases like 'mako'. Use standard Matplotlib colormaps (magma, inferno, viridis) for portability.
  - For density plots use LogNorm or hexbin(bins='log') to reveal structure across wide dynamic ranges.
  - Save figures at dpi=150 and include small stats textbox (median bias, std, N) on the plot.

- Automation & reproducibility
  - Provide a re-runnable script under scripts/eda_sh26.py (included in this skill's references) that performs column discovery, filtering, and generates the above plots.
  - When making substitutions (e.g., dist5 -> dist50), include an explicit note in saved figure filenames and in the JSON/text summary.

- When to patch this section
  - If a new canonical data path, column naming convention, or plotting filename scheme emerges, update this snippet. Keep the script in scripts/ up-to-date with any API or path changes.

Pointers:
- references/sh26_dist50_eda.md — session-specific notes, column lists, and assumptions.
- scripts/eda_sh26.py — runnable example to reproduce the plots and CSV summary.

