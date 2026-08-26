---
name: scientific-figure-production-qa
description: Use for large-catalog scientific figure QA.
version: 1.0.0
author: Hermes Curator
license: MIT
---

# Scientific Figure Production and QA

Use this class-level workflow when generating or revising scientific plots from
large catalogs, especially sky maps, residual maps, and numbered figure
bundles. The goal is a scientifically valid, readable, reproducible artifact,
not merely a successful Python process.

## Workflow

1. **Inspect before editing**
   - Read the plot module, shared renderer, registry specification, and the
     canonical/reference figure.
   - Identify coordinate conventions, units, sign conventions, masks, binning,
     normalization, and expected output/page numbering.

2. **Validate data semantics**
   - Apply the hard convergence/population filter consistently.
   - Treat finite sentinels as invalid when the catalog uses sentinel values;
     `np.isfinite` alone is not sufficient.
   - Define explicit physical ranges per quantity and record them in metadata.
   - For comparisons, state the difference exactly, e.g. `SH26 - reference`,
     and apply unit conversions before subtraction.
   - For per-cell medians, define and record the minimum stars per cell.

3. **Use the appropriate large-data path**
   - Push down only the required columns.
   - For catalogs around 400M rows, prefer the verified PyArrow-direct loader
     over a Dask CLI path known to coalesce partitions into oversized tasks.
   - Run independent jobs only when resource and I/O contention are understood;
     avoid duplicate launchers and verify process/output state before relaunch.
   - Use isolated temporary source/output directories for remote HPC renders;
     do not overwrite a live working copy.

4. **Make sky maps self-explanatory**
   - Use one shared Mollweide renderer for geometry, graticules, longitude
     wrapping, seam, GC marker, and colorbar placement.
   - State the Galactic `(l,b)` convention, center, increasing-longitude
     direction, and seam.
   - Give masked/no-data pixels a neutral color distinct from valid values and
     explain the treatment visibly.
   - Use sequential normalization for positive densities/absolute quantities
     and zero-centered diverging normalization for signed residuals.
   - Do not use `LogNorm` for quantities that can be zero or negative.

5. **Verify labels and annotations**
   - Matplotlib colorbar axes and a main `pcolormesh` axis can both contain a
     `QuadMesh`. Never skip every `QuadMesh` axis when injecting plot labels:
     skip only an untitled colorbar axis (or use an explicit colorbar-axis
     identity test). Otherwise P## labels silently disappear from Mollweide
     maps.
   - Verify a real PNG at native or downscaled resolution for the visible P##
     identifier, title, units, mask note, and absence of clipping/overlap.
     Do not rely only on PDF text extraction.

6. **Assemble without dropping pages**
   - If the canonical PDF contains appended pages not present in the local
     figure directory, do not blindly rebuild from the directory.
   - Replace the intended page interval explicitly with PyMuPDF/pdfunite and
     preserve all other pages.
   - Verify page count and extractable labels around both the replacement range
     and preserved appended pages.

7. **Final gates**
   - Render all requested plots successfully.
   - Inspect sidecars: dataset, loader, convergence count, physical ranges,
     minimum cell count, sign convention, and unit scale.
   - Run the bundle audit: source IDs, duplicate IDs, sidecars, images, and PDF
     page count.
   - Perform visual QA on a montage plus at least one actual PNG.
   - Compute and report a checksum only after the final artifact is assembled.
   - Commit and push only after these checks pass.

## Reusable verification commands

```bash
PYTHONPATH=src python3 -m compileall -q src/sh26/plots
python3 scripts/audit_figure_bundle.py --sidecar-dir paper/figures --pdf sh26_all_figures.pdf
pdfinfo sh26_all_figures.pdf | grep -E 'Pages|File size'
sha256sum sh26_all_figures.pdf
```

For residual maps, independently calculate finite/physical-range counts and
check the direction of the median residual on a representative sample before
trusting the color scale.

## References

- `references/mollweide-full-catalog-qa.md` — reusable incident and verification
  details from a full-catalog P40–P50 production run.
