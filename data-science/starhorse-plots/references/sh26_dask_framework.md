# SH26 Dask Plot Framework — Built Aug 8, 2026 (updated Aug 14 for 50M scale)

Modular replacement for the old starhorse2026 monolith. Validated at 200k scale
(26 figures in 8 s) and at 50M scale (39 figures in ~14 min, 0 failed).

## Core pieces (src/sh26/)

| File | Role |
|------|------|
| `registry.py` | `PlotSpec` dataclass + auto-discovery of `plots/p*.py`; column-union calc |
| `context.py` | `PlotContext`: style (seaborn-v0_8-whitegrid, white bg), save png/pdf, JSON sidecar, **P## reference-label badge injection in `save()`** |
| `lazy_catalog.py` | `LazyCatalog` Dask loader (current); `DERIVED_DEPS` graph; schema scan once; per-plot column pushdown |
| `dataio.py` | Legacy `Catalog` — kept for reference; `lazy_catalog.py` supersedes it for 50M-scale runs |
| `cli.py` | `python -m sh26 list / plots`; id parsing `1,3,7` + ranges `8-11`; `--param pNN.key=val` |
| `plots/` | one file per figure id, `SPEC` + `make(df, ctx)` |

## Plot contract (every p*.py follows it)

```python
from sh26.registry import PlotSpec

SPEC = PlotSpec(
    id=1, name="cmd", title="Color–Magnitude Diagram",
    columns=["teff50", "phot_g_mean_mag_march2021"],  # raw Parquet columns (include cols helpers use!)
    derived=["mg0", "bprp0"],     # computed after materialization
    params={"gridsize": 200},     # CLI-overridable
)

def make(df, ctx):                # df: ready pandas frame (only declared cols)
    ...
    return ctx.save(fig, SPEC, n_points=len(d))
```

**Column completeness check:** if a helper or `make()` body uses a column that
is NOT in `SPEC.columns`/`SPEC.derived`, the plot crashes with KeyError at
runtime (not at spec load). P01 and P30 both needed
`phot_g_mean_mag_march2021` added for exactly this reason.

## Derived-column dependency graph (DERIVED_DEPS)

- `mg0` ← phot_g_mean_mag_march2021, AV50, dist50, teff50
- `bprp0` ← phot_bp_mean_mag, phot_rp_mean_mag, AV50, teff50
- `XGal/YGal/ZGal/RGal` ← l, b, dist50 (Rsun=8.19 kpc)
- `gj0` ← phot_g_mean_mag_march2021, Jmag, AV50, teff50 (A_J ≈ 0.789·A_V)
- `plx_frac_err` ← parallax_lindegren2021, parallax_error_fabricius2021

Key design point: plots declare columns; loader reads ONLY the union from Parquet
(pyarrow pushdown) → ~10-20 of 128 columns per plot.

**CRITICAL: the loader never drops rows** (unless `--no-cuts` is absent and the
plot opts into quality cuts via the loader's mask). All science cuts live in
individual plots (their own masks). Rule: loader = read + derive only;
filtering = each plot's own job.

## Resource ceiling (host-tuned, Aug 14 update)

```yaml
# config/dask.yaml — sized to the HOST, not the dataset
dask:
  n_workers: 3
  threads_per_worker: 4      # 12 threads total
  memory_per_worker: "4.5GB" # ~14 GB total — standing user cap on this host
```

**PITFALL:** an oversized `memory_limit` does NOT protect from the OS OOM
killer. On this host, 4 workers × 8GB (32GB total) got OOM-killed (exit -9)
on 50M rows. Per-worker limits above ~7GB die regardless of spill settings.
Size workers so the TOTAL fits free RAM, and let Dask spill the rest.
50M rows × ~10 pruned columns ≈ a few GB per compute → fits comfortably.

## Provenance sidecar

Every figure writes `sh26_pNN_name.json`: plot id, dataset label, n_points,
columns/derived lists, params, git hash, ISO timestamp. Satisfies the paper
reproducibility requirement without a separate logging pass.

**P## reference labels:** `context.py save()` injects a red P## badge into the
top-left of every axes before save, so each figure can be referenced/corrected
by number. Never skip this — the user references plots by P## id.

## Extending (future papers)

1. New figure → `plots/pNN_x.py` with unique id — auto-registered, appears in
   `sh26 list`, runs via `-p NN`, gets pruning + provenance free.
2. New derived column → add to `DERIVED_DEPS` + `_derive()`.
3. New dataset → point `--data` at another Parquet dir; column names per-SPEC.

## Gotchas hit during build

- `distributed` loggers (worker/nanny/scheduler) flood stdout at INFO on cluster
  shutdown → cli.py sets `distributed/dask/tornado` to ERROR unless `--verbose`.
- **Never `int(len(ddf))` on the lazy frame** — forces a full count compute over
  all partitions (50M rows). Read schema/counts from parquet metadata instead.
- `_add_derived` must be importable at module level (Dask pickles the function
  reference for map_partitions) — no closures over local state.
- `dd.to_parquet` fragments output into hundreds of tiny parts unless you
  `.repartition(npartitions=N)` first (sampling script pitfall).

## Unit convention (CRITICAL — verified Aug 14)

| Column family | Unit |
|---|---|
| `dist50` (SH26), `dist*_sh21`, `dist*_weiler_w25` | kpc |
| `r_med_*_bj21`, `r_lo_*_bj21`, `r_hi_*_bj21` | **parsecs** |

BJ21 columns must be divided by 1000 before any 1:1 distance comparison
(P11/P12). Diagnostic: `median(dist50 / col)` ≈ 0.001 → col is in parsecs.

## Plotting the FULL catalog (Arman's requirement)

For paper figures the user wants ALL available data — never cut before plotting.
Run with `--no-cuts`. Hardcoded axis limits were removed everywhere — plots use
only `ax.invert_*axis()` for direction, no range caps.

**Final CMD recipe** (p01_cmd.py): no xlim/ylim (full axis range), only NaN
mask, `ax.invert_yaxis()`, cmap `viridis`, `LogNorm(vmin=1)`, gridsize 300.
