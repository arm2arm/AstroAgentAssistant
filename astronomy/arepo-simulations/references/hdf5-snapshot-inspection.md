# HDF5 Snapshot Inspection Guide

## Quick Inspection Checklist

1. **Verify connectivity** first:
   ```bash
   curl -s -o /dev/null -w "%{http_code}" https://s3.data.aip.de:9000
   ```
   HTTP 200/400 = reachable. HTTP 000 = connection refused (try different endpoint).

2. **Download the file** — use s3fs, not boto3 directly (s3fs is already in project venv):
   ```python
   import s3fs
   fs = s3fs.S3FileSystem(anon=True, client_kwargs={"endpoint_url": "https://s3.data.aip.de:9000"})
   with fs.open("bucket/path/file.hdf5", "rb") as f:
       with open("local.hdf5", "wb") as out:
           out.write(f.read())
   ```

3. **Inspect structure** (fast, no data loading):
   ```python
   import h5py
   with h5py.File("file.hdf5", "r") as f:
       f.visititems(lambda n, o: print(n + ("/" if isinstance(o, h5py.Group) else f" [{o.shape}] {o.dtype}")))
   ```

4. **Read metadata**:
   ```python
   with h5py.File("file.hdf5", "r") as f:
       hdr = dict(f['Header'].attrs)
       print("BoxSize:", hdr['BoxSize'])
       print("Redshift:", hdr['Redshift'])
       print("Particles:", hdr['NumPart_Total'])
   ```

## Arepo vs Gadget Differences

| Feature | Arepo | Gadget-2/3/4 |
|---------|-------|--------------|
| Group names | `PartType0` through `PartType5` | Same |
| Coordinate units | Mpc/h | Mpc/h |
| Velocity units | cm/s (peculiar) | cm/s (peculiar) |
| Grid | Moving mesh (finite volume) | SPH |
| Header structure | Standard Gadget-compatible | Standard |
| Additional groups | May have `PartType0/` or `PartType0/` subgroups | Typically flat |

Both formats are HDF5 and share the same group structure. The main difference is
in physics, not file format.

## Common Column Names

### Gas (PartType0)
- `Coordinates` — (N, 3) float64, Mpc/h
- `Velocities` — (N, 3) float32, cm/s (peculiar, not comoving)
- `Density` — (N,) float32, g/cm³
- `Hsml` — (N,) float32, cm (smoothing length)
- `InternalEnergy` — (N,) float32, erg/g
- `ParticleIDs` — (N,) uint32 or uint64

### Stars (PartType4)
- `Coordinates` — same units
- `Velocities` — same units
- `FormEpoch` — float32, cosmic time at formation
- `Metals` — float32, metal mass fraction
- `ParticleIDs` — same

### Dark Matter (PartType1)
- `Coordinates` — same units
- `Velocities` — same units
- `ParticleIDs` — same

## Unit Conversion Reference

| Quantity | Raw unit | Conversion to | Formula |
|----------|----------|---------------|---------|
| Position | Mpc/h | kpc/h | × 1000 |
| Position | Mpc/h | pc | × 1e6 |
| Velocity | cm/s | km/s | × 1e-5 |
| Velocity | cm/s | m/s | × 1e-2 |
| Density | g/cm³ | kg/m³ | × 1000 |
| Density | g/cm³ | M⊙/pc³ | × 4.779e13 |
| Smoothing length | cm | pc | × 3.24078e-17 |
| Smoothing length | cm | kpc | × 3.24078e-20 |
| Internal energy | erg/g | K | T = (2/3) × u × μ × mp / k |
| Temperature | — | K | μ ≈ 0.6 for ionized gas |

Where: μ = 0.6 (mean molecular weight), mp = 1.67262e-24 g, k = 1.38065e-16 erg/K

## Zoom-in Detection

To detect if a snapshot is a zoom-in (zoomed subregion of a larger box):

```python
import h5py
with h5py.File("file.hdf5", "r") as f:
    hdr = dict(f['Header'].attrs)
    coords = f['PartType0/Coordinates'][:]
    
    box_size = hdr['BoxSize']
    coord_range = coords.max(axis=0) - coords.min(axis=0)
    
    ratio = box_size / coord_range.max()
    if ratio > 100:
        print(f"Zoom-in detected: {ratio:.0f}:1")
        print(f"Zoom region size: ~{coord_range.max() * 1000:.0f} kpc/h")
        print(f"Box size: {box_size} Mpc/h")
    else:
        print(f"Full box: {box_size} Mpc/h")
```

## Performance Tips

- **Large snapshots** (>100M particles): load only needed columns, use memory mapping
- **Streaming reads**: read groups individually instead of loading entire file
- **Parallel reads**: use `h5py` with parallel I/O if multiple files exist
- **Downsampling**: for visualization, sample subset (e.g., every 10th particle)
