---
name: hdf5-on-s3-cached
description: Access HDF5 files stored on S3 by creating a reliable local cache first, extracting reusable subsets, and converting repeated tabular work products to local Parquet.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [python, hdf5, s3, caching, parquet, dask, data-engineering]
    category: python
    related_skills: [data-aip-de-s3, s3-parquet-sampling, dask-mcp-docs-first]
---

# HDF5 on S3 Cached

## When to Use
Use this skill when scientific data lives in HDF5 files on S3 or another object store and downstream analysis would be unreliable or inefficient if every access hit the remote object directly.

## Procedure

### 1. Treat remote HDF5 as a cache-first format
For S3-hosted HDF5, do not assume efficient random remote access by default. Prefer downloading or materializing a stable local cached copy first.

### 2. Create a local cached file
Example pattern:
```bash
mkdir -p ./cache
aws s3 cp s3://bucket/path/data.h5 ./cache/data.h5
```

### 3. Inspect the structure locally
Use `h5py` after the file is local:
```python
import h5py
with h5py.File('./cache/data.h5', 'r') as f:
    print(list(f.keys()))
```

### 4. Extract only the needed subset
Avoid loading the entire file eagerly if you only need one group or dataset.

### 5. If the extracted result is tabular, convert it to local Parquet
For repeated analysis or plotting, prefer a local Parquet cache:
```python
import pandas as pd

df = pd.DataFrame({...})
df.to_parquet('./cache/extracted_subset.parquet', index=False)
```

### 6. Use Dask when the extracted working set is large
If the extracted tabular subset is still large, switch to Dask for downstream processing and keep the effective working footprint near **32GB RAM**.

### 7. Plot from the local cached derivative, not the remote HDF5
Prefer plotting from:
- local Parquet cache
- Dask DataFrame derived from local cache
- `hvplot` / Datashader for dense large results

## Pitfalls
- Do not assume remote HDF5 behaves like cloud-native columnar parquet.
- Do not repeatedly reopen a large HDF5 object from S3 if a local cache can be made once.
- Do not skip conversion to Parquet when your repeated downstream work is tabular.
- Do not default to eager pandas if the extracted table is still large.

## Verification
- A local cached HDF5 file exists.
- Reused downstream work reads from the local cache, not directly from S3.
- Repeated tabular work uses a local Parquet derivative when appropriate.
