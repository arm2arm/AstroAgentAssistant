---
name: data-aip-de-s3
description: Work with data.aip.de and S3-backed datasets using reproducible local caching, Dask-first reads for huge data, and plotting workflows that scale to large astronomy catalogs.
version: 1.1.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [astronomy, s3, parquet, hdf5, dataset, data-engineering, dask]
    category: astronomy
    related_skills: [shboost24-cmd, s3-parquet-sampling, hdf5-on-s3-cached, dask-hvplot-datashader-scientific-plots]
---

# data.aip.de S3 Access

## When to Use
Use this skill when accessing astronomy datasets on data.aip.de or S3-compatible endpoints, especially parquet-backed catalogs or large scientific files that should not be re-read repeatedly from the network.

## Procedure
1. Identify endpoint, bucket, prefix, authentication mode, and file format.
2. If the source data is from **S3 or TAP**, plan a **local cache** immediately.
3. Prefer column pruning before any large read.
4. For huge datasets, use **Dask first** and keep the default working footprint around **32GB RAM**.
5. Cache reusable subsets locally as **Parquet** whenever the result is tabular.
6. Prefer `hvplot` for scientific plots; for large data prefer **Dask + hvPlot**, and for very large density-style plots use **Dask + hvPlot + Datashader**.
7. Record exact paths, storage options, cache locations, and selected columns for reproducibility.

## Recommended access patterns

### Small / moderate parquet
- Read only required columns.
- Cache locally as a Parquet subset immediately.

### Huge parquet
- Use `dask.dataframe.read_parquet(...)`.
- Apply column pruning and filters early.
- Persist only after reducing the working set.
- Write the reduced result to a local Parquet cache.

### TAP-derived tables
- Query remotely with explicit column selection.
- Save the result locally as Parquet before downstream plotting or repeated analysis.

### HDF5 on S3
- Do not assume efficient random remote access.
- Prefer creating a local cached copy first.
- If you extract a tabular subset for repeated analysis, save that subset locally as Parquet.

## Pitfalls
- Avoid repeated full remote scans when a local cache is sufficient.
- Do not assume public/anonymous access without checking.
- Do not use pandas for multi-GB remote parquet when Dask is the appropriate default.
- Do not keep plotting directly from remote S3 objects if a stable local cache can be created first.

## Verification
- Endpoint and dataset path are recorded.
- Local cache location is explicit.
- Large jobs use Dask rather than eager pandas loads.
- Plotting path is explicit (`hvplot` / `hvplot+datashader` where appropriate).
