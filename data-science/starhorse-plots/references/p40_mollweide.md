# P40 — Mollweide all-sky density plot (session 2026-08-15)

File: `src/sh26/plots/p40_mollweide_density.py` (auto-registered, id 40).
Suite is now **40 figures** (p01–p40). Regenerate combined PDF with
`python3 scripts/combine_figures.py -i paper/figures/ -o sh26_all_200k.pdf`.

## What the user wanted (in order of correction)
1. Add a Mollweide projection plot of all-sky density.
2. **Fix:** "before plotting the data in lon needs to be shifted with periodic boundary condition" — raw `l` ∈ [0,360) double-mapped the sky. Fix: wrap to [−180,+180) and re-center the histogram grid before projecting.
3. **Style:** remove the square axes frame; coordinate labels belong on the ellipse; colorbar vertical and close to the plot.

## Implementation notes
- No basemap/cartopy/healpy on this host → analytic Mollweide in pure matplotlib.
- Ellipse: x ∈ [−2√2, 2√2], y ∈ [−1, 1]. Boundary: `x²/8 + y² = 1`.
- θ solver: bisection (40 iters, 1e-12) on monotone `f(θ)=sin(2θ)+2θ−s`,
  s = π·sinφ. Bisection over [0, π/2] on |s|, then sign-restore for s<0.
  Newton stalls near the poles (θ' ill-conditioned, f'→1 at π/2) — pole
  landed at y=0.9906 after 25 iters in debugging; bisection gives exactly 1.0.
- Control points to verify after any change:
  (0,0)→(0,0); (90,0)→(1.4142,0); (180,0)→(2.8284,0); (0,±90)→(0,±1.0000).
- Histogram 360×180 bins (nbins param) on wrapped (l, b); `pcolormesh` gets
  projected bin-EDGE coordinates (n_b+1 × n_l+1), `counts.T` for (n_b, n_l)
  cells, `LogNorm(vmin=1)`.
- Layout: `fig.add_axes((0.04, 0.10, 0.84, 0.78))` on a (11.5, 8.0) figure;
  `ax.axis("off")`; `fig.colorbar(im, ax=ax, orientation="vertical", pad=0.02,
  fraction=0.025)`.
- Graticule: meridians every 30° (skip 0/±180 = GC/anti-GC lines), parallels
  at ±30/±60; white alpha 0.35.
- Labels: latitudes (−30/0/+30°) via `_mollweide(−180, b)` on the left edge;
  longitudes (−135…+135°) at `x=(2√2/π)·λ` just below the ellipse; pole
  labels top/bottom (bottom pole offset to x≈1.9 to avoid the 0° label).
- GC/anti-GC: `ax.plot`+`ax.annotate` with **scalar** coords — a 1-element
  array in `xy` crashes matplotlib `ax.annotate` with
  `TypeError: only 0-dimensional arrays can be converted to Python scalars`.
- LSP false positives: dict-unpack (`ax.plot(mx, my, **gr)`) and
  `add_axes([list])` trip Pyright type checks; use tuples for rects.

## Run
```bash
cd /home/hermes/projects/SH26 && PYTHONPATH=src python -m sh26 plots -p 40 \
  --no-cuts --data data/sh26_cache_200k.parq
```
(~2.5 s; 201,057 points on the 200k cache.)
