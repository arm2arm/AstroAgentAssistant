---
name: sh26-plot-production
description: "Use when producing SH26 paper figures and 50M Dask runs."
---

# SH26 Paper-Figure Production

Reproducible pipeline for the SH26 paper: a declarative plot registry
(**P01–P111 as of 2026-08-25**, tag `sh26.plots.v0.2.0`, commit `93c3dcc`),
a CLI that runs figures over 50M-row Parquet with per-plot column pushdown,
and combined per-dataset PDF deliverables. v0.2.0 adds `src/sh26/aggregate.py`
(Dask-side partial aggregation — binned products without client-side
materialization, entry `LazyCatalog.get_aggregated`), compact
`SH_OUTFLAG_CODE` (uint16) flag decoding, per-sidecar `code_fingerprint`
+ `library_versions` provenance, and a 207-test suite that runs green in
one process (tests never spawn a LocalCluster — see conftest).

Repo: `/home/hermes/projects/SH26` (branch `main`, remote `origin` →
`git@gitlab.aip.de:<user>/SH26.git`). **Commit + push after every
verified change** (user-approved default; user "refer and correct"
workflow depends on it).

Full figure catalog, helper APIs, class cuts, and dataset stats:
`references/catalog.md` — read it before touching this project.

Full-catalog (402M) plot runs driven FROM the agent host onto <compute-node>
(disposable git worktree at a tag SHA, sh25 conda env, two-hop md5-verified
script transfer, tmux + MASTER.log launcher, artifact relay, octal-`01`
bash pitfall, vision-QA false alarms):
`references/<compute-node>-agent-host-full-catalog-rerun-20260825.md`.

Long / hour-scale jobs (t-SNE on large samples, anything past 600 s or
4 GiB): `references/p90-long-embeddings.md` — terminal-tool caps, the
user-systemd oneshot pattern (systemd-native `append:` redirection,
NEVER `sh -c '... 2>&1'` in ExecStart), the rsyslog quadtree-flood
pitfall, t-SNE/UMAP benchmarks, subset-first protocol. P90 OOM wall +
Newton offload context: `references/p90-embeddings-oom-newton-offload.md`.

## Served-table mode (full 402M, 2026-08-21)

Fast path for interactive full-catalog plotting: publish the final table on
a cluster scheduler, then plots pull only their columns from worker memory.

- **Publisher** (runs ON the cluster node, connects to *your* scheduler —
  does NOT start a cluster): `scripts/sh26_publish.py publish|unpublish|status
  --scheduler tcp://IP:PORT`. Default `--data` = the project final
  (`.../final/combined/sh26_final_joined_v190826`); `--columns auto`
  (= live registry union, 53 cols) | `all` | comma list; filters
  `MISSING==False` (serve only the ~327M converged) unless `--no-converged`;
  adds 7 derived cols in `map_partitions`; float32 → ~90–100 GB resident;
  writes `server_info.json`. `unpublish` frees worker RAM.
- **Client** (unchanged invocation): `python -m sh26 plots -p ... --data
  publish:sh26 --served tcp://IP:PORT --no-cuts --outdir ...`. `LazyCatalog`
  connects (no local cluster); `get_dataset(name)` returns a **lazy
  dask.dataframe** (dask 2026.7.1 — verified), so `ddf[cols].compute()`
  projects on the workers = real pushdown over the wire. `close()`
  disconnects but **never stops the remote cluster**. The convergence filter
  is a no-op on an already-converged table.
- Access: agent host has NO route to 192.168.111.x — tunnel
  `ssh -L 8787:localhost:8787 arm2arm@141.33.4.144` and use
  `--served tcp://127.0.0.1:8787`.
- Gate 1 (local 200k, real cluster + real CLI): served P01 is
  **byte-identical** to the parquet path (n_points + PNG bytes). pyarrow-direct
  (`scripts/run_p94_direct.py` / `/tmp/run_p_direct.py`) remains the fallback
  when no server is up. NOTE `get_dataset` in 2026.7 has NO `columns=` kwarg —
  project with `ddf[cols]`.
- **Gate 2 finding (2026-08-21): publish WORKS, client plot path OOMs at 4×30 GB.**
  `sh26_publish.py publish` on <compute-node>: read+filter+derive+persist of 53 raw +
  7 derived cols (327,477,457 converged rows) took **115 s**, ~80 GB resident,
  verified from client (real 327,477,457 rows, MISSING all False, 1011 partitions,
  `client.get_dataset("sh26")` = lazy dask.dataframe — API is client methods,
  NOT `distributed.publishing` module imports). But the first served plot (P66)
  worker-OOMed mid-compute: dask_expr auto-inserts a `repartitiontofewer`
  (shuffle) after the read, whose single fused key needs a worker buffer the
  30 GB worker can't spare while holding ~20 GB of table partitions →
  "Couldn't gather 1 keys, rescheduling" infinite loop. Same failure class as
  the 402M CLI. Fixes to try (not yet done): republish with
  `repartition(divisions=None, npartitions≈workers*4)` at PUBLISH time so clients
  never repartition; or bigger workers (2×60 GB); or disable the repartition
  optimization. Until then pyarrow-direct remains the production path.
  `sh26_publish.py` n_rows bug fixed 2026-08-21 (`len(ddf)`, not
  `ddf.count().sum()` which sums per-column non-nulls ≈ rows×ncols).

## Datasets

| Dataset | Path | Rows |
|---|---|---|
| 50M full | `data/sh26_joined_50m.parq` (8 parts, ~22 GB) | 50,000,025 |
| 50M d5 | same, `--dist-cut 5` | 37,236,050 |
| 50M + PM | `data/sh26_joined_50m_pm.parq` (pmra/pmdec; base schema lacks them) | 50M |
| 200k full | `data/sh26_cache_200k.parq` | 201,057 |
| 200k d5 | same, `--dist-cut 5` | 149,415 |

Canonical combined deliverables (89 pp each at 2026-08-17, rasterized):
`sh26_all_50m.pdf`, `sh26_all_50m_d5.pdf`, `sh26_all_200k_d5.pdf`.
NOTE: all three are built from the SAME `paper/figures/` dir (figures
rendered from the 50M dataset); the per-dataset names are legacy
convention — dataset provenance lives in each figure's JSON sidecar
(`dataset` field), not in the combined PDF.

### Full-catalog vintages (<compute-node>, 402M rows, 3032 parts)

Lineage `.../final/combined/`: v190826 (133c +4 PM) → v220826 (133c, +`SH_OUTFLAG`
large_string) → **v250826 (134c, +`ruwe2` float32)**. **PAPER VINTAGE = v220826**
(133 cols). CRITICAL routing fact (cost 4 failed renders, 2026-08-25): a plot
that lists `ruwe2` in `SPEC.columns` (**RAW**) — P107/P108/P109, all titled
"(v250826)" — reads it as a STORED column, which only exists in **v250826**.
Running them on v220826 fails at the read with
`ArrowInvalid: No match for FieldRef.Name(ruwe2)`. So the full-402M bundle is
**108 plots on v220826 + P107/P108/P109 on v250826** (same 402M rows, different
vintage per plot). `ruwe2` as a *derived* column (`derived=["ruwe2"]`, e.g. P100)
works on v220826 — `_derive` computes it from `ruwe`+`l`+`b`; only the stored
(`columns`) plots need v250826. **P90/P91 (per-star t-SNE/UMAP) are NOT
batch-renderable at 402M** — opt-in by design — so a full bundle is **109/111,
not 111**; don't chase the last two.

## Run patterns

All 50M runs: `--no-cuts --threads 16 --memory 64GB`.

**50M runs go FOREGROUND in ~8-plot chunks** — never background:

```
cd /home/hermes/projects/SH26
PYTHONPATH=src python3 -m sh26 plots -p 43-50 \
  --data data/sh26_joined_50m.parq --no-cuts --outdir paper/figures \
  --threads 16 --memory 64GB
```

Chunks ≈ 25–100 s each (warm page cache). 200k: single foreground call,
`--threads 8 --memory 8GB`.

Rebuild combined PDFs after each suite:

```
python3 scripts/combine_figures.py -i paper/figures -o sh26_all_50m.pdf
```

Param override without code edits: `--param pNN.key=value`
(`cli.parse_params` coerces int/float; P90 uses it for `subsample`).

## Adding a new figure

1. Write `src/sh26/plots/pNN_<name>.py` defining module-level
   `SPEC = PlotSpec(id=NN, name=..., title=..., columns=[raw parquet cols],
   derived=[...])` and `def make(df, ctx)`.
2. `ctx.save(fig, SPEC, n_points=...)` is the only save path — it injects
   the red `PNN` tag, rasterizes dense collections, writes
   PNG + PDF + JSON sidecar.
3. Verify: `PYTHONPATH=src python3 -m sh26 list` (registry auto-discovers),
   smoke-run `-p NN` on `data/sh26_cache_200k.parq --no-cuts`.
4. Then the full 50M chunked runs + PDF rebuilds, commit, push.

## Hard convergence filter (2026-08-16)

`LazyCatalog.get()` (and legacy `dataio.Catalog`) ALWAYS filter
`MISSING == False` (converged rows) FIRST — before quality cuts, dist
cuts, and derived columns. `MISSING` is always included in the column
pushdown; there is no CLI flag to disable it. Log line:
`converged (MISSING == False): N -> M rows`. Consequence: P63/P64
(SHBOOST True/False panels) now show only converged stars — the
"non-converged" population is excluded by construction from all figures.
On 50M: 50,000,025 -> 40,719,146 converged.

## Critical pitfalls (all hit in production)

- **Host RAM pressure from other tenants (seen 2026-08-18):** host is
  shared — with ~100 GB used by other tenants, Dask `--memory 64GB`
  reads stall >600 s on 10-column 50M runs (foreground timeout), and
  `--memory 16GB` stalls the same. Background = 4 GiB cgroup OOM as
  always. WORKING FALLBACK: run the plot via the user-systemd oneshot
  pattern with a Dask-free pyarrow-direct loader (read columns with
  `pyarrow.dataset`, `to_pandas()`, apply `MISSING == False`
  convergence filter yourself, call the module's `make(pdf, ctx)` with
  a `PlotContext(outdir=Path(...))`). Template:
 `scripts/run_p94_direct.py` + `~/.config/systemd/user/sh26-p94.service`
 (read 25.5 s + make 60 s for P94, no OOM, no timeout).
 - **Background terminal jobs die at ~P12 on full 42+ plot runs.**
- **Deredden per-selection, not per-catalog:** if a plot only needs
  `mg0`/`bprp0` for a spatial subselection, set `derived=[]` and call
  `sh26.photutils.MG0/BPRP0` inside `make()` on the masked rows —
  avoids 50M-row extinction math.
  Hermes worker scopes (`hermes-worker-*.scope`) have a HARD 4 GiB cgroup
  cap (`tools/process_registry.py`; env can only tighten). Host RAM is
  irrelevant — kernel OOM-kills inside the scope. Foreground gateway runs
  are uncapped but capped at 600 s per call. This is why 50M suites run
  in foreground chunks and hour-scale jobs use the user-systemd oneshot
  (see `references/p90-long-embeddings.md`).
- **Never pass `--memory 4GB`** to Dask runs: worker OOM-restart loop.
- **Acrobat renders hexbin/scatter/pcolormesh vector PDFs extremely
  slowly.** `context.save()` sets `rasterized=True` on
  `PolyCollection`/`PathCollection`/`QuadMesh` before saving (import
  `QuadMesh` from `matplotlib.collections`, mpl 3.11). Keep it.
- **Unit trap:** `r_*_bj21` columns are **parsecs**; `dist50` is kpc.
  Scale by 0.001 before any Δ (helper param `ref_scale`).
- **Sentinels, not NaN:** photometry mags (Gaia PSF/SM, 2MASS, WISE) use
  `-1e4` = no phot; `xgbdist_*_mean` uses `-9999` = no match (std can be
  6.4e10). `np.isfinite`-mask; `-1e4` passes `notna`.
- **`l` ∈ [0,360)** — wrap with `wrap_l()` (from `_mollweide_helper`) to
  [−180,180) before any binned or Mollweide product. GC center, seam at
  anti-GC.
- **Non-converged stars (SHBOOST=False) have NO SHBoost24 predictions.**
  xgbdist is all NaN on that population (0/68,809 on 200k — verified).
  "What SHBoost says about non-converged stars" plots are impossible by
  construction; document the population instead (CMD/G/Teff-logg, P63–P64).
  On 50M: 9.28M MISSING, 23.2M non-converged. NOTE: since the hard
  convergence filter removed MISSING rows from all plots, the old
  "non-converged ~23.2M" n_points expectation is stale — converged-only
  sample is ~40.7M on 50M.
- **Template-generated plot modules:** when generating modules from a
  Python string template, verify every `.format()` key is passed — an
  unfilled placeholder (e.g. a literal `SH26COL`) passes the registry
  import but NameErrors at plot time. `grep` the generated files for the
  placeholder AND `importlib`-import each module before running.
- Heredocs containing `&` trip the Hermes shell parser — write a script
  file to `/tmp` instead.
- **Open-ended histogram bins swap easily** (P86: two outer met bins were
  interchanged + overlapping, counts summed above the total). After
  binning, verify the bins partition (per-bin sum == total selected).
- **matplotlib fill_between/plot have no `step` kwarg** — use
  `ax.fill_between(x, h, step="pre")` / `ax.step(x, h, where="pre")` with
  explicit edge arrays.
- **`context.save()` stamps the P## label on EVERY axis in `fig.get_axes()` —
  which INCLUDES the colorbar's axis** (a colorbar axis carries a `QuadMesh`
  artist). Pre-2026-08-21 the red `PNN` tag was drawn on top of the color
  scale on single-panel hexbin figures. `save()` now skips any axis whose
  children contain a `QuadMesh` (verified: hexbin colorbar axis → True, bare
  hist axis → no false positive). If you add a new plot type, confirm its
  colorbar still gets skipped.
- **Star count in every figure title (user rule, 2026-08-21):** `save()`
  appends ` · N = {n_points:,}` to each panel title (skips the append when
  the title already contains `n =`, e.g. the SH21/Weiler comparison helpers
  which embed their own count). Do NOT add a separate top-right badge — it
  collides with the colorbar.
- **XYZ hexbin plots (P65–P70) default to 512×512 grid (user rule,
  2026-08-21):** "similar plots" follow this — 512 costs ~0 runtime
  difference at 402M. `_xyz_helper.xyz_plot` reads `gridsize` from SPEC
  params with default 512; optional per-axis `extent` param
  (e.g. P65: X/Y/Z ∈ [−50, 50] kpc) sets hexbin `extent` + xlim/ylim.
  New XYZ-style plots: keep `gridsize: 512` in the SPEC.
- **Full-402M single-plot runs: use the pyarrow-direct loader, NOT the Dask
  CLI.** The CLI (`python -m sh26 plots`) fails at 402M rows:
  `repartitiontofewer` merges the tiny `blocksize=32MB` partitions into
  ~12.36 GiB chunks that exceed the per-worker limit (`--memory X` is divided
  across config `n_workers`, so `--memory 128GB`/26 workers = 4.96 GB each →
  `MemoryError`). The direct path reads ONLY the plot's columns via
  `pyarrow.dataset(...).to_table(columns=[...])`, applies the
  `MISSING==False` convergence filter, calls `sh26.lazy_catalog._derive`,
  then `make(pdf, ctx)`. Template on <compute-node>: `/tmp/run_p_direct.py <id>`
  (P01 on 402M: read 402M in ~12s, converged 327,477,457, hexbin ~80s,
  total ~3.5 min, ~15 GB peak). Runs in foreground — no Dask, no spill, no
  per-worker limit.
- **Hand-rolled pyarrow-direct loaders must mirror `LazyCatalog.get()`'s
  post-derive steps, not just `_derive` (P99 KeyError, 2026-08-25).** Stage 4
  made P99 consume the compact `SH_OUTFLAG_CODE`, which `get()` attaches via
  `_attach_flag_code(pdf, keep_str)` AFTER `_derive` (it decodes the large_string
  `SH_OUTFLAG` → uint16 code, then drops the string col unless requested). A
  custom loader that stops at `_derive` then does `keep=[c for c in
  (spec.columns, spec.derived) if c in pdf.columns]` silently lacks
  `SH_OUTFLAG_CODE` → `make()` raises `KeyError`. Fix: in `scripts/run_plot_full.py`
  (and any `/tmp/run_p*.py` clone), after `_derive` add
  `pdf = _attach_flag_code(pdf, keep_str=("SH_OUTFLAG" in spec.columns or
  "SH_OUTFLAG" in spec.derived))` before the `keep` slice. General rule: when a
  plot starts failing on a *derived/compact* column the Dask path produces, diff
  your loader against `get()` for the post-compute calls you skipped (float32
  recast, `_attach_flag_code`, etc.).
- **This sklearn build's `QuantileTransformer` (1.9.0) has NO `n_jobs` kwarg**
  kwarg** — pass `random_state` only; `n_jobs=-1` crashes the run.
- **`pkill -f <pattern>` can match the tool call's own command line**
  (kills your watcher / hangs the call). Kill by explicit PID or bracket
  the pattern (`pkill -f 'name[.]py'`). `pgrep -af` includes the wrapper
  bash — filter to the python script path.

## QA pattern (programmatic, no vision dependency)

After each run, before committing:

```python
import json, glob
from PIL import Image
import numpy as np
for f in sorted(glob.glob('paper/figures/sh26_p*.png')):
    meta = json.load(open(f[:-4] + '.json'))
    im = np.asarray(Image.open(f).convert('L'))
    print(meta['plot_id'], meta['n_points'], round((im < 240).mean(), 3))
```

Check: sidecar `n_points` sane vs expected class sizes (converged-only
sample since 2026-08-16: 50M -> ~40.7M rows; RC ~3.8M, SMR ~44.7k);
non-white fraction > 0.05 (no blank canvases). `vision_analyze` may be
flaky (timeouts; fails on full-res >5000px images) — downscale with PIL
`thumbnail((1100,1100))` before vision; treat it as spot-check, not gate.

## Style conventions (user rules, non-negotiable)

- White background; hexbin (user prefers plain hexbin over smoothed
  approaches — speed).
- **Axis labels carry the actual column name** (`(col: <name>)`, derived
  cols labeled by derived name).
- Every figure carries the `[PNN]` plot number (injected by `ctx.save`).
- One numbered file per figure + JSON sidecar; full catalog, `--no-cuts`.
- CMD/Kiel diagrams: invert axes only, no xlim/ylim changes beyond data.
- English, concise.
- Large ML embeddings: user prefers **subset-first** (1% → 10% → full),
  seeded (42), reproducible; "stop watching" = no continuous watchers,
  status on request only — see P90 + `references/p90-long-embeddings.md`.
