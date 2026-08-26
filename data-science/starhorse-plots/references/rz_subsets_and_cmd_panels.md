# R–Z subsets (P34–P39) data cut + P36 dual-panel CMD convention (2026-08-14)

## Distance boxes: P08/P10/P11/P12 all [0, 50] kpc

All four distance-comparison plots (`_sh21_helper`, `box=(0, 50)`) share
identical axes — P08/P10 set first on user request "[0:50]", P12 (BJ21
photo-geo) set to the same box later the same day; P11 already had it.
See comparison_plot_box_ranges.md for the helper contract.

## R-cut: 0 < R < 100 kpc on P34–P39

User mandate: "P34–P39 the xaxis select data: 0<R<100". Implemented as a DATA
mask (not just axis limits) so the hexbin fills the window:

```python
d = d[(d["RGal"] > 0) & (d["RGal"] < 100)]
```

Applied to the filtered sample in each `make()`:
- P34 with SHBoost (nummodels>0) / P35 without SHBoost (SHBOOST=False) /
  P37 metal-poor / P38 SMR / P39 OB:
  filter applied to `d` right after the subset mask

Terminology (user correction 2026-08-15): SHBOOST = whether SHBoost (xgbdist)
was used in the calculation, NOT convergence. Titles say "with/without SHBoost".
- P36 red clump: filter applied to `rc`

~150 s for all six on the 50M cache (`-p 34-39`).

## P36 dual panel: R–Z + CMD

User asked for a second CMD next to the R–Z panel of the red-clump plot.
P36 is now a 2-panel figure (`figsize=(15, 6.5)`):

- (a) R–Z hexbin of the RC subset (0 < R < 100, as above)
- (b) CMD of the SAME RC sample — `mg0` vs `bprp0`, `ax.invert_yaxis()`,
  YlOrBr to match panel (a), suptitle carries the RC selection + count

`SPEC.derived` must include `["RGal", "ZGal", "mg0", "bprp0"]` so the
column-pruned Dask loader fetches the photometry columns (`mg0`/`bprp0`
deps: `phot_g_mean_mag_march2021`, `phot_bp_mean_mag`, `phot_rp_mean_mag`,
`AV50`, `teff50`).

## Convention: CMD panels use P1's axis range (user rule, 2026-08-14)

"use always the cmd plots axis range same as on P1". P1 is data-driven
(full catalog, no cuts), so sub-sample CMDs (e.g. P36 RC) must fix their
limits to the FULL-catalog bounds, computed from the unfiltered `df`:

```python
from sh26.plots._helpers import cmd_range
xmin, xmax, ymin, ymax = cmd_range(df)   # full catalog, finite values only
...
ax.invert_yaxis()
ax.set_xlim(xmin, xmax)
ax.set_ylim(ymax, ymin)   # inverted y: pass (max, min) order
```

`cmd_range(df, col_x="bprp0", col_y="mg0")` lives in `_helpers.py`.
**Pitfall:** after `invert_yaxis()`, `set_ylim(ymax, ymin)` — reversed order —
or the limits flip and you get a blank panel.

Any NEW CMD panel added to the suite must use `cmd_range` on the full
catalog, not on the sub-sample, so figures are directly comparable.

## Re-render + combine

```bash
cd /home/hermes/projects/SH26 && PYTHONPATH=src python -m sh26 plots \
  -p 34-39 --no-cuts --data data/sh26_joined_50m.parq
python3 scripts/combine_figures.py -i paper/figures/ -o sh26_all_50m_optimized.pdf
```
