---
name: astronomy-analysis-project
description: Build reproducible Parquet astronomy analysis projects.
category: data-science
---

# Astronomy Analysis Project Scaffolding

Class-level guide for building a reproducible astronomy data analysis project: Parquet catalog I/O, quality cuts, reusable plotting functions, and thin Jupyter frontends — matching the StarHORSE / SHBoost analysis workflow.

## When to Use

- New stellar astronomy dataset (Gaia, APOGEE, SH26, etc.) arriving as Parquet
- Need to reproduce a paper's figure set from an older dataset
- Multi-collaborator project requiring reproducibility and HPC support

## Project Structure

```
project/
├── config/storage.yaml          # Backend config (local/S3)
├── pyproject.toml
├── requirements.txt
├── README.md
├── .gitignore
├── src/<pkg>/
│   ├── __init__.py
│   ├── dataio.py               # Parquet reader, column selection, filters
│   ├── analysis.py             # Quality cuts, derived columns, stats
│   └── plots.py                # Figure functions (one per plot family)
├── notebooks/                   # Thin Jupyter frontends (one per figure)
├── paper/figures/               # Generated PNG+PDF+metadata
├── results/                     # CSV summary tables
└── logs/
```

## Step 1: Config

`config/storage.yaml`:

```yaml
storage:
  backend: local  # "local" | "s3"
  local:
    base_path: "/path/to/parquet_dataset/"
  s3:
    endpoint: ""
    bucket: ""
    region: "us-east-1"
    path_prefix: "dataset/"
  dataset:
    layer: "silver"
```

Switch backends by changing `backend` only — all code reads from config.

## Step 2: Data Access Layer (`dataio.py`)

Use `pyarrow.parquet.read_table()` with `columns` and `filters` params.
Support both single file and directory-style partitioned dataset.

```python
import pyarrow.parquet as pq

def load_catalog(columns=None, config_path="config/storage.yaml"):
    config = yaml.safe_load(open(config_path))
    path = config["storage"]["local"]["base_path"]
    if config["storage"]["backend"] == "s3":
        path = f"s3://{config['storage']['s3']['bucket']}/{config['storage']['s3']['path_prefix']}"
    table = pq.read_table(path, columns=columns, filters=None)
    return table.to_pandas()
```

## Step 3: Analysis Functions (`analysis.py`)

Define quality cuts as filter functions:

```python
def filter_quality_cuts(df, config_path="config/storage.yaml"):
    mask = pd.Series(True, index=df.index)
    if "ruwe" in df.columns:
        mask &= df["ruwe"].notna() & (df["ruwe"] <= 1.4)
    # parallax SNR, distance range, etc.
    return df[mask]
```

Derived columns (colors, absolute magnitude, uncertainties):

```python
def compute_derived_columns(df):
    result = df.copy()
    result["g_bp_rp"] = df["phot_bp_mean_mag"] - df["phot_rp_mean_mag"]
    # absolute magnitude
    result["mg"] = df["phot_g_mean_mag_march2021"] - 5 * np.log10(df["dist50"]) + 5
    # uncertainties
    result["e_mass"] = (df["mass84"] - df["mass16"]) / 2.0
    return result
```

## Step 4: Plot Functions (`plots.py`)

Each plot family as a function returning output path:

```python
def plot_kiel_diagram(df, outdir="paper/figures"):
    fig, ax = plt.subplots(figsize=(7, 6))
    mask = df["teff50"].notna() & df["logg50"].notna()
    ax.hexbin(df.loc[mask, "teff50"], df.loc[mask, "logg50"],
              gridsize=100, mincnt=1, cmap="viridis",
              norm=mcolors.LogNorm(vmin=1))  # NOT minmax=True
    ax.invert_xaxis()
    ax.invert_yaxis()
    path = Path(outdir) / "kiel_diagram.png"
    fig.savefig(path, dpi=300)
    return path
```

## Step 5: Notebook Frontends

Thin notebooks calling the module:

```python
import sys
sys.path.insert(0, "../src")
from starhorse2026.dataio import load_sample
from starhorse2026.plots import plot_kiel_diagram

df = load_sample("quality_cut")
plot_kiel_diagram(df)
```

## Reproducibility

Every figure saves:
- PNG + PDF copies
- Metadata text file (timestamp, commit hash, parameters used)
- Summary CSV in results/

## Evolution: PlotSpec registry + Dask pruning (validated in SH26, Aug 2026)

For larger catalogs (10⁸+ rows) or long-lived multi-paper projects, the flat
`plots.py` module above has been superseded by a registry pattern:

- **One file per figure** (`plots/p01_cmd.py`, …), each declaring
  `SPEC = PlotSpec(id, name, columns=[...], derived=[...], params={...})`
  + `make(df, ctx)`. Auto-discovered by a registry; CLI selects by id/range.
- **Column-pruned Dask loading**: the loader computes the union of columns
  across selected plots and passes it to `dd.read_parquet(columns=…)` —
  only those columns are ever read from disk. Derived columns (MG0, galactic
  coords) are added lazily via `map_partitions`.
- **Resource ceiling via LocalCluster**: `n_workers × threads_per_worker`
  and `memory_limit` give a hard cap, with spill-to-disk instead of OOM.
  **Tune `memory_limit` to the host, not to the dataset** — an oversized
  per-worker `memory_limit` does NOT protect you from the OS OOM killer.
  On the SH26 local host the standing cap is **~14 GB total**
  (3 workers × 4.5 GB); per-worker limits above ~7 GB get OOM-killed
  (exit code `-9`) even with spill enabled. Size workers so the total fits
  the machine's free RAM, and let Dask spill the rest to disk.
- **JSON provenance sidecar per figure** (n_points, git hash, params,
  timestamp) replaces ad-hoc metadata files.

See the `starhorse-plots` skill (references/sh26_dask_framework.md) for the
full working implementation. Use the simple pattern above for quick projects;
graduate to the registry pattern when a project will produce multiple papers
or the catalog outgrows RAM.

## Pitfalls

- **`int(len(ddf))` materializes the whole catalog**: calling `len()` on a Dask DataFrame triggers a full count compute over every row/partition — on a 50M×128-col joined catalog this can OOM or take minutes for no reason. Only call it on the pruned, column-subset frame the current plot actually needs (and cache the lazy Dask frame so you read the parquet metadata once, not per plot).
- **Distance units across catalogs differ — verify before any 1:1 comparison plot**: Bailer-Jones 2021 columns (`r_med_geo_bj21`, `r_med_photogeo_bj21`, `r_lo_*/r_hi_*`) are in **parsecs** while SH26 `dist50` and the SH21/Weiler `dist50_*` columns are in **kpc**. Plotting raw BJ21 vs `dist50` produces a hexbin squished into the bottom-left corner with an x-axis max ~48,000 "kpc". Divide BJ21 distances by 1000 first. Quick diagnostic: `median(dist50 / <col>)` ≈ 1 means same unit; ≈ 0.001 means `<col>` is in parsecs.
- **Loader never drops rows**: Do NOT apply science cuts (ruwe, parallax SNR, dist50 range) in the data loader or via Parquet pushdown. Global pre-plot cuts silently thinned the SH26 CMD from 201k → 37k rows and were reverted. Each plot applies its own mask (or none); quality cuts are opt-in per run (`--cuts`), not baked into loading.
- **pyarrow `filters` not `filter`**: `pq.read_table()` takes `filters=...` (plural), NOT `filter=`. Using `filter` raises `TypeError: read_table() got an unexpected keyword argument 'filter'`.
- **matplotlib hexbin `minmax` removed**: In matplotlib 3.7+, `minmax=True` and `reduce_C_function=` are NOT supported on `hexbin()`. Use `norm=LogNorm(vmin=1)` instead.
- **matplotlib colorbar tick formatting**: `cb.ax.set_yticklabels()` after `LogNorm` can mislabel ticks unless you use `FixedLocator`. Prefer `LogFormatterSciNotation` from `matplotlib.ticker` for clean log labels.
- **DataFrame alignment after dropna**: Calling `.dropna()` on individual columns returns series with DIFFERENT indices. Always use a boolean mask (`df[...].notna() & df[...].notna()`) to align columns before plotting.
- **Parquet column count**: pyarrow `ParquetDataset` may return fewer columns if some parquet files lack certain columns. Use `columns=[...]` in `read_table()` and handle missing columns explicitly.
- **Data path in config**: The `config/storage.yaml` `base_path` must be an absolute path — relative paths resolve from CWD which changes between make targets and notebook execution.
- **CMD extinction corrections**: When plotting CMDs from SHBoost-style datasets, DO NOT use a simple flat `E(BP-RP)/A_V = 1.33` dereddening factor. The original notebooks use temperature-dependent Gaia EDR3 extinction corrections via `photutils.py` (coefficients from F. Anders). Use `MG0(G_obs, AV, dist, Teff)` and `BPRP0(BP_obs, RP_obs, AV, Teff)` — the `AG(AV,Teff)`, `ABP(AV,Teff)`, `ARP(AV,Teff)` polynomials — not `1.33 * E(BP-RP)`. A flat correction will wash out the main sequence turn-off and red clump structure.

See `matplotlib-pitfalls` skill for hexbin log scale, inverted axis, and NaN handling issues.
