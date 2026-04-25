---
name: shboost-cmd-visualization
title: ShBoost CMD Visualization and Animation
description: >-
  Generate a high‑resolution density CMD (hexbin) from the ShBoost star dataset, cache locally as Parquet, add colour‑matched population annotations, a detailed legend, log‑scaled colour bar, and create a GIF animation cycling through population labels.
author: Hermes
date: 2026-04-04
---

## Overview

**Note:** This skill has been updated to include an alternative Datashader‑based pipeline for very large datasets (hundreds of millions of rows) and a `--test-sample` CLI flag to quickly generate a plot from ~200 k stars for testing. The Datashader route provides fast rendering with a dark background and log‑scaled density, while the original Matplotlib hexbin implementation remains available for smaller samples.

---
## Overview
This skill loads a large S3 Parquet dataset (or a cached local copy), samples a configurable number of stars, and produces:
1. A static PNG CMD with a 512×512 hexbin density map, log‑scaled colour bar, and clearly placed, colour‑matched population annotations.
2. A GIF animation that highlights each stellar population in turn with a red arrow.

The workflow works for datasets up to tens of millions of rows and yields publication‑ready figures.

## Prerequisites
- Python 3.12+ with `pandas`, `dask[dataframe]`, `numpy`, `matplotlib`, `seaborn` installed.
- Access to the S3 bucket containing the ShBoost Parquet files (configure `STORAGE_OPTS`).
- `ffmpeg` optional; the GIF is saved using PillowWriter which needs no external encoder.

## Files
- `shboost_plot_cached.py` – the main script.
- `shboost_cache.parquet` – local cache of the sampled dataset (created automatically).

## Parameters (edit at the top of the script)
```python
TARGET_ROWS = 50_000_000   # change to desired sample size
S3_PARQUET_GLOB = "s3://my-bucket/shboost/*.parquet"
STORAGE_OPTS = {"anon": True}  # adjust credentials as needed
```

## Step‑by‑Step Procedure
1. **Create the script** – copy the content below into `shboost_plot_cached.py`.
2. **Install dependencies** (if not already present):
   ```bash
   python -m venv shboost-env && source shboost-env/bin/activate
   pip install pandas dask[complete] numpy matplotlib seaborn
   ```
3. **Run the script** (optionally force a fresh sample):
   ```bash
   ./shboost-env/bin/python shboost_plot_cached.py          # uses cached Parquet if present
   ./shboost-env/bin/python shboost_plot_cached.py --force-refresh  # re‑samples from S3
   ```
   The script will:
   - Load or fetch a Parquet sample (`load_or_fetch`).
   - Plot the CMD with a hexbin (`mesh = plt.hexbin(..., norm=LogNorm())`).
   - Apply a log‑scaled colour bar.
   - Add colour‑matched annotations via a helper `add_label` that uses arrows and offsets to avoid overlap.
   - Create a legend with marker colours matching the annotation text.
   - Save `shboost_cmd.png`.
   - Call `create_animation(df)` to produce `shboost_population_animation.gif`.
4. **Inspect outputs** – the PNG and GIF will be in the same directory.

## Important Implementation Details

**REANA tip:** When running this script as part of a REANA workflow, make sure the Python file is listed under `inputs.files` in `reana.yaml` so it gets shipped to the compute backend. Example snippet:
```yaml
inputs:
  files:
    - shboost_plot_cached.py
```

- **Caching**: Checks for `shboost_cache.parquet`; if missing or `--force-refresh` is used, samples `TARGET_ROWS` from S3 and writes the cache.
- **Hexbin Normalisation**: `LogNorm()` makes low‑density regions visible.
- **Annotation Colours**: A `color_map` dictionary ties each population name to a Matplotlib tab colour, guaranteeing text colour matches the legend marker.
- **Optimised Placement**: `add_label` uses fixed offsets (`xy` + `offset`) chosen to stay clear of dense regions, reducing overlap.
- **Animation**:
  - Uses `matplotlib.animation.FuncAnimation`.
  - Re‑uses a single `Annotation` object; only its text, position, and colour are updated each frame.
  - Saved as a GIF via `PillowWriter` (no ffmpeg required).
  - `save_count=len(populations)` guarantees all frames are written.

## Pitfalls & Troubleshooting
- **`png_path` Scope**: Ensure the `png_path` variable is defined in the outer scope (default `"shboost_cmd.png"`). The animation function receives it as a default argument.
- **Arrow Colour**: Arrowprops must be set on the Annotation at creation; later frames only need to update the text and colour.
- **Blitting**: `blit=False` is required for full annotation updates; using `blit=True` caused missing arrows.
- **Large Datasets**: For >50 M rows you may need to increase VM memory or lower `TARGET_ROWS`.
- **Missing `ffmpeg`**: The original MP4 saving raised errors; the skill now forces GIF output with PillowWriter.

## Verification
After running the script you should have two files:
- `shboost_cmd.png` – static CMD with clear legends and annotations.
- **Large Datasets**: For >50 M rows you may need to increase VM memory or lower `TARGET_ROWS`.
- **Missing `ffmpeg`**: The original MP4 saving raised errors; the skill now forces GIF output with PillowWriter.
- **Local S3 latency**: Fetching ~218 M rows from S3 locally takes very long. Use a sampling flag (`SAMPLE_FRAC = 0.01`) for local development; disable it for production REANA runs where the full dataset is fully parallelizable.

## Toggleable Stellar Population Cuts

For isolating specific stellar populations, define an `apply_cuts(df)` function that chains boolean masks on `mg0` (G magnitude) and `bprp0` (BP−RP colour):

```python
def apply_cuts(df):
    mask = pd.Series(True, index=df.index)
    if cut_main_sequence:
        mask &= (df['mg0'] >= -3) & (df['mg0'] <= 12) & (df['bprp0'] >= 0.2) & (df['bprp0'] <= 2.5)
    if cut_giant_branch:
        mask &= (df['mg0'] >= -3) & (df['mg0'] <= 5) & (df['bprp0'] >= 0.5) & (df['bprp0'] <= 4.0)
    if cut_red_giants:
        mask &= (df['mg0'] >= -2) & (df['mg0'] <= 6) & (df['bprp0'] >= 0.8) & (df['bprp0'] <= 3.5)
    if cut_blue_stragglers:
        mask &= (df['mg0'] >= -1) & (df['mg0'] <= 9) & (df['bprp0'] >= -0.1) & (df['bprp0'] <= 0.6)
    if cut_white_dwarfs:
        mask &= (df['mg0'] >= 5) & (df['mg0'] <= 16) & (df['bprp0'] >= -0.3) & (df['bprp0'] <= 0.8)
    if cut_horizonal_branch:
        mask &= (df['mg0'] >= -2) & (df['mg0'] <= 3) & (df['bprp0'] >= -0.1) & (df['bprp0'] <= 0.6)
    return df[mask]
```

Set the `cut_*` booleans at the top of the script to enable/disable each filter. Multiple cuts can be combined — all enabled masks chain together (AND logic).

## Future Enhancements (optional)
- Add CLI flags to select specific populations for animation.
- Export the animation as MP4 when ffmpeg is available.
- Parameterise colour maps or hexbin grid size.
- Enable interactive Jupyter output.

---