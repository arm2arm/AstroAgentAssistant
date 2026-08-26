# Pending SKILL.md updates (2026-08-15 — apply at next foreground opportunity)

SKILL.md body edits were blocked by the curator's read-before-write guard this
turn. Apply these three patches directly to SKILL.md (they were verified
against the on-disk file):

1. **Figure count**: suite is now **42 plots (p01–p42)**, not 39. Update both
   `# Plot inventory (39 figures, p01–p39)` headings and the table row
   `| Figures | 39 files ... p39_rz_ob_stars.py ...` to
   `| Figures | 42 files: p01_cmd.py … p42_mollweide_av.py`.
   P40–P42 = Mollweide all-sky density / median [Fe/H] / median A_V
   (already documented under the P40/P41-P42 entries in the inventory).

2. **Replace the stale `--dist-cut` guidance** in § Plot generators: the
   `**CRITICAL — Distance sub-catalogs**` block that says the CLI "will
   IGNORE" a dist50 request and to use `scripts/gcx_plots.py` is OUTDATED —
   the native `--dist-cut <kpc>` flag now exists (see
   references/cli_dist_cut_flag.md). Replace the block with:
   "For `dist50 < X kpc` re-plots use `--dist-cut X`: force-injects `dist50`
   into the column-pushdown set, filters after materialization + QC, records
   the cut in every JSON sidecar. Other-column cuts still need the legacy
   wrapper (references/gcx_custom_distance_cuts.md)."

3. **Add PDF rasterization pointer** to the Pitfalls section (full notes in
   references/pdf_rasterization.md):
   "Acrobat-slow PDFs from hexbin/scatter/pcolormesh vector paths: `save()`
   in `src/sh26/context.py` marks PolyCollection/PathCollection/QuadMesh
   artists `rasterized=True` before PDF save (mpl 3.11: import QuadMesh from
   `matplotlib.collections`, NOT `matplotlib.axes._axes`). Verified instant
   rendering; text/axes stay vector."

## Also verified this session (no edit needed, facts for the record)

- `--dist-cut 5` on 50M: 37,236,050 rows (74.5%); full 42-plot suite ~12.5 min
  at `--threads 16 --memory 64GB`; combined PDF `sh26_all_50m_d5.pdf`.
- P8–P12 and P17–P20 all draw through `_sh21_helper.sh21_vs_sh26` (hexbin),
  so the rasterization fix covers every previously-slow figure.
- Repo is on GitLab: `git@gitlab.aip.de:<user>/SH26.git` — commit + push
  after each verified change (user-mandated 2026-08-15).
- P19 smoothed/KDE alternative was REJECTED by user as too slow; keep plain
  hexbin with `box=(-0.5, 0.5)` on the 0.1-dex-quantized [Fe/H] data.
