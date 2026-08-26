---
name: arepo-simulations
title: Arepo Cosmological Simulations — HDF5 Analysis, Projections, and Clustering
description: >-
  Complete guide to working with Arepo simulation HDF5 files: structure inspection,
  unit conversion, radial profiles, slice projections, and dimensionality reduction
  (UMAP/t-SNE) for clustering analysis.
author: Hermes Agent
date: 2026-05-06
tags: [arepo, simulation, hdf5, cosmology, particle-analysis, clustering]
---

# Arepo Cosmological Simulations

This umbrella skill covers the full workflow for Arepo simulation data:
access, inspection, analysis, visualization, and clustering.

---

## 1. HDF5 File Structure

### Standard Arepo Snapshot Format

```
Header/
  ATTRS:
    BoxSize: float (Mpc/h)
    MassTable: array(7) — particle masses per type (0 if not present)
    NumPart_ThisFile: array(7, int32) — particles in THIS file per type
    NumPart_Total: array(7, uint32) — total particles per type (all files)
    Redshift: float
    Time: float (cosmic time)
PartType0/  (gas/hydro)
  PartType0/Coordinates: (N, 3) float64  — Mpc/h
  PartType0/Density: (N,) float32         — g/cm^3
  PartType0/Hsml: (N,) float32           — smoothing length (cm)
  PartType0/InternalEnergy: (N,) float32  — erg/g
  PartType0/ParticleIDs: (N,) uint32
  PartType0/Velocities: (N, 3) float32    — cm/s
PartType1-5: Dark matter, stars, wind, BHs, outflows (type-dependent)
```

### Key Units
| Column | Unit | Convert To | Formula |
|--------|------|------------|---------|
| Coordinates | Mpc/h | kpc/h | `× 1000` |
| Coordinates | Mpc/h | pc/h | `× 1e6` |
| Velocities | cm/s | km/s | `× 1e-5` |
| Hsml | cm | pc | `÷ 3.086e18` |
| Hsml | cm | kpc | `÷ 3.086e21` |
| InternalEnergy | erg/g | Temperature (K) | `T = (2/3) × u × μ × m_p / k_B` |
| Density | g/cm³ | log₁₀ | `np.log10(density)` |

### Temperature from Internal Energy
```python
mu = 0.6        # mean molecular weight (ionized H+He)
m_p = 1.6726219e-24   # proton mass (g)
k_B = 1.380649e-16    # Boltzmann constant (erg/K)
T = (2.0/3.0) * internal_energy * mu * m_p / k_B
```

---

## 2. Data Access

## 2. Data Access

### S3 Access (pmviewer2023 bucket) — Preferred: `urllib.request`
```python
import urllib.request, os

bucket = "https://s3.data.aip.de:9000/pmviewer2023"
key    = "data/HiRes_H_1_t_0_snapshot_307.hdf5"   # naming: HiRes_H_1_t_0_snapshot_NNN.hdf5
local  = "/home/hermes/snapshot_307.hdf5"

print(f"Downloading {key} ...")
urllib.request.urlretrieve(f"{bucket}/{key}", local)
size_mb = os.path.getsize(local) / 1024**2
print(f"Saved: {size_mb:.1f} MB  {local}")
```
No credentials needed — works anonymously. **No `s3fs` dependency required.**

### S3 Access via s3fs (alternative, needs venv packages)
```python
import s3fs
fs = s3fs.S3FileSystem(
    anon=True,
    client_kwargs={"endpoint_url": "https://s3.data.aip.de:9000"}
)
```

### Generic S3 Listing (XML API, no auth)
```python
import urllib.request, xml.etree.ElementTree as ET, re

url = f"https://s3.data.aip.de:9000/pmviewer2023/?list-type=2"
req = urllib.request.Request(url, method="GET")
with urllib.request.urlopen(req, timeout=10) as r:
    xml = r.read().decode()

root = ET.fromstring(xml)
ns = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
for obj in root.findall("s3:Contents", ns):
    key  = obj.find("s3:Key", ns).text
    size = int(obj.find("s3:Size", ns).text)
    print(f"  {size/1024/1024:6.1f} MB  {key}")
```

### Known AIP S3 Buckets
| Bucket | Contents |
|--------|----------|
| `shboost2024/` | Photometry catalog (Parquet, ~218M rows) |
| `pmviewer2023/` | Arepo simulation snapshots — see **two series below** |

### ⚠️ Two snapshot series in pmviewer2023 — NOT the same!
| Series | Key pattern | Snap range | Components | Size |
|--------|------------|------------|------------|------|
| HiRes zoom-in | `data/HiRes_H_1_t_0_snapshot_NNN.hdf5` | 118–307+ | **Gas only** (PartType0, ~787k) | ~41 MB |
| Full-cosmo | `data/snap_NNN.hdf5` | **400–500 only** | DM+gas+stars+BHs (all PartTypes) | ~155 MB |

> **snap_118 does not exist in full-cosmo.** Use `HiRes_H_1_t_0_snapshot_118.hdf5` for gas-only or `snap_400` as the earliest multi-component snapshot.
> For DM+gas+stars 2×3 projections, use the **`simulation-visualization`** skill — it has the full pipeline, PCA alignment, and animation scripts.
| `scr4agent/` | Media uploads only (not data) |

### CRITICAL: S3 Endpoint
`https://s3.data.aip.de:9000` is reachable ✅. `https://s3.aip.de:9000` is NOT reachable ❌ (connection refused). **Always use `s3.data.aip.de:9000`** for ALL AIP S3 buckets.

### HDF5 Inspection (quick)
```python
import h5py
with h5py.File(path, 'r') as f:
    # Print full tree
    f.visititems(lambda name, obj: print(name))
    # Print group attrs and datasets
    for grp_name in f.keys():
        grp = f[grp_name]
        if isinstance(grp, h5py.Group):
            print(grp_name, "attrs:", dict(grp.attrs))
            for ds_name in grp.keys():
                ds = grp[ds_name]
                print(f"  {ds_name}: {ds.shape} {ds.dtype}")
```

**Alternative step-by-step inspection** (from simulation-data merge):
```python
import h5py

with h5py.File("snapshot.hdf5", "r") as f:
    def print_tree(name, obj):
        indent = '  ' * name.count('/')
        if isinstance(obj, h5py.Group):
            print(indent + name + '/')
        else:
            print(indent + name + ': shape=' + str(obj.shape) + ' dtype=' + str(obj.dtype))
    f.visititems(print_tree)

    hdr = dict(f['Header'].attrs)
    print("Particles:", hdr['NumPart_Total'])
    print("BoxSize:", hdr['BoxSize'])
    print("Redshift:", hdr['Redshift'])
```

### Generic Particle Data Extraction
```python
with h5py.File("snapshot.hdf5", "r") as f:
    coords = f['PartType0/Coordinates'][:]  # (N, 3) Mpc/h
    vel = f['PartType0/Velocities'][:]      # (N, 3) cm/s
    density = f['PartType0/Density'][:]     # (N,) g/cm³
    hsml = f['PartType0/Hsml'][:]           # (N,) cm
    ue = f['PartType0/InternalEnergy'][:]   # (N,) erg/g
```

---

## 1a. General Astrophysical Simulation Data (Gadget, FLASH, etc.)

The patterns above work for Arepo, Gadget, FLASH, and similar N-body/SPH codes. Key differences:

### Gadget-specific Notes
- Uses `PartType0` through `PartType5` just like Arepo
- HDF5 group naming convention: `PartType0` (gas), `PartType1` (dm), `PartType2` (stars), etc.
- Same unit system: coordinates in code units (often length in code units, velocities in code units/s)
- May use different file splitting (one file per particle type vs. all-in-one)

### FLASH-specific Notes
- FLASH uses different HDF5 grouping — check `visititems()` to map the structure
- May use different coordinate conventions (Cartesian, cylindrical, or spherical)
- Output files are organized by time step, not snapshot number

### Common HDF5 Inspection Pattern (universal)
```python
import h5py
with h5py.File(path, 'r') as f:
    def print_tree(name, obj):
        indent = '  ' * name.count('/')
        if isinstance(obj, h5py.Group):
            print(indent + name + '/')
        else:
            print(indent + name + ': shape=' + str(obj.shape) + ' dtype=' + str(obj.dtype))
    f.visititems(print_tree)
```

---

## 3. Installation Requirements

All packages must be installed in the **project venv** (NOT in execute_code sandbox):
```bash
/home/hermes/.hermes/hermes-agent/venv/bin/pip3 install h5py s3fs dask scikit-learn umap-learn matplotlib
```

Common missing packages:
- `h5py` — HDF5 file reading
- `s3fs` — S3 access
- `scikit-learn` — PCA, t-SNE
- `umap-learn` — UMAP dimensionality reduction

---

## 4. Analysis Patterns

### Radial Bar Analysis
```python
# Compute radial distance
r = np.sqrt(np.sum(coords_kpc**2, axis=1))
r_bins = np.logspace(np.log10(r.min()+0.01), np.log10(r.max()), 20)

# Bin statistics
for i in range(len(r_bins) - 1):
    mask = (r >= r_bins[i]) & (r < r_bins[i+1])
    if np.sum(mask) > 0:
        mean_density = np.mean(np.log10(density[mask]))
        mean_temp = np.mean(np.log10(T[mask]))
        mean_vel = np.mean(vel_mag[mask])
```

### 2D Slice Projections
```python
# XY, XZ, YZ projections
ax.scatter(coords_kpc[:, 0], coords_kpc[:, 1], c=np.log10(density), cmap='viridis', s=0.5)
ax.scatter(coords_kpc[:, 0], coords_kpc[:, 2], c=np.log10(T), cmap='hot_r', s=0.5)
ax.scatter(coords_kpc[:, 1], coords_kpc[:, 2], c=vel_mag, cmap='coolwarm', s=0.5)
```

### Dimensionality Reduction (UMAP/t-SNE)
```python
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import umap
from sklearn.manifold import TSNE

# Feature selection (pick relevant columns)
features = np.column_stack([
    np.log10(density),
    np.log10(T),
    vel_mag,
    np.log10(hsml_kpc + 1e-10),
    r,
    coords_kpc[:, 0], coords_kpc[:, 1], coords_kpc[:, 2]
])

# Normalize
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)

# UMAP
umap_result = umap.UMAP(n_neighbors=15, min_dist=0.1, metric='euclidean',
                         random_state=42, n_components=2).fit_transform(features_scaled)

# t-SNE
tsne_result = TSNE(n_components=2, perplexity=30, learning_rate='auto',
                   init='pca', random_state=42, n_iter=1000).fit_transform(features_scaled)
```

---

## 5. Clustering Analysis

### Identifying Gas Phases
After UMAP/t-SNE reduction, apply clustering:
1. **HDBSCAN** — density-based, finds arbitrary cluster shapes
2. **K-Means** — spherical clusters, need to pick k
3. **Gaussian Mixture Models** — probabilistic clustering

### Feature Selection for Clustering
- **Physics-focused**: density, temperature, entropy only
- **Kinematic**: velocity components, vorticity, shear
- **Spatial**: normalized radius, angular position
- **Mixed**: all features (use StandardScaler)

### Performance Tips
- Subsample to ~100K points before UMAP/t-SNE
- Use PCA (2 components) for quick visualization first
- t-SNE is slow — use `n_iter=500` for prototyping

---

## 5. PCA-Based Face-On / Edge-On Projection

PCA on particle positions finds the principal axes of the mass distribution. Projecting onto the top-2 PCs gives a **face-on** view; PC1×PC3 gives **edge-on**. This works for galaxies, halos, and any flattened structure.

### Full Workflow
```python
import h5py, numpy as np, matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from scipy.ndimage import gaussian_filter

# --- Load ---
f = h5py.File(path, 'r')

# Collect all particle positions + masses (for cosmological boxes)
# For zoom-in (HiRes): use PartType0/gas only
# For full box: weight by mass to reflect total matter distribution
all_coords, all_mass = [], []
for pt in ['PartType0','PartType1','PartType2','PartType3','PartType4']:
    try:
        c = f[f'{pt}/Coordinates'][:].astype(np.float64)
        m = f[f'{pt}/Masses'][:].astype(np.float64) if f'{pt}/Masses' in f else np.ones(len(c))
        all_coords.append(c)
        all_mass.append(m)
    except Exception:
        pass

coords_all = np.vstack(all_coords)
mass_all   = np.concatenate(all_mass)

# --- PCA (mass-weighted recommended) ---
weighted = coords_all * mass_all[:, None]
pca = PCA(n_components=3)
pca.fit(weighted - weighted.mean(axis=0))
rot = pca.transform(weighted - weighted.mean(axis=0))
x, y, z = rot[:, 0], rot[:, 1], rot[:, 2]
# Explained variance tells you the morphology:
#   PC1 ~48-50% → disk-like (flattened)
#   PC1 ~86%   → halo-like (nearly spherical)

# --- Density-weighted smoothed grid (SPH-like) ---
NX = NY = 600
SIGMA = 2.0   # pixels; mimic SPH smoothing kernel

def build_grid(xp, yp, weights, nx=NX, ny=NY, sigma=SIGMA):
    xmn, xmx = np.percentile(xp, [0.5, 99.5])
    ymn, ymx = np.percentile(yp, [0.5, 99.5])
    hist, xe, ye = np.histogram2d(xp, yp, bins=[nx, ny],
                                  range=[[xmn, xmx], [ymn, ymx]],
                                  weights=weights)
    hist = gaussian_filter(hist.T, sigma=sigma)
    hist *= weights.sum() / max(hist.sum(), 1e-30)   # normalize
    with np.errstate(divide='ignore'):
        log_h = np.log10(hist + 1e-30)
    return xe, ye, log_h, xmn, xmx, ymn, ymx

print("Computing face-on ...")
_, _, z_face, xmn, xmx, ymn, ymx = build_grid(x, y, mass_all)
print("Computing edge-on ...")
_, _, z_edge, _, _, zmn, zmx = build_grid(x, z, mass_all)

# Robust color range: clip to 1st-99th percentile of occupied pixels
vmin = min(np.percentile(z_face[z_face > -20], 1),
           np.percentile(z_edge[z_edge > -20], 1))
vmax = max(np.percentile(z_face[z_face > -20], 99),
           np.percentile(z_edge[z_edge > -20], 99))

# --- 1x2 plot ---
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, img, ext, xlbl, ylbl, title in [
    (axes[0], z_face, [xmn, xmx, ymn, ymx], 'PC1', 'PC2', 'Face-on  (PC1 × PC2)'),
    (axes[1], z_edge, [xmn, xmx, zmn, zmx], 'PC1', 'PC3', 'Edge-on  (PC1 × PC3)'),
]:
    ax.imshow(img, origin='lower', aspect='auto',
              extent=ext, cmap='jet', vmin=vmin, vmax=vmax,
              interpolation='bilinear')
    ax.set_xlabel(xlbl, fontsize=12)
    ax.set_ylabel(ylbl, fontsize=12)
    ax.set_title(title, fontsize=14, pad=8)

# shared horizontal colorbar (bottom)
fig.subplots_adjust(bottom=0.20, wspace=0.30)
cax = fig.add_axes([0.13, 0.07, 0.74, 0.03])
sm = plt.cm.ScalarMappable(cmap='jet', norm=plt.Normalize(vmin=vmin, vmax=vmax))
sm.set_array([])
cbar = fig.colorbar(sm, cax=cax, orientation='horizontal')
cbar.set_label(r'$\log_{10}\,\rho$', fontsize=12)

fig.suptitle('Snapshot — PCA  |  Gaussian-smoothed density projection', fontsize=14, y=0.99)
plt.savefig('snapshot_pca.png', dpi=150)
```

### Key Decisions

| Choice | Zoom-in (HiRes) | Full cosmological box |
|--------|----------------|-----------------------|
| Particles | PartType0 (gas only) | All types (mass-weighted) |
| Weights | `density` | `mass_all` |
| PC1 variance | ~48% (disk) | ~86% (halo) |
| Sigma | 1.8–2.0 px | 2.0 px |
| Grid | 600×600 | 600×600 |

### Pitfalls
- Reset matplotlib with `plt.rcParams.update(plt.rcParamsDefault)` before starting, NOT with `plt.style.use('default')` (may re-apply dark style from rc)
- Color range: set `vmin/vmax` from 1st/99th percentile of **occupied pixels only** (values > -20), not global min/max
- `np.log10(0)` → `-inf`; add `+1e-30` before log to avoid NaN
- For `snap_500`: PartType1-3 have mass=1.0, PartType0/PartType4 have mass~8e-7 — mass-weighting is essential

---

## 6. Morphological Decomposition (Bulge / Bar / Disk)

For particle-classification into structural components, use this pipeline:

### Step 1: Find Center (Density-Weighted)
```python
center_x = np.sum(coords_kpc[:, 0] * density) / np.sum(density)
center_y = np.sum(coords_kpc[:, 1] * density) / np.sum(density)
center_z = np.sum(coords_kpc[:, 2] * density) / np.sum(density)
center = np.array([center_x, center_y, center_z])
r_c = coords_kpc - center
```

### Step 2: Inertia Tensor → Rotation Axis
```python
I = np.zeros((3, 3))
for i in range(3):
    for j in range(3):
        I[i, j] = np.sum(r_c[:, i] * r_c[:, j])
eigenvalues, eigenvectors = np.linalg.eigh(I)
sort_idx = np.argsort(eigenvalues)
eigvecs_sorted = eigenvectors[:, sort_idx]  # smallest eigenvalue = rotation axis

# Rotation axis = eigvecs_sorted[:, 0]
# Disk plane = span of eigvecs_sorted[:, 1] and eigvecs_sorted[:, 2]
```

### Step 3: Rotate to Eigenframe
```python
R_prime = np.dot(r_c, eigvecs_sorted)
x_disk = R_prime[:, 1]    # intermediate axis (kpc/h, already converted)
y_disk = R_prime[:, 2]    # largest axis (kpc/h)
z_disk = R_prime[:, 0]    # rotation axis (kpc/h)

R_disk = np.sqrt(x_disk**2 + y_disk**2)  # kpc/h (ALL ALREADY IN KPC/H)
phi_disk = np.arctan2(y_disk, x_disk)
```

### Step 4: Binned Ellipticity Profile
```python
R_bins = np.logspace(np.log10(R_disk.min()+0.01), np.log10(R_disk.max()), 20)
ellipticity_bin = []
for i in range(len(R_bins) - 1):
    mask = (R_disk >= R_bins[i]) & (R_disk < R_bins[i+1])
    if np.sum(mask) < 50:
        ellipticity_bin.append(np.nan)
        continue
    Cov = np.cov(x_disk[mask], y_disk[mask], aweights=density[mask])
    eigvals, eigvecs = np.linalg.eigh(Cov)
    a, b = np.sqrt(np.abs(eigvals[1])), np.sqrt(np.abs(eigvals[0]))
    ell = (a - b) / (a + b)
    ellipticity_bin.append(ell)
```

### Step 5: Map Ellipticity BACK TO PARTICLE LEVEL
```python
# CRITICAL: ellipticity_bin is per-bin; particle_masking needs per-particle
ellipticity_particle = np.zeros(len(R_disk))
for i in range(len(R_bins) - 1):
    mask = (R_disk >= R_bins[i]) & (R_disk < R_bins[i+1])
    if not np.isnan(ellipticity_bin[i]):
        ellipticity_particle[mask] = ellipticity_bin[i]
```

### Step 6: Classification
```python
R_bar = R_center_of_max_ellipticity
ellipticity_threshold = 0.15

bulge_mask = (R_disk < 0.5 * R_bar) | (np.abs(z_disk) > 1.0)  # central/thick
bar_mask = ((R_disk >= 0.5 * R_bar) & (R_disk < 2 * R_bar) &
            (ellipticity_particle > ellipticity_threshold))
disk_mask = ((R_disk > R_bar) & (np.abs(z_disk) <= 1.0) &
             (ellipticity_particle < ellipticity_threshold))
halo_mask = ~bulge_mask & ~bar_mask & ~disk_mask
```

### Important Notes
- **Velocities may be extremely small** (std ~ 0.001 km/s in zoom simulations).
  If `np.std(vel_km_s)` is tiny, skip kinematic approaches; use morphological only.
- Eigenvalue ratios like 8%:42%:50% indicate a moderately flattened system
  (not a razor-thin disk). z_disk std of 3–5 kpc/h is typical.
- Bar detection requires ellipticity > 0.15; many systems have no strong bar.
- See `references/morphological-decomposition.md` for the full walkthrough.

## 6. Pitfalls & Tips

### Pitfalls
- `set_edgecolor()` not `set_edge_color()` — matplotlib API change
- LaTeX in labels (`$M_\odot$`) can break `tight_layout()` — use simple text
- `execute_code` sandbox lacks `s3fs`, `h5py`, `scikit-learn` — use terminal with venv
- `s3.aip.de:9000` unreachable — always use `s3.data.aip.de:9000`
- Arepo coordinates are in **Mpc/h**, not kpc or parsec
- Velocity units are **cm/s**, not km/s
- Not all snapshots contain all particle types — check `NumPart_ThisFile`

### Tips
- Always inspect HDF5 structure before analysis (`f.visititems(print)`)
- Use `np.log10()` for density/temperature — wide dynamic range
- Color plots by physical property (density, temperature, velocity) for insight
- Radial bins should be logarithmic for zoom simulations (wide dynamic range)
- Surface density = mass / (2πr Δr) for annular bins

---

## 7. Quick Reference

See also:
- `references/pmviewer2023-snapshots.md` — bucket inventory, HiRes snapshot 307 structure, stat ranges
- `references/morphological-decomposition.md` — full walkthrough of the morphological decomposition pipeline (bulge/bar/disk classification via inertia tensor + ellipticity).

### Typical Arepo Snapshot Contents
| Particle Type | Code | Description |
|---------------|------|-------------|
| PartType0 | 0 | Gas (hydrodynamics) |
| PartType1 | 1 | Dark matter |
| PartType2 | 2 | Stars |
| PartType3 | 3 | Stellar wind |
| PartType4 | 4 | Black holes |
| PartType5 | 5 | Outflows |

### Common File Naming
`HiRes_H_1_t_0_snapshot_XXX.hdf5`
- `HiRes`: zoom-in/high-resolution region
- `H_1`: snapshot identifier
- `t_0`: time group
- `snapshot_XXX`: snapshot number

### Example Inspection
```python
import h5py
with h5py.File('snapshot_118.hdf5', 'r') as f:
    header = dict(f['Header'].attrs)
    print("Particles per type:", header['NumPart_ThisFile'])
    print("BoxSize:", header['BoxSize'], "Mpc/h")
    print("Redshift:", header['Redshift'])
    print("Time:", header['Time'])
```
