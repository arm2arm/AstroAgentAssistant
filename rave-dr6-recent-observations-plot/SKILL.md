---
name: rave-dr6-recent-observations-plot
title: Plot the newest 100 RAVE DR6 observations (RA vs Dec)
author: Hermes Assistant
version: 1.0
description: Retrieve the most recent 100 entries from the RAVE DR6 `dr6_obsdata` table and generate a simple RA‑Dec scatter plot. Handles missing Python dependencies, installs them if necessary, and falls back to astropy for galactic coordinates if needed.
---

# Overview
This skill demonstrates how to query the RAVE DR6 TAP service for the latest 100 observations, then produce a scatter plot of RA vs Dec (and optionally Galactic X/Y).

# Prerequisites
```bash
# Install required Python packages (run once)
pip install --quiet pyvo pandas matplotlib seaborn astropy --break-system-packages
```

# Steps
1. **Create a Python script** (`rave_recent_plot.py`) with the following content:
```python
import warnings, numpy as np, pandas as pd, matplotlib
warnings.filterwarnings('ignore')
matplotlib.use('Agg')
import matplotlib.pyplot as plt, seaborn as sns, pyvo

# Connect to the RAVE TAP service
service = pyvo.dal.TAPService('https://www.rave-survey.org/tap/')

# Query the newest 100 observations (ordered by obsdate descending)
query = '''
SELECT TOP 100 ra_input, dec_input, obsdate
FROM ravedr6.dr6_obsdata
ORDER BY obsdate DESC
'''
result = service.run_sync(query)
# Convert to pandas DataFrame
df = result.to_table().to_pandas()

# Plot RA vs Dec
plt.figure(figsize=(8,6))
sns = sns.scatterplot(data=df, x='ra_input', y='dec_input', hue='obsdate', palette='viridis', edgecolor='white', s=80)
plt.title('Newest 100 RAVE DR6 Observations (RA vs Dec)')
plt.xlabel('RA (deg)')
plt.ylabel('Dec (deg)')
plt.legend(title='Obsdate', loc='best')
plt.grid(True, ls='--', alpha=0.5)
plt.tight_layout()
plt.savefig('rave_newest_ra_dec.png', dpi=180)
print('Saved plot to rave_newest_ra_dec.png')
```
2. **Run the script**:
```bash
python3 rave_recent_plot.py
```
   The PNG file `rave_newest_ra_dec.png` will be created in the current directory.

3. *(Optional)* **Plot Galactic X/Y** if you need a galactic projection:
   - Add the following after step 1 (requires `astropy`):
```python
from astropy.coordinates import SkyCoord
import astropy.units as u
# Convert RA/Dec to Galactic coordinates
coords = SkyCoord(ra=df['ra_input'].values*u.deg, dec=df['dec_input'].values*u.deg, frame='icrs')
gal = coords.galactic
l = gal.l.rad
b = gal.b.rad
# Compute planar projection
x = np.cos(b) * np.cos(l)
y = np.cos(b) * np.sin(l)
# Plot
plt.figure(figsize=(8,8))
sns = sns.scatterplot(x=x, y=y, hue=df['obsdate'], palette='plasma', edgecolor='white', s=80)
plt.scatter(0,0,c='gold',s=300,marker='o',edgecolor='orange',linewidth=2,zorder=10)
plt.title('Newest 100 RAVE DR6 Observations (Galactic X/Y)')
plt.xlabel('x = cos(b) cos(l)')
plt.ylabel('y = cos(b) sin(l)')
plt.axis('equal')
plt.legend(title='Obsdate', loc='best')
plt.grid(True, ls='--', alpha=0.5)
plt.tight_layout()
plt.savefig('rave_newest_xy_gal.png', dpi=180)
print('Saved galactic plot to rave_newest_xy_gal.png')
```

# Pitfalls & Tips
- The `dr6_obsdata` table does **not** contain galactic longitude/latitude; you must compute them from RA/Dec (shown in the optional block).
- All 100 rows currently share the same `obsdate = 20130404`, so the hue will appear uniform. If you query a broader date range, colour coding becomes useful.
- If `pyvo` is missing, the install command above will add it; the `--break-system-packages` flag is required in the sandbox environment.
- Use `service.run_sync()` (synchronous) – avoid `submit_job()` which leads to errors on this TAP endpoint.
- Ensure the script runs in a directory where you have write permission for the PNG output.

# Verification
After running, open `rave_newest_ra_dec.png`. It should display a scatter of points across the RA‑Dec ranges (~146°‑225° RA, –42° to –47° Dec) corresponding to the latest RAVE observations.
```
