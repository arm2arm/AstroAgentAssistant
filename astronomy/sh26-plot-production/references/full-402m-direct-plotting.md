# Plotting the full 402M catalog (v190826) on <compute-node> — pyarrow-direct path

Validated 2026-08-21. P01 (CMD) rendered on the full 402,121,784-row
catalog in **214 s total** (read 11.8 s + hexbin 79.7 s), 7 columns
pushed, 327,477,457 converged, 322,771,318 plotted (finite phot).
Peak RAM ~15 GB on <compute-node> (754 GB node) — trivial.

## Why the CLI/Dask path FAILS on 402M (2026-08-21)

`python -m sh26 plots -p 1 --data .../sh26_final_joined_v190826
--no-cuts --threads 48 --memory 128GB` dies in ~96 s with:

```
MemoryError: Task ('repartitiontofewer-...') has 12.36 GiB worth of input
dependencies, but worker ... has memory_limit set to 4.96 GiB.
```

Mechanics (two independent problems, both structural):
1. `LazyCatalog._ddf` reads with `blocksize="32MB"` → ~6000 tiny partitions
   for 402M rows. Dask's `repartitiontofewer` coalesces them into
   ~12.36 GiB output chunks before materialization.
2. `--memory` is a TOTAL budget; `LazyCatalog._ensure_cluster` divides it
   by `n_workers` (from config/dask.yaml) → per-worker `memory_limit` far
   smaller than the chunk. Bumping `--memory` alone doesn't fix it unless
   the per-worker limit exceeds the chunk size (~13 GiB+).

Not the same as the 2026-08-18 host-RAM-pressure stall — this fails
deterministically on an empty 754 GB node. (Also seen: stale scheduler on
port 8787 from an old run → "Port 8787 already in use" warning; kill stale
schedulers before CLI runs, or just use the direct path.)

**Rule: for 402M, don't fight the Dask CLI. Use pyarrow-direct.**
Single-plot or few-plot runs: direct loader, no Dask at all. (The
served-table + bincount architecture from `full-catalog-402m-plan.md`
remains the plan for the full cheap campaign; until it lands, direct
loader is the working path for individual plots.)

## The runner (generic, any plot id)

`/tmp/run_p_direct.py <plot_id>` was deployed on <compute-node> (2026-08-21);
copy in `templates/run_p_direct.py` in this skill. It:
- resolves the plot's columns via `registry.spec(PID)` +
  `sh26.lazy_catalog._resolve` (pushdown + MISSING always),
- reads ONLY those columns with `pyarrow.dataset.to_table(columns=...)`,
- applies the hard `MISSING == False` convergence filter (matches
  `LazyCatalog.get()` semantics),
- computes derived cols via `sh26.lazy_catalog._derive` (mg0/bprp0/XGal…
  in float32),
- calls `registry.make_fn(PID)(pdf, ctx)` with
  `PlotContext(outdir=..., dataset=<full path>, extra={"loader":
  "pyarrow-direct", "quality_cuts": False})`.

Run (on <compute-node>, nohup + log, ~2–5 min for most plots):

```
nohup /lustre/<user>/SOFTWARE/conda/sh25/bin/python /tmp/run_p_direct.py 1 \
  > /tmp/p01_direct.log 2>&1 &
```

Outputs land in `/lustre/<user>/hermes/sh26_full/figures/` (png + pdf +
json sidecar with `loader: pyarrow-direct` provenance).

## Deploying the script over double-SSH (agent host → 144 → <compute-node>)

Heredocs and multi-layer quoting mangle through two ssh hops (and the
Hermes shell parser chokes on `&` in heredocs). Working pattern:

```python
b64 = base64.b64encode(script_text.encode()).decode()
cmd = ("ssh arm2arm@141.33.4.144 'ssh -o ConnectTimeout=8 <compute-node>.nnew "
       "\"printf %s '" + b64 + "' | base64 -d > /tmp/run_p_direct.py "
       "&& /lustre/<user>/SOFTWARE/conda/sh25/bin/python -m py_compile "
       "/tmp/run_p_direct.py && echo OK\"'")
```

Verify with `py_compile` + `wc -c` before running. (`scp` two-hop works
too but the agent→144 leg has timed out before; `printf %s | base64 -d`
is one command, no intermediate file.)

## Caveats

- **Memory scales with pushed-column count × rows.** P01 (7 cols float32)
  ≈ 12 GB frame + derive temporaries ≈ 20 GB peak. 10+ column plots
  (P43–P50 style with Δ columns) can hit 30–40 GB — still fine on
  <compute-node>, still avoid the Dask CLI. For multi-panel plots that need
  several column sets, read in one pass (union of columns) and slice.
- **Hexbin cost scales with rows.** P01 at gridsize 300 = ~80 s for
  320M points. If a plot is slow, drop `gridsize` via
  `registry.spec(NN).params["gridsize"] = 256` in the runner (the bincount
  fast renderer from the full-catalog plan is the real fix).
- **float32 throughout**: v190826 is all-float32, so no
  `_cast_float32` needed; derived cols come out float32 automatically.
- **Do NOT import plot modules as `sh26.plots.p01`** — module names are
  `p01_cmd` etc. Always go through `sh26.registry` (`spec` / `make_fn`).
- Convergence count on v190826: 327,477,457 (81.4% of 402,121,784) — use
  this as the QA anchor for sidecar `n_points` sanity on 402M figures.
- Old join artifacts still in the final/combined tree:
  `__tmp_base/`, `__tmp_dups/`, `__tmp_enriched/` dirs (from 2026-08-19
  resume run) are stale and reclaimable.
