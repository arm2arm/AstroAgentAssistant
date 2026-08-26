# P91 pattern: full-catalog rest-sample UMAP with selection overplotted

Session 2026-08-18. P91 = schematic companion to P90: instead of
subsampling the box, embed a 1% seeded rest sample of the FULL converged
50M and overplot the P90 inner-box selection in red across UMAP / CMD /
X-Y panels.

## Recipe

- Sample: `RandomState(42).choice(40,719,146, int(0.01*N))` → 407,191;
  then **drop rows with any NaN in the 14 features** → 401,431 plottable
  (this mask MUST run before QuantileTransformer/UMAP — see pitfall).
- Cache key scheme: `md5("p91|n={n_plottable}|nn=15|md=0.1|seed=42|rf=0.01")[:12]`.
- Embedding via user-oneshot (`p91-run.service` runs the whole
  `sh26 plots -p 91` command with `PYTHONPATH=src`, `--no-cuts`,
  `--threads 16 --memory 64GB`) — for 401k the total fits in ~5 min so
  the plain plot command works where P90 full-box needed precompute
  scripts. UMAP on 401k×14-D: 273 s. Re-render from cache: 15 s.
- Selection overplot (user spec): red scatter (seeded cap 150k,
  s=0.3, alpha=0.12) on UMAP + CMD; X-Y panel uses a red `Rectangle`
  outline instead (a scatter there just re-draws the box). Hexbin base
  EXCLUDES selected stars so full-sample density stays unambiguous.
- CMD panel: P01 convention + `invert_xaxis()` (see SKILL.md style rule).
- `make(df, ctx)` receives the full-converged df (40.7M rows); the
  in-module column stack + mask is the only materialization (~3 GB
  float32→float64 columns via to_numpy).

## Pitfall hit (cost one failed run)

**UMAP `ValueError: Input contains NaN`** when the rest sample keeps NaN
rows. P90's module built its matrix on the box+finite population by
construction, so the trap didn't exist there; P91's full-catalog rest
sample contains no-PM-match / dropout rows. Fix: finite-in-14-D mask on
the rest sample BEFORE preprocessing; selection mask then operates on
the finite subset (box membership is implied by finiteness of XGal/YGal).

## User corrections this session (P90/P91, both applied)

1. P91 CMD: "make ranges and appearance similar to P1" → drop fixed
   extent, P01 labels, gridsize 300, invert_yaxis.
2. P91 CMD: "x axis must be flipped" → `invert_xaxis()`.
3. P90 middle CMD panel: "y and x axis are not same as in P1" → axes
   were swapped (mg0 on x); moved to (BP−RP)₀ x / M_G,0 y + P01
   conventions.
