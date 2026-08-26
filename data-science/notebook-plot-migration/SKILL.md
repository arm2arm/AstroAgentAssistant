---
name: notebook-plot-migration
description: "Migrate plots from older analysis notebooks into a consolidated target notebook, converting from hvplot/holoviews to matplotlib."
version: 1.0.0
author: Hermes Agent
tags: [notebook, matplotlib, hvplot, plot, migration, jupyter]
---

# Notebook Plot Migration

## Overview

Migrate plotting cells from older analysis notebooks into a consolidated target notebook, converting from `hvplot`/`holoviews` to pure `matplotlib`.

## When to Use

- User asks to consolidate plots, merge notebooks, or move plots from old notebooks into a master notebook
- Converting old `hvplot`/`holoviews` cells to `matplotlib` for reproducibility
- Adding new plots from old notebooks to a current analysis notebook

## Workflow

### 1. Inventory old notebooks

Scan all old notebooks for plotting cells:

```python
import json, glob, os

old_nb_dir = '/path/to/old_notebooks/'
notebooks = sorted(glob.glob(os.path.join(old_nb_dir, '*.ipynb')))

for nb_path in notebooks:
    with open(nb_path) as f:
        nb = json.load(f)
    for cell in nb['cells']:
        if cell['cell_type'] != 'code':
            continue
        src = ''.join(cell['source'])
        if any(kw in src for kw in ['hvplot', 'hv.', 'plt.', 'hexbin', 'hist2d', 'savefig']):
            print(f"{os.path.basename(nb_path)}: plotting cell found")
```

Check which columns are available in the target dataset (`df26.columns`) before committing to a migration plan.

### 2. Build matplotlib equivalents

For each old `hvplot.hexbin(...)` or `hvplot.scatter()` call, write pure `matplotlib` code:

**hvplot hexbin → matplotlib hexbin:**
```python
# OLD (hvplot)
pimg = df.hvplot.hexbin(x='col_a', y='col_b', cmap='viridis', aggregator='count', logz=True)

# NEW (matplotlib)
hb = ax.hexbin(df['col_a'], df['col_b'], gridsize=100, cmap='viridis', mincnt=1, norm=LogNorm())
```

**hvplot scatter → matplotlib scatter:**
```python
# OLD
df.hvplot.scatter(x='col_a', y='col_b')

# NEW
ax.scatter(df['col_a'], df['col_b'], s=1, alpha=0.3)
```

### 3. Append cells to target notebook

```python
with open('/path/to/target.ipynb') as f:
    nb = json.load(f)

new_cell = {
    "cell_type": "code",
    "execution_count": None,
    "id": "unique-cell-id",
    "metadata": {},
    "outputs": [],
    "source": [line + '\n' for line in code.splitlines()]
}

nb['cells'].append(new_cell)

with open('/path/to/target.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)
```

### 4. Test

Run all new cells in sequence with the appropriate dataframe in the namespace:

```python
ns = {'df26': df, 'pd': pd, 'np': np, 'plt': plt, 'os': os, 'LogNorm': LogNorm}
for i in range(new_start_idx, len(nb['cells'])):
    src = '\n'.join(nb['cells'][i]['source'])
    exec(src, ns)
```

### 5. Verify output files

Check that generated PNGs are non-empty (>1KB).

## Pitfalls

- **`log=True` does NOT work with `plt.hexbin()`** — use `norm=LogNorm()` instead. `log=True` is a `seaborn`/`hvplot` parameter that `matplotlib.hexbin` does not recognize. This causes `AttributeError: PolyCollection.set() got an unexpected keyword argument 'log'`.
- **Notebook cell source lines need trailing newlines** — when building cells programmatically, each line in the `source` list must end with `\n`. `''.join(lines)` without newlines concatenates them into a single line, producing `SyntaxError` or `AttributeError` on the first char.
  - Correct: `source = [line + '\n' for line in code.splitlines()]`
  - Verify: run `''.join(cell['source'])[:50]` and check newlines appear
- **Check column names first** — old notebooks often use renamed columns (e.g. `BPRP0` → `bprp0_sh21`, `MG0` → `mg0_sh21`). Always verify column availability before writing migration code.
- **Subsample large datasets** — `hexbin` on millions of points is slow and produces huge PNGs. Use `df.sample(200000)` when `len(df) > 200000`.
- **`plt.hexbin` uses `mincnt=1`** to only draw bins with at least 1 point (equivalent to `logz=True` filtering out zero bins).
- **For 2D histograms with log scale on both axes**, use `ax.hist2d()` with `bins=[np.logspace(...), np.logspace(...)]` and `norm=LogNorm()`, not `hexbin`.
- **Relative paths in notebook cells** fail when exec'd from a different working directory. Always use absolute paths for `os.path.join('/home/hermes/...', 'img')`.
- **Kiel diagrams / hexbin + log scale + inverted xlim = empty plot.** `ax.hexbin()` creates hexagons in linear data space. Calling `ax.set_xscale('log')` followed by `ax.set_xlim(hot, cool)` (hot > cool, i.e. inverted) corrupts hex center mapping — all hexagons end up outside the visible range, producing a blank plot. Fix: use `np.histogram2d()` on a log-spaced grid and render with `ax.pcolormesh()`. This pre-bins data in log space before drawing, so log-axis transforms don't re-map the geometry.
  ```python
  # WRONG (empty plot on log-scale + inverted xlim):
  hb = ax.hexbin(df['teff'], df['logg'], gridsize=60, cmap='viridis')
  ax.set_xscale('log')
  ax.set_xlim(2000, 40000)  # inverted: hot at left, cool at right → empties

  # CORRECT (pcolormesh on pre-binned log data):
  xedges = np.logspace(np.log10(2000), np.log10(40000), 61)
  yedges = np.linspace(np.log10(0), np.log10(5.5), 56)
  H, _, _ = np.histogram2d(np.log10(df['teff']), np.log10(df['logg']),
                           bins=[xedges, yedges])
  im = ax.pcolormesh(xedges, yedges, H.T, cmap='viridis', shading='auto')
  ax.set_xscale('log')
  ax.set_xlim(2000, 40000)   # now hex centers are already in log space
  ax.set_yscale('log')
  ```
- **Notebook structural hygiene** — after migrating plots, restructure the target notebook: (1) single data load in Cell 0, (2) one markdown header per plot type, (3) explicit data filter/convert before each plot call (no repeated imports), (4) no `.head()` or column-list output cells (pollutes execution history). Pattern: `Load → Filter → Transform → Plot → Save`.
- **When migrating multi-panel comparisons** (e.g. SH26 vs SH21 vs model), use `fig, axes = plt.subplots(1, 3, figsize=(15, 4))` and iterate over axes. Save with `fig.savefig(...)` once. Match axis conventions (e.g. Kiel y-axis: high log g at bottom = `ax.invert_yaxis()`).
