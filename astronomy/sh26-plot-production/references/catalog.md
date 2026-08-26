# SH26 Figure Catalog + Data Reference

Read this before adding or modifying SH26 figures. Figure IDs are stable —
never reuse a retired ID. As of 2026-08-18 the suite is **P01–P94**.

## Helper modules (src/sh26/plots/)

| Helper | Purpose | Key params |
|---|---|---|
| `_helpers.py` | `hexbin2d` (rasterized, lognorm), `hist1d`, `binned_mean_std`, `errorbar_band`, `cmd_range` | gridsize, cmap, vmin |
| `_mollweide_helper.py` | `mollweide_map`, `mollweide`, `wrap_l`, `make_figure` (pure mpl, bisection solver) | nbins |
| `_sh21_helper.py` | `sh21_vs_sh26(df,ctx,spec,c21,c26,label,box=)` — 1:1 hexbin | box |
| `_shboost_helper.py` | `shboost_vs_sh26` — hexbin + diff hist + mean-diff vs G | diff_sign |
| `_uncert_helper.py` | `uncertainty_hist` — single σ=(q84−q16)/2 histogram | bins |
| `_sky_mollweide.py` | `diff_mollweide` (P43–P50), `sigma_sky_mollweide` (P61–P62), `median_per_pixel` | ref_scale, nbins, min_n |
| `_delta_d_helper.py` | `delta_d_stats` (P51–P53) — Δd hist + binned vs G | ref_scale |
| `_sigma_vs_g.py` | `sigma_vs_g` (P54–P60) — σ hist + binned vs G | bins |
| `_xyz_helper.py` | `xyz_plot` (P65–P70) — X–Y / X–Z / Y–Z hexbins | gridsize, cmap |
| `_disk_helper.py` | disk suite (P76–P82): `volume_weighted_profile`, `fit_scale_height` (nbody single-exp + 400 bootstrap), `gmm_2comp_noisy`/`gmm_responsibilities` (P79), `toomre_peculiar` (P80/P82 — see `toomre-pm-kinematics.md`) | see docstrings |

## Figure map

- P01–P07: CMD, Kiel, Kiel+met, sky density/A_V, cartesian, R–Z dist
- P08–P12: SH21/Weiler25/BJ21 1:1 hexbins (dist, A_V)
- P13–P16: teff/logg/met/mass vs dist
- P17–P20: SH26 vs SH21 {met,logg,teff,mass} hexbins
- P21–P24, P31–P33: σ posterior-width histograms (teff,logg,met,mass,dist,Av,age)
- P25–P26: color-color, parallax err vs dist
- P27–P30: SHBoost vs SH26 {teff,logg,met,Av}
- P34–P39: R–Z density per class
- P40–P42: Mollweide all-sky (density, median [Fe/H], median A_V)
- P43–P50: per-pixel median Δ{d,Av,teff,logg,met,mass} vs (l,b), Mollweide
  - P43 Δd vs Weiler25, P44 vs SH21, P45 vs BJ21 (ref_scale=0.001)
  - P46–P50 vs SH21 (A_V, T_eff, log g, [Fe/H], mass)
- P51–P53: Δd difference stats vs W25/SH21/BJ21 (hist + binned mean vs G)
- P54–P60: σ vs G for teff, logg, met, mass, dist, A_V, age
- P61–P62: median σ(dist), σ(T_eff) vs sky (Mollweide)
- P63–P64: non-converged (SHBOOST=False) CMD + G; T_eff–log g joint
- P65–P70: XYZ per class (converged, XP, RC, metal-poor, SMR, OB)
- P71: 10° GC box (|l|,|b|<5°): Δd + ΔA_V vs SH21
- P72: Galactic bar dashboard (v2, 2026-08-16) — bar is an IN-PLANE
  (X-Y) elongated overdensity of old stars through the GC, NOT a vertical
  Z(R) band (that grabbed ~66% of the old annulus = disk warp, rejected).
  base = old (age50≥8) |Z|<1 kpc, 1.5<R<5.5 kpc; axis = azimuthal density
  peak through GC (cross-checked vs 2nd moment); bar = within 0.8 kpc
  perp to axis (45% of base, selection elongation 2.48 vs base 1.13).
  Panels: X-Y/X-Z/Y-Z with bar overlay (red), R-Z edge-on ridge + null,
  l-b, CMD (mg0 vs bprp0), Kiel (teff-logg inverted), l-LOS, UMAP+HDBSCAN
  (13-D physics, fixed 80k), cluster table, age/[M/H]. 50M: 484k cands,
  axis φ=3.8°, ridge +2.9° (273σ), l-ratio 3.26. Uses derived
  XGal/YGal/ZGal/RGal/mg0/bprp0.
- P73: UMAP of the FULL 50M catalog via binned-density embedding (2026-08-16).
  Per-star UMAP on 40.7M rows is infeasible (HNSW + sparse eigendecomposition
  > any single node), so: 11-D physics features (XGal,YGal,ZGal,teff50,logg50,
  mass50,age50,met50,mg0,bprp0,AV50) binned on a quantile grid
  r = round(cell_cap^(1/D)) per dim (D=11, cap=3e5 → r=3, 3^11=177k total
  cells — occupied cells provably ≤ cap in ONE O(n) pass; no coarsening loop,
  no 11-D resolution cliff: halving from 8 skips 4→2 = 4.19M→2k). All rows
  counted (35.5M mapped = 87.3% after [q01,q99] trim); UMAP on the 33,813
  occupied cells. v2 (2026-08-16): per-row cluster labels via 177k-int16
  cell→cluster lookup; panels (g) CMD and (h) X-Y drawn as per-cluster
  hexbins (top-20 clusters tab20 colors, smaller ones grey, noise grey
  underneath, legend top-8 by star count). Run ~5.5 min on 50M bg scope.
P74: t-SNE vs UMAP (1x2), SAME binned-density cells as P73 (reuses
p73._grid_cells/_cell_centers); color = star count per hexbin (log) via
hexbin(C=cnt, reduce_C_function=sum) — CMD/Kiel count convention. t-SNE
perplexity=30 seeded n_jobs=8 (170s on 33.8k cells); UMAP unseeded.
P75: same 1x2 t-SNE/UMAP layout colored by cell-center [M/H] (met50,
mean per hexbin, viridis; met range on 50M cells -0.67..+0.13, med
-0.21). PITFALL (caught 2026-08-16): P73's `occ` was cell IDs, not star
counts — occ.sum()/argsort(occ) gave bogus n_points (~3e9), color scale,
top-12 and cluster n_stars. _grid_cells now returns (occ, edges, n_used,
ids_full, cnt); cnt = per-cell star counts (np.unique return_counts).
Check sidecar n_points ≈ stars_mapped after any binned plot change.
UMAP is unseeded n_jobs=8 (umap-learn forces n_jobs=1 when seeded;
verified 2026-08-16) + HDBSCAN eom (65–79 clusters, run-to-run). Panels:
UMAP density cloud (log10 stars/cell, cluster contours, top-12 stars),
top-12 cell table, UMAP-1 occupancy profile, full-catalog age/[M/H]/(BP-RP)0
histograms, per-cluster CMD + X-Y hexbins, summary. Uses column VIEWS of
the float32 frame (no n×D copy) + del df after panels → peak ~3.5 GB
(fits the 4 GiB background scope).

## Disk suite P76–P82 (2026-08-16/17, thin/thick disk analysis — plan P76–P82)

All on converged 50M (n_points 40,719,146 except noted); helpers in
`_disk_helper.py`; `--no-cuts` full-catalog per user rule.

- P76: thin/thick scale heights — chemistry-selected subsample fits
  (nbody method). h_thin (young age<6, met>−0.2) = 0.139 kpc;
  h(old & met<−0.4) = 0.221 kpc = EFFECTIVE (contaminated by old thin
  tail, lower limit on true h_thick); per-[M/H]-bin h is the headline
  (0.136→0.826 kpc over met +0.3→−2.1); thin fraction 0.7375 (weakly
  constrained); flaring visible in annuli. Breaks thin/thick degeneracy
  (Vieira 2023, Bovy 2015).
- P77: metallicity signature of the disk via Red Clump (3.13M stars,
  R 2–12, |Z|<3.5): median [M/H] falls −0.105 (|Z|<0.5) → −0.518
  (2.5–3.5); self-test (panel c): met cuts recover h 0.173 (rich) vs
  0.319 kpc (poor) — the Vieira-2023 result.
- P78: vertical age structure (two-infall test): age50/met50 medians vs
  |Z|, R 2–12, sigZ<0.5 clip (n_base 20.96M). Age gradient 5.08 Gyr at
  |Z|<0.05 → ~11.1 at 2.5+; caveat: photometric age σ~2–3 Gyr — the
  gradient is the signal, not individual ages.
- P79: per-star thin/thick GMM on (age50,met50) with per-star diagonal
  obs noise from q16/84; fit on 500k, responsibilities on 39.3M.
  Components COLLAPSED (both ~age 7.0, w 0.607/0.394) — p_thick ≈ 0.40
  nearly flat in R, mild rise in Z (0.375→0.437). PROXY membership only.
- P80: kinematics from RV subset only (3.09M, 7.6% of converged):
  V_pec,los = RV − solar − circular; σ(V) 34.6 (|Z|<0.1) → ~80 km/s
  (|Z|~3). RV-only caveat: no full U,V,W; superseded by P82 where PM
  allows.
- P81: scale heights from 3 standard candles (RC 2.35M, RGBT 1.37M,
  Miras 119k). RC h(Z) 0.259 (R 6–9) / 0.276 (9–10), RGBT 0.235/0.258 —
  agree within 0.02 kpc, both flare; Miras fully clipped by height
  error (distant AGB), no h. RC+RGBT agreement is the robust result;
  RGBT/Miras are photometric proxies (qualitative cross-check).
- P82: full U,V,W from PM (16.77M PM stars, 41.2% of converged).
  σ(W) 47.1→56.9 km/s over |Z| 0→1; ⟨V_pec⟩(R) zero-crossing at
  R≈7.7 kpc (inside R0=8.19) over 19 bins 3.5–13 kpc = flat
  rotation-curve residual. Transform + validation: see
  `toomre-pm-kinematics.md` (read BEFORE touching this code).

- P83: red-clump l–b sky maps (reference-style extinction-law systematics
  diagnostic, cf. Schlafly+ 2017 Fig. D.1): 3 stacked panels in
  0<l<250°, |b|<20°, 0.5° bins, min 3 stars/px — log10 count (grey),
  median teff50 (cividis), median met50 (RdYlGn); l axis 250→0 (fliplr +
  reversed extent). RC selection = P81 (teff 4500–6200, logg 2–3.5,
  G≤17.5). 50M: 3.48M RC total, 1.77M in region. PITFALL: hand-rolled
  per-bin median with np.argpartition returns INDICES — reindex into the
  segment (unit-test vs np.median on random bins before trusting).
- P84: Galactic X-Y hexbins by SHBOOST usage (P63-style 3 panels, shared
  count vmax from full sample): ALL 40.7M / True 23.58M (57.9%) /
  False 17.14M (42.1%). Convergence-filtered sample — the False panel is
  converged-but-no-SHBoost, NOT the old non-converged population. Extent
  -20..20 kpc.
- P85: X-Y by SHBOOST, central box X[-4,4] Y[-3,3] kpc pre-selected, ALL
  panels zoomed to the box, 3 panels (ALL/True/False) shared count scale:
  in-box 2.03M (True 1.44M 71% / False 0.59M 29% — SHBoost share rises in
  the inner disk vs 58/42 full-disk).
- P86: parallax [mas] vs [M/H] bins (5 bins, log-count step histos, 8.2
  kpc dotted line), central box X[-4,4] Y[-3,3], 3 SHBOOST groups, bins
  ordered by count, shared y. Box: 1.72M with pi>0 (True 1.32M /
  False 0.40M); >=-0.4 is 67%. P87: same on FULL converged: 39.39M
  (True 23.25M / False 16.14M); >=-0.4 is 79%. Watch: two open-ended
  met bins swap easily — verify bins partition (sum == total).
- P88: P86 for metal-rich met50>=0.3 central box — fine re-bins
  [0.30,0.56] (5 bins), 3 SHBOOST groups: 75,820 stars (True 62.0k /
  False 13.8k).
- P89: met50 [M/H] histogram, inner box (P85 selection), 3 SHBOOST
  groups, shared x/y: 2,032,412 stars; medians ALL −0.269, True −0.255,
  False −0.315 (xgbdist used preferentially for metal-rich nearby disk).
- P90: RAW per-star t-SNE + UMAP + CMD (bprp0 vs mg0) hexbins, inner box
  X[-4,4] Y[-3,3]. 14 features: l, b, dist50, teff50, logg50, met50,
  AV50, XGal, YGal, ZGal, mg0, bprp0, pmra, pmdec (pmra/pmdec from
  data/sh26_joined_50m_pm.parq — the base 50M schema lacks them). USER
  REJECTED the P73–P75 cell/binning for P90: raw per-star,
  QuantileTransformer (uniform) ONLY, no imputation. Box sample =
  1,941,062 (95.5% of the 2.03M box; 4.5% lack finite PM/phot).
  t-SNE pp30/1000it/8jobs + UMAP nn15/md0.1/8jobs, seed 42, /tmp cache
  keyed md5("p90|n=..|pp=..|mi=..|nn=..|md=..|seed=42[|sub=f]")[:12].
  `subsample` spec param (1.0 full; CLI override `--param p90.subsample=0.1`).
  1% test OK: 19,410 stars, t-SNE 74 s + UMAP 16 s (fits foreground).
  10% (194,106) via user-systemd oneshot (key 3f8c8b965afb). Full
  1.94M × 1000 iters NOT viable on host (~40-45 min/iter gradient
  phase, single-core) — subset-first per user. Ops detail:
  `p90-long-embeddings.md` + `p90-embeddings-oom-newton-offload.md`.

- P91: UMAP (14-D) full-catalog 1% with inner box overplotted + CMD + X-Y.
- P92: Δd vs SH21 — inner box (row 1) vs full catalog (row 2).
- P93: SH21 vs SH26 distance, inner box vs full catalog (2 rows).
- P94: Magellanic Clouds enhanced view (2026-08-18): 2x3 — LMC
  (l 272-292, b -43..-23) + SMC (l 300-313, b -18..-2) sky hexbins
  (1.15M converged in-box), combined distance histogram with member
  bands (LMC 38-62 kpc: 82,681 members, clean peak ~49 kpc; SMC
  45-75 kpc: 1,313), dereddened member CMDs, member T_eff-[M/H].
  `derived=[]` — mg0/bprp0 computed inside make() on in-box rows only.
  NOTE: foreground disk dominates both sightlines (~99% <10 kpc); SMC
  member sample modest. **LMC l~280 b~-33, SMC l~306 b~-10** — verify
  with astropy before any MC work (first draft wrongly used l~70-95,
  the wrong side of the sky). Rendered via user-systemd oneshot +
  `scripts/run_p94_direct.py` (Dask stalled under host RAM pressure).

## Class cuts (derived from SH26 posteriors)

| Class | Cut | Where |
|---|---|---|
| converged | `nummodels > 0` | P34, P65 |
| non-converged | `SHBOOST == False` | P35, P63–P64 |
| Red Clump | 4500<Teff<6200 & 2<logg<3.5 | P36, P67 |
| metal-poor | met50 < −1 | P37, P68 |
| super-metal-rich | met50 > +0.5 | P38, P69 |
| OB | Teff > 10000 K | P39, P70 |
| XP | logg ∈ [1.5,3.0] & Teff < 5500 K | P66 |

## 50M row counts (n_points, reference for QA)

converged 40.7M; non-converged (SHBOOST=False) 23.2M; XP 3.0M; RC 3.8M;
metal-poor 459.6k; SMR 44.7k; OB 131k; P64 (Teff-logg finite, non-conv) 17.1M;
P71 GC box 1.65M; P72 bar candidates 484k (old base 1.07M); P73 binned UMAP
33,813 occupied cells / 35.5M stars mapped (50M converged).
Disk suite: P77 RC 3.13M; P78 base 20.96M (sigZ<0.5 clip); P79 GMM base
39.32M; P80 RV 3.09M (7.6%); P81 RC 2.35M / RGBT 1.37M / Miras 119k;
P82 PM 16.77M (41.2%).
P90 box: 2,032,412 converged in X[-4,4] Y[-3,3]; 1,941,062 finite in
all 14 embedding columns.
Comparators: 40.7M rows have finite (l,b,dist50) + ref.

## Data gotchas (column level)

- `l` ∈ [0,360) → `wrap_l()` before binning/Mollweide.
- Photometry (Gaia PSF/SM G..Y, 2MASS JHK, WISE W1/2): `-1e4` = no phot (sentinel).
- `xgbdist_{teff,logg,met,av}_mean`: `-9999` = no SHBoost match; `_std` can be 6.4e10.
- `r_*_bj21`: parsecs (÷1000 → kpc). `dist50`, `dist*_weiler_w25`, `*_sh21`: kpc.
- 50M: 9.28M `MISSING` (no SH26 posterior), 23.2M `SHBOOST==False`.
- G magnitude: `phot_g_mean_mag_march2021` (6–18.5).
- pmra/pmdec: base 50M schema does NOT carry them; use
  `data/sh26_joined_50m_pm.parq` (pre-joined) or `data/pm_50m.parquet`
  (49,993,036 rows: pos, source_id, pmra, pmdec, pmra_error, pmdec_error,
  astrometric_params_solved). **Full 402M v190826 catalog DOES carry all 4
  PM columns for every row** (verified 2026-08-21: 0 nulls, 0 zeros, median
  pmra −2.235 µas/yr, |pmra|<1 in 18.4% — real data, not placeholders).
  P82/P90–P93 are therefore unblocked on the full catalog.
- Parallax column is in **mas** (50M median 0.385 ≈ 2.6 kpc); 8.2 kpc
  line = π 0.122 mas.

## Provenance

Each figure writes a JSON sidecar `sh26_pNN_<name>.json` with plot_id,
n_points, params, columns, git hash, timestamp, dataset, and any extra
cuts (quality_cuts, dist_cut_kpc). This is the "refer and correct" anchor
the user relies on.
