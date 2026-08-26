# P90/P91 CMD-panel axis state + hexbin fixed-range pitfalls (2026-08-18)

Session 2026-08-18. Companion to `p91-full-rest-sample-umap.md` and
`p90-fraction-ladder.md`. Captures the FINAL CMD-axis state after a
churn of user corrections, plus two matplotlib traps hit while forcing a
fixed CMD range.

## FINAL CMD-axis state (authoritative)

P90 middle panel and P91 middle panel are BOTH now:
- P01 axis ORDER: x = (BP−RP)₀ (`bprp0`), y = M_G,0 (`mg0`), P01 two-line
  column labels, `gridsize=300`, viridis, vmin=1.
- **NO `invert_xaxis()`, NO `invert_yaxis()`** — plain ascending limits.
  The user explicitly rescinded the inversion ("do not do any
  transformation on x and y axises on CMD plot"). The earlier
  "invert axes" CMD/Kiel convention in SKILL.md is STALE for these
  embedding-CMD panels; do not re-add inversion unless the user re-asks.
- P91 additionally has a FIXED range from spec params:
  `cmd_xlo=-2, cmd_xhi=8, cmd_ylo=-6, cmd_yhi=15`, applied as
  `ax.set_xlim(xlo, xhi)` / `ax.set_ylim(ylo, yhi)` (ascending args).
- P90 CMD is data-driven (no fixed range); P91 is fixed. If the user
  later wants P90 to match P91's fixed box, mirror the params over.

## Correction sequence (so a future agent doesn't re-tread)

1. "make ranges/appearance similar to P1" → P01 labels + gridsize 300 +
   fix the swapped axes (mg0 was on x).
2. "x axis must be flipped" → added `invert_xaxis()` (P91).
3. P90 "y and x axis not same as in P1" → P90 axes were swapped; fixed.
4. "change x axis [-2:8]" (P91) → fixed range requested.
5. "do not do any transformation on x and y axises" → removed BOTH
   inversions; final = plain ascending limits. Net: no inversion.

## matplotlib pitfalls (hit while forcing the fixed CMD range)

1. **`extent` requires ymax > ymin.** `hexbin2d(..., extent=[xmin,xmax,
   ymin,ymax])` with the CMD's inverted y (15 then −6) →
   `ValueError: In extent, ymax must be greater than ymin`. Final design
   drops `extent` and uses plain `set_xlim`/`set_ylim` with ascending
   limits.
2. **`extent` does not bound the axes — the overplot does.** A fixed
   `extent` on the hexbin is overridden by any auto-scaled artist drawn
   after it: the red selection `scatter` (which can sit outside the
   [−2,8]×[−6,15] window) re-expands the data range, so the panel shows a
   wider range than requested. To enforce a HARD fixed range, set
   `ax.set_xlim`/`ax.set_ylim` AFTER the scatter, and don't rely on
   `extent` alone. (This is why the "extent + set_xlim/set_ylim" combo is
   what finally produced the requested window.)
