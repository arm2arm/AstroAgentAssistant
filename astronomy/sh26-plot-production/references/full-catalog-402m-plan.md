# Full 402M Catalog Migration — Plan (2026-08-18)

Canonical in repo: `doc/full_catalog_plan.md` (commit 18a5a55). This
file is the skill-level copy; the repo file is source of truth for
live status (dataset prep happens in a separate session).

## Data facts (verified 2026-08-18)

- Full catalog: Newton `/lustre/<user>/ipython/SH2025/reana/final/combined/sh26_final_joined/`
  - 4,094 parts, 210 GB, **402,121,784 rows**, 129 columns
  - Schema = 50M schema + `source_id` (+ g/r/i/z/y_mean_mag_error_SH extras)
  - **No pmra/pmdec** (same as 50M base)
- Expected converged (MISSING==False): ~327M (50M rate: 9.28M/50M =
  18.6% MISSING → 40.7M converged; extrapolate the rate).
- Reserved node: `<compute-node>.nnew` from Newton (141.33.4.144) — hmemt
  class, 96 cores (4×24), 770 GB RAM. Exclusive reservation for this
  work (no preemption concern). Access model (direct SSH login vs
  sbatch-only) unverified — first probe task; determines watchdog design.

## Required columns (audited from all 94 SPECs, 2026-08-18)

Raw (51):
- Core posteriors (18): teff50/16/84, logg50/16/84, met50/16/84,
  mass50/16/84, age50/16/84, dist50/16/84, AV50/16/84
- Sky/astrometry (6): l, b, parallax_lindegren2021,
  parallax_error_fabricius2021, radial_velocity, radial_velocity_error
- Photometry (5): phot_g_mean_mag_march2021, phot_bp_mean_mag,
  phot_rp_mean_mag, g_mean_psf_mag_SH, Jmag (Jmag feeds derived gj0, P25)
- SH21 (6): dist50_sh21, teff50_sh21, logg50_sh21, met50_sh21,
  mass50_sh21, av50_sh21
- Weiler25 (1): dist50_weiler_w25
- BJ21 (2): r_med_geo_bj21, r_med_photogeo_bj21
- SHBoost (5): xgbdist_teff_mean, xgbdist_logg_mean, xgbdist_met_mean,
  xgbdist_av_mean, SHBOOST
- Flags (1): nummodels
- Always: MISSING (hard convergence filter)
- Optional (only if quality cuts on; we run --no-cuts): ruwe
- PM (4, NOT in full catalog — join via source_id): pmra, pmdec,
  pmra_error, pmdec_error → needed by P82, P90, P91, P92, P93

Derived (7), compute in map_partitions:
- XGal, YGal, ZGal, RGal — from l, b, dist50 (R0 = 8.19 kpc)
- mg0 — phot_g_mean_mag_march2021, AV50, dist50, teff50
- bprp0 — phot_bp_mean_mag, phot_rp_mean_mag, AV50, teff50
- gj0 — phot_g_mean_mag_march2021, Jmag, AV50, teff50

Per-plot column map: regenerate anytime by importlib-sweep over
`src/sh26/plots/p*.py` reading SPEC.columns + SPEC.derived.

## Architecture

1. Served Dask table on <compute-node>:
   - LocalCluster ~24 workers × 4 threads × ~24 GB
   - read parquet once (column-pruned) → MISSING==False → derived in
     map_partitions → persist() (~60–70 GB float64, ~35 GB float32)
   - compact converged+derived parquet → /lustre/<user>/hermes/sh26_full/
     (crash rebuild takes minutes; also usable without the live server)
   - watchdog restart script; server_info.json (address, n_rows,
     git hash, build time, column list)
2. Client: plots pull only their 1–4 columns (seconds), never the frame.
3. bincount fast renderer for hexbin/Mollweide/R–Z at N > ~5M
   (np.bincount on quantized indices → pcolormesh/hexbin at cell centers;
   visually indistinguishable at paper resolution).

## Cost classes (user rule: no expensive plots by default)

- cheap (default `--all`): P01–P89 bincount-renderable; P73–P75 as-is
  (binned-density UMAP — cost is cell count, not rows)
- expensive (opt-in `--include-expensive`): P72 UMAP panel, P79 GMM
  full-scale, P90, P91 (per-star t-SNE/UMAP)
- PM-dependent (P82, P90–P93): stay 50M until a full PM join exists

## Steps (each with a gate)

0. Probe <compute-node> (read-only): nproc/free/python/dask versions, /lustre
   read speed, login vs sbatch model, converged count on 402M.
1. Repo changes (local), gated on 50M: SPEC.cost + --include-expensive;
   bincount fast path in _helpers.hexbin2d + mollweide/R–Z helpers;
   --data full-path support; config/dask_full.yaml.
   GATE: P01/P40/P65 on 50M — bincount vs direct: per-bin sum identity,
   peak positions unchanged, sidecar n_points equal.
2. Served-table build (dataset-prep session, <compute-node>): serve.py + persist
   + compact parquet + watchdog + server_info.json.
   GATE: table.count() + 2-column pull end-to-end.
3. Cheap campaign on <compute-node> (Agg backend): figures + JSON sidecars →
   /lustre/<user>/hermes/sh26_full/figures/.
   GATE: programmatic QA (sidecar n_points vs probe count,
   non-white fraction > 0.05 per figure).
4. Fetch + sh26_all_full.pdf rebuild, commit.
5. Paper: numbers from full sidecars (converged ≈327M, RC/SMR/bar/
   scale-height n's), rebuild PDF, commit + push.

## Open questions (ask user before step 5)

1. Where is a 402M-scale PM parquet? (unblocks P82/P90–P93)
2. <compute-node> access model (direct SSH vs sbatch) → watchdog design.
3. Confirm: full-run numbers ARE the paper's claim (≈300M sources).
