---
name: gaia-dr3-tap-query
title: Query Gaia DR3 Catalog via TAP/pyvo (AIP endpoint)
author: Hermi (sorgenfresser)
version: 1.0
description: Retrieve the nearest 100 stars from Gaia DR3 using the TAP service hosted at AIP (https://gaia.aip.de/tap/). Includes Parquet storage, preview CSV, and RA/Dec & Galactic XY plots.
---

# Overview
This skill shows how to programmatically query the Gaia DR3 catalog via a TAP service using the `pyvo` library. It obtains the 100 stars with the largest parallax (closest distances) and produces useful visualisations.

# Prerequisites
```bash
pip install --quiet pyvo pandas matplotlib seaborn
```

# TAP Service
Use the AIP-hosted Gaia TAP endpoint:
```
https://gaia.aip.de/tap/
```
(It provides a stable ADQL interface; other ESA endpoints often reject `TOP`/`LIMIT` syntax or require different auth.)

# Steps
## 1. Connect to the service
```python
import pyvo, warnings
warnings.filterwarnings('ignore')
service = pyvo.dal.TAPService('https://gaia.aip.de/tap/')
```

## 2. Define the query
We want the 100 stars with the highest parallax (positive values only):
```python
query = """
SELECT TOP {N} source_id, ra, dec, l, b, parallax, phot_g_mean_mag, bp_rp  # replace {N} with desired number (e.g., 10)
FROM gaiadr3.gaia_source
WHERE parallax > 0
ORDER BY parallax DESC
"""
```
`TOP 100` works with the AIP service; `LIMIT` is not supported here.

## 3. Execute synchronously
```python
result = service.run_sync(query)
```
If you see a `DALQueryError` or `Cannot parse query` older endpoints, switch to the AIP URL.

## 4. Convert to pandas and cache
```python
import pandas as pd
df = result.to_table().to_pandas()
parquet_path = '/home/hermes/gaia_dr3_closest100.parquet'
df.to_parquet(parquet_path, index=False)
# preview CSV (first 20 rows)
df.head(20).to_csv('/home/hermes/gaia_dr3_closest100_preview.csv', index=False)
```

## 5. Plot RA vs Dec (equirectangular)
```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('whitegrid')
plt.figure(figsize=(12,5))
sc = plt.scatter(df['ra'], df['dec'], c=df['parallax'], cmap='plasma', s=60, edgecolors='white', linewidths=0.4)
plt.xlabel('RA [deg]')
plt.ylabel('Dec [deg]')
plt.title('Gaia DR3: 100 Closest Stars (by parallax)')
plt.colorbar(sc, label='Parallax [mas]')
plt.savefig('/home/hermes/gaia_dr3_ra_dec.png', dpi=180, bbox_inches='tight')
plt.close()
```

## 6. Galactic XY projection (Sun at origin)
```python
import numpy as np
l_rad = np.radians(df['l'].values)
b_rad = np.radians(df['b'].values)
xgal = np.cos(b_rad) * np.cos(l_rad)
ygal = np.cos(b_rad) * np.sin(l_rad)
plt.figure(figsize=(8,7))
sc2 = plt.scatter(xgal, ygal, c=df['parallax'], cmap='plasma', s=70, edgecolors='white', linewidths=0.5)
plt.scatter(0,0,c='gold',s=300,marker='o',edgecolors='orange')
plt.annotate('Sun', xy=(0,0), xytext=(0.07,0.07), fontsize=12, color='darkorange', fontweight='bold', arrowprops=dict(arrowstyle='->', color='darkorange'))
plt.xlabel('xgal = cos(b) cos(l)')
plt.ylabel('ygal = cos(b) sin(l)')
plt.axis('equal')
plt.xlim(-1.1,1.1); plt.ylim(-1.1,1.1)
plt.colorbar(sc2, label='Parallax [mas]')
plt.title('Galactic XY Projection')
plt.savefig('/home/hermes/gaia_dr3_xy.png', dpi=180, bbox_inches='tight')
plt.close()
```

# Pitfalls & Tips
- **Endpoint matters**: The ESA TAP endpoint (`gea.esac.esa.int`) rejected `TOP`/`LIMIT` and gave connection errors. The AIP endpoint works reliably.
- **Query syntax**: Use `TOP N` rather than `LIMIT N` for this service.
- **Positive parallax filter**: Excludes ill‑determined distances.
- **Large queries**: Keep `TOP` modest (e.g., 100) to avoid timeout.
- **Installation**: `pyvo` may need `--break-system-packages` in this environment.
- **File paths**: The skill writes files to `/home/hermes/` – adjust if a different directory is preferred.

# Verification
After running, you should have:
- `/home/hermes/gaia_dr3_closest100.parquet`
- `/home/hermes/gaia_dr3_closest100_preview.csv`
- `/home/hermes/gaia_dr3_ra_dec.png`
- `/home/hermes/gaia_dr3_xy.png`
All plots show the Sun at the centre of the Galactic XY view and colour‑code stars by parallax.
---
