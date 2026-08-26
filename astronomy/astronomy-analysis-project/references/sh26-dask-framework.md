# SH26 Dask Plotting Framework (validated Aug 2026)

Reference implementation of the registry + Dask pattern from
`astronomy-analysis-project/SKILL.md` §"Evolution: PlotSpec registry + Dask pruning".
Project: `/home/hermes/projects/SH26/`, package `src/sh26/`.

## Layout

```
src/sh26/
├── registry.py    # PlotSpec dataclass + auto-discovery of plots/p*.py
├── context.py     # PlotContext: style, save (png/pdf), JSON provenance
├── dataio.py      # Catalog: Dask read_parquet(columns=union) + lazy derivations
├── cli.py         # `python -m sh26 list|plots --all|-p 1,3,7|--combine`
└── plots/
    ├── _helpers.py       # hexbin2d, hist1d, binned_mean_std, errorbar_band
    ├── _sh21_helper.py   # shared SH21-vs-SH26 renderer (P17–P20)
    ├── _uncert_helper.py # shared posterior-width renderer (P21–P24)
    └── p01_cmd.py … p26_parallax_err_vs_dist.py   # one file per figure
```

## Plot contract (every plot file)

```python
from sh26.registry import PlotSpec
SPEC = PlotSpec(
    id=27, name="myplot", title="…",
    columns=["teff50", "logg50"],   # raw Parquet columns (union drives pruning)
    derived=["mg0"],                # lazy columns dataio computes
    params={"gridsize": 200},       # CLI-overridable: --param p27.gridsize=300
)
def make(df, ctx):
    # df: pandas, already column-pruned + derived; apply plot's own mask
    fig, ax = plt.subplots(...)
    ...
    return ctx.save(fig, SPEC, n_points=len(d))   # writes png/pdf + .json sidecar
```

## Data flow

1. CLI collects selected ids → `registry.required_columns(ids)` union.
2. `dd.read_parquet(path, columns=union, engine="pyarrow", split_row_groups=True)`
   — unread columns never touch RAM.
3. Derived columns (mg0, bprp0, XGal/YGal/ZGal/RGal, gj0, plx_frac_err) added
   via `map_partitions`. Dependency map lives in `dataio.DERIVED_DEPS`.
4. One `.compute()` per run → cached pandas frame reused by all plots.

## Resource ceiling (config/dask.yaml)

```yaml
dask:
  n_workers: 4
  threads_per_worker: 4      # 16 threads total
  memory_per_worker: "8GB"   # 32 GB ceiling; spills to disk beyond
  spill_dir: "/tmp/sh26_dask_spill"
```

`dataio.dask_cluster()` builds a `LocalCluster` from this; a `_ClusterGuard`
context manager closes client+cluster. Override per-run via CLI
`--threads N --memory 12GB`.

## Critical rule: loader never drops rows

**Do NOT apply science cuts in the loader** (no ruwe / parallax-SNR / dist50
pushdown in `dataio`). The user wants figures to show the full catalog; each
plot applies its own mask (or none). Global cuts silently thinned the CMD
from 201k → 37k rows and were reverted. Quality cuts live in
`apply_quality_cuts()`, only enabled when the caller passes `--cuts` (default
is now `--no-cuts` for figure production).

## Makefile targets

```make
make plots            # PYTHONPATH=src python -m sh26 plots --all
make plots P=1,3,7    # subset
make plots P=8-11     # range
make combine          # scripts/combine_figures.py → sh26_all_figures.pdf
make list             # figure table
```

## Provenance sidecar

`ctx.save()` writes `sh26_pNN_name.json` next to each figure:
`{plot_id, dataset, n_points, params, columns, derived, git, timestamp}`.

## Numbers (SH26 200k cache)

- 26 figures in ~9 s, 0 failed.
- Full catalog 201 057 rows; CMD points 160 975 (only true NaN photometry
  excluded). Giants 13 256, main seq 136 935, faint/WD 1 169.
