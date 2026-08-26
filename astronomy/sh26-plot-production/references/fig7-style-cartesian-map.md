# Fig. 7-style Cartesian map workflow

## Trigger
Use when adapting a published two-panel Galactic Cartesian map to SH26.

## Reference pattern
Khalatyan et al. (2024), arXiv:2407.06963, Fig. 7 uses a 100 x 100 kpc^2 face-on XGal-YGal map: left panel is stellar density; right panel is per-pixel median metallicity. The paper uses a broad parent sample for density and applies a metallicity-uncertainty limit plus a minimum occupancy to the median map.

## SH26 implementation lessons
- Inspect the paper caption and image first, then map every required observable to the real Parquet schema.
- If an observable is absent, do not silently substitute it; either stop for the missing join or explicitly rename/document the proxy. In SH26, `met50` is [M/H], not calibrated [Fe/H].
- Register a new stable P## ID; do not modify or reuse an existing figure.
- For two-panel maps, keep counts separate: density uses all finite XGal/YGal rows; the median-property map uses only finite property values passing its uncertainty threshold and minimum pixel occupancy.
- Record both parent and filtered counts in the JSON sidecar and make panel titles explicit. `ctx.save()` appends the overall `n_points` to panel titles unless the title already contains `n = ...`, so set a filtered panel title explicitly when needed.
- Verify registry discovery, run a 200k smoke render, inspect PDF/PNG text and non-white fraction, then render the full catalogue with the pyarrow-direct path.
- If the cluster worktree has unrelated uncommitted changes, do not pull, stash, or overwrite it. Export the committed `src/` tree to an isolated temporary directory and run there; write full outputs to a new versioned location until QA passes.

## Verified P101 pattern
Raw columns: `l`, `b`, `dist50`, `met50`, `met16`, `met84`; derived: `XGal`, `YGal`. Use `sigma_met = (met84 - met16)/2`, `N >= 4` per pixel, and label the result `[M/H]`, not `[Fe/H]`. Full v220826 execution read 402,121,784 rows, retained 327,477,457 converged rows, and produced 286,772,569 rows passing the metallicity uncertainty filter.
