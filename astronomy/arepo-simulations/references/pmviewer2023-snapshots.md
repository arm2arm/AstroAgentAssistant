# pmviewer2023 Bucket — Snapshot Reference

**Bucket:** `https://s3.data.aip.de:9000/pmviewer2023`
**Access:** anonymous read (no credentials)
**Files:** 299 HDF5 snapshots + config/assets

---

## File Naming

```
HiRes_H_1_t_0_snapshot_NNN.hdf5    # HiRes zoom-in simulations
snap_NNN.hdf5                       # standard resolution snapshots
```

---

## HiRes Snapshot 307 — Full Structure

```
Header/
  (contains: BoxSize, NumPart_Total, NumPart_ThisFile, Redshift, Time, MassTable, ...)
PartType0/                            # Gas only (803,554 particles)
  Coordinates    (803554, 3) float64   # Mpc/h  — box ≈ ±0.02 Mpc/h
  Density        (803554,) float32     # g/cm³  — range: 1e3 to 1e8
  Hsml           (803554,) float32     # smoothing length (cm)
  InternalEnergy (803554,) float32     # erg/g
  ParticleIDs    (803554,) uint32
  Velocities     (803554, 3) float32   # cm/s
```

### Observed Stats (snapshot 307)
| Field | Value |
|-------|-------|
| Particles | 803,554 |
| Box extent | ±0.02 Mpc/h (both x, y, z) |
| Density min | ~1 × 10³ g/cm³ |
| Density median | ~9.8 × 10⁵ g/cm³ |
| Density max | ~1.2 × 10⁸ g/cm³ |

---

## snap_400–500 — Full Cosmological Box

~147 MB each, 101 files (400–500). **All particle types present** (unlike HiRes which is gas-only zoom).

### snap_500 — Full Structure
```
snap_500.hdf5  |  147.4 MB  |  ~5.3M total particles

Header/             BoxSize, NumPart_Total, Redshift, Time, MassTable, Parameters
Config/
Parameters/
PartType0/          Gas (109,026)  mass=8.53e-07
  Coordinates   (109026, 3) float32   — code units
  Density       (109026,) float32
  InternalEnergy(109026,) float32
  Masses        (109026,) float32
  Velocities    (109026, 3) float32
  ParticleIDs   (109026,) uint32
  Subfind* fields (DMDensity, Density, Hsml, VelDisp)
  StarFormationRate (109026,) float32
  NeutralHydrogenAbundance (109026,) float32
  ElectronAbundance (109026,) float32
PartType1/          Dark matter (1,200,000)  mass=1.0
  Coordinates (1200000, 3) float32
  Velocities  (1200000, 3) float32
  Subfind* fields
PartType2/          Dark matter (800,000)  mass=1.0
PartType3/          Dark matter (400,000)  mass=1.0
PartType4/          Stars (862,817)  mass=8.30e-07
  Coordinates (862817, 3) float32
  Masses      (862817,) float32
  Velocities  (862817, 3) float32
  Subfind* fields
PartType5/          BHs (2)  mass=1.0
  Coordinates (2, 3) float32
  Velocities  (2, 3) float32
```

**Key differences from HiRes:**
- DM particles have mass=1.0 (code units), gas/stars ~1e-6 — **mass-weighting essential** for PCA
- Box is large: extent ~−1180 to +1713 (code units)
- PC1 variance ~86% → halo-dominated, near-spherical
- HiRes PC1 ~48% → disk-like (flattened)

---

## Color Maps (in bucket)

```
data/col_0.rgba
data/col_inferno.rgba
data/gas.rgba
```

## Config Files

```
data/pm_cool.ini
data/pm_cool_0_0_0.ini
data/pm_cool_0_0_1.ini
data/pm_cool_0_0_200.ini
data/run_pm_0_hdf5.sh
data/particles.cache.npy   # 7.8 GB — pre-processed particle data
```