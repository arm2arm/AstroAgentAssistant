---
name: shboost24-cmd
description: Generate colour-magnitude diagrams from SHboost24 data using local Parquet caching and agreed plotting conventions.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [astronomy, shboost24, plotting, parquet, cmd]
    category: astronomy
    related_skills: [starhorse-access, data-aip-de-s3, cmd-plotting, reana-shboost24, s3-parquet-sampling, dask-hvplot-datashader-scientific-plots]
---

# SHboost24 CMD

## When to Use
Use this skill when generating CMD plots from SHboost24 parquet data, especially from S3-backed datasets with local Parquet caching.

## Procedure
1. Check whether a local cached Parquet subset already exists.
2. If the source data is huge, read and reduce it with **Dask** first.
3. Keep only the required columns before plotting.
4. Cache the working table locally as Parquet before repeated plotting.
5. Prefer `hvplot` for scientific interactive/clean plotting.
6. For dense or very large data, prefer **Dask + hvPlot + Datashader** (`rasterize=True` / `datashade=True`).
7. Preserve original axes and invert only the y-axis.
8. Save PNG only unless the user explicitly asks otherwise.

## Pitfalls
- Do not emit PDF by default.
- Do not transform axes unless explicitly requested.
- Avoid reading unnecessary columns from very large parquet datasets.
- Do not skip the local cache step for S3-derived data you will revisit.
- Do not force raw-point plotting for dense large catalogs when Datashader would communicate the structure better.

## Verification
- Output file exists and is PNG.
- The plot uses hexbin density.
- The y-axis is visually inverted only.
