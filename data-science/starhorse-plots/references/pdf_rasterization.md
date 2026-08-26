# Rasterising dense collections in PDF output (Acrobat slowness fix)

**Symptom:** combined SH26 figure PDFs (42 pages) render extremely slowly in
Acrobat Reader — worst on the big hexbins (P08–P12, P17–P20, P01 CMD).
Root cause: matplotlib writes hexbin cells / scatter points / pcolormesh
shades as *vector paths* into the PDF; Acrobat strokes millions of cell
edges per page flip.

**Fix (implemented 2026-08-15 in `src/sh26/context.py` `save()`):** mark
the dense artists `rasterized=True` before `savefig(format="pdf")`.
Matplotlib then embeds them as a single 300-dpi bitmap XObject; text,
axes, lines and colorbar text stay vector.

```python
# in PlotContext.save(), before the savefig loop
from matplotlib.collections import PolyCollection, PathCollection, QuadMesh
for ax in fig.get_axes():
    for artist in ax.get_children():
        if isinstance(artist, (PolyCollection, PathCollection, QuadMesh)):
            artist.set_rasterized(True)
```

**Pitfalls:**
- matplotlib 3.11: `QuadMesh` imports from **`matplotlib.collections`**
  (`matplotlib.axes._axes.QuadMesh` no longer exists; Pyright errors on
  the old path). `ax.hexbin()` returns a `PolyCollection`; scatter a
  `PathCollection`; pcolormesh a `QuadMesh`.
- Verification: `grep -a -c '/Subtype /Image' file.pdf` (or regex count)
  should show 1–3 raster XObjects per dense page and ~zero vector
  line-draw ops; old un-rasterized P19 was 105 KB of paths, new one 286 KB
  of JPEG-compressed bitmap — instant in Acrobat.
- PNG output is unaffected (already raster at `dpi=300`).
- Raster quality: the bitmap is saved at figure dpi (300) so zoom in
  Acrobat is pixelated beyond ~3× — acceptable for paper-figure review;
  keep the vector source (the script) if vector PDF is ever required.

**Related user preference:** user asked for smooth/KDE alternatives to
griddy quantized hexbins (P19 [Fe/H]) — rejected as too slow
("stop smoothed way, too slow keep normal hexbin"). Keep plain hexbin for
50M-row plots; quantization (0.1 dex grid in the data) is data-intrinsic,
not a plotting artifact.
