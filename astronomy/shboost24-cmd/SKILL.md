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
    related_skills: [starhorse-access, data-aip-de-s3, cmd-plotting, reana-shboost24]
---

# SHboost24 CMD

## When to Use
Use this skill when generating CMD plots from SHboost24 parquet data, especially from S3-backed datasets with local Parquet caching.

## Procedure
1. Check whether a local cached Parquet subset already exists.
2. Keep only the required columns before plotting.
3. Generate a hexbin number-density CMD on a 512x512 grid.
4. Preserve original axes and invert only the y-axis.
5. Save PNG only unless the user explicitly asks otherwise.

## Pitfalls
- Do not emit PDF by default.
- Do not transform axes unless explicitly requested.
- Avoid reading unnecessary columns from very large parquet datasets.

## Verification
- Output file exists and is PNG.
- The plot uses hexbin density.
- The y-axis is visually inverted only.
