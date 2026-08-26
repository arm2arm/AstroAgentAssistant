# P72 — ML search for the Galactic bar (technique reference)

Session-validated technique (2026-08-16) for detecting/characterizing the
MW bar in the SH26 catalog. Module: `src/sh26/plots/p72_bar_ml_dashboard.py`.

## Core physical insight (do NOT skip)

The bar is **not** a chemical/parameter cluster. Bar stars and old
thick-disk stars share Teff/logg/[M/H], so parameter-space clustering
(UMAP/HDBSCAN/GMM on astrophysical params) separates by evolutionary
family, NOT by structure — verified empirically: HDBSCAN on the old
subpopulation found 3 clusters, none bar-shaped. The bar's detectable
signature is **spatial**: a tilted overdensity ridge in the
(R_Gal, Z_Gal) plane, strongest in the **old (age ≳ 8 Gyr)** population.
ML is used to (a) document that parameter space does NOT isolate the bar,
(b) cluster for comparison, while the actual SELECTION is the tilted
ridge.

## Independent feature set (13 dims)

Galactocentric X, Y, Z (NOT l/b/dist50 — same 3-D position, not
independent, and l has a 360° seam that breaks distance metrics);
radial_velocity + rv_missing flag (RV is ~91% missing in 200k — include
as imputed value + missing indicator, never as a required axis);
teff50, logg50, met50, mass50, age50, G (phot_g_mean_mag_march2021),
BPRP = phot_bp_mean_mag − phot_rp_mean_mag, AV50.

Scaling: `QuantileTransformer(output_distribution="normal",
n_quantiles=2000, random_state=42)` (rank-Gaussian; robust to the
sentinels/NaNs after dropna).

## Pipeline (as implemented in P72)

1. Converged-only frame (hard MISSING==False filter from the loader).
2. Ridge fit on old annulus (age50≥8, R 3–12 kpc, |Z|<1.8 kpc):
   - KDE density map (scipy gaussian_kde on ≤250k subsample) for the
     VISUAL ridge curve only.
   - Reported slope: **binned density-weighted ridge** — mean Z in 24
     uniform R bins (≥5 stars/bin), polyfit(1). O(n) per iteration →
     200 Z-permutation nulls are cheap. A KDE-refit null loop (200 ×
     full KDE) is infeasible.
   - Sign test: z = slope / std(nulls), p = P(|null| ≥ |slope|).
3. Bar selection: old annulus stars within `bar_zwidth` (default 0.8 kpc)
   perpendicular distance of the fitted line.
4. ML: fixed 120k seeded subsample (reproducible on any dataset size) →
   UMAP(n_neighbors=50, min_dist=0.1, seed=42) + HDBSCAN
   (min_cluster_size=2%, min_samples=0.5% of subsample). t-SNE optional
   (sklearn 1.9: kwarg is `max_iter`, NOT `n_iter` — that changed).
5. Independent checks on the selection: l-distribution peak at l~0/180
   (bar LOS) vs l~90/270 wings; near-side (R<8.19) Z<0 excess for a
   positive tilt; age/met/CMD comparisons vs the old-annulus rest.

## 200k results (converged 163,374)

- Old annulus 51,740 (29.9% of annulus); bar candidates 34,149
  (66% of old annulus at 0.8 kpc width).
- Binned ridge slope +0.022 (~4σ, 200 nulls); KDE-ridge slope +0.156
  (inflated by smoothing on a curved ridge — report the binned one).
- Near side P(Z<0)=57% (med_Z −0.20 kpc) vs far side 52.6% — positive
  tilt direction. l-ratio (l~0 vs l~90/270) = 2.4.
- Measured tilt is much less than the canonical ~20°: we observe from
  INSIDE the bar, and 200k is a limited sample. Frame results as
  "bar candidates" (spatial selection), not "the bar."

## Environment notes

- ML deps (installed 2026-08-16, project venv): `umap-learn 0.5.12`,
  `hdbscan`, `scikit-learn 1.9.0`.
- UMAP with `random_state` forces `n_jobs=1` (library behavior) — 163k×13
  ≈ 1–2 min; fine.
- numpy 2.4.6 here: `ndarray.median()`/`.abs()` methods DO NOT EXIST —
  use `np.median`, `np.abs` (mean/std/var are fine).
- matplotlib 3.11: `cbar_label` only accepted by the `hexbin2d` helper;
  raw `ax.hexbin` + `cbar_label` → AttributeError. Multiple hexbins per
  axis: raw hexbin per artist + `fig.colorbar(hb, ax=ax, label=...)`.

## 50M run pattern

P72 runs on the full 50M converged sample (40.7M rows): ridge on the
full old annulus, ML on the same fixed 120k subsample.
`-p 72 --data data/sh26_joined_50m.parq --no-cuts --threads 16
--memory 64GB`, foreground.
