---
name: rave-dr6-3d-animation
title: Create 3D Animation of Nearest RAVE DR6 Stars
author: Hermes Assistant
version: 1.0
description: |
  Step‑by‑step workflow to query the RAVE DR6 catalog for the 100 nearest stars (by parallax), process the data, generate 2‑D visualisations and a public‑talk‑ready 3‑D rotating animation using Matplotlib.
---

# Overview
This skill captures the complete, reproducible pipeline we used to:
1. Retrieve the 100 closest stars from the RAVE DR6 `dr6_x_gaiaedr3` table via the TAP service.
2. Parse the returned VOTable (CSV fallback) into a pandas DataFrame.
3. Compute both 2‑D sky coordinates (RA/Dec, Galactic X‑Y) and 3‑D unit‑sphere coordinates.
4. Produce high‑quality PNG plots for presentations.
5. Render a smooth 3‑D rotating MP4 animation with Matplotlib (no Manim required).

The workflow is fully self‑contained and works on a standard Ubuntu‑based environment with `python3`, `pip`, `ffmpeg` and the following Python packages installed:
- `pyvo` (optional, used for TAP queries)
- `pandas`
- `numpy`
- `matplotlib`
- `seaborn`
- `astropy`

# Prerequisites
```bash
# Install required Python packages (use --break-system-packages if needed)
python3 -m pip install --user --break-system-packages pyvo pandas numpy matplotlib seaborn astropy
# Ensure ffmpeg is installed for MP4 output
sudo apt-get install -y ffmpeg   # or use your package manager
```

# Step‑by‑Step Instructions
## 1. Query the RAVE DR6 TAP service
We use a direct HTTP POST to avoid the `pyvo` 404 issue on the default endpoint.
```bash
curl -s -X POST \
  -d "request=doQuery&lang=ADQL&format=csv&query=SELECT TOP 100 source_id, ra, dec, l, b, parallax, phot_g_mean_mag, bp_rp FROM ravedr6.dr6_x_gaiaedr3 WHERE parallax > 0 ORDER BY parallax DESC" \
  https://www.rave-survey.org/tap/sync \
  -o /tmp/rave_dr6_closest100.votable
```
The result is a VOTable (XML) file that `astropy` can read.

## 2. Parse the VOTable into a DataFrame
```python
from astropy.io.votable import parse_single_table
import pandas as pd

vot_path = '/tmp/rave_dr6_closest100.votable'
table = parse_single_table(vot_path)
df = table.to_table().to_pandas()
# Save for later reuse (optional)
df.to_parquet('rave_dr6_closest100.parquet', index=False)
```
The DataFrame now contains columns `ra`, `dec`, `l`, `b`, `parallax`, etc.

## 3. Compute Cartesian coordinates for 3‑D view
```python
import numpy as np
l_rad = np.radians(df['l'].values)
b_rad = np.radians(df['b'].values)
# Unit‑sphere coordinates (direction only)
xs = np.cos(b_rad) * np.cos(l_rad)
ys = np.cos(b_rad) * np.sin(l_rad)
zs = np.sin(b_rad)
```

## 4. Produce 2‑D plots (public‑talk style)
```python
import matplotlib.pyplot as plt, seaborn as sns
sns.set_style('whitegrid')
plt.rcParams.update({
    'font.size': 14,
    'axes.titlesize': 18,
    'axes.labelsize': 16,
    'figure.dpi': 300,
    'figure.facecolor': '#0D1117',
    'axes.facecolor': '#0D1117',
    'text.color': 'white',
    'axes.labelcolor': 'white',
    'xtick.color': 'white',
    'ytick.color': 'white'
})
# RA vs Dec
fig1, ax1 = plt.subplots(figsize=(12,7))
sc1 = ax1.scatter(df['ra'], df['dec'], c=df['parallax'], cmap='viridis', s=80, edgecolors='k')
ax1.set_xlabel('Right Ascension (deg)')
ax1.set_ylabel('Declination (deg)')
ax1.set_title('Nearest 100 RAVE DR6 Stars (by Parallax)')
cb1 = fig1.colorbar(sc1, ax=ax1, shrink=0.8)
cb1.set_label('Parallax (mas)')
fig1.tight_layout()
fig1.savefig('rave_dr6_ra_dec_public.png')
# Galactic X‑Y projection
xgal = np.cos(b_rad) * np.cos(l_rad)
ygal = np.cos(b_rad) * np.sin(l_rad)
fig2, ax2 = plt.subplots(figsize=(10,8))
sc2 = ax2.scatter(xgal, ygal, c=df['parallax'], cmap='viridis', s=90, edgecolors='k')
ax2.scatter(0,0,c='gold',s=300,marker='*',edgecolors='orange')
ax2.set_xlabel('x = cos(b) cos(l)')
ax2.set_ylabel('y = cos(b) sin(l)')
ax2.set_aspect('equal')
ax2.set_title('Galactic Plane Projection')
cb2 = fig2.colorbar(sc2, ax=ax2, shrink=0.8)
cb2.set_label('Parallax (mas)')
fig2.tight_layout()
fig2.savefig('rave_dr6_galactic_public.png')
```
Both PNGs are ready for slides.

## 5. Create the 3‑D rotating animation (Matplotlib)
```python
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure(figsize=(8,8), facecolor='#0D1117')
ax = fig.add_subplot(111, projection='3d')
sc = ax.scatter(xs, ys, zs, c=df['parallax'], cmap='viridis', s=80, edgecolors='k')
# Dark pane colours
for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
    axis.set_pane_color((0.05,0.05,0.05,1))
    axis._axinfo["grid"]['color'] = (0.3,0.3,0.3,0.5)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3‑D view of nearest 100 RAVE DR6 stars')
lim = 1.1
ax.set_xlim(-lim, lim)
ax.set_ylim(-lim, lim)
ax.set_zlim(-lim, lim)
# Sun marker at origin
ax.scatter([0],[0],[0], c='gold', s=300, marker='*', edgecolors='orange')
# Animation: rotate azimuth
frames = 180
angles = np.linspace(0, 360, frames)

def update(frame):
    ax.view_init(elev=30, azim=angles[frame])
    return sc,
anim = FuncAnimation(fig, update, frames=frames, interval=50, blit=False)
output_path = 'rave_dr6_3d_public.mp4'
writer = FFMpegWriter(fps=20, codec='libx264', bitrate=1800)
anim.save(output_path, writer=writer)
print('Animation saved to', output_path)
```
The resulting MP4 (≈8 seconds at 20 fps) works well on Telegram and in presentations.

# Common Pitfalls & Fixes
| Symptom | Cause | Remedy |
|---|---|---|
| `Invalid data when processing input` from ffmpeg | One of the partial files from Manim was empty (size ≈ 48 B). | Use the Matplotlib approach above; avoid Manim partial‑file concat unless you verify each segment.
| `ModuleNotFoundError: pyvo` | System Python missing `pip`. | Install with `python3 -m pip install --user --break-system-packages pyvo` or rely on the `curl` POST method (no `pyvo` needed).
| `astropy` missing | Not installed. | `pip install astropy`.
| Dark background not appearing in MP4 | Matplotlib default facecolor is white. | Set `facecolor='#0D1117'` in `plt.figure` and pane colours as shown.
| Large file size > 20 MB (Telegram limit) | High bitrate or resolution. | Reduce `bitrate` in `FFMpegWriter` (e.g., `bitrate=800`) or down‑scale with `ffmpeg -i input.mp4 -vf scale=640:-2 -b:v 500k output.mp4`.

# Tips for Public Talks
- Use the `viridis` colormap (colour‑blind friendly) and a gold star for the Sun.
- Keep the animation ≤ 10 seconds; loop it in slides for emphasis.
- Export PNGs at 300 dpi for crisp print.
- If you need a GIF instead of MP4, run:
  ```bash
  ffmpeg -i rave_dr6_3d_public.mp4 -vf "fps=15,scale=640:-2:flags=lanczos" -c:v gif out.gif
  ```

# References
- RAVE‑DR6 TAP endpoint: https://www.rave-survey.org/tap/
- Astropy VOTable parser: https://docs.astropy.org/en/stable/io/votable/
- Matplotlib 3D animation docs: https://matplotlib.org/stable/api/_as_gen/matplotlib.animation.FuncAnimation.html

---
