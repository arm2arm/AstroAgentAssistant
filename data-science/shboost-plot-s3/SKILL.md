---
name: shboost-plot-s3
description: Plot a sampled subset of the ShBoost 2024 star dataset stored on a public S3 bucket.
author: Hermes
version: 1.0
---

# Goal
Create a reusable script that reads the `shboost2024` Parquet files from the public S3 bucket, samples a configurable number of stars (e.g., ~100 000), and produces a scatter plot using seaborn/matplotlib.

## Prerequisites
- Python 3.8+
- Virtual environment (optional but recommended)
- Packages: `dask[dataframe]`, `s3fs`, `matplotlib`, `seaborn`, `pandas`

## Steps
1. **Create a virtual environment** (optional) and install dependencies:
   ```bash
   python3 -m venv ~/shboost-env
   source ~/shboost-env/bin/activate
   pip install --quiet dask[dataframe] s3fs matplotlib seaborn pandas
   ```
2. **Define S3 connection parameters** (the bucket is public, SSL‑enabled):
   ```python
   S3_ENDPOINT = "https://s3.data.aip.de:9000"
   storage_opts = {
       "use_ssl": True,
       "anon": True,
       "client_kwargs": {"endpoint_url": S3_ENDPOINT},
   }
   PARQUET_GLOB = "s3://shboost2024/shboost_08july2024_pub.parq/*.parquet"
   ```
3. **Lazy‑load the dataset with Dask** (no data transferred yet):
   ```python
   import dask.dataframe as dd
   df = dd.read_parquet(PARQUET_GLOB, storage_options=storage_opts)
   ```
4. **Determine the sampling fraction for the desired row count**:
   ```python
   TARGET_ROWS = 100_000  # modify as needed
   total_rows = df.shape[0].compute()
   sample_frac = min(TARGET_ROWS / total_rows, 1.0)
   print(f"Sampling {sample_frac:.6%} → ~{TARGET_ROWS:,} rows (dataset size {total_rows:,})")
   ```
   *Pitfall*: `total_rows` triggers a cheap metadata read; if the bucket were private you’d need credentials.
5. **Sample and materialise the data**:
   ```python
   df_sample = df.sample(frac=sample_frac, random_state=42).persist()
   sample_pd = df_sample.compute()
   print(f"Sampled {len(sample_pd):,} rows")
   ```
   *Tip*: `.persist()` keeps the sampled partitions in memory, speeding up later operations.
6. **Plot** (choose any two columns you want). Example uses `bprp0` vs `mg0`:
   ```python
   import matplotlib.pyplot as plt
   import seaborn as sns

   x_col, y_col = "bprp0", "mg0"
   plt.figure(figsize=(10, 6))
   sns.scatterplot(
       data=sample_pd,
       x=x_col,
       y=y_col,
       hue="xgb_inputflag",  # optional, remove if column missing
       palette="viridis",
       s=10,
       alpha=0.6,
       linewidth=0,
   )
   plt.title(f"ShBoost 2024 – {len(sample_pd):,} random stars")
   plt.xlabel(x_col)
   plt.ylabel(y_col)
   plt.tight_layout()
   plt.show()
   ```
   *Pitfall*: If the optional hue column does not exist, remove `hue=` argument to avoid a KeyError.

## Verification
- The script should print the total dataset size, the sampling fraction, and the exact number of sampled rows.
- A Matplotlib window (or inline figure in Jupyter) displays a scatter plot without errors.

## Common Issues & Fixes
| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `No module named 'dask'` | Packages not installed | Re‑run the `pip install` step inside your venv |
| `ClientError: 403 Forbidden` | Wrong endpoint or missing credentials (bucket is public, so ensure `anon=True` and correct endpoint) | Verify `S3_ENDPOINT` and `storage_opts` settings |
| `KeyError` for hue column | Column not present in sampled data | Remove the `hue=` argument or pick an existing column |
| MemoryError when sampling large fraction | Not enough RAM for the sample | Decrease `TARGET_ROWS` or increase swap/available memory |

## Extensibility
- Change `TARGET_ROWS` to any number (e.g., 1 000 000) – the script automatically recalculates the fraction.
- Swap `x_col` / `y_col` to visualise other parameters (e.g., `xgb_logteff`, `xgb_logg`).
- Export the figure with `plt.savefig('shboost_plot.png')` before `plt.show()` for offline usage.

---

**Usage**: Save the script as `shboost_plot.py`, make it executable, and run `./shboost_plot.py`.

**Author note**: This skill was distilled from an interactive troubleshooting session where the raw notebook was parsed, the sampling logic clarified, and a clean, end‑user‑friendly script was produced.
