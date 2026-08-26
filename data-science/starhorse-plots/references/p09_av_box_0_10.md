# P09 A_V box cut (2026-08-15) — supersedes part of comparison_plot_box_ranges.md

Applied to P09 (`src/sh26/plots/p09_vs_sh21_av50.py`) on 2026-08-15 after user
requested "p9 make axis range 0:10":

```python
return sh21_vs_sh26(df, ctx, SPEC, "av50_sh21", "AV50",
                    r"$A_V$ [mag]", box=(0, 10))
```

`box=(lo, hi)` in `_sh21_helper.sh21_vs_sh26` cuts data outside the box on
BOTH axes and sets xlim/ylim to it; the red 1:1 line spans exactly the box.
Same one-line pattern as P08/P10 (`box=(0.0, 50.0)` kpc) and P11
(`box=(0, 50)` kpc).

Column trap: SH26-side A_V is `AV50` (uppercase) vs SH21-side `av50_sh21`
(lowercase prefix); quantiles are `AV16`/`AV84` (uppercase) and
`av16_sh21`/`av84_sh21`. Do NOT confuse A_V with the distance columns.

Quick re-render (200k cache, ~1.5 s):

```bash
cd /home/hermes/projects/SH26 && PYTHONPATH=src python \
  -m sh26 plots -p 9 --no-cuts --data data/sh26_cache_200k.parq
```

Full-suite 200k run verified 2026-08-15: `--all --no-cuts --data
data/sh26_cache_200k.parq` → 39 ok / 0 failed in ~17 s (all enriched columns
present in the 200k cache, so nothing skips), then
`python3 scripts/combine_figures.py -i paper/figures/ -o sh26_all_200k.pdf`.
