# SH26 axis-range conventions (user-corrected 2026-08-25)

User rejected P108's first render: "the x and y ranges are not consistent
with our previous plots". The established conventions (authoritative for
ALL new figures):

## CMD (every CMD panel)
- x = `(BP-RP)_0 [mag]`, fixed **x ∈ [−2, 8]**
- y = `M_G,0 [mag]`, fixed **y ∈ [−5, 15]**, **INVERTED** (bright at top)
- Implementation (P36 rule): `ax.set_xlim(-2, 8); ax.set_ylim(15, -5)`
- Supersedes the (−1.5, 4) × (−4, 16) range found in P102/P104/P107 —
  do NOT copy those for new figures.

## Kiel (every Kiel panel)
- Data-driven extent: plain `ax.hexbin(x, y, gridsize=...)` with NO
  `extent` and no manual xlim/ylim (P02 convention) — hexbin sets the
  range from the data.
- Then invert BOTH axes: `ax.invert_xaxis(); ax.invert_yaxis()`
  (Teff hot→cool left-to-right, logg low at top).
- Do NOT clip to percentiles — that also broke consistency with P02.

## Multi-population grids (P108 class)
- Hold the range FIXED across all panels of a column so rows compare 1:1:
  - CMD: the fixed P36 range already does this for free.
  - Kiel: hexbin's extent is per-panel data-driven; for strict equality
    across rows you must pass a shared extent — the user accepted
    per-panel data-driven Kiel (2026-08-25), so default to that.
- Verify with vision tick-reading on a ~1400px JPEG: report exact tick
  values per column and confirm row-identical ranges before committing.

## Shared color scale for comparable panels
- Compute `cmax` once from the FULL panel's hexbin
  (throwaway fig/ax, `hexbin(...).get_array().max()`, `plt.close`).
- `norm = LogNorm(vmin=1, vmax=max(cmax, 2))` on every panel; filtered
  panels then read as "same locations, lower colors = fewer survivors".
- `ax.hexbin` takes `bins="log"` OR `norm=`, never both — the floor trick
  REQUIRES `norm=LogNorm(...)` with `bins` omitted.

## Fix provenance
P108 first commit `6f173fe` (wrong ranges) → correction commit `e595fbf`
(CMD P36 + Kiel data-driven; re-run 5.8 min on <compute-node>; vision tick-verified:
CMD x −2→8, y −5→15 inverted; Kiel data-driven; identical across 3 rows).
Detail: `references/p108-cmd-kiel-populations-20260825.md` (its "Kiel axes"
bullet predates the correction — this file wins).
