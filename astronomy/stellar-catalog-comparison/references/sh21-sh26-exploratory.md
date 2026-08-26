# SH21–SH26 exploratory comparison recipe

## Session-derived design

For the SH26 full catalog, the requested approximately 27M inner sample was verified as X[-5,5] × Y[-4,4] kpc. The narrower established X[-4,4] × Y[-3,3] selection gives only about 16M and should not be substituted when the request is 27M.

Use the converged base sample first, then finite-pair masks independently for each parameter. In the SH26 joined schema the relevant pairs are:

- `dist50` / `dist50_sh21`
- `AV50` / `av50_sh21`
- `teff50` / `teff50_sh21`
- `logg50` / `logg50_sh21`
- `met50` / `met50_sh21`

`SHBOOST=True` identifies the SH26 xgbdist path; `SHBOOST=False` is the non-SHBoost path.

## Clean figure recipe

A 5×2 figure is preferable to a dense 5×3 diagnostic dashboard:

1. Each row is one physical parameter.
2. Left panel: normalized SH21 and SH26 distributions.
3. Right panel: `Delta = SH26 - SH21` distributions.
4. Color encodes SHBOOST True/False.
5. Line style encodes SH21 versus SH26.
6. One global legend only.
7. Per-row residual annotation reports N, median Delta, and MAD for each subgroup.

Keep panel titles short. Put the selection, base N, subgroup counts, and residual convention in the figure-level title and JSON provenance.

## QA checklist

- Verify the spatial box and base count numerically before plotting.
- Confirm subgroup counts sum to the base count.
- Confirm every parameter has both SH21 and SH26 curves for both subgroup states.
- Use per-parameter N; do not apply an all-five-parameter complete-case cut unless requested.
- Check that display clipping affects only axes, not residual statistics.
- Inspect the rendered image for title/legend/annotation collisions.
- Extract PDF text as a second check for all five parameter names, units, selection, counts, and `Delta = SH26 - SH21`.
- If updating a multi-page bundle, replace the existing page rather than appending a duplicate and verify the final page count.
