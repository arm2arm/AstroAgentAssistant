# Disk thin/thick decomposition (Wave 1) — status, method, pitfalls

Session: 2026-08-16. User asked for thin/thick disk structure analysis;
workflow: research → written plan → explicit "go" → implement wave by wave,
pausing between waves. Wave 1 scope: P76 (scale heights), P77 (metallicity
decomp), P79 (per-star P_thick GMM). **STATUS: P76–P79 NOT implemented.**
`src/sh26/plots/_disk_helper.py` exists; validated for the parts below, but
has one known pending cleanup (MCMC walker-init clamping) and the
constrained subsample fits are NOT yet validated end-to-end on synthetic data.

## Data facts (200k cache probe)
- Converged (MISSING==False): 163,374 / 201,057 rows (~81%).
- met50, age50, dist50 → XGal/YGal/ZGal/RGal: **100% finite** on converged.
  met50 range −2.28…+0.56, median −0.21; (met84−met16) median 0.32.
- radial_velocity: **only 8.8% finite** (14.4k) → kinematics is a
  consistency check, never the headline.
- Proper motions: **not in the catalog** (Gaia DR3 join needed for full
  U,V,W / nbody-style kinematics).
- Red clump (4500<Teff<6200, 2<logg<3.5): 15.3k on 200k → ~3.8M on 50M
  (standard candles; typical studies use 1e4–1e5).

## Literature anchors (verified 2026-08-16)
- Vieira et al. 2023 (Galaxies 11, 77): Gaia DR3, sech² fits + kinematic
  fast/slow split: h_thin ≈ 280 pc, h_thick ≈ 800 pc; 2-comp fits break at
  |Z|>700 pc (halo term needed).
- Bp/Rp spectra series part IV (MNRAS 2025/26, RC + MCMC two-sech²):
  h_thin V-shaped in R (bar heating inside R<6.4 kpc); h_thick 0.45→0.75
  kpc from R=2.5→8 kpc.
- Khanna et al. 2025 (A&A 701): old all-sky disk via red clump.
- Recio-Blanco 2024: bimodality in mono-metallicity RC sequences.
- Park et al.: thin-vs-thick-vs-3-component (old-thick) debate → do the
  BIC 2-vs-3 test.
- ESA 2022/23: thick disk formed ~13 Gyr ago (age anchor).
- Paper state: `doc/main.tex` "Improved Milky Way density maps" subsections
  are skeletons (Sgr/MCs/Inner Galaxy empty, Discussion empty) → high value.

## THE thin/thick degeneracy (verified, with numbers)
A two-component exponential TOTAL |Z| profile does NOT uniquely fix
(h_t, h_T, f): a 1e10-count (noise-free) Poisson draw from a true
(300, 800, 0.8) kpc profile over |Z|<3.5 kpc has MLE (268, 682, 0.70),
2.5e8 log-lik ABOVE the truth; the MLE profile still beats the truth on
total counts even though it's 31% off at |Z|=3.5 (most counts live
|Z|<1.5). NEVER present "2-comp fit of the total profile = the scale
heights" as a result — it is an overclaim.

## Method (user-approved 2026-08-16): break the degeneracy with chemistry
- h_thin(R): fit young/metal-rich subsample (age50<5, met50>−0.3,
  thin-dominated) with h_T FIXED (nuisance, default 0.80 kpc); h_t free.
- h_thick(R): fit old/metal-poor subsample (age50>9, met50<−0.5, |Z|>0.5
  kpc, thick-dominated) with h_t FIXED to the annulus value above; h_T free.
- f(R) (thin fraction; BOTH exp terms equal 1 at z=0 so f/(1−f) IS the
  midplane number-density ratio): fit the FULL profile with both h FIXED; f free.
- Model: n(z) = f·exp(−|z|/h_t) + (1−f)·exp(−|z|/h_T). Exponential (not
  sech²): curvature at z=0, no flat-bottom degeneracy; local approx to the
  sech² used by nbody fits.
- Volume weighting: per-star weight 1/σ_plx; R-Jacobian is constant in Z
  within an annulus → absorbed by normalisation. Clip
  σ_plx ≤ 0.05·max(|Z|, 0.3) + 0.02.

## _disk_helper.py (src/sh26/plots/) — validated state
- `exp_profile`, `volume_weighted_profile`, `fit_exp_mcmc(zc, n, fix_ht=,
  fix_hT=)` (ALL kpc: h_min=0.02, h_max=3.0), `gmm_2comp_noisy(X, S)`
  (EM with per-star obs noise), `gmm_responsibilities` (fast E-step for
  applying a subsample-fit mixture to the full catalog).
- **Single-component fits VERIFIED**: pure Exp(0.3 kpc) profile from 1e6+
  stars recovers h=0.300 exactly (1-comp ML scan); Exp(0.8) → 0.770.
- 2-comp full-profile MCMC reproduces the degeneracy (269/682/0.70) —
  consistent with the likelihood surface.
- **PENDING CLEANUP**: the walker-init clamping loop in `fit_exp_mcmc`
  (around `pos = pos0 + spread*…`) is convoluted for the mixed
  free/fixed-parameter cases; simplify before trusting constrained runs.
  Constrained (fix_ht/fix_hT) path is NOT yet validated end-to-end.

## emcee 3.1.6 pitfalls (all hit this session)
- `EnsembleSampler(nwalkers, ndim, log_prob)` — NO `seed=` kwarg; `run_mcmc`
  has no `rng=` kwarg. Seed via `np.random.seed(seed)` before the run
  (emcee uses the global numpy state); use default_rng for init spread.
- **Default RedBlueMove FREEZES (acceptance 0.0) when any initial walker
  has −inf log_prob** (init outside prior). Fix: clamp every walker inside
  prior support at init. With clean inits, affine-invariant moves are fine
  (Stretch/DE/DESnooker all agree to 0.1%).
- Moves available: DEMove, DESnookerMove, GaussianMove, KDEMove, MHMove,
  Move, RedBlueMove, StretchMove, WalkMove — NO SliceMove.
- `sampler.acceptance_fraction` is a PROPERTY, not a method.

## Unit / API traps
- z in **kpc** everywhere; h-prior and likelihood sanity checks must use
  the same units — a leftover `h > 1.0` check (pc-scale on kpc data) turns
  every proposal into −inf → walkers freeze silently.
- numpy 2.4: `np.trapz` removed → `from numpy import trapezoid`.
- Synthetic exponential |Z|: z = ±x (equal-prob sign); **NOT** x·(2U−1) —
  that halves the magnitude (mean|2U−1|=0.5) and fabricates a false
  "2× fitter bias".

## Planned figures (Wave 1 — NOT built)
- P76 `disk_scale_heights`: per-annulus (R edges 1.5/4/7/12) N–|Z|
  volume-weighted + fit overlay; h_thin(R), h_thick(R) ±1σ (16–84); f(R);
  BIC 2-vs-3; local zoom ±1.5 kpc.
- P77 `disk_met_decomp`: [M/H] vs |Z| RC hexbin; per-|Z|-bin metallicity
  distributions; h fits for met>0 vs met<−0.3 (tests that OUR photometric
  [M/H] independently separates the components).
- P79 `disk_gmm_prob`: GMM on (age50, met50) with per-star Σ from
  (age16/84, met16/84) → P_thick per star; R–Z hexbin colored by mean
  P_thick; f_thick(R), f_thick(|Z|); P_thick vs |Z| with RV-subset cross-check.
