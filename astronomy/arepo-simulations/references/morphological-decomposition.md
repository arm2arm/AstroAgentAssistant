# Morphological Decomposition Workflow

Session 2026-05-06: Decomposed Arepo snapshot 118 (786,828 gas particles) into bulge/bar/disk components.

## Key Learnings

### 1. Velocities Can Be Meaningless
- Snapshot 118: `std(vel_km_s) = 0.001 km/s` — too small for kinematic classification.
- Always check `np.std(vel_km_s)` before attempting velocity-based methods.
- Fallback: use purely morphological methods (density, spatial structure, ellipticity).

### 2. Inertia Tensor Reveals Tilted Axes
- Snapshot 118 eigenvalue ratios: 8.0% : 42.0% : 50.0% — moderately flattened, NOT a thin disk.
- Rotation axis: (0.52, -0.24, 0.82) — tilted ~70° from Z.
- **Wrong approach**: assuming Z is the rotation axis → projects everything into wrong plane.
- **Correct approach**: inertia tensor → eigenvectors → rotate coordinate system.

### 3. Unit Consistency is Critical
- `coords_kpc = coords * 1000` converts Mpc/h → kpc/h.
- After rotation, coordinates are ALREADY in kpc/h. Do NOT divide by 1000 again.
- Bug pattern: `x_disk = R_prime[:, 1] / 1000` → collapses coordinates to 0.02 kpc/h.

### 4. Ellipticity Must Be Mapped Back to Particle Level
- Ellipticity computed per radial bin (shape N_bins) cannot be used to mask N_particles.
- **Fix**: create `ellipticity_particle = np.zeros(N)` and fill per particle via bin assignment.
- This was the #1 cause of repeated `ValueError: operands could not be broadcast` errors.

### 5. Typical Results for Gas-Only Zoom Simulations
- No strong bar (ellipticity < 0.2) → bar fraction near 0%.
- Bulge/disk split ~45/50% is typical for gas-rich systems.
- Halo fraction ~4% captures outlying/unclassified particles.

### 6. Debugging Printouts to Include
```
Eigenvalue ratios: 8.0%, 42.0%, 50.0%
Rotation axis: (0.522, -0.241, 0.818)
Disk plane R range: 0.02 to 19.75 kpc/h
Disk thickness (Z'): -19.04 to 19.13 kpc/h
z_disk std: 3.56 kpc/h
Max ellipticity: 0.206 at R = 0.38 kpc/h
```