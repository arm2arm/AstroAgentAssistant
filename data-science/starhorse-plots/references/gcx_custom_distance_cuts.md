## Custom Distance Cuts for Galactic Center Sub-Catalogs

### Pattern
When generating a sub-set of figures with a `dist50 < N kpc` distance cap (e.g., GCx plots), do NOT rely on the native CLI. The individual plot renderers apply their own internal masks (`dropna`, photometry guards) and never see a global distance cut if you just pipe the CLI output.

### Correct Workflow
1. **Use the wrapper script:** `scripts/gcx_plots.py`
   - Sets `PLOT_IDS = [...]` for the specific figures required
   - Loads full data: `Catalog(columns, derived, quality_cuts=False)`
   - Applies mask: `df = df_full[(df_full["dist50"].notna()) & (df_full["dist50"] < N)]`
   - Passes the sliced `df` to every registry render function.

2. **Column pruning workaround:** (CRITICAL)
   Dask column pruning reads ONLY the union of columns required by the requested plots. If you request plot N8 (`teff50`) but apply a filter on `dist50`, the KeyError will trigger because `dist50` was pruned. The script fixes this:
   ```python
   if "dist50" not in columns:
       columns.append("dist50")
   ```
   This guarantees the filtering column survives the Dask read graph.

3. **Provenance & Output:**
   Outputs are written to `paper/figures_gcx/`. The PlotContext is passed `extra={"cut": "dist50 < N kpc"}`, which embeds the distance cut in every JSON sidecar automatically. A PyMuPDF combiner merges the subset into a single output PDF at project root (`sh26_gcx_n1_nN.pdf`).
