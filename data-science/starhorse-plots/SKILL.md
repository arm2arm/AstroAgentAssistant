---
name: starhorse-plots
title: StarHorse plotting recipes — SH/SH26
description: |
  Class-level plotting skill for working with StarHorse outputs (SH/SH26). Encodes preferred plot types, axis ranges, column conventions, and reproducible notebook patches used across sessions. Designed to be a living umbrella: add references/ examples from sessions in references/.
tags:
  - starhorse
  - plotting
  - notebooks
  - data-visualization
  - reproducibility
---

# Overview

This skill documents the canonical plotting patterns we use when visualizing StarHorse outputs (dist50, teff50, met50, log50, av50, etc.). It captures:

- preferred plot types and when to use them (hexbin / hist2d / pcolormesh for dense clouds, scatter for small samples, hvplot/datashader for interactive multi-million-point views, healpy/cartopy for sky maps),
- sensible axis defaults and unit/scale rules (which columns are already log-scaled, recommended ranges),
- notebook editing conventions used in this session (patch in-place, save images to a centralized img folder, guard cells against missing columns),
- pitfalls discovered and guardrails (vmin/vmax issues, missing papermill, absolute paths).

# Quick defaults

- **Project root**: `/home/hermes/projects/SH26/`
- **Image output dir**: `paper/figures/` (PNG + PDF + JSON sidecar per figure)
- **Config**: `config/storage.yaml` (data backend) + `config/dask.yaml` (Dask cluster sizing — currently 3 workers × 4.5GB ≈ 14GB cap, host-tuned)
- **Current architecture (Aug 2026)**: Dask-backed `sh26` package replaced the old dual pipeline — see § Plot generators below

# Plot inventory (39 figures, p01–p39)

| Range | Category | Key helpers |
|-------|----------|-------------|
| p01–p07 | Core diagnostics: CMD, Kiel, sky maps, Galactic distributions | `_helpers.hexbin2d` |
| p08–p09, p16–p20 | SH21 vs SH26 comparisons: 2-panel (hexbin+1:1 with optional box; Δ symlog hist on FULL sample) | `_sh21_helper.sh21_vs_sh26` |
| p10–p12 | External distance: Weiler W25, Bailer-Jones geoRMS, BJ photo-geo — same 2-panel helper | `_sh21_helper.sh21_vs_sh26` |
| p13–p15 | Parameter vs distance (Teff, logg, [Fe/H]) | `_helpers.binned_mean_std` + `errorbar_band` |
| p26 | Parallax quality 2-panel: log–log σ_ϖ/ϖ vs d + 1/d theory curve; median S/N vs d + Gaia S/N=2/5/10 thresholds | bespoke (2-panel) |
| p21–p24 | Stellar parameter uncertainty 3-panel (teff, logg, met, mass): log σ hist + σ vs param + relative σ vs G | `_uncert_explore.uncertainty_explore` |
| p27–p30 | SHBoost vs SH26 3-panel: hexbin + diff hist + binned diff vs G | `_shboost_helper.shboost_vs_sh26` (3-panel layout, requires `phot_g_mean_mag_march2021` in SPEC.columns) |
| p31–p33 | Distance/Av/Age uncertainty 3-panel (A_V masks AV50≤0 — relative σ undefined at zero extinction) | `_uncert_explore.uncertainty_explore` (mask=) / bespoke p31 |
| p34–p39 | XYZR density subsets: SHBoost-used (SHBOOST=True), without SHBoost (SHBOOST=False), red clump, metal-poor ([Fe/H]<-1), SMR ([Fe/H]>+0.5), OB (Teff>10000K) | `_helpers.hexbin2d` |

# Column naming conventions for distance comparisons

**Distance columns in parquet:**
- SH26: `dist50`, percentiles `dist05/dist16/dist84/dist95`  (kpc)
- SH21: `dist50_sh21`, quantiles `dist*_sh21`  (kpc; Av as `av*_sh21`)
- Weiler W25: `dist50_weiler_w25`, quantiles `dist*_weiler_w25`  (kpc)
- Bailer-Jones 21: `r_med_geo_bj21` (geodetic), `r_med_photogeo_bj21` (photo-geometric), uncertainties as `r_lo_*/r_hi_*` pairs, flag in `flag_bj21`  — **⚠️ THESE ARE IN PARSECS, NOT kpc**
- SHBoost means (XGBoost): `xgbdist_teff_mean`, `xgbdist_logg_mean`, `xgbdist_met_mean`, `xgbdist_av_mean` with std columns `*_std`

**UNIT TRAP — Bailer-Jones distances are in parsecs.** `r_med_geo_bj21` / `r_med_photogeo_bj21` (and the `_lo_*/_hi_*` bounds) are in **parsecs**, while `dist50` and the SH21/Weiler `dist50_*` columns are in **kpc**. Plotting raw BJ21 vs `dist50` squishes the hexbin diagonal into the bottom-left corner with an x-axis max ~48,000 "kpc". Divide BJ21 by 1000 before plotting (P11/P12 do `d[c+"_kpc"] = d[c]/1000.0`). Do NOT convert `dist50_sh21` or `dist50_weiler_w25` — they're already kpc. Quick diagnostic: `median(dist50 / <col>)` ≈ 1 → same unit; ≈ 0.001 → `<col>` is in parsecs. Sanity after fix: median SH26/BJ21 ≈ 0.91–0.93.

**SHBOOST flag (CRITICAL semantics, user-corrected 2026-08-15):** `SHBOOST` bool = whether SHBoost (xgbdist) was **used in the calculation** for that star — it is NOT a convergence flag. Never label SHBOOST=False plots "non-converged"; use "stars without SHBoost (SHBOOST=False)". Stars with SHBOOST=False have no xgbdist values at all (0 of ~69k on 200k). `nummodels` int count is a separate quantity (nummodels>0 ≈ has SH26 posterior; P34/P65 use it as the "converged" class). `phot_variable_flag` for variability status. No XP column in current cache.

# Adding a comparison plot: SHBoost 3-panel pattern

For SHBoost vs SH26 with hexbin + difference histogram + binned diff vs G:

```python
from sh26.registry import PlotSpec
from sh26.plots._shboost_helper import shboost_vs_sh26

SPEC = PlotSpec(
    id=NN, name="vs_shboost_<param>", title="…",
    columns=["xgbdist_<param>_mean", "<param>50", "phot_g_mean_mag_march2021"],
)

def make(df, ctx):
    return shboost_vs_sh26(df, ctx, SPEC,
                           c_boost="xgbdist_<param>_mean", c26="<param>50",
                           label=r"$...$", unit="", diff_range=(lo, hi))
```

**CRITICAL:** Include `phot_g_mean_mag_march2021` in `SPEC.columns` or the vs-G panel silently fails with KeyError. The helper also checks G range > 3 & < 21 and filters finite diffs before binning.

**SENTINEL TRAP (fixed 2026-08-15):** `xgbdist_*_mean` columns (teff/logg/met — NOT av) store **−9999 as a finite "no-match" sentinel** on 46.6% of rows (always SHBOOST=False). Unmasked, panel (a) axis span becomes [−9999, …] (real data a sliver) and panel (b) shows a spike at Δ≈+10000. `shboost_vs_sh26` now masks `c_boost <= sentinel_max` (default −9000) by default, and takes `diff_range=(lo,hi)` to clip the difference histogram so the bulk stays readable (current: teff ±150 K, logg ±0.4, met ±0.4, av ±2.0). Panel titles carry n and median Δ; panel (b) shows the median line + clipped count.

# Adding an XYZR density subset (p34–p39 pattern)

```python
SPEC = PlotSpec(
    id=NN, name="rz_<subset>", title="R–Z: <label>",
    columns=["cut_column_if_any"],   # met50, teff50, SHBOOST, etc.
    derived=["RGal", "ZGal"],
    params={"gridsize": 200, "cmap": "<distinctive_map>"},
)

def make(df, ctx):
    p = SPEC.params
    d = df[mask].dropna(subset=["RGal", "ZGal"])
    fig, ax = plt.subplots(figsize=(8, 7))
    hexbin2d(ax, d["RGal"], d["ZGal"], gridsize=p["gridsize"], cmap=p["cmap"], vmin=1)
    ax.set_xlabel("R [kpc]")
    ax.set_ylabel("Z [kpc]")
    ax.set_title(f"<label>: {len(d):,}")
    return ctx.save(fig, SPEC, n_points=len(d))
```

# Data cache architecture

| Layer | Source | Rows (Aug 2026) | Notes |
|-------|--------|-----------------|-------|
| `sh26_cache_200k.parq/` | REANA workflow output (local) | ~201k | 8 parts × ~25k rows, ~110 MB. Quality-cut sample with enriched SH21/Weiler/BJ join columns. G=6–18.5. **Use for comparison plots** (SH21 vs SH26 p08-p12, p17-p20). |
| `sh26_joined_50m.parq/` | Sampled from Newton `sh26_final_joined/` | ~50M | 8 parts × ~6.25M rows, ~22 GB. Full enriched parquet (SH21, Weiler W25, Bailer-Jones, SHBoost). Random sample via `scripts/sample_parquet.py` on Newton (`--target-rows 50000000`). **Default for production plots (Aug 2026).** |
| `sh26_joined_5m.parq/splits/` | Sampled from Newton `sh26_final_joined/` | ~5M | 8 parts, ~2.4 GB. Same enrichment; quick-iteration / low-RAM fallback. |

**TRUE data source on Newton (141.33.4.144):**
```
/lustre/<user>/ipython/SH2025/reana/final/combined/sh26_final_joined/
  part.*.parquet   # 4094 parts, ~785k rows each (~300M total)
                    # FULL joined parquet: includes all SH21, Weiler W25,
                    # Bailer-Jones 21, and SHBoost columns
```

**NEVER use `sh26_phase1_dedup/`** — that's raw catalog WITHOUT enriched comparison columns (only ~84 cols vs ~129 in joined). Comparison plots will fail.

## Getting fresh data from Newton

When the local cache is stale or you need more rows:

1. **SSH to Newton:** `arm2arm@141.33.4.144`
2. **Sample with Dask** (low-mem, ~5M target):
   ```bash
   ssh arm2arm@141.33.4.144 "cd /lustre/<user>/ipython/SH2025/reana && \
     python3 scripts/sample_parquet.py \
       --input final/combined/sh26_final_joined/ \
       --output sampled/sh26_5m_sample.parq/"
   ```
   Script uses `ddf.sample(frac=...)` + `.repartition(npartitions=8)` → exactly 8 consolidated splits, ~2.4 GB. Takes 3–5 min (metadata scan over 4094 parts dominates). Uses `%s`/`.format()` in print, NOT f-strings (SSH heredoc mangles `{}`).
3. **Transfer locally:**
   ```bash
   scp arm2arm@141.33.4.144:".../sampled/sh26_5m_sample.parq/splits/part.*.parquet" \
     /home/hermes/projects/SH26/data/sh26_joined_5m.parq/splits/
   ```
4. **Run plots:** `--data data/sh26_joined_5m.parq/splits/`

## Comparison plot skip-guard pattern (p08-p12, p17-p20)

Comparison plots that need enriched SH21/Weiler/BJ columns must check for column presence before calling the helper. If missing, return a sentinel list so the CLI doesn't crash:

```python
def make(df, ctx):
    missing = [c for c in SPEC.columns if c not in df.columns]
    if missing:
        print("  ⊘ pXX skipped (missing enriched: %s)" % str(missing))
        return [ctx.outdir / f"{SPEC.slug}_skipped.txt"]
```

**NEVER** strip missing columns in `dataio._build()` — Dask `read_parquet` throws on non-existent columns before any skip-guard can fire. The fix is per-plot column checking, not loader-level masking.
- Default distance plotting range: 0.1 — 100 (use log axes when plotting dist50-like columns)
- Default teff plotting range: 1000 — 10000 K (linear axes; teff50 is already linear)
- **Linear Scaling Preference**: Even for Kiel diagrams, the user prefers **linear axes** for `teff50` and `logg50` (do not use `ax.set_xscale('log')`). The physical distribution in SH26 is already correctly captured in these spaces.
- **Production Kiel Ranges**:
  - $T_{eff}$: `[11000, 2000]` K (reversed)
  - $\log g$: `[-0.5, 5.5]` (inverted via `ax.invert_yaxis()` or via ylim order)
- **Grid Density**: Use `gridsize=200` for production-quality Kiel/CMD density plots.
- **Handling NaNs**: **Mandatory** `df.dropna(subset=['teff50', 'logg50'])` before hexbin/hist2d to avoid blank plots.
- **Telegram Delivery**: Always use `MEDIA:/path/to/file.png` — S3 upload script is a fallback only if Telegram boxes render empty.

# Plot generators

**Architecture changed Aug 2026 — the dual pipeline (starhorse2026/plots.py + generate_all_plots.py) is gone.** Use the modular Dask framework:

| | sh26 framework (current) |
|---|---|
| Entry | `PYTHONPATH=src python -m sh26 plots --all` (or `-p 1,3,7` / `-p 8-11`) |
| Package | `src/sh26/` — registry.py, context.py, dataio.py, cli.py, plots/ |
| Figures | 39 files, one per id: `plots/p01_cmd.py` … `p39_rz_ob_stars.py` (see § Plot inventory below) |
| Loading | Dask `LazyCatalog`: Parquet column pruning (union of needed cols), lazy derived cols, LocalCluster 3w×4.5GB (~14GB cap, host-tuned). **Loader never drops rows** — no dist50 pushdown. |
| Full catalog | **Use `--no-cuts` for paper figures** — user wants ALL data plotted, no ruwe/parallax pre-cuts. Each plot applies its own mask. |
| Output | `paper/figures/sh26_pNN_name.{png,pdf,json}` — JSON sidecar = provenance (n_points, git, params, timestamp) |
| Adding a plot | drop `p27_x.py` with `SPEC = PlotSpec(id=27, …)` + `make(df, ctx)` — auto-registered |
| Param override | CLI `--param p01.gridsize=300` lands on SPEC.params |
| Tests | `pytest tests/test_plots_smoke.py` — 27 tests, synthetic frame, 2.4 s |
| Makefile | `make plots`, `make plots P=1,3,7`, `make combine`, `make list` |

**CRITICAL — Distance sub-catalogs**: The CLI (`sh26 plots -p N --no-cuts`) loads the FULL catalog and passes it raw to plot functions. If the user requests `dist50 < X kpc`, the CLI will IGNORE it because individual renderers only apply their own NaN/photometry masks.

**Correct pattern**:
1. Use `scripts/gcx_plots.py` — sets `PLOT_IDS = [...]`, loads full catalog via `Catalog(...)`, applies a pandas boolean mask on dist50, then passes the filtered `df` to each registry renderer so every figure respects the cut.
2. **Column-pruning fix**: Dask reads ONLY columns requested by selected plots. If no plot needs `dist50`, it's pruned and the filter crashes with `KeyError: 'dist50'`. The wrapper script fixes this by force-appending `"dist50"` to `columns` before querying the registry (see references/gcx_custom_distance_cuts.md).
3. Filtered outputs land in `paper/figures_gcx/` with a combined PDF at project root (`sh26_gcx_n1_nN.pdf`).

**Legacy note**: the old `starhorse2026` package, `src/generate_all_plots.py`, and `src/OLD_SH_analysis_notebooks/` were deleted in the Aug 2026 refactor. Backup tarball at `/home/hermes/projects/SH26_backup_20260808.tar.gz` if ever needed. The temperature-dependent extinction physics (`photutils.MG0/BPRP0/AG/ABP/ARP`) was preserved verbatim in `sh26/photutils.py`.

# Plot inventory (39 figures, p01–p39)

**Core diagnostics (p01–p07):** CMD, Kiel (density + metallicity), sky density/Av maps, Galactic XY/XZ/R-Z distributions.

**SH21 comparisons (p08–p20):** SH26 vs SH2021 for distance (p08), Av (p09), Teff (p17), logg (p18), [Fe/H] (p19), mass (p20). `_sh21_helper.sh21_vs_sh26()` — 2-panel: hexbin+1:1 (optional `box` clips panel a only) + Δ = SH26 − ref symlog histogram on the FULL valid sample (title: n, median Δ, % within ±diff_clip). SH21/W25/BJ21 columns have NaNs only, no sentinels (verified 2026-08-15). Pass `diff_unit` + `diff_clip` per parameter.

**Distance comparisons (p10–p12):** Weiler W25 geoRMS (p10), Bailer-Jones 21 geodetic (p11), Bailer-Jones 21 photo-geometric (p12). Uses `_sh21_helper.sh21_vs_sh26()` since the hexbin API is identical.

**SHBoost comparisons (p27–p30):** SH26 vs SHBoost24 mean for Teff, logg, [Fe/H], Av. Three-panel layout: (a) hexbin comparison, (b) difference histogram, (c) binned mean-difference vs G magnitude. Uses `_shboost_helper.shboost_vs_sh26()` which requires `phot_g_mean_mag_march2021` in SPEC.columns.

**Parameter-vs-distance (p13–p16):** Teff, logg, [Fe/H], mass binned vs distance mean±std bands.

**Uncertainty plots (P21–P24, P32–P33):** 3-panel via `_uncert_explore.uncertainty_explore` (log σ hist + σ vs param + relative σ vs G); P31 bespoke. P32 masks AV50≤0 rows (relative σ undefined at zero extinction). **PITFALL (bit P32/P33, 2026-08-15):** panel (c) needs `phot_g_mean_mag_march2021` in `PlotSpec.columns` — if missing, the lazy loader omits it and the panel renders as an EMPTY 0–1 axis. The helper now raises ValueError if G is absent, and caps panel-(c) y at p90×1.25 (bright-end near-zero-denominator bins reach 150–700% relative σ and would otherwise squash the trend; P32 median ~24% clips 5/72 bins, P33 median ~30% clips none). P25 is a 2-panel color–color (density + median Teff per cell) and masks the Jmag=−1e4 2MASS sentinel (22.6% of rows).

**XYZR density subsets (p34–p39):** R-Z hexbin sliced by: with SHBoost (nummodels>0, p34), without SHBoost (SHBOOST=False, p35), red clump (p36), metal-poor [Fe/H]<-1 (p37), super-metal-rich [Fe/H]>+0.5 (p38), OB stars Teff>10000K (p39). P43–P71 (added 2026-08-15): Δ-vs-sky Mollweide (P43–P50, `_sky_mollweide.py`), Δd stats vs W25/SH21/BJ21 (P51–P53, `_delta_d_helper.py`), σ vs G (P54–P60, `_sigma_vs_g.py`), σ vs sky (P61–P62), **P63 SHBoost usage CMD 3-panel (full / True / False) with SHARED count scale — vmax = full-sample max cell count binned at the figure gridsize, so all three colorbars are identical and populations compare visually** (bespoke), **P64 SHBoost usage T_eff–log g 3-panel (full / True / False), same shared-count-scale pattern as P63 + P2-matched inverted axes** (bespoke), XYZ per class (P65–P70, `_xyz_helper.py`), 10° GC box vs SH21 (P71).

**P40 Mollweide all-sky density:** pure-matplotlib Mollweide (no basemap/cartopy installed). Equations: solve `sin2θ+2θ = π·sinφ` by vectorised bisection over θ∈[0,π/2] for |s| then restore sign (Newton is ill-conditioned near poles — do NOT use it); `x=(2√2/π)·λ·cosθ`, `y=sinθ`. Project the bin EDGES of a 2D histogram (n_b+1 × n_l+1 corners) for `pcolormesh`. GC/anti-GC markers need scalar coords (1-elem arrays crash `ax.annotate`).

**P41/P42 Mollweide median property maps:** per-pixel MEDIAN (met50 / AV50) via `np.digitize`+`np.argsort`+`np.unique(keys, return_index, return_counts)` groupby; `med` must be sized to the FULL grid `n_b*n_l` (unique keys skip empty bins — assigning `med[len(ukey)]` or `idx_cnt.reshape` silently mismaps); counts via `np.bincount(keys, minlength=n_b*n_l)`; NO `.T` on the manually-built grid (histogram2d returns transposed, manual reshape does not — pcolormesh demands C=(n_b, n_l)). Layout (P40–P42, user-approved): frame off, coordinate labels on the ellipse, short horizontal colorbar centered below the map (`fig.add_axes((0.235, 0.065, 0.45, 0.02))`). Shared code: `src/sh26/plots/_mollweide_helper.py` (mollweide, wrap_l, mollweide_map, make_figure).

# Column naming conventions

**SH26 columns:** `teff50`, `logg50`, `met50`, `dist50`, `AV50`, `mass50`, `age50` + quantiles (`*16`, `*84`). Percentile 50 = median.

**Galactic longitude wrap (user rule, 2026-08-15):** `l` in the parquet is [0, 360) — plotting it raw puts the GC on the l=0/360 seam (right edge). All sky maps MUST wrap `l` to (−180, 180) via `wrap_l` (`_mollweide_helper.py`) so the GC is at the plot center. Applied to: P04/P05 (hexbin sky density / median A_V) and P40–P42, P43–P50, P61–P62 (Mollweide).

**Log-axis density pitfall (P26, 2026-08-15):** `ax.hexbin()` bins uniformly in the INPUT coordinate space, so on log-scale axes the cells get misplaced and the plane renders empty or corner-crowded. For log–log density, bin explicitly in log10 space: `np.histogram2d(log10x, log10y, bins=(nb,nb))` + `pcolormesh(10**xe, 10**ye, H.T, norm=LogNorm(vmin=1), rasterized=True)`. For reference curves, fit a data-driven power law (median per log-d bin) rather than anchoring on a near-field "floor" (which floats below the data).

**SH21 legacy columns:** `<param>_sh21` (e.g., `teff50_sh21`, `dist50_sh21`, `av50_sh21`). Loaded as pre-joined columns in parquet.

**External distance columns:**
- Bailer-Jones 21: `r_med_geo_bj21` (geodetic), `r_med_photogeo_bj21` (photo-geometric) + uncertainty bounds `_lo_*/_hi_*`
- Weiler W25: `dist50_weiler_w25` + quantiles
- SHBoost means: `xgbdist_teff_mean`, `xgbdist_logg_mean`, `xgbdist_met_mean`, `xgbdist_av_mean` with std columns `*_std`

**Flags:** `SHBOOST` (bool — SHBoost used in calculation, NOT convergence), `nummodels` (int; >0 ≈ has SH26 posterior). No XP flag column in current cache.

**Adding a comparison plot:** Drop the file into `plots/`, declare SPEC with id/name/title/columns/derived, implement `make(df, ctx)`. For 3-panel comparisons (hexbin + diff hist + vs-G), reuse `_shboost_helper.shboost_vs_sh26()`. Remember to include `phot_g_mean_mag_march2021` in columns if using the G-magnitude panel.

# Data cache architecture (CRITICAL — use JOINED data only)

**TRUE source on Newton (141.33.4.144):**
```
/lustre/<user>/ipython/SH2025/reana/final/combined/sh26_final_joined/
  ~4094 parts, ~400M rows, ~989 GB total
  INCLUDES: SH21, Weiler W25, Bailer-Jones, SHBoost columns (128 cols)
```

**NEVER use `sh26_phase1_dedup/`** — raw catalog WITHOUT enriched comparison columns (only ~84 cols). All p08-p12/p17-p20 plots will fail.

## Sampling from Newton to local cache

Script on Newton: `/lustre/<user>/ipython/SH2025/reana/scripts/sample_parquet.py`

```bash
ssh arm2arm@141.33.4.144 "cd /lustre/<user>/ipython/SH2025/reana && \
  python3 scripts/sample_parquet.py --input final/combined/sh26_final_joined/ \
    --output sampled/Nsample.parq/"

for i in {0..7}; do
  scp arm2arm@141.33.4.144:".../sampled/Nsample.parq/splits/part.${i}.parquet" \
    /home/hermes/projects/SH26/data/sh26_joined_Nm.parq/
done
```

## Combining figures into PDF

```bash
cd /home/hermes/projects/SH26 && python3 scripts/combine_figures.py -i paper/figures/ -o sh26_all_figures.pdf
```

# Memory-safe plotting for big data (CRITICAL)

**User mandate:** "Fix plotting routines to use dask for memory management, always use those columns what you need to plot." Conservative dask+pandas management — never load what the plot doesn't need.

### Working solution: Dask LocalCluster with a ~14GB total cap
`lazy_catalog.py` uses a Dask `LocalCluster` sized to the HOST, not the dataset: **3 workers × 4.5GB ≈ 14GB total** (standing user cap on this host). Per-worker memory_limit above ~7GB gets OOM-killed (exit -9) even with spill enabled — an oversized `memory_limit` does NOT protect from the OS killer.

Key properties that make 50M rows work:
1. **Parquet metadata scanned once** — schema (128 cols) read from first part's metadata; never `len(ddf)` on the lazy frame (forces full compute).
2. **Per-plot column pushdown** — each plot computes only `spec.columns` + `spec.derived` deps (+ 3 QC cols), so 50M × ~10 cols ≈ a few GB, comfortably in budget.
3. **Derived columns in pandas AFTER materialization** (small frame, cheap).

History: pure-`to_pandas()` of all columns OOMs (~25GB); a first Dask attempt with 4 workers × 8GB also died (per-worker OOM, exit -9); an intermediate PyArrow row-group chunked reader worked sequentially but was slow (~23 min for 39 plots). The final Dask 3×4.5GB setup: **39 plots on 50M rows in ~14 min, 0 failures.**

Run: `PYTHONPATH=src python -m sh26 plots --all --no-cuts --data data/sh26_joined_50m.parq`

# Notebook-editing conventions

- Patch notebooks in-place; do not create extra helper scripts unless absolutely necessary.
- Each plotting cell should:
  - be self-contained (define xcol/ycol; detect/assign df or df26 fallback),
  - create IMG_DIR if missing and save PNG there using absolute paths,
  - guard against empty datasets and avoid Invalid vmin/vmax by computing vmin/vmax from non-zero bins,
  - print the written filename as `WROTE <path>` for deterministic detection by automation.

# Pitfalls & fixes (from this session)

- **Full-catalog plotting (user requirement)**: For paper figures plot ALL available data — never pre-cut. Global quality cuts + a silent `dist50` pushdown gutted Fig 1 (CMD) to a bright red clump. Fix: `--no-cuts` at the CLI and no row filtering in the loader. See references/sh26_dask_framework.md § Plotting the FULL catalog.
- **CMD wash-out (invisible faint main sequence)**: A Hess/CMD with `cmap='Greys'` + unbounded `LogNorm` renders sparse faint-star bins (1–2 counts) white-on-white — the data is present but the plot looks empty below the bright clump. Fix: high-contrast cmap (`inferno`) + `norm=LogNorm(vmin=1)`. Details in references/sh26_dask_framework.md.
- **"Plot still looks half-empty" — diagnose data vs. perception BEFORE more edits**: After all cuts/limits were removed and cmap fixed, the CMD *still* looked half-filled. Root cause was perceptual, not data: the catalog is intrinsically bright-dominated (25 % of stars in MG0∈[4,6); only 41 stars in [12,15)), so on any log scale the faint main sequence is orders of magnitude fainter visually. **Diagnose numerically first** — dump a 2D `np.histogram2d` occupancy table (mg0 × bprp0) and a 3-band pixel-fill fraction of the PNG. Both proved the full diagonal sequence was drawn. Don't keep editing the plot when the data is genuinely skewed — offer a `sqrt` norm (compresses bright-end dynamic range, lifts faint bins) instead of `log` if the user wants the faint end to pop.
- Invalid vmin/vmax in LogNorm arises when histogram has all zeros or when vmin==vmax. Fix: mask zero bins, compute vmin from non-zero bins and ensure vmin < vmax (fallback to 1e-10 if needed).
- **Matplotlib Compatibility**: Matplotlib 3.8+ changed `ax.hexbin` and `PolyCollection`. The parameter `reduce_fcn` is deprecated/removed in some contexts; use `reduce_C_function` instead.
- **Papermill Execution**: When running notebooks headlessly via Papermill, ensure the `kernelspec` is present in the notebook metadata or explicitly provide the kernel name using the `-k` flag (e.g., `papermill input.ipynb output.ipynb -k python3`).
- **Style Consistency**: Apply unified styling (e.g., `plt.style.use('seaborn-v0_8-whitegrid')`) and publication-quality `rcParams` across all cells when consolidating exploratory notebooks into a production-ready `all_plots.ipynb`.
- **Handling NaNs**: StarHorse datasets often contain NaNs for failed fits in `teff50`, `logg50`, and `met50`. Matplotlib's `hexbin` and `hist2d` can produce blank/empty plots or incorrect binning if NaNs are present. **Always** use `df.dropna(subset=['teff50', 'logg50'])` before plotting Kiel or CMD diagrams to ensure correct density estimation.
- **Double-Log Pitfall**: A frequent error is applying `ax.set_xscale('log')` to `teff50` or `logg50`. Both are already in the appropriate space (linear for $T_{eff}$ and logarithmic for $\log g$) for standard Kiel/CMD plots. Adding a log scale will result in distorted or empty-looking plots.
- **Notebook JSON Integrity**: When patching notebooks via regex or `patch`, ensure that multiline strings or line continuation characters (`\n`, `\r`) are handled correctly. Broken JSON or syntax errors in code cells (e.g., `\\n` escaping issues) will crash `papermill`. Using a Python script to load the notebook JSON and manipulate the `source` list directly is more robust than regex patching.
- **Absolute Paths**: Always use absolute paths for input data and output images within notebook cells to ensure execution stability via Papermill/nbconvert.

# Verification

- After running a plotting cell, verify the file exists and that cells printed `WROTE /absolute/path/to/file.png`.
- Optionally perform a small label-area crop for visual legibility checks.

# References

- references/session_sh26_plots.md — session-specific summary and notebook examples
- references/sh26_project_structure.md — current post-refactor layout + 26 figure ids
- references/sh26_dask_framework.md — Dask framework internals: PlotSpec contract, DERIVED_DEPS graph, resource ceiling, extension recipe
- references/cmd_photutils.md — extinction-correction physics notes
