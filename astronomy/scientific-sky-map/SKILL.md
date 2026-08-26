---
name: scientific-sky-map
title: Scientific Sky Maps — Projection, Rendering, and Plotting
description: >-
  Generate all-sky and sky-region maps with custom physics models, celestial
  coordinate transformations, and projection rendering. Covers Mollweide,
  Aitoff, orthographic, hammer, and equirectangular projections with the
  reliable inverse-project + bilinear interpolation + imshow approach.
author: Hermes Agent
date: 2026-04-30
tags: [matplotlib, astronomy, sky-map, projection, physics-visualization, celestial-coordinates]
---

# Scientific Sky Map

Generate all-sky or sky-region maps with custom spatial models, coordinate
transformations, and projection rendering.

## When to Use

User asks to create a sky map / all-sky visualization for any astronomical
messenger or dataset — e.g. neutrino sky maps, gamma-ray all-sky maps
(Fermi-LAT style), X-ray sky surveys, radio continuum maps, cosmic microwave
background maps, or any celestial coordinate visualization with a physics-based
spatial model.

---

## 1. Grid in Native Coordinates

Choose the coordinate system appropriate to the physics:

- **Galactic coordinates (l, b)** — Milky Way studies, Galactic Center,
  diffuse plane emission
- **Equatorial (RA, Dec)** — extragalactic surveys, specific source catalogs
- **Ecliptic** — solar system or zodiacal science

Set resolution: `nx ≈ 800–1000`, `ny ≈ 400–500` for publication quality.

```python
nx, ny = 800, 400
l = np.linspace(-180, 180, nx) * np.pi / 180
b = np.linspace(-90, 90, ny) * np.pi / 180
L, B = np.meshgrid(l, b)
l_deg = np.degrees(L)
b_deg = np.degrees(B)
```

---

## 2. Coordinate Transformations

Common J2000 equatorial ↔ galactic rotation matrix (ICRS to Galactic):

```python
x_eq = cos(Dec)*cos(RA); y_eq = cos(Dec)*sin(RA); z_eq = sin(Dec)
x_gal = -0.05485948*x_eq - 0.87343709*y_eq - 0.48383502*z_eq
y_gal =  0.49410943*x_eq - 0.44482963*y_eq + 0.74698228*z_eq
z_gal = -0.86766615*x_eq - 0.19807637*y_eq + 0.45598378*z_eq
l = degrees(atan2(y_gal, x_gal)) % 360.0
b = degrees(asin(clamp(z_gal, -1, 1)))
```

---

## 3. Projection — Inverse-Project + Bilinear Interpolation + imshow

### Core Problem
Naive `pcolormesh` on projected (X, Y) coordinates creates tiny distorted cells
at high latitudes → jagged artifacts. matplotlib's `MollweideAxes` has limited
API (no `set_lonrecenter`, `celestial=True`, `spherical` kwargs).

### Step 1 — Compute data on regular lon/lat grid

```python
nx, ny = 600, 300
l = np.linspace(-180, 180, nx)
b = np.linspace(-90, 90, ny)
L, B = np.meshgrid(l, b)
data = ...  # shape (ny, nx)
```

### Step 2 — Define projection functions

```python
def mollweide(lon_deg, lat_deg):
    lon = np.radians(lon_deg)
    lat = np.radians(lat_deg)
    nu = np.arcsin(np.clip(np.sin(lat), -1, 1))
    for _ in range(10):
        nu = nu - (2*nu - np.sin(2*nu) - np.pi*np.sin(lat)) / (2 - 2*np.cos(2*nu) + 1e-12)
    x = (2.0 / np.pi) * np.cos(nu) * lon
    y = np.sin(nu)
    return x, y

def mollweide_inverse(x, y):
    nu = np.arcsin(np.clip(y, -1, 1))
    sin_lat = (2*nu - np.sin(2*nu)) / np.pi
    lat = np.degrees(np.arcsin(np.clip(sin_lat, -1, 1)))
    cos_nu = np.sqrt(1 - y**2 + 1e-12)
    lon = np.degrees((np.pi / 2) * x / cos_nu)
    lon = (lon + 180) % 360 - 180
    return lon, lat
```

### Step 3 — Create output grid and inverse-project

```python
im_w, im_h = 1600, 800
xlim, ylim = (-2.1, 2.1), (-1.1, 1.1)
ImX, ImY = np.meshgrid(np.linspace(*xlim, im_w), np.linspace(*ylim, im_h))
Lon, Lat = mollweide_inverse(ImX, ImY)
mask = (ImX**2 / 4.0 + ImY**2) <= 1.0
```

### Step 4 — Bilinear interpolation

```python
lon_1d = L[0, :]; lat_1d = B[:, 0]
lon_idx = np.clip(np.searchsorted(lon_1d, Lon), 0, nx - 2)
lat_idx = np.clip(np.searchsorted(lat_1d, Lat), 0, ny - 2)
l0, l1 = lon_1d[lon_idx], lon_1d[lon_idx + 1]
b0, b1 = lat_1d[lat_idx], lat_1d[lat_idx + 1]
f_interp = bilinear_interpolate(data, l0, l1, b0, b1, Lon, Lat, mask)
```

### Step 5 — Plot with imshow

```python
fig, ax = plt.subplots(figsize=(16, 8))
im = ax.imshow(f_interp, extent=[*xlim, *ylim],
               cmap=cmap, aspect='equal', interpolation='bilinear',
               origin='lower')
```

### Step 6 — Draw grid lines

```python
for l_val in np.arange(-150, 180, 30):
    x, y = mollweide(np.full(200, l_val), np.linspace(-90, 90, 200))
    ax.plot(x, y, 'w-', alpha=0.2, linewidth=0.8)
for b_val in [-60, -30, 0, 30, 60]:
    x, y = mollweide(np.linspace(-180, 180, 200), np.full(200, b_val))
    ax.plot(x, y, 'w-', alpha=0.2, linewidth=0.8)
```

### Other Projections

#### Aitoff

```python
def aitoff(lon_deg, lat_deg):
    lon = np.radians(lon_deg); lat = np.radians(lat_deg)
    nu = np.arcsin(np.sin(lat) / 2)
    x = 2*np.sqrt(2)*np.cos(nu)*np.sin(lon/2)
    y = np.sqrt(2)*np.sin(nu)
    return x, y
```

Mask: `x²/8 + y²/2 <= 1`

#### Orthographic

```python
def ortho(lon_deg, lat_deg):
    lon = np.radians(lon_deg); lat = np.radians(lat_deg)
    return np.cos(lat)*np.sin(lon), np.sin(lat)
```

Mask: `x² + y² <= 1`

#### Hammer / Aitoff (built-in matplotlib)

```python
ax = fig.add_subplot(111, projection='hammer')
```

#### Equirectangular (sky region)

Direct: `x = RA, y = Dec`

### Mask boundaries reference

| Projection   | Mask condition        |
|------------- |-----------------------|
| Mollweide    | `x²/4 + y² <= 1`     |
| Aitoff       | `x²/8 + y²/2 <= 1`   |
| Orthographic | `x² + y² <= 1`       |

### Common Pitfalls

1. **`ax.pcolormesh(X, Y, data)`** — creates distorted cells at high latitudes.
   Use inverse-project + bilinear interp + `imshow` instead.
2. **`ax.set_lonrecenter(0)`** — doesn't exist on `MollweideAxes`.
3. **`ax.add_subplot(projection='mollweide', celestial=True)`** — `celestial`
   is not valid; use manual projection.
4. **Tick label count** — MollweideAxes has 11 default x-ticks;
   `set_xticklabels` with wrong count raises `ValueError`.
5. **Performance** — bilinear interp is O(im_w × im_h); for im_w > 2000,
   reduce resolution or use `scipy.interpolate.RegularGridInterpolator`.

---

## 4. Physics Model Components

Typical components:

- **Diffuse emission**: Gaussian in latitude (σ ≈ 5–15°), azimuthal modulation
- **Point sources**: Gaussian profiles with log-normal flux
- **Compact sources**: Galactic Center, named objects
- **Background**: Uniform extragalactic or isotropic floor

```python
# Diffuse: Gaussian latitude + azimuthal modulation
lat_profile = exp(-0.5 * (b_deg / sigma_lat**2))
# Point sources
for src in sources:
    dlon = (l_deg - src.l + 180) % 360 - 180  # wrap
    dlat = b_deg - src.b
    source_flux += src.flux * exp(-0.5*(dlon**2 + dlat**2) / (2*src.sigma**2))
```

---

## 5. Colormap — Fermi-LAT Style

```python
colors = [
    (0.05, 0.00, 0.10), (0.20, 0.00, 0.25),
    (0.50, 0.10, 0.35), (0.80, 0.15, 0.20),
    (1.00, 0.40, 0.10), (1.00, 0.80, 0.20),
    (1.00, 1.00, 0.90), (1.00, 1.00, 1.00),
]
cmap = LinearSegmentedColormap.from_list('sky_map', colors, N=256)
```

---

## 6. Rendering

```python
fig, ax = plt.subplots(figsize=(16, 8))
ax.imshow(f_interp, extent=[*xlim, *ylim],
          cmap=cmap, aspect='equal', interpolation='bilinear',
          origin='lower',
          vmin=np.percentile(f_interp, 1),
          vmax=np.percentile(f_interp, 99.5))
ax.set_facecolor('#0D1117')
```

**Styling defaults:**
- Dark background: `facecolor='#0D1117'` or `'#050510'`
- White text and ticks
- Colorbar with white labels
- Labels in native coordinate system (l/b or RA/Dec)
- Percentile clipping (1st–99th) for dynamic range

### Upload and Deliver

```bash
python3 ~/.hermes/scripts/s3_media_upload.py /tmp/sky_map.png
```

---

## Pitfalls

- **Mollweide iteration**: Newton-Raphson for `2ν - sin(2ν) = π sin(b)`
  requires 5–10 iterations; watch for division by zero near `cos(2ν) ≈ 0.5`.
- **Longitude wrapping**: Always wrap Δl to [-180°, 180°].
- **Projections with pcolormesh**: Use `shading='auto'` or manual projection.
- **Colorbar limits**: Use percentile clipping to avoid bright sources washing
  out faint signal.
- **Coordinate confusion**: Be explicit about degrees vs radians at each step.
  Projection iteration works in radians; model Gaussians typically use degrees.
