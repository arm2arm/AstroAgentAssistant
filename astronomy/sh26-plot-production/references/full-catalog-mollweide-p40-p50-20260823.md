# Full-catalog Mollweide P40–P50 recipe (2026-08-23)

Validated workflow for rerendering P40–P50 on the 402M-row SH26 catalog.

## Production path

Use the PyArrow-direct runner, not the Dask CLI. The direct runner resolves the registry columns, reads only those columns from `sh26_final_joined_v220826`, applies `MISSING == False`, calls `_derive` when needed, and invokes the registered plot function. Deploy source to an isolated workspace such as `/lustre/<user>/tmp/p40_50_full`; never overwrite the live `/lustre/<user>/hermes/SH26` source. Write outputs to an isolated result directory and verify each result before retrieval.

P40–P50 can run concurrently on the high-memory node. Expected convergence anchor: `327,477,457` rows. Require 11 JSON, 11 PNG, and 11 PDF artifacts; each sidecar should contain `loader: pyarrow-direct`. If a nested stdin/base64 transfer creates a zero-byte launcher, transfer through the intermediate Newton host with `scp` and verify using `wc -c`.

## Validity and binning

Finite values are not enough: joined products can contain finite sentinel/outlier values. Apply physical ranges to both values in comparison maps before calculating per-pixel medians, and record the ranges in sidecars:

- distance: `(0, 100)` kpc
- extinction: `(-1, 20)` mag
- effective temperature: `(2500, 50000)` K
- surface gravity: `(-1, 6)` dex
- metallicity `[M/H]`: `(-3, 1)` dex
- mass: `(0, 20)` solar masses

Use a 512×256 sky grid and `min_n=50` finite stars per cell. Use a linear normalization for median `A_V`; `LogNorm` is inappropriate near zero or for negative estimates.

## P100-style presentation

Use one shared Mollweide renderer with Galactic longitude wrapped to `[-180, 180)`, `l=0°` centered, seam at `±180°`, GC/anti-GC labels, graticules, explicit coordinate annotation, neutral grey masked/no-data pixels, and horizontal labelled colorbars. Difference maps must state `Δ = SH26 − reference`; BJ21 distances require `ref_scale=0.001` because the source column is in parsecs while `dist50` is in kpc.

## Bundle replacement

When `paper/figures/` has fewer PDFs than the canonical bundle because later pages were appended separately, do not run `combine_figures.py` as the final operation. Start from the committed canonical PDF, replace only the desired human page indices with the new one-page PDFs, and verify both the replaced labels and preserved appended pages. Final checks: page count, sidecar/image completeness, audit script status, and SHA256.
