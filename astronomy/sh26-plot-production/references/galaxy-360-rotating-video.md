# 360° rotating SH26 galaxy videos (2026-08-21, done)

Deliverables: `/tmp/sh26_galaxy_faceon_360.mp4` + `/tmp/sh26_galaxy_xyz_360.mp4`
(4 s seamless loops, 1280×1280, 120 frames @ 30 fps, inferno on black,
star count in every title). Source scripts: <compute-node> `/tmp/gal_sample.py`,
`/tmp/gal_render.py`, `/tmp/gal_encode.sh`; data `/tmp/sh26_xyz_10m.npz`
(10M uniform subsample seed 42 of the 327,477,457 converged stars).

## What worked

- **Sample**: pyarrow-direct, columns `l,b,dist50,MISSING` only → 10M
  `rng.choice(replace=False)` indices → float32 X/Y/Z → npz (24.9 s total,
  page-cache-hot). 9,984,703 survived the ±50 kpc box.
- **Face-on video**: X–Y density grid (1024²) rotated in-plane per frame —
  exact 2D bincount, no projection.
- **XYZ video**: rotate about Z, orthographic projection at 30° elevation
  (`sy = yr*cos(el) + zr*sin(el)`, `los = -yr*sin(el) + zr*cos(el)`), 3D
  bincount 512³ then `.sum(axis=1)` over the LOS axis (grid layout is
  `[iv, il, iu]` from `iv*(nb*nb) + il*nb + iu`). Color = LOS-integrated
  number density.
- 1.4 s/frame at 1280² → full 2×120-frame render ≈ 5 min on <compute-node>.

## Pitfalls hit (in order)

1. **`to_pydict()` on 402M rows is the slow path** (minutes, Python objects).
   Use `tbl[col].to_numpy(zero_copy_only=False)` per column — read was 9.9 s.
2. **Linear normalization washes out galaxies**: number density falls
   exponentially; only the core survives linear scaling. Use
   `LogNorm(vmin=1, vmax=max)` with zero-count cells set to 1.
3. **`np.clip` binning maps out-of-frame points INTO edge bins** → fake
   bright frame-edge ring. Mask with `inb = (|x|<=LIM) & (|y|<=LIM)` and
   filter the arrays BEFORE bincount.
4. **Galactocentric centering**: XGal origin is the Sun (−8.19 kpc). For a
   rotation video, do `X = X + 8.19` then subtract the measured density
   centroid `(X.mean(), Y.mean())` — the residual Sun↔GC offset otherwise
   makes the bulge wobble as it spins.
5. **Disk extent**: r90 ≈ 10 kpc. A ±50 kpc frame renders a "tiny knot"
   (vision QA said no disk). Frame at ±12 kpc. Measure the radial density
   profile FIRST (`np.hypot(X,Y)` histogram / annulus means) before picking
   frame extent.
6. **ffmpeg `%03d` + angle-named frames = silent 1-frame video** (encoded
   only `xyz_000.png`, exit 0). Rename frames to sequential `tag_%03d.png`
   and verify with `ffprobe -count_frames ... nb_read_frames`.
7. **Bash `$name_` variable trap**: `"$dir/$name_%03d.png"` expands `$name_`
   (undefined → empty). Use `${name}_%03d.png`.
8. QA: `vision_analyze` on a *full* 1280² frame flagged the white **title
   text** as "brightest pixel"; radial profiles centered on image center
   mislead because the colorbar offsets the axes. Crop to the axes region
   first, or locate the peak on the data grid directly.
