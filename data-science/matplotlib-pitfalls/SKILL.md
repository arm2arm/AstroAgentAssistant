---
name: matplotlib-pitfalls
description: Common matplotlib gotchas that silently produce wrong output — hexbin+log+inverted-axis blank plots, LogNorm usage, notebook cell source joining pitfalls.
category: data-science
---

# Matplotlib Pitfalls & Known Bugs

Workarounds for common matplotlib gotchas that silently produce wrong output (empty plots, wrong binning, etc.).

## Hexbin + Greys + Unbounded LogNorm = Invisible Sparse Data (CMD wash-out)

### Symptom
A color–magnitude / density hexbin looks "cut" or "partially plotted": only the dense peak (e.g. red clump) shows; faint/sparse regions (main sequence, low-count tails) look empty even though the underlying data has many points there. `df` confirms tens of thousands of points in the "missing" region.

### Root Cause
`cmap='Greys'` maps low values → near-white. Combined with unbounded `norm=LogNorm()` (vmin defaults to data min ≈ 1), bins holding only 1–2 counts render white-on-white against the white figure background. The data IS plotted — just invisible; the high-count bins dominate the log stretch so the sparse population vanishes.

### Fix
High-contrast colormap + pin `vmin=1` + fixed extent so the sparse region fills the panel:

```python
from matplotlib.colors import LogNorm
fig, ax = plt.subplots(figsize=(10, 8))
hb = ax.hexbin(x, y, gridsize=250, cmap='inferno',
               norm=LogNorm(vmin=1), mincnt=1,
               extent=(x0, x1, y_lo, y_hi))  # extent: ASCENDING y
ax.set_ylim(y_hi, y_lo)   # invert magnitude axis separately, NOT via extent
fig.colorbar(hb, ax=ax, label='Counts')
```

- `extent` requires ascending y (`ymin < ymax`); invert the axis afterwards with `set_ylim(hi, lo)` — never reverse the extent (raises "ymax must be greater than ymin").
- Use a dark-through colormap (`inferno`, `viridis`, `magma`); avoid light-to-white maps (`Greys`) for sparse density on white backgrounds.

### Verify without vision QA
When image-inspection tools time out, confirm populations numerically: count points in magnitude/color windows (giants / main-sequence / faint bins). High counts + empty-looking figure ⇒ rendering problem (cmap/norm), not the data.

## Hexbin + Log Scale + Inverted X-Axis = Blank Plot

### Symptom
`ax.hexbin()` followed by `ax.set_xscale('log')` and reversed `ax.set_xlim(hi, lo)` produces a completely blank plot despite valid data.

### Root Cause
`hexbin` creates hexagonal bins in **linear** x-space. When `set_xscale('log')` is applied *after* the hexbin, the bins are mapped through a log transform — but with a **reversed** xlim (hot-on-left convention), the transformed hex grid is displaced outside the visible range. The data is there, the hex grid exists, but none of it falls in the plot viewport.

### Fix: Use `pcolormesh` with Pre-Computed Log Bins

```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

# Data
x = data_teff  # e.g. 2500-25000 K
y = data_logg  # e.g. -0.5 to 5.8

# Log-spaced x bins (pre-computed)
x_edges = np.logspace(np.log10(2500), np.log10(25000), 200)
y_edges = np.linspace(-0.5, 5.8, 120)

# Histogram in pre-computed bin grid
H, _, _ = np.histogram2d(x, y, bins=[x_edges, y_edges])
H = H.T  # transpose for pcolormesh convention

fig, ax = plt.subplots(figsize=(10, 10))
im = ax.pcolormesh(x_edges, y_edges, H, cmap='inferno',
                   norm=LogNorm(), shading='auto')
fig.colorbar(im, ax=ax, label='count (log)')

ax.set_xscale('log')
ax.set_xlim(25000, 2500)  # reversed — now safe, bins already log-spaced
ax.set_ylim(-0.5, 5.8)
```

### When This Pattern Appears
- **Kiel diagrams** (Teff vs log g, hot on left): the most common case in stellar astronomy
- Any 2D histogram (hexbin, hist2d) where the x-axis is log-spaced AND reversed
- CMD plots (color vs magnitude) if using log-scale x with reversed axis

### Verification
After plotting, check `hb.get_array()` for hexbin — if it's all NaN or empty after `set_xscale`+`set_xlim`, the bins are lost. With `pcolormesh`, verify `(H > 0).sum()` is large and the image renders before saving.

## Hexbin / Hist2D + NaNs = Blank Plots

### Symptom
A plot using `ax.hexbin()` or `plt.hist2d()` appears completely empty or blank, even though the input arrays contain valid data.

### Root Cause
If the input arrays contain any `NaN` values, Matplotlib's binning logic (especially when calculating `LogNorm` or using a `C` parameter with `reduce_C_function`) may fail to render the bins correctly. In some versions, the presence of NaNs causes the entire collection to fail rendering silently.

### Fix
Always filter out NaNs from the plotting variables before calling the binning function:

```python
# Create a temporary dataframe/view for plotting
df_plot = df.dropna(subset=['x_col', 'y_col'])
plt.hexbin(df_plot['x_col'], df_plot['y_col'], ...)
```

## AttributeError: PolyCollection.set() got an unexpected keyword argument 'reduce_fcn'

### Symptom
`AttributeError: PolyCollection.set() got an unexpected keyword argument 'reduce_fcn'` when calling `ax.hexbin`.

### Fix
In Matplotlib 3.8+, the parameter `reduce_fcn` was renamed to `reduce_C_function`.

```python
# OLD
hb = ax.hexbin(x, y, C=z, reduce_fcn=np.median)

# NEW (3.8+)
hb = ax.hexbin(x, y, C=z, reduce_C_function=np.median)
```

## Kiel Diagram Axis Convention

### Symptom
Kiel diagram (Teff vs log g) has high log g on top instead of bottom — the evolutionary sequences (main sequence, giant branch) appear flipped compared to standard stellar astronomy convention.

### Convention
Kiel diagrams follow the H-R diagram convention: **hot on left, high log g on bottom**. This means BOTH axes are inverted relative to normal matplotlib defaults:
- **X-axis**: Teff, log scale, reversed (20000 → 2000 K, hot on left)
- **Y-axis**: log g, linear scale, **reversed** (5.5 → -0.5, high gravity at bottom)

### Fix
When building a Kiel diagram, flip BOTH axes:
```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

TEFF_MIN, TEFF_MAX = 2000, 40000
LOGG_MIN, LOGG_MAX = -0.5, 5.5

# Pre-compute log-spaced bins
teff_edges = np.logspace(np.log10(TEFF_MIN), np.log10(TEFF_MAX), 200)
logg_edges = np.linspace(LOGG_MIN, LOGG_MAX, 120)

# 2D histogram
H, _, _ = np.histogram2d(teff_values, logg_values, bins=[teff_edges, logg_edges])
H = H.T

fig, ax = plt.subplots()
im = ax.pcolormesh(teff_edges, logg_edges, H, cmap='inferno', norm=LogNorm(), shading='auto')

# BOTH axes inverted — standard Kiel convention
ax.set_xscale('log')
ax.set_xlim(TEFF_MAX, TEFF_MIN)    # 40000 → 2000, hot on left
ax.set_ylim(LOGG_MAX, LOGG_MIN)   # 5.5 → -0.5, high logg at bottom
```

### Note
The old SH2021 notebook used `logteff = np.log10(teff50)` on a linear axis with `invert_xaxis=True`. My implementation uses raw Teff with `set_xscale('log')` — visually equivalent, same axis convention. The y-axis flip (`set_ylim(LOGG_MAX, LOGG_MIN)`) is equally required in both approaches.

## Hexbin LogNorm Warning

### Symptom
`ax.hexbin(..., log=True)` raises `AttributeError: PolyCollection.set() got an unexpected keyword argument 'log'`

### Fix
Use `norm=LogNorm()` instead of `log=True`:

```python
# WRONG
hb = ax.hexbin(x, y, log=True)

# RIGHT
from matplotlib.colors import LogNorm
hb = ax.hexbin(x, y, norm=LogNorm())
```

## Telegram/Mobile Rendering: Empty Media Boxes

### Symptom
`MEDIA:/path/to/image.png` results in an empty dark box or "image not found" in the Telegram mobile client, even if the file exists on the agent's filesystem.

### Root Cause
The `MEDIA:` protocol relies on the platform gateway's ability to pull and upload the file. Large files, slow disk I/O, or transient gateway-to-backend connection issues can cause the upload to time out or fail silently, leaving a placeholder in the chat.

### Fix: S3 Fallback
Upload the file to the AIP S3 media bucket and use the returned URL.

```bash
# Upload via terminal
python3 ~/.hermes/scripts/s3_media_upload.py /home/hermes/projects/SH26/img/sh26_kiel.png
# Output: ![uploaded](https://s3.data.aip.de:9000/scr4agent/hermes/...)
```

Include the resulting markdown image link in your response. This ensures the Telegram client loads the image from a stable CDN/S3 endpoint.

## Jupyter Notebook Syntax Errors: Unexpected Character after Line Continuation

### Symptom
`SyntaxError: unexpected character after line continuation character` when executing a notebook cell that was patched or written programmatically.

### Root Cause
When writing code strings to a JSON notebook's `source` list, using `\n` inside a string that is already being escaped (e.g., in a Python f-string or raw string) can result in literal `\n` characters appearing in the notebook source instead of actual newlines. Jupyter/IPython interprets `\n` as a backslash followed by 'n', and if it follows a line-ending backslash, it triggers the "unexpected character" error.

### Fix
Ensure the `source` field in the notebook JSON is a list of strings, where **each string ends with a real newline** `\n`. Avoid embedding `\n` markers inside a single long string in the list.

```python
# WRONG (Literal \n in source)
"source": ["ax.set_xlim(11000, 2000)\\nax.set_ylim(5.5, -0.5)"]

# RIGHT (List of terminated strings)
"source": [
    "ax.set_xlim(11000, 2000)\n",
    "ax.set_ylim(5.5, -0.5)\n"
]
```

## Renderer-Based Collision Detection for Diagram Figures (vision-free QA)

### When
Schematic figures (FancyBboxPatch cards, badges, `ax.text` labels) need overlap/clipping QA but visual inspection is unavailable or unreliable. This method is *exact* — in practice it caught real text-on-text collisions that PIL pixel statistics (ink fractions, edge checks) completely missed.

### Technique
Ask matplotlib's own renderer for every artist's bounding box and intersect them:

```python
import matplotlib
matplotlib.use('Agg')
# ... build the figure so `fig`, `ax` exist ...
fig.canvas.draw()
ren = fig.canvas.get_renderer()

texts = [(t.get_text()[:30], t.get_window_extent(ren))
         for t in ax.texts if t.get_text()]

def overlap(b1, b2):
    return not (b1.x1 <= b2.x0 or b2.x1 <= b1.x0
                or b1.y1 <= b2.y0 or b2.y1 <= b1.y0)

bad = [(t1, t2) for i, (t1, b1) in enumerate(texts)
       for t2, b2 in texts[i+1:] if overlap(b1, b2)]

# clipping check: anything outside the canvas?
W, H = fig.get_size_inches() * fig.dpi
out = [t for t, b in texts
       if b.x0 < -1 or b.y0 < -1 or b.x1 > W+1 or b.y1 > H+1]
print("text-text overlaps:", bad, "| outside canvas:", out)
```

Iterate layout fixes until `bad == []` and `out == []`. Patch extents work the same way via `p.get_window_extent(ren)` on `ax.patches`.

### Preferred structure: function-per-figure + BUILDERS dict
Restructure multi-figure generator scripts so each figure is a function returning `(fig, ax)`, registered in a dict. This eliminates helper-name collisions entirely AND makes whole-library QA a short loop:

```python
def fig_drp_levels(): ...; return fig, ax
def fig_reana_flow(): ...; return fig, ax

BUILDERS = {'drp_levels': fig_drp_levels, 'reana_flow': fig_reana_flow}

if __name__ == '__main__':
    for name, builder in BUILDERS.items():
        fig, _ = builder()
        _save(fig, name)
```

QA all figures at once (no source slicing needed):
```python
import importlib.util, sys
spec = importlib.util.spec_from_file_location("figs", "make_all_figs.py")
m = importlib.util.module_from_spec(spec); sys.modules["figs"] = m
spec.loader.exec_module(m)   # __main__ guard blocks generation
for name, builder in m.BUILDERS.items():
    fig, ax = builder()
    fig.canvas.draw()
    # ... renderer overlap + clipping checks from above, per figure ...
```

### Fallback: testing one figure block from a flat script
If the script is still flat (module-level blocks), slice the source between block markers and `exec` it into a namespace:

```python
src = open('make_all_figs.py').read()
header = src[:src.index('# Fig 1')]          # imports + palette + helpers
block  = src[src.index('# Fig 3'):src.index("save('figname')")]
ns = {}
exec(compile(header + block, 'figblock', 'exec'), ns)
fig, ax = ns['fig'], ns['ax']                # then run the check above
```

### Palette conformance audit (verify a restyle actually landed)
After changing a figure set's palette, verify per-PNG that new accent colors are present and stale ones are gone:

```python
a = np.asarray(Image.open(f'{name}.png').convert('RGB')).astype(int)
for lab, rgb in NEW_PALETTE.items():
    present = (np.abs(a - rgb).sum(axis=2) < 30).sum() > 200
for lab, rgb in OLD_PALETTE.items():
    stale = (np.abs(a - rgb).sum(axis=2) < 20).sum() > 500
```
Caveat: anti-aliased edges of grey text can false-positive as old light-grey shadow colors (~#D0D0D0). Cross-check against a figure known to be clean before concluding shadows remain.

### Complementary PIL checks (cheap, catch different problems)
- Edge clipping: nonwhite fraction on 3-px border rows/cols should be ~0.
- Presence of accent-colored elements: count pixels within tolerance of expected RGB.
These do NOT detect text-on-text overlap — use the renderer for that.

## Matplotlib 3.11: hexbin `minmax` Parameter Removed

### Symptom
`AttributeError: PolyCollection.set() got an unexpected keyword argument 'minmax'` when calling `ax.hexbin()`.

### Root Cause
In Matplotlib 3.11, the `minmax` parameter was removed from `hexbin()`. This parameter was only ever useful with `reduce_C_function=np.log1p` to force log-scaled bins — but `hexbin` never applied `reduce_C_function` as a color transform anyway. The correct approach is always `norm=LogNorm()` on the `HexBin` collection.

### Fix
```python
# WRONG (3.11+)
hb = ax.hexbin(x, y, reduce_C_function=np.log1p, minmax=True)

# RIGHT — let Matplotlib handle log scaling via norm
from matplotlib.colors import LogNorm
hb = ax.hexbin(x, y, norm=LogNorm(vmin=1))

# For grayscale CMD plots (no log scale needed)
hb = ax.hexbin(x, y, cmap='Greys', mincnt=1)
```

**Note:** `minmax=True` with `reduce_C_function` was a combination that never worked correctly even in earlier versions — it set vmin/vmax to the min/max of the *transformed* C values (i.e., log1p of counts), not the original counts. The `LogNorm` approach gives the correct log-scale color mapping.

### Related
See also: the `reduce_C_function` parameter is also **removed** in newer matplotlib versions. Use `C=...` to pass pre-binned values and `norm=LogNorm()` instead.

## Matplotlib 3.9+ Boxplot API Changes

### Symptom
`TypeError: list indices must be integers or slices, not str` when calling `ax.boxplot()` with `boxprops=[{'facecolor': ...}, ...]` (list of dicts). Also `MatplotlibDeprecationWarning: The 'labels' parameter of boxplot() has been renamed 'tick_labels'`.

### Root Cause
Matplotlib 3.9+ changed how `boxplot` processes `boxprops` — a list of dicts triggers `cbook.normalize_kwargs()` which iterates `.items()` on each element, failing on a dict-of-dicts. Also `labels=` was renamed to `tick_labels=`.

### Fix: Use Default boxplot + Manual Styling
```python
bp = ax.boxplot([group_a, group_b], patch_artist=True)
# Then style via bp dict keys — NOT via complex kwargs
for i, box in enumerate(bp['boxes']):
    box.set_facecolor(colors[i])
    box.set_alpha(0.3)
for i, med in enumerate(bp['medians']):
    med.set_color(colors[i])
    med.set_linewidth(2)
# For tick labels (3.9+):
ax.set_xticklabels(['Label A', 'Label B'])
```

### Why `patch_artist=True` + simple call works
When `patch_artist=True` and no complex `boxprops` list is passed, `boxplot` returns `bp['boxes']` as `Rectangle` patches that support `set_facecolor()`. This is the most compatible approach across matplotlib versions.

### When to Use bxp() Directly
For full control, build `bxp()` data dicts manually (requires `med`, `q1`, `q3`, `whislo`, `whishi`, `fliers`, `boxes`, `caps`, `widths` keys). But the simple `boxplot()` + manual styling is usually sufficient and more maintainable.

## Helper-Name Collisions in Flat Multi-Figure Scripts

### Symptom
Pyright errors like `Type "FancyBboxPatch" is not assignable to declared type "(...) -> None"`, or wrong behavior at runtime, after adding helper functions to one figure block of a script that draws several figures at module top level.

### Root Cause
All figure blocks share one module namespace. A helper `def card(...)` / `def badge(...)` added for one figure collides with plain variables named `card` / `badge` (assigned patches, circles) in another block.

### Fix
Prefix block-local helpers (`_lcard`, `_nbadge`) or wrap each figure in its own function. Before naming a helper after a common noun (card, badge, box, arrow, circle), grep the script for existing assignments to that name.

## Matplotlib Animation → MP4/GIF: Silent Failures on Agg Backend

### Failure 1: FuncAnimation + blit = static/blank frames
`FuncAnimation(fig, update, blit=True)` on the Agg backend silently produces identical empty or static frames. `set_data()` and `set_xdata/set_ydata` do NOT mark artists as stale under Agg—so `fig.canvas.draw()` renders the prior state.

**Fix:** Per-frame save loop with explicit line removal and redraw:
```python
x = np.linspace(0, 4*np.pi, 500)
fig, ax = plt.subplots(figsize=(8,5))
ref_line = ax.plot(x, np.sin(x), color='#ddd')[0]  # keeps reference visible
frames_buf = []
for i in range(1, len(x)+1):
    for child in ax.lines:
        if child is not ref_line:
            child.remove()
    ax.plot(x[:i], np.sin(x[:i]), color='red', lw=3)
    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba())[:, :, :3]
    frames_buf.append(buf)

import imageio.v2 as imageio
imageio.mimsave('/tmp/out.gif', frames_buf, fps=25)  # GIF works fine via Pillow
```

### Failure 2: Odd-dimension PNGs → x264 = zero-byte MP4 silently
`bbox_inches='tight'` frequently produces odd pixel widths (e.g., 717 px). x264 silently rejects them—no CLI error, just an empty output stream with 0 kb/s bitrate.

**Fix:** Force even dimensions via vf scale filter:
```bash
ffmpeg -y -framerate 25 -start_number 1 \
  -i '/tmp/frames/f_%04d.png' \
  -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p" \
  -c:v libx264 -preset ultrafast -movflags +faststart \
  /tmp/out.mp4
```

### Failure 3: imageio mimsave(.mp4) needs ffmpeg backend plugin
`imageio.mimsave('out.mp4', frames)` fails with `Could not find a capable backend`. Pillow writer only supports GIF.

**Fix:** `pip install "imageio[ffmpeg]"` OR save as GIF via imageio (reliable for small frame counts) and convert to MP4 via ffmpeg separately.

### Proven pipeline (tested, always works on this host)
1. Per-frame PNG save with explicit artist removal/redraw (step 1 pattern above)
2. ffmpeg encode with `trunc(iw/2)*2` even-dimension guard
3. **Always verify:** `ffprobe out.mp4 | grep "Duration"`. Zero duration = broken MP4 even if the file exists and has a non-zero size.
