---
name: rave-dr6-tap-query
title: Query RAVE DR6 Catalog via TAP/pyvo
author: Hermes Assistant
version: 1.0
description: Query the RAVE DR6 catalog hosted at https://www.rave-survey.org/tap/ using pyvo (TAPService.run_sync). Useful for accessing stellar parameters, Gaia cross-matches, distances, and Galactic coordinates (l, b). Includes galactic projection (xgal/ygal) and equirectangular (RA/Dec) plotting recipes.
---

# Overview
Query the RAVE (RAdial Velocity Experiment) 6th Data Release via its Table Access Protocol (TAP) endpoint using the `pyvo` library. This avoids browser-based queries and lets you pull data directly into Python/pandas for analysis or plotting.

The RAVE TAP service is at `https://www.rave-survey.org/tap/` and hosts ~30 tables including the main DR6 tables, Gaia DR2/EDR3 cross-matches, seismic data, and more.

# Prerequisites
```bash
pip install --quiet pyvo pandas matplotlib seaborn
```

# Key Tables
| Table | Description |
|---|---|
| `ravedr6.dr6_sparv` | Master file + classification + obs diagnostics |
| `ravedr6.dr6_x_gaiaedr3` | Gaia EDR3 cross-match — **has ra, dec, parallax, phot_g_mean_mag, bp_rp** |
| `ravedr6.dr6_x_gaiadr2` | Gaia DR2 cross-match |
| `ravedr6.dr6_orbits` | Orbital parameters |
| `ravedr6.dr6_seismic` | Seismic data |
| `ravedr6.dr6_madera` | Asteroseismic parameters |

# Steps
## 1. Connect to the TAP service
```python
import pyvo, pandas as pd, numpy as np, warnings
warnings.filterwarnings('ignore')

tap = pyvo.dal.TAPService('https://www.rave-survey.org/tap/')
```
## 2. Run a synchronous query (including radial velocity)
```python
query = """
SELECT TOP 100
    source_id, ra, dec, l, b, parallax, dr2_radial_velocity
FROM ravedr6.dr6_x_gaiaedr3
WHERE parallax > 0
ORDER BY parallax DESC
"""
result = tap.run_sync(query)
df = result.to_table().to_pandas()
# If radial velocity is missing, fall back to NaN
if 'dr2_radial_velocity' not in df.columns:
    df['dr2_radial_velocity'] = np.nan
rv_col = 'dr2_radial_velocity'
```
## 3. Save locally as Parquet (requires `pyarrow`)
```python
# Ensure Parquet engine is available
import pandas as pd
# `pip install pyarrow` may be required beforehand
df.to_parquet('rave_dr6_closest100.parquet', index=False)
```
## 4. Galactic projection (xgal vs ygal) – colour by RV
```python
l_rad = np.radians(df['l'].values)
b_rad = np.radians(df['b'].values)
df['xgal'] = np.cos(b_rad) * np.cos(l_rad)
df['ygal'] = np.cos(b_rad) * np.sin(l_rad)
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, seaborn as sns
sns.set_style('whitegrid')
fig, ax = plt.subplots(figsize=(8,7))
scatter = ax.scatter(df['xgal'], df['ygal'], c=df[rv_col], cmap='plasma', s=70, edgecolors='white', linewidths=0.5, alpha=0.9)
ax.scatter(0,0,c='gold',s=300,marker='o',edgecolors='orange',linewidths=2,zorder=10)
ax.annotate('Sun', xy=(0,0), xytext=(0.07,0.07), fontsize=12, color='darkorange', fontweight='bold', arrowprops=dict(arrowstyle='->',color='darkorange',lw=1.5))
ax.set_xlabel('xgal = cos(b) cos(l)')
ax.set_ylabel('ygal = cos(b) sin(l)')
ax.set_aspect('equal')
cb = fig.colorbar(scatter, ax=ax, shrink=0.8)
cb.set_label('Radial velocity [km/s]')
fig.tight_layout()
fig.savefig('rave_dr6_xgal_ygal.png', dpi=180)
```
## 5. Plot RA vs Dec – colour by RV
```python
fig2, ax2 = plt.subplots(figsize=(12,5))
scatter2 = ax2.scatter(df['ra'], df['dec'], c=df[rv_col], cmap='plasma', s=60, edgecolors='white', linewidths=0.4, alpha=0.9)
ax2.set_xlabel('RA [deg]')
ax2.set_ylabel('Dec [deg]')
ax2.set_title(f'RA vs Dec — {len(df)} RAVE DR6 Stars')
cb2 = fig2.colorbar(scatter2, ax=ax2, shrink=0.8)
cb2.set_label('Radial velocity [km/s]')
fig2.tight_layout()
fig2.savefig('rave_dr6_ra_dec.png', dpi=180)
```
## 1. Connect to the TAP service
```python
import pyvo, pandas as pd, warnings
warnings.filterwarnings('ignore')

tap = pyvo.dal.TAPService("https://www.rave-survey.org/tap/")
```

## 2. List all available tables
```python
for t in tap.tables:
    print(t.name)
```

## 3. Check columns of a table
```python
t = tap.tables['ravedr6.dr6_x_gaiaedr3']
for c in t.columns:
    print(c.name)
```

## 4. Run a synchronous query
Use `run_sync()` — **not** `query()` or bare `submit_job()` (those either don't exist or use async and fail with 400 errors). Note that `l` (Galactic longitude) and `b` (Galactic latitude) are also available in `dr6_x_gaiaedr3`:
```python
query = \"\"\"
SELECT TOP 100
    source_id, ra, dec, l, b, parallax, phot_g_mean_mag, bp_rp
FROM ravedr6.dr6_x_gaiaedr3
WHERE parallax > 0
ORDER BY parallax DESC
\"\"\"
result = tap.run_sync(query)
df = result.to_table().to_pandas()
```

## 5. Save locally as Parquet
```python
df.to_parquet('rave_dr6_closest100.parquet', index=False)
```

## 6. Galactic projection (xgal vs ygal)
The `dr6_x_gaiaedr3` table also contains `l` (Galactic longitude) and `b` (Galactic latitude). Project onto the Galactic plane:

```python
import numpy as np
l_rad = np.radians(df['l'].values)
b_rad = np.radians(df['b'].values)
df['xgal'] = np.cos(b_rad) * np.cos(l_rad)
df['ygal'] = np.cos(b_rad) * np.sin(l_rad)
```

Plot with the Sun at the origin:
```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style('whitegrid')
fig, ax = plt.subplots(figsize=(8, 7))
scatter = ax.scatter(df['xgal'], df['ygal'], c=df['parallax'], cmap='plasma',
                     s=70, edgecolors='white', linewidths=0.5, alpha=0.9)
# Sun at Galactic centre
ax.scatter(0, 0, c='gold', s=300, marker='o', edgecolors='orange', linewidths=2, zorder=10)
ax.annotate('Sun', xy=(0, 0), xytext=(0.07, 0.07),
            fontsize=12, color='darkorange', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='darkorange', lw=1.5))
ax.set_xlabel('xgal = cos(b) cos(l)')
ax.set_ylabel('ygal = cos(b) sin(l)')
ax.set_aspect('equal')
ax.set_xlim(-1.1, 1.1); ax.set_ylim(-1.1, 1.1)
cb = fig.colorbar(scatter, ax=ax, shrink=0.8)
cb.set_label('Parallax [mas]', rotation=270, labelpad=12)
fig.tight_layout()
fig.savefig('rave_dr6_xgal_ygal.png', dpi=180)
```

## 7. Plot RA vs Dec (equirectangular projection)
```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style('whitegrid')
fig, ax = plt.subplots(figsize=(12, 5))
scatter = ax.scatter(df['ra'], df['dec'], c=df['parallax'], cmap='plasma',
                     s=60, edgecolors='white', linewidths=0.4, alpha=0.9)
ax.set_xlabel('RA [deg]')
ax.set_ylabel('Dec [deg]')
ax.set_title(f'RA vs Dec — {len(df)} RAVE DR6 Stars')
cb = fig.colorbar(scatter, ax=ax, shrink=0.8)
cb.set_label('Parallax [mas]', rotation=270, labelpad=12)
fig.tight_layout()
fig.savefig('rave_dr6_ra_dec.png', dpi=180)
```

# Pitfalls & Tips
- **`run_sync()` is the correct method** — `submit_job()` uses async and returns 400 Bad Request on this server.
- **`query()` does not exist** on TAPService — always use `run_sync()` for synchronous queries.
- The `ravedr6.dr6_x_gaiaedr3` table is the best source for distances (parallax), coordinates (ra, dec), AND Galactic coordinates (l, b) in one table.
- Filter `parallax > 0` to exclude negative parallax entries (which correspond to stars with poorly constrained distances).
- If you need only a few columns, select them explicitly to reduce data transfer.
- The TAP service may time out on very large queries; use `TOP N` or `WHERE` clauses to limit results.
- `pyvo` may not be pre-installed — install with `pip install --quiet pyvo` before use.
- For the 100 closest stars, `parallax > 0 AND ORDER BY parallax DESC` gives the nearest stars first (parallax in mas → distance in pc ≈ 1000/parallax).
- **When using `curl` to hit the TAP sync endpoint, the response is a VOTable XML, not a plain CSV.** Use a POST request with appropriate parameters, or prefer the `pyvo` library which handles parsing automatically. If you must use `curl`, you’ll need to parse the VOTable (e.g., with `astropy.io.votable`).
- **`run_sync()` is the correct method** — `submit_job()` uses async and returns 400 Bad Request on this server.
- **`query()` does not exist** on TAPService — always use `run_sync()` for synchronous queries.
- The `ravedr6.dr6_x_gaiaedr3` table is the best source for distances (parallax), coordinates (ra, dec), AND Galactic coordinates (l, b) in one table.
- Filter `parallax > 0` to exclude negative parallax entries (which correspond to stars with poorly constrained distances).
- If you need only a few columns, select them explicitly to reduce data transfer.
- The TAP service may time out on very large queries; use `TOP N` or `WHERE` clauses to limit results.
- `pyvo` may not be pre-installed — install with `pip install --quiet pyvo` before use.
- For the 100 closest stars, `parallax > 0 AND ORDER BY parallax DESC` gives the nearest stars first (parallax in mas → distance in pc ≈ 1000/parallax).