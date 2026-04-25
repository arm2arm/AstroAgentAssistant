---
name: rave-dr6-3d-public-animation
description: Generate a public‑talk‑ready 3‑D animation of the 100 nearest RAVE DR6 stars using matplotlib.
category: astronomy
---

# Purpose
Create a smooth, dark‑background MP4 animation that visualises the spatial distribution of the 100 nearest stars from the RAVE DR6 catalog, with the Sun at the centre. The animation should be suitable for presentations, social media, or outreach.

# Prerequisites
- **matplotlib** with `ffmpeg` writer (`pip install matplotlib ffmpeg`).
- **pandas**, **numpy** for data handling.
- **astroquery** for TAP access (`pip install astroquery`).
- Network access to the RAVE DR6 TAP service (https://rave-survey.org/tap).

# WARNING: Do NOT use Manim for 3D star animations
Manim v0.20.1 is **impractical** for this use case:
- 3D rendering with `Dot3D` is extremely slow (~5+ minutes for 30s of output).
- APIs are broken: `set_background_color()` removed, `lerp_color()` removed, `Vector()` no longer works as a coordinate constructor.
- **Use matplotlib 3D + FuncAnimation instead** — same visual result, seconds vs minutes.

# Workflow

## 1. Query RAVE DR6 (via Vizier VOTable — most reliable)
```python
import pandas as pd

# Most reliable Vizier endpoint for RAVE DR6 nearest stars
url = "https://vizier.cds.unistra.fr/viz-bin/VOTable/-2/2/-1?_outAll=1&-c=185.34603190%2B33.19542000&-c.eq=J2000&-c.u=arcsec&-c.r=500&-c.geom=enc"
# Better: query the whole catalogue and filter by parallax
```

Alternative: query the RAVE DR6 × Gaia DR2 cross-match from Vizier:
```python
from astroquery.vizier import Vizier

vizier = Vizier(columns=["*", "RADECODE"])
result = vizier.get_catalogs("I/358/gaiadr3")[0]  # or use TAP endpoint
```

Simpler approach — query TAP directly:
```python
from astroquery.utils.tap.core import TapPlus

tap = TapPlus(url="https://rave-survey.org/tap")
query = """
SELECT source_id, ra, dec, l, b, parallax, pmra, pmdec,
       radial_velocity, phot_g_mean_mag, bp_rp
FROM gaiadr2.x gaiadr2 dr6_x_gaiadr2
WHERE parallax IS NOT NULL AND parallax > 0
ORDER BY parallax DESC
LIMIT 100
"""
# Note: RAVE TAP JOINs may return 500 errors; use cross-match table directly
result = tap.launch_job(query).get_results()
df = result.to_pandas()
```

## 2. Convert to Cartesian coordinates (parsecs)
```python
import numpy as np

# distance = 1/parallax (mas to pc)
df['distance'] = 1000.0 / df['parallax']

# Convert spherical (l, b) to Cartesian (x, y, z) in parsecs
l_rad = np.deg2rad(df['l'].values)
b_rad = np.deg2rad(df['b'].values)
d = df['distance'].values

x = d * np.cos(b_rad) * np.cos(l_rad)  # cos(b)*cos(l)
y = d * np.cos(b_rad) * np.sin(l_rad)  # cos(b)*sin(l)
z = d * np.sin(b_rad)                  # sin(b)
```

## 3. Create the matplotlib 3D animation
```python
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.colors as mcolors
import matplotlib.cm as cm

rv = df['radial_velocity'].values
rv_min, rv_max = rv.min(), rv.max()
norm = mcolors.Normalize(vmin=rv_min, vmax=rv_max)
colors = [cm.coolwarm(norm(r)) for r in rv]

fig = plt.figure(figsize=(10, 10), dpi=100)
fig.patch.set_facecolor('#0D1117')
ax = fig.add_subplot(111, projection='3d')
ax.set_facecolor('#0D1117')

# Plot stars
scatter = ax.scatter(x, y, z, c=colors, s=60, edgecolors='white',
                     linewidths=0.3, alpha=0.9)

# Sun at origin
ax.scatter([0], [0], [0], c='gold', s=200, marker='*',
           edgecolors='orange', linewidths=1.5, label='Sun')

# Labels and styling
ax.set_xlabel('cos(b)·cos(l)  [pc]', color='white', fontsize=10)
ax.set_ylabel('cos(b)·sin(l)  [pc]', color='white', fontsize=10)
ax.set_zlabel('sin(b)  [pc]', color='white', fontsize=10)
ax.set_title('100 Nearest RAVE DR6 Stars — 3D View',
             color='white', fontsize=14, pad=15)
ax.tick_params(colors='white', labelsize=9)

# Hide pane fills for clean look
for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
    axis.pane.fill = False
    axis.pane.set_edgecolor('gray')

# Colourbar
cbar = fig.colorbar(scatter, ax=ax, shrink=0.6, pad=0.1)
cbar.set_label('Radial Velocity [km/s]', color='white', fontsize=10)
cbar.ax.tick_params(colors='white', labelsize=8)

# Animation: smooth rotation
def animate(frame):
    ax.view_init(elev=25, azim=frame)
    return []

ani = FuncAnimation(fig, animate, frames=360, interval=30,
                    blit=False, repeat=True)
ani.save('rave_dr6_closest100_3d.mp4', writer='ffmpeg', fps=30)
plt.close()
```

## 4. Render parameters
- **frames=360, interval=30** → 12s total, one full rotation
- **dpi=100, figsize=(10,10)** → 1000×1000 output, good quality-to-size ratio
- Adjust `interval` for faster/slower rotation
- Adjust `elev` for initial viewing angle (0 = equatorial, 90 = pole-on)

# Verification
- Open the MP4; you should see a dark canvas with a golden star at the centre (the Sun) and a rotating 3D cloud of coloured points.
- Stars are coloured by radial velocity: blue (approaching, negative RV), white (~0 km/s), red (receding, positive RV).
- The animation runs ~12s, completing a full 360° rotation.
- File size typically 2–4 MB for 1000×1000 at 30fps.

# Pitfalls & Tips
- **TAP JOINs fail with 500 errors** on the RAVE server — use the cross-match table (`dr6_x_gaiadr2`) directly, not JOIN queries.
- **Parallax → distance** — parallax in milliarcseconds (mas); divide by 1000 before inversion for parsecs.
- **matplotlib 3D is the recommended approach** — it's fast (renders in seconds vs minutes for Manim), reliable, and produces identical visuals.
- **ffmpeg must be installed** for matplotlib MP4 output (`sudo apt install ffmpeg` or check system availability).
- **Colour mapping** — `cm.coolwarm` gives a natural blue→white→red gradient perfect for radial velocities.
- **Data caching** — save the query result as Parquet (`df.to_parquet('rave_dr6_closest100.parquet')`) to avoid re-querying.
- **Axis labels** — use Galactic coordinates (cos(b)·cos(l), etc.) for the spatial view; these align with the standard Galactic plane orientation.
- **Dark background** — set both `fig.patch.set_facecolor('#0D1117')` and `ax.set_facecolor('#0D1117')`.

---
*Updated by Hermes agent. Switched from Manim to matplotlib due to Manim v0.20.1 API incompatibilities and performance issues.*
