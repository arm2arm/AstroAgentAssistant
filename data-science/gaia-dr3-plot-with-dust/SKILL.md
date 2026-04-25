---
name: gaia-dr3-plot-with-dust
title: Gaia DR3 – 100 Closest Stars Plot with Dust Overlay
author: Hermi (sorgenfresser)
version: 1.0
description: Retrieve the 100 nearest Gaia DR3 stars (by parallax) and produce a two‑panel research‑paper‑style figure. The left panel shows RA vs Dec, the right panel shows a Galactic XY projection overlaid with an all‑sky dust‑extinction map (SFD) using the dustmaps package.
---

# Overview
This skill demonstrates how to combine a Gaia DR3 query (via the AIP TAP service) with an extinction map to visualise the nearest stars against Milky‑Way dust lanes. The output is a 12 × 6 in, 300 dpi PNG suitable for inclusion in a manuscript.

# Prerequisites
```bash
pip install --quiet --break-system-packages \
    pyvo pandas matplotlib seaborn dustmaps
# Download the SFD dust map (run once)
python -c "import dustmaps.sfd; dustmaps.sfd.fetch()"
```

# Steps
## 1. Query Gaia DR3 for the 100 closest stars
```python
import warnings, os
warnings.filterwarnings('ignore')
import pyvo, pandas as pd

service = pyvo.dal.TAPService('https://gaia.aip.de/tap/')
query = """
SELECT TOP 100 source_id, ra, dec, l, b, parallax, phot_g_mean_mag, bp_rp
FROM gaiadr3.gaia_source
WHERE parallax > 0
ORDER BY parallax DESC
"""
result = service.run_sync(query)

df = result.to_table().to_pandas()
# Cache for later reuse
df.to_parquet('/home/hermes/gaia_dr3_closest100.parquet', index=False)
```

## 2. Prepare the dust‑extinction background
```python
from dustmaps.sfd import SFDQuery
from astropy.coordinates import SkyCoord
import astropy.units as u
import numpy as np

# Build a regular (l, b) grid covering the Galactic XY square
l_grid = np.linspace(0, 360, 720)   # 0.5° steps
b_grid = np.linspace(-90, 90, 360) # 0.5° steps
L, B = np.meshgrid(l_grid, b_grid)
coords = SkyCoord(l=L*u.deg, b=B*u.deg, frame='galactic').icrs

dust = SFDQuery()
ebv = dust(coords)   # reddening E(B‑V) in mag
```

## 3. Create the figure
```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

fig, axs = plt.subplots(1, 2, figsize=(12, 6), facecolor='white')

# ----- Left: RA vs Dec -----
ax = axs[0]
sc = ax.scatter(df['ra'], df['dec'], c=df['parallax'], cmap='viridis',
                s=60, edgecolor='black', linewidth=0.4)
ax.set_xlabel('RA [deg]', fontsize=12)
ax.set_ylabel('Dec [deg]', fontsize=12)
ax.set_title('Gaia DR3 – 100 Closest Stars (RA/Dec)', fontsize=14)
fig.colorbar(sc, ax=ax, label='Parallax [mas]')

# ----- Right: Galactic XY + dust -----
ax = axs[1]
# Show dust as a faint grayscale background
ax.imshow(ebv, extent=[-1.1, 1.1, -1.1, 1.1], origin='lower',
          cmap='gray_r', alpha=0.4, interpolation='nearest')
# Convert star positions to Galactic Cartesian (unit sphere)
l_rad = np.radians(df['l'].values)
b_rad = np.radians(df['b'].values)
x = np.cos(b_rad) * np.cos(l_rad)
y = np.cos(b_rad) * np.sin(l_rad)
sc2 = ax.scatter(x, y, c=df['parallax'], cmap='viridis',
                 s=70, edgecolor='black', linewidth=0.5)
# Sun marker
ax.scatter(0, 0, c='gold', s=300, marker='o', edgecolor='orange')
ax.annotate('Sun', xy=(0,0), xytext=(0.07,0.07), fontsize=10,
            color='darkorange', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='darkorange'))
ax.set_xlabel('x = cos(b)·cos(l)', fontsize=12)
ax.set_ylabel('y = cos(b)·sin(l)', fontsize=12)
ax.set_title('Galactic XY Projection (dust overlay)', fontsize=14)
ax.set_aspect('equal')
ax.set_xlim(-1.1, 1.1)
ax.set_ylim(-1.1, 1.1)
fig.colorbar(sc2, ax=ax, label='Parallax [mas]')

# Save
out_path = '/home/hermes/gaia_dr3_paper_style_with_dust.png'
plt.tight_layout()
plt.savefig(out_path, dpi=300, bbox_inches='tight')
plt.close()
print(f'DONE – figure saved to {out_path}')
```

# Pitfalls & Tips
- **Dustmap download** – `dustmaps.sfd.fetch()` needs internet once; subsequent runs are instant.
- **Grid resolution** – 0.5° steps give a smooth background without excessive memory use. Adjust `l_grid`/`b_grid` for higher‑resolution plots.
- **AIP TAP endpoint** – `https://gaia.aip.de/tap/` works reliably; other ESA endpoints may reject the `TOP` syntax.
- **File paths** – The script writes to `/home/hermes/`; change if you prefer another directory.
- **Dependencies** – `dustmaps` pulls in `astropy`; ensure the environment has the compatible version (>=5.0).

# Verification
After execution you should find:
- `/home/hermes/gaia_dr3_closest100.parquet` (full data)
- `/home/hermes/gaia_dr3_paper_style_with_dust.png` (the final figure)

The figure shows the stars colour‑coded by parallax over a faint dust‑extinction background, ideal for a research article.
---
