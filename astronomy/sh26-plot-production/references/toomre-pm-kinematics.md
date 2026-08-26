# Toomre PM→velocity (P82): transform, validation, data provenance

Class note for ANY proper-motion kinematics on the SH26 catalog (full
U,V,W from (l,b,d,pmra,pmdec), not just RV). Hand-rolled tangent-plane
formulas are NOT trustworthy: use exact rotation-matrix algebra and
validate against astropy ground truth BEFORE producing a figure.

## The transform (`_disk_helper.py::toomre_peculiar`)

- Galactic cartesian axes ARE the Toomre basis: +x→GC = U, +y prograde = V,
  +z→NGP = W.
- IAU J2000 rotation hardcoded as `_R_G2I` (orthogonal to 1e-16, det=1).
  Positions: `v_icrs = _R_G2I @ v_gal`. **Velocities: `v_gal = _R_I2G @ v_icrs`**
  where `_R_I2G = _R_G2I.T` — using the same matrix for both is a subtle bug.
- ICRS tangential basis: `e_ra = (-sin ra, cos ra, 0)` (per unit RA),
  `e_dec = (-sin dec cos ra, -sin dec sin ra, cos dec)`;
  `v_icrs = k*d*(pmra*e_ra + pmdec*e_dec)`, k = 4.74047, d in kpc, pm in mas/yr.
- Gaia `pmra` = μ_α (already cos-dec weighted). v_r = 0 (catalog has no RV).
- Solar/rotation subtraction (Schonrich 2010): U+=11.1, V+=Vp=12.24,
  W+=7.25 km/s, R0=8.19 kpc, V0=239.5 km/s, near-flat curve (vc_slope=0).
- Returns (U_pec, V_pec, W_pec) in km/s.

## astropy 8.0.1 ground truth (working recipe)

```python
import numpy as np, astropy.units as u
from astropy.coordinates import (ICRS, Galactic, SphericalRepresentation,
    SphericalDifferential, CartesianRepresentation)
import sh26.plots._disk_helper as H

def astro_uvwh(l, b, d, pmra, pmdec):
    """Scalar ground truth: heliocentric (U,V,W) km/s from (l,b,d,pmra,pmdec)."""
    g = Galactic(l=u.deg*l, b=u.deg*b, distance=u.kpc*d)
    ic = g.transform_to(ICRS())
    cosd = np.cos(np.deg2rad(ic.dec.deg))
    sph = SphericalRepresentation(lon=ic.ra, lat=ic.dec, distance=g.distance)
    diff = SphericalDifferential(d_lon=(u.mas/u.yr)*(pmra/cosd),  # raw d(ra)/dt!
                                 d_lat=(u.mas/u.yr)*pmdec,
                                 d_distance=0*u.km/u.s)          # REQUIRED kwarg
    c = ICRS(sph.with_differentials(diff)).represent_as(CartesianRepresentation)
    vs = c.differentials['s']          # appears only after represent_as
    v = np.array([vs.d_x.to(u.km/u.s).value,   # native unit kpc*mas/(rad*yr)
                  vs.d_y.to(u.km/u.s).value,
                  vs.d_z.to(u.km/u.s).value])
    return H._R_I2G @ v                # = R_G2I.T @ v_icrs
```

Loop ~500 scalar stars (l∈[0,360), b∈[−85,85), d∈[0.1,15] kpc, |pm|<60).
Expected: max|Δ| ≈ 5e-4 km/s vs `toomre_peculiar`. PASS threshold 1e-3 km/s.

## Pitfalls (each cost hours)

1. NGP-scalar `(l,b)→cos(dec)` formula: wrong by up to 61° (dec −60.19° vs
   true −28.94° at the GC). Use row-3 of the exact rotation instead.
2. Velocity needs the TRANSPOSE of the galactic→ICRS matrix (see above).
3. `UnitSphericalRepresentation.with_differentials()` silently DROPS the
   velocity differential (`differentials` ends up empty). Use
   `SphericalRepresentation(lon=, lat=, distance=)` with a real distance
   (kwargs — positional order is lon, lat, distance) +
   `SphericalDifferential(d_lon=, d_lat=, d_distance=)`.
4. `SphericalDifferential.d_lon` is RAW d(ra)/dt, NOT μ_α. Feed `pmra/cos(dec)`;
   d_lat = pmdec directly.
5. Returned `CartesianDifferential` native unit is `kpc*mas/(rad*yr)` —
   convert with `.to(u.km/u.s)`. Do NOT multiply by a hand 4.74047 constant
   (1 mas/yr @ 1 kpc stores value 1.0 in that unit, not 4.74).
6. astropy 8: frame constructors take NO velocity kwargs; build frames from
   representations carrying differentials. `.to(frame)` is gone →
   `.transform_to(frame)`.
7. **Referee protocol** — the "8e3 km/s FAIL" scare was 100% referee-side
   (pitfalls 4+5), while the helper was already correct:
   (a) compare helper vs astropy on SCALAR stars in a loop first —
   vectorized frame paths can hide index/unit bugs;
   (b) check |v| magnitudes on BOTH sides before trusting max|Δ|;
   (c) use a physical threshold (1e-3 km/s), not 1e-6 — mm/s is below the
   float floor for km/s-scale vectors.

## Validation result (2026-08-16, astropy 8.0.1, numpy 2.4.6)

500-star scalar round-trip: max|Δ| = 4.9e-4 km/s (~0.5 m/s). Helper correct.

## P82 sanity anchors (50M, converged-only)

- 40,719,146 converged → 16,770,182 PM stars (41.2%). Cuts: plx SNR>5,
  pm err<2 mas/yr, dist50<5 kpc, |Z|<3 kpc, 2≤R<15 kpc.
- σ(W): 47.1 (|Z|~0) → 56.9 (|Z|~1) km/s; σ(U) 38→60; σ(V) 29→50.
- ⟨V_pec⟩(R) zero-crossing at R≈7.7 kpc (just inside R0=8.19), 19 filled bins
  spanning 3.5–13 kpc, near-linear through the crossing — that shape IS the
  flat rotation curve; a big deviation means transform bug, not physics.
- Warm 50M run ~13 s (foreground). Cold-cache runs can raise a transient Dask
  `CommClosedError` (worker death) that Dask reschedules past — re-run warm,
  then verify sidecar `n_points` == full converged count and that high-R bins
  are populated before trusting the output.

## PM data provenance

- PM source on Newton: `gaiadr3/GaiaSource.float32.parq` (302 GB; pmra/pmdec +
  errors + solved flag). Join chain (all on Newton): 50M rows → exact float64
  (l,b) match against the 402M-row input tiles → source_id (Phase A: 99.986%)
  → GaiaSource lookup → pmra/pmdec (Phase B).
- PM appended as real columns, position-aligned PER DATASET (200k and 50M
  have different row orders; only 4,246 rows overlap — no shared map).
  `data/pm_50m.parquet` (1.8 GB, key `pos`) and `data/pm_200k.parquet` are
  the compact fetched sidecars.
- PM values verified exact vs AIP Gaia DB API (source_id 298895364329216:
  pmra −12.8851903, pmdec 0.6726590, solved 31).
- Newton pyarrow is old: `to_numpy(zero_copy=...)` kwarg unsupported —
  use plain `.to_numpy()`.
