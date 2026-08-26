# Axis-label convention: show the plotted column names (2026-08-14, user rule)

User mandate: "fix axis names so we recognize what columns are plotting" (after
P08/P10 got `(col: ...)` labels). Applied suite-wide the same day to all 39 plots.

## Rule

Every `set_xlabel`/`set_ylabel` appends the actual column on a second line:

```python
ax.set_xlabel(r"Distance $d$ [kpc]\n(col: dist50)")
```

- **Raw parquet column** → column name: `(col: dist50_sh21)`, `(col: met50)`
- **Derived column** (not a parquet field) → derived name: `(col: bprp0)`,
  `(col: mg0)`, `(col: RGal)`, `(col: ZGal)`, `(col: XGal/YGal/ZGal)`,
  `(col: plx_frac_err)`
- **Unit-converted alias** (P11/P12): label the alias actually plotted,
  `r_med_geo_bj21_kpc` / `r_med_photogeo_bj21_kpc`
- **Two-column derivations** show both:
  - `_uncert_helper`: `f"σ ({label})\n(cols: ({c16}, {c84}))/2"`
  - `_shboost_helper` diff hist: `f"SH26 − SHBoost [{unit}]\n(cols: {c26} − {c_boost})"`
  - `_shboost_helper` vs-G panel: `f"$G$ [mag]\n(col: {c_g})"`

## Where it lives (2026-08-14 state)

- Helpers bake it in — new comparison plots get it free:
  `_sh21_helper` (P08–P12), `_shboost_helper` (P27–P30), `_uncert_helper` (P21–P24, P31–P33)
- One-line edits in: P01–P07, P13–P16, P25, P26, P34–P39
- Suite-wide re-render after label changes:
  `PYTHONPATH=src python -m sh26 plots --all --no-cuts --data data/sh26_joined_50m.parq`
  then `python3 scripts/combine_figures.py -i paper/figures/ -o sh26_all_50m_optimized.pdf`

## P11 vs P12 — keep BOTH (user asked to remove one)

They look nearly identical but plot different BJ21 estimators:

- P11: `r_med_geo_bj21` — geoRMS, parallax-only
- P12: `r_med_photogeo_bj21` — photo-geometric, blends photometry

They agree for most stars and diverge where parallax is poor (far/faint).
Verdict 2026-08-14: both kept. If ever asked to drop one, drop P12 (fewer
sources have the photometric part) — but confirm first.
