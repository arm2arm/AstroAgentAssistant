# SH26 Project Structure — Verified Aug 8, 2026 (post-refactor)

Supersedes earlier versions: the starhorse2026 package, generate_all_plots.py,
and OLD_SH_analysis_notebooks/ were deleted 2026-08-08. Backup:
/home/hermes/projects/SH26_backup_20260808.tar.gz (14 MB).

## File layout

```
/home/hermes/projects/SH26/
├── config/
│   ├── storage.yaml              # data backend + paths
│   └── dask.yaml                 # 4w×4t=16 threads, 4×8GB=32GB cap, spill dir
├── src/sh26/
│   ├── __init__.py / __main__.py # python -m sh26 entry
│   ├── dataio.py                 # Dask Catalog: pruning, lazy derived cols
│   ├── analysis.py               # quality cuts (ruwe, plx SNR), summaries
│   ├── photutils.py              # Anders 2020-21 extinction (MG0/BPRP0/AG/ABP/ARP)
│   ├── registry.py               # PlotSpec auto-discovery from plots/
│   ├── context.py                # style + save + JSON provenance sidecars
│   ├── cli.py                    # list / plots subcommands
│   └── plots/                    # p01_cmd.py … p26_parallax_err_vs_dist.py
│       ├── _helpers.py           # hexbin2d, hist1d, binned_mean_std, errorbar_band
│       ├── _sh21_helper.py       # shared P17–P20 renderer
│       └── _uncert_helper.py     # shared P21–P24 renderer
├── tests/test_plots_smoke.py     # 27 tests, synthetic 5k frame, ~2.4 s
├── paper/figures/                # sh26_pNN_name.{png,pdf,json}
├── notebooks/                    # 4 thin frontends (imports need sh26 rename)
├── results/                      # CSV/JSON summaries (moved from img/)
├── scripts/combine_figures.py    # PyMuPDF merge
├── doc/                          # LaTeX paper (aa.cls, main.tex)
├── Makefile                      # plots / plots P=ids / combine / list / pdf
└── sh26_all_figures.pdf          # combined 26-page output
```

## Canonical commands

```bash
make plots                    # all 26 figures (8 s on 200k cache)
make plots P=1,3,7            # subset
make plots P=8-11             # range
make combine                  # sh26_all_figures.pdf
PYTHONPATH=src python -m sh26 plots --all --combine
PYTHONPATH=src python -m sh26 plots -p 1 --param p01.gridsize=300
```

## 26 figure ids

p01 cmd · p02 kiel · p03 kiel_met · p04 skymap_density · p05 skymap_av ·
p06 cartesian_dist · p07 rz_dist · p08–p11 teff/logg/met/mass _dist ·
p12 av_dist · p13–p16 teff/logg/met/mass _vs_dist · p17–p20 vs_sh21_* ·
p21–p24 teff/logg/met/mass _uncertainty · p25 color_color ·
p26 parallax_err_vs_dist

## Quality cuts (default; skip with --no-cuts)

ruwe ≤ 1.4, parallax > 10·σ_ϖ, 0.01 < dist50 < 100 kpc (pushdown).
