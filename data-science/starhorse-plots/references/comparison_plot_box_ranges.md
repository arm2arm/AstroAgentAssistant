# Ranging comparison plots — box cut (P08/P10, 2026-08-14)

`_sh21_helper.sh21_vs_sh26(df, ctx, spec, c21, c26, label, name21="SH21", box=None)`
accepts `box=(lo, hi)`:

- **Cuts** points outside [lo, hi] on BOTH axes (mask applied before hexbin)
- **Sets** `xlim`/`ylim` to the box; the red 1:1 line spans exactly the box
- Without `box`, axis limits are data-driven (min/max of surviving points)

## Applied (2026-08-14)

P08 (`dist50_sh21` vs `dist50`) and P10 (`dist50_weiler_w25` vs `dist50`) set to
`box=(0.0, 50.0)` kpc — user requested "[0:50]" range. Edit is one line per plot:

```python
return sh21_vs_sh26(df, ctx, SPEC, "dist50_sh21", "dist50",
                    r"Distance [kpc]", box=(0.0, 50.0))
```

## Quick re-render

```bash
cd /home/hermes/projects/SH26 && PYTHONPATH=src python \
  -m sh26 plots -p 8,10 --no-cuts --data data/sh26_joined_50m.parq
```

~30 s on the 50M cache — column-pruned Dask, no full-catalog materialization.
Outputs: `paper/figures/sh26_p08_vs_sh21_dist50.{png,pdf,json}`,
`sh26_p10_vs_weiler_w25_dist.{png,pdf,json}`.

## Why P08 ≠ P10 columns

X column is the external catalog's distance for the same source:
- P08: `dist50_sh21` — StarHorse 2021 (SH21) distance, kpc
- P10: `dist50_weiler_w25` — Weiler et al. 2025 (W25) distance, kpc

Y is always SH26 `dist50`. Both are distinct published catalogs (different
sampling/methods), so scatter differs between the two. Neither needs unit
conversion (unlike BJ21 `r_med_*_bj21`, which is in parsecs — see SKILL.md
UNIT TRAP).
