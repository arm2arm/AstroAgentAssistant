---
name: hdf5-on-s3-cached
description: Access HDF5 files stored on S3 by creating a reliable local cache first, extracting reusable subsets, and converting repeated tabular work products to local Parquet.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [python, hdf5, s3, caching, parquet, dask, data-engineering]
    related_skills: [python-mcp-docs-first, dask-mcp-docs-first]
---

# HDF5 on S3 Cached

Use this skill when scientific data lives in HDF5 files on S3 or another object store and downstream analysis would be inefficient if every access hit the remote object directly.

## Procedure
1. Treat remote HDF5 as cache-first rather than cloud-native columnar storage.
2. Create a stable local cached copy of the HDF5 file.
3. Inspect the file structure locally with `h5py`.
4. Extract only the needed subsets.
5. If the extracted result is tabular, convert it to local Parquet for repeated analysis.
6. If the extracted working set is still large, switch to Dask and keep the effective footprint near 32GB RAM.
7. Plot from the local cached derivative, preferring hvPlot and Datashader for dense large results.

## Pitfalls
- Do not assume efficient random remote HDF5 access by default.
- Do not repeatedly reopen large HDF5 objects from S3 if a local cache can be made once.
- Do not skip conversion to Parquet when repeated downstream work is tabular.

## Verification
- A local cached HDF5 file exists.
- Reused downstream work reads from the local cache, not directly from S3.
- Repeated tabular work uses a local Parquet derivative when appropriate.
