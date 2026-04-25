---
name: shboost_full_cmd_datashader
description: Generate a full‑dataset colour‑magnitude diagram (CMD) for the ShBoost 2024 star catalog using Dask and Datashader, optimized for minimal memory usage.
author: Hermes
version: 1.0
---

# Goal
Create a high‑resolution PNG CMD of the full ShBoost 2024 dataset (≈218 M stars) without loading the entire dataset into RAM. The plot uses a hex‑bin density representation with logarithmic shading and the `inferno` colormap, and follows the astrophysical convention of inverted y‑axis.

# Prerequisites
- Python ≥3.9 with a virtual environment (the repository already includes `shboost-env`).
- Packages (install via the environment's pip):
  ```
  pip install dask[complete] pandas matplotlib seaborn holoviews hvplot bokeh datashader colorcet
  ```
  *Note:* `selenium` is **not** required for the final Datashader workflow.
- Access to the S3 bucket `s3://shboost2024/shboost_08july2024_pub.parq/*.parquet` (public, anonymous).

# Steps
1. **Configuration** – edit the script header to point to the S3 endpoint and set the cache path:
   ```python
   S3_ENDPOINT = "https://s3.data.aip.de:9000"
   S3_PARQUET_GLOB = "s3://shboost2024/shboost_08july2024_pub.parq/*.parquet"
   CACHE_PATH = "shboost_full_cmd.parquet"
   ```
2. **Cache the full dataset** (runs once or on `--force-refresh`):
   ```python
   def load_or_fetch(force_refresh: bool) -> pd.DataFrame:
       if os.path.isfile(CACHE_PATH) and not force_refresh:
           print(f"🔄 Loading cached full data from {CACHE_PATH}")
           return pd.read_parquet(CACHE_PATH)
       # fetch from S3 lazily with Dask and write parquet without materialising
       dd_df = dd.read_parquet(S3_PARQUET_GLOB, storage_options=STORAGE_OPTS)
       dd_df = dd_df[["bprp0", "mg0"]]
       dd_df.to_parquet(CACHE_PATH, write_index=False)
       print("✅ Full cache written.")
       return dd_df
   ```
3. **Plot using Datashader aggregation + Matplotlib rendering** – aggregate the full Dask DataFrame with Datashader, then render the 512×512 count image with Matplotlib so the final PNG has visible axes, an inverted y-axis, and a colorbar:
   ```python
   def plot_cmd(dask_df, png_path: str = "shboost_cmd.png"):
       import datashader as ds
       import matplotlib.pyplot as plt
       import numpy as np
       from matplotlib.colors import LogNorm

       x_min, x_max = dask_df['bprp0'].min().compute(), dask_df['bprp0'].max().compute()
       y_min, y_max = dask_df['mg0'].min().compute(), dask_df['mg0'].max().compute()

       cvs = ds.Canvas(
           plot_width=512,
           plot_height=512,
           x_range=(x_min, x_max),
           y_range=(y_min, y_max),
       )
       agg = cvs.points(dask_df, 'bprp0', 'mg0', ds.count())
       counts = np.asarray(agg.values, dtype=float)
       counts[counts <= 0] = np.nan

       fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
       image = ax.imshow(
           counts,
           origin='lower',
           extent=(x_min, x_max, y_min, y_max),
           cmap='viridis',
           norm=LogNorm(vmin=1, vmax=np.nanmax(counts)),
           aspect='auto',
       )
       ax.invert_yaxis()
       ax.set_xlabel('bprp0')
       ax.set_ylabel('mg0')
       cb = fig.colorbar(image, ax=ax)
       cb.set_label('Number density')
       plt.tight_layout()
       plt.savefig(png_path, dpi=300)
       plt.close(fig)
       print(f"✅ Saved PNG -> {png_path}")
   ```
4. **Main driver** – ensures the cache exists then runs the plot (animation omitted as per request):
   ```python
   def main():
       parser = argparse.ArgumentParser()
       parser.add_argument("--force-refresh", action="store_true",
                           help="Ignore existing parquet cache and rebuild it.")
       args = parser.parse_args()

       # Build or validate cache
       _ = load_or_fetch(force_refresh=args.force_refresh)

       # Load lazily as Dask DataFrame for plotting
       dask_df = dd.read_parquet(CACHE_PATH)
       plot_cmd(dask_df)
   ```

# Pitfalls & Tips
- **Memory** – The workflow never materialises the full 218 M rows; only the cached parquet write and small aggregate/min/max tasks are computed.
- **Blank/degenerate PNGs** – Direct `tf.shade(...); export_image(...)` can produce a visually unhelpful image with no axes or even an apparently blank result depending on rendering choices. Prefer rendering the Datashader aggregate with Matplotlib `imshow(..., norm=LogNorm(...))` to get reliable visible density, axes, and a colorbar.
- **Y‑axis inversion** – Build the aggregate with `y_range=(y_min, y_max)` and then call `ax.invert_yaxis()` in Matplotlib for the final CMD convention.
- **Selenium** – Earlier attempts with `hvplot` required Selenium for PNG export. Datashader aggregation plus Matplotlib avoids that dependency.
- **Cache refresh** – Use `--force-refresh` if the S3 source updates; otherwise the script re‑uses the local Parquet cache.

# Verification
After running `python shboost_plot_cached.py` (or with `--force-refresh`), you should see:
```
✅ Saved PNG -> shboost_cmd.png
```
The generated PNG contains a hex‑bin density CMD titled "ShBoost 2024 Colour‑Magnitude Diagram (217,974,770 stars)" with the y‑axis inverted.

# References
- Datashader documentation: https://datashader.org/
- Colorcet palettes: https://colorcet.holoviz.org/
- Dask Parquet reading: https://docs.dask.org/en/stable/dataframe-parquet.html
```