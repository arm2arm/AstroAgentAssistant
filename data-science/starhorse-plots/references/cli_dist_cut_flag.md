# CLI `--dist-cut` flag (added 2026-08-15)

Native way to re-plot the whole figure suite on a distance-restricted subset —
supersedes the old `scripts/gcx_plots.py` workaround for the common
`dist50 < N kpc` case.

## Run

```bash
# count the subset first (standalone, cheap)
python3 - <<'PY'
import dask.dataframe as dd
df = dd.read_parquet("data/sh26_joined_50m.parq", columns=["dist50"], engine="pyarrow")
print(len(df[df["dist50"].notnull() & (df["dist50"] < 5)]))
PY

# sanity-check the CLI on the 200k cache (~20 s), THEN the full 50M run (background)
PYTHONPATH=src python -m sh26 plots --all --no-cuts --dist-cut 5 \
  --data data/sh26_joined_50m.parq --outdir paper/figures_50m_d5 \
  --threads 16 --memory 64GB
```

Then combine:
```bash
python3 scripts/combine_figures.py --input paper/figures_50m_d5 --output sh26_all_50m_d5.pdf
```

## Implementation (src/sh26/lazy_catalog.py, src/sh26/cli.py)

- `LazyCatalog(dist_cut=<float>)` — new kwarg. In `get()`:
  - if set, force-add `"dist50"` to the pushed column set (otherwise Dask
    column-pruning drops it and the filter would KeyError on plots that
    otherwise don't need a distance column),
  - after materialization + QC mask, filter
    `pdf["dist50"].notna() & (pdf["dist50"] < self.dist_cut)` and log
    `dist50 < N kpc: <before> -> <after> rows`.
- `PlotContext.extra["dist_cut_kpc"] = N` — lands in every JSON provenance
  sidecar so a subset run is distinguishable from a full run.
- CLI flag `--dist-cut <float>` (kpc) wired in `cmd_plots`.

## Verified numbers (2026-08-15)

| dataset | total rows | dist50 < 5 kpc | fraction |
|---------|-----------|----------------|----------|
| `sh26_cache_200k.parq` | 201,057 | 149,415 | 74.3% |
| `sh26_joined_50m.parq` | 50,000,025 | 37,236,050 | 74.5% |

Full 42-plot 50M subset run uses `--threads 16 --memory 64GB` (2 workers ×
32 GB). The foreground terminal caps at 600 s, so background-run with
`notify_on_complete=true` and poll `grep -cE "dist50 < 5.0 kpc"` on the log
to track progress.

## Note for other column cuts

`--dist-cut` is the only native subset flag. For cuts on other columns
(e.g. `met50 < -1`, `SHBOOST == True`) you still need the legacy wrapper
pattern from `references/gcx_custom_distance_cuts.md` — apply a pandas
boolean mask on the materialized frame before calling each renderer.
