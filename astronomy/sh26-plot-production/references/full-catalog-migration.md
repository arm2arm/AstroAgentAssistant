# Full 402M catalog migration — state & recipes

Authoritative continuation point: `doc/full_catalog_plan.md` in the repo
(commit f03cfb2, 2026-08-18). This file is the skill-side summary + the
non-obvious recipes. Dataset prep happens in a separate session.

## Full catalog facts (verified 2026-08-18)

- Path (Newton): `/lustre/<user>/ipython/SH2025/reana/final/combined/sh26_final_joined/`
- 402,121,784 rows, 4,094 parts (`part.NNNN.parquet`, ~50 MB each), 210 GB
- Schema: 129 cols = 50M schema (128) + `source_id` + 5 PSF phot error cols
  (`{g,r,i,z,y}_mean_mag_error_SH`). **No pmra/pmdec** — PM must be joined
  via `source_id`; no 402M PM file located yet, so P82/P90–P93 stay 50M.
- MISSING/SHBOOST semantics (from the build notebook below):
  base = A∪B inputs; `MISSING` = no match to split tables C/D. All
  downstream joins are LEFT → SH21/BJ21/W25/Gaia cols are NaN on
  unmatched rows **even for converged stars**.
- Expected converged (MISSING==False): ~327M (50M rate).

## Compute: reserved node <compute-node>

- Reachable ONLY from Newton: `ssh arm2arm@141.33.4.144` → `ssh <compute-node>.nnew`.
  Private IPs 192.168.111.203 / 192.168.119.203 (newton21 subnet); **NO
  route from the agent host** — Dask clients connect via `ssh -L` port
  forward, or run the client process on Newton/the node.
- 96 cores / ~754–770 GB RAM. Dask env:
  `/lustre/<user>/SOFTWARE/conda/sh25/bin/python3` (dask 2025.10.0, py3.12)
  — same env the June builds used.
- Node state 2026-08-18: stale **STOPPED** scheduler (PIDs 7770/7773, state T
  since Jun 10) holds :8786 — port accepts connections but never responds;
  kill before starting fresh. No workers; ~728 GB RAM free. CPU contention:
  another tenant's pluto job held ~80/96 cores at check time — **re-check
  before scheduling**.

## Architecture (decided 2026-08-18)

1. Served Dask table on <compute-node>: pruned read (51 raw cols) → `MISSING==False`
   filter → derived (`mg0`, `bprp0`, `gj0`, `XGal/YGal/ZGal/RGal`) in
   `map_partitions` → `persist()` ≈ 327M × 60 cols ≈ 60–70 GB (float64)
   / ~35 GB (float32). Also dump a compact converged+derived parquet to
   `/lustre/<user>/hermes/sh26_full/` (crash-rebuild + non-server use).
   Watchdog restart; `server_info.json` (address, n_rows, git hash, columns).
2. Plots pull 1–4 columns per plot (never the full frame).
3. **bincount fast renderer**: hexbin/Mollweide/R–Z via `np.bincount` on
   quantized indices for N > ~5M (matplotlib.hexbin on 327M raw points is
   the real wall, not the read). GATE: per-bin sum identity + peak positions
   vs direct render on 50M (P01/P40/P65).
4. **Cost classes (user rule 2026-08-18)**: cheap plots run by default;
   expensive (per-star ML: P72 UMAP panel, P79 GMM full, P90, P91) only
   with `--include-expensive`. P73–P75 binned UMAP stay cheap (cost = cell
   count, not rows).

## Required columns (audited from all 94 SPECs, 2026-08-18)

- 51 raw: core posteriors ×18 (teff/logg/met/mass/age/dist/AV × 50/16/84);
  sky/astro ×6 (l, b, parallax_lindegren2021, parallax_error_fabricius2021,
  radial_velocity, radial_velocity_error); phot ×5 (G_march2021, BP, RP,
  g_mean_psf_mag_SH, Jmag ← gj0); SH21 ×6 (`*_sh21`); W25 ×1
  (dist50_weiler_w25); BJ21 ×2 (r_med_{geo,photogeo}_bj21); SHBoost ×5
  (xgbdist_{teff,logg,met,av}_mean, SHBOOST); nummodels.
- + `MISSING` (always); `ruwe` only if quality cuts (we run `--no-cuts`).
- + 7 derived: X/Y/Z/RGal, mg0, bprp0, gj0 (deps in lazy_catalog.DERIVED_DEPS).
- PM (pmra, pmdec, pmra_error, pmdec_error) NOT in catalog — needed by
  P82, P90–P93; join via `source_id` once a 402M PM parquet is located.
- Per-plot map: re-sweep `SPEC.columns`/`SPEC.derived` over
  `src/sh26/plots/p*.py` with an importlib loop (5 s).

## Catalog build recipe — sh2026_join_executed.ipynb (the proven join)

Build notebook: `/lustre/<user>/ipython/SH2025/reana/sh2026_join_executed.ipynb`
(produced the 402M catalog; final readback verified len 402,121,784).

Inputs (all keyed on `source_id`):
- A = `SH2025/IN_SH_2021_RERUN/WITH_SHBOOST/` (SH26, SHBoost branch)
- B = `SH2025/IN_SH_2021_RERUN/WITHOUT_SHBOOST/` (SH26, other branch)
- C = `SH2025/reana/final/results/shboost_splits/`
- D = `SH2025/reana/final/results/splits/`
- Gaia = `SH2025/gaiadr3/GaiaSource.float32.parq` (9 cols: ruwe, RV±err,
  varflag, GSPPhot teff/logg/mh/distance/ag)
- SH21 = `SH2025/gaiadr3/STAGE3_FINAL_SH_2021/sh_edr3_2021_v1.2.parq/` (24 cols)
- BJ21 = `SH2025/gaiadr3/BailerJones2021/gedr3dist_512_split.dump.parq/`
- W25 = `SH2025/gaiadr3/weiler25_distances_small.parq`

Join chain: `A⋈C` → `SHBOOST=True`, `MISSING=C.__matched_C.isnull()`;
`B⋈D` → `SHBOOST=False`, `MISSING=D.__matched_D.isnull()`; `base=concat`;
then LEFT `⋈Gaia ⋈SH21(→_sh21) ⋈BJ21(→_bj21) ⋈W25(→_w25)`; `to_parquet`.
All joins LEFT from base → one row per A∪B source (402,121,784).

**Key technique — CO-ALIGNED JOIN** (reuse for any 400M-row ID join,
e.g. the PM join):
1. `dd.read_parquet(path, engine="pyarrow", index=False)` — do NOT pass
   `columns=` at load (pyarrow `__index_level_0__` bug); select columns
   AFTER load; ensure the id col present; rename id → `source_id`.
2. EVERY input: `ddf.set_index("source_id", npartitions=1024, shuffle="disk")`
   → all tables partition-aligned on the key, so joins need NO hash-shuffle
   at join time (disk shuffle happens once per input).
3. Cluster used: <compute-node>, 64 procs / 128 threads / 1.94 TiB.
4. `to_parquet` warns "Sending large graph 12 MiB" — harmless.
5. NOTE: the notebook's red papermill "Exception at In [6]" banner is
   STALE (older failed run); the saved notebook completed successfully.

Related notebooks (lineage, not yet read): `sh2026_join.ipynb` →
`_corrected` / `_out` / `_out.optimized` / `_out.safer` → `_executed` (final).
`sh2026_raw.ipynb` = earlier naive `read_parquet(...).persist()` attempt
(no pruning, no filter) — superseded by the architecture above.
