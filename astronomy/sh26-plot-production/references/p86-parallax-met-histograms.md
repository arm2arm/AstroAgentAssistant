# P86 — Parallax histograms by [M/H] (reference-style, central box)

Built 2026-08-17 in `src/sh26/plots/p86_parallax_met_center.py`.
Reference figure: filled parallax histograms per metallicity bin on a
log-count axis with a dotted line at 8.2 kpc.

## Recipe

- Sample: P85 central box X[−4,4] × Y[−3,3] kpc (derived XGal/YGal),
  converged-only, plus `parallax_lindegren2021 > 0` and finite.
  50M: 1.72M (of 2.03M in box; ~15% lack valid positive parallax).
- Bins (met50, reference palette): <−1.7 purple | −1.7…−1.2 teal |
  −1.2…−0.8 gold | −0.8…−0.4 #FF6644 | ≥−0.4 magenta.
  50M counts: 574k / 11.3k / 40.7k / 517k / 1.15M.
- 100 bins 0–1 mas, log y from 1. Dotted line `pi = 1/8.2 mas ≈ 0.122`.
- Step-histogram idiom (got two failures before landing):
  ```python
  h, _ = np.histogram(x, bins=edges)
  ax.fill_between(edges[:-1], h, 1, step="pre", color=c, alpha=0.55)
  ax.step(edges[:-1], h, where="pre", color=c, lw=1.0)
  ```
  - `fill_between(..., step="mid")` on `edges` (n+1 pts) with `h`
    (n pts) → `ValueError: 'x' has size 101, but 'y1' has size 100`.
  - `ax.plot(..., step="pre")` → `AttributeError: Line2D.set() got an
    unexpected keyword argument 'step'` — step belongs to
    `Axes.step(..., where=...)` or `fill_between`, never `plot`.

## Column gotcha

`parallax_lindegren2021` is in **mas** (median 0.385 ≈ 2.6 kpc) despite
the "lindegren" name — NOT radians, NOT arcsec. Range includes negative
outliers (−5.6 … 77.5 mas), so always mask `pi > 0` before binning.

## User workflow note

User asked for a "similar plot" from a pasted reference image — the
deliverable matched by: same x-axis (parallax mas, 0–1), same bin
boundaries/palette, same 8.2 kpc line, same log counts. When reproducing
reference figures, mirror axis ranges/labels/binning first; colors second.
