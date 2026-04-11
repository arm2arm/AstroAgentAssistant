---
name: data-aip-de-s3
description: Work with data.aip.de and S3-backed astronomy datasets using reproducible local caching patterns.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [astronomy, s3, parquet, dataset, data-engineering]
    category: astronomy
    related_skills: [shboost24-cmd, starhorse-access]
---

# data.aip.de S3 Access

## When to Use
Use this skill when accessing astronomy datasets on data.aip.de or S3-compatible endpoints, especially parquet-backed catalogs.

## Procedure
1. Identify endpoint, bucket, prefix, and authentication mode.
2. Prefer column pruning and sampling before full reads.
3. Cache reusable subsets locally as Parquet.
4. Record exact paths and storage options for reproducibility.

## Pitfalls
- Avoid repeated full remote scans when a local cache is sufficient.
- Do not assume public/anonymous access without checking.

## Verification
- Endpoint and dataset path are recorded.
- Local Parquet cache location is explicit.
