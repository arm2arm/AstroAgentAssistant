# Full-catalog Mollweide QA reference

## Reusable lessons

- A Matplotlib Mollweide main axis using `pcolormesh` contains a `QuadMesh`,
  just like the colorbar. A blanket `QuadMesh` skip can remove P## labels
  from the actual map. Skip only untitled colorbar axes.
- Verify an actual PNG visually; PDF text extraction can miss rasterized or
  artist-level labels.
- For 402M-row catalogs, use a PyArrow-direct, column-pushdown loader and
  record the converged count in every sidecar. Avoid duplicate concurrent
  launchers, which can cause I/O contention and partial output directories.
- For catalogue residuals, use explicit physical input ranges, state
  `SH26 - reference`, and convert BJ21 parsecs to kpc before subtraction.
- When a PDF contains appended pages absent from the local figure directory,
  replace the intended page interval explicitly rather than rebuilding from
  the directory alone.
