# P83 sky-map layout recipe (user-iterated final, 2026-08-17)

Reference-style RC l–b sky maps (cf. Schlafly+ 2017 Fig. D.1), produced in
`src/sh26/plots/p83_rc_sky_systematics.py`. This is the final, user-confirmed
layout — reuse it for any future stacked sky-map figure.

## Sample & binning

- Red Clump, same selection as P81: teff50 4500–6200 K, logg50 2.0–3.5,
  G (phot_g_mean_mag_march2021) ≤ 17.5. 50M: 3.48M RC total.
- Region: 0 < l < 250°, −20 < b < 20°; 0.5° bins; min 3 stars/px
  (masked otherwise). 50M: 1.77M in region, 39,076 filled pixels.
- Binned medians via stable-sort + per-bin np.argpartition. PITFALL:
  argpartition returns INDICES — reindex into the segment
  (`seg[np.argpartition(seg, kth)[kth]]`), never `part[-1]` on the
  indices array (that yields bogus "median" values, e.g. 0.5–1805 "K").
  Unit-test vs np.median on random bins before trusting a hand-rolled
  binned statistic.

## Layout (all values user-confirmed through 5 correction rounds)

```python
fig, axes = plt.subplots(3, 1, figsize=(10.5, 8.0),
                         gridspec_kw=dict(hspace=0.26, left=0.05,
                                          right=0.935, top=0.975,
                                          bottom=0.055))
```

Rules (user corrections, in order received):
1. **Tight layout** via `gridspec_kw` only — `fig.tight_layout()` is
   INCOMPATIBLE with inset colorbar axes (warns + misplaces).
2. **Colorbars: inset axes flush at the panel right edge**, exactly
   panel height, ~3% gap:
   `cax = ax.inset_axes([1.03, 0, 0.035, 1])`; `fig.colorbar(im, cax=cax)`.
   NOT `fig.colorbar(im, ax=ax, fraction=0.02, pad=...)` (default
   placement leaves them short of panel height and far from the plot).
3. **Black frame on every panel**: all 4 spines black, lw 1.4; colorbar
   axes too (lw 1.0, white face).
4. **No gridlines**: the global style (`seaborn-v0_8-whitegrid` in
   `context.py:38`) re-adds a grid — call `ax.grid(False)` per panel.
5. **x-axis flipped 250→0**: `extent=(l_hi, l_lo, b_lo, b_hi)` +
   `np.fliplr` on the (n_b, n_l) arrays + `ax.set_xlim(l_hi, l_lo)`.
6. **x tick labels + xlabel on EVERY panel**: never `sharex=True` (it
   strips labels from the upper rows).
7. **Count panel**: map is log10(count), but the colorbar is labeled in
   LINEAR counts — `cb.set_ticks([0,1,2,3])`, `set_ticklabels(["1","10",
   "100","1000"])`.
8. **Fixed color windows when the user asks**: teff50 panel
   `vmin=4500, vmax=5000`; met50 panel `vmin=-0.1, vmax=0.4`.
   Out-of-range pixels saturate at the colormap ends — expected, not a
   bug (do not "fix" by auto-scaling).

## Colormaps

count: gray | teff50: cividis | met50: RdYlGn. All `interpolation="nearest"`.

## QA

- 50M run: foreground, `--no-cuts --threads 16 --memory 64GB`, ~1 s
  (single plot) + Dask spin-up; cold-cache `CommClosedError` is the
  known transient — re-run warm.
- `ctx.save(fig, SPEC, n_points=n, extra={...})` — note the kwarg is
  `extra`, not `extras` (TypeError otherwise).
- Check sidecar medians are inside the selection window (teff50 within
  4500–6200 etc.) — an out-of-window range means a binned-statistic bug,
  not a data problem.
