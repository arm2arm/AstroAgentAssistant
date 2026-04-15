---
name: s3-parquet-sampling
description: Efficiently sample a subset of a massive Parquet dataset stored on an S3-compatible bucket, cache the sampled rows locally as a Parquet file for fast reuse, and produce high-resolution PNG plots suitable for analysis and publication.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [python, parquet, s3, sampling, plotting, matplotlib, data-science]
    category: python
    related_skills: [cmd-plotting, reana-serial-python, shboost24-cmd]
---

# S3 Parquet Sampling and Plotting

## When to Use
Use this skill when working with a large Parquet dataset (billions of rows) on S3 where loading the full dataset is impractical. Sample a subset, cache it locally as Parquet for fast reuse, and generate high-resolution PNG plots.

## Procedure

### 1. Sample from S3
```python
import pyarrow.parquet as pq
import pyarrow.compute as pc

# Open dataset without loading all data
dataset = pq.ParquetDataset('s3://bucket/path/to/data/')

# Sample N rows (e.g., 100_000)
sample_size = 100_000
total_estimate = sum(r.num_rows for r in dataset.files)
sample_fraction = sample_size / max(total_estimate, 1)

# Filter to ~sample_fraction of files
import random
sampled_files = random.sample(dataset.files, max(1, int(len(dataset.files) * sample_fraction)))

table = pq.concat_tables(pq.ParquetDataset(f).read() for f in sampled_files)
df = table.to_pandas()
```

### 2. Cache locally as Parquet
```python
import pandas as pd
df.to_parquet('/tmp/sample_cache.parquet', index=False)
print(f"Cached {len(df)} rows, {df.memory_usage(deep=True).sum() / 1e6:.1f} MB")
```

### 3. Load from cache (fast reuse)
```python
import pandas as pd
df = pd.read_parquet('/tmp/sample_cache.parquet')
```

### 4. Plot (hexbin density)
```python
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, seaborn as sns

sns.set_style('whitegrid')
fig, ax = plt.subplots(figsize=(10, 6))

hb = ax.hexbin(df['x'], df['y'], gridsize=50, cmap='plasma', mincnt=1)
ax.set_xlabel('x')
ax.set_ylabel('y')
fig.colorbar(hb, ax=ax).set_label('Count')
fig.tight_layout()
fig.savefig('/tmp/plot.png', dpi=300)
```

## S3 Access Patterns

| Pattern | Code |
|---|---|
| With credentials | `pq.ParquetDataset('s3://bucket/path/', filesystem=pyarrow.fs.S3FileSystem(access_key='...', secret_key='...'))` |
| Public bucket | `pq.ParquetDataset('s3://bucket/path/')` |
| Via s5cmd | `!s5cmd cp s3://bucket/path/file.parquet /tmp/` |

## Pitfalls
- Do NOT load the full Parquet dataset into memory — always sample first.
- Do NOT save more columns than needed — use `df[['col_a', 'col_b']]` to drop unused columns before saving.
- Do NOT use PDF by default — PNG only unless explicitly requested.
- Parquet memory footprint: `df.memory_usage(deep=True).sum()` — ensure it fits in available RAM.
- When sampling across multiple Parquet files, random.sample distributes across files, not rows within files.

## Verification
- Cached Parquet file exists and has non-zero size.
- Plot is PNG format.
- Data shape matches the sampled subset (not all data).
- Figure is readable with appropriate axis labels and colorbar.