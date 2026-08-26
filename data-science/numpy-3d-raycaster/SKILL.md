---
name: numpy-3d-raycaster
version: 1.0.0
tags: [numpy, raycasting, 3d, equirectangular, animation]
description: NumPy raycaster for 3D equirectangular video frames.
---

# NumPy Vectorized 3D Raycasting (equirectangular)

Pure-numpy raycasters for generating 360° equirectangular frames — no Blender, no matplotlib render loop. Camera at origin, scene rotates per frame.

## Equirectangular direction grid (precomputed once)

```python
W, H = 2048, 1024  # MUST be 2:1
lon = np.linspace(-np.pi, np.pi, W, endpoint=False)
lat = np.linspace(np.pi/2, -np.pi/2, H + 1)[:H]
Lon, Lat = np.meshgrid(lon, lat)

dir_x = np.cos(Lat) * np.sin(Lon)
dir_y = np.sin(Lat)
dir_z = np.cos(Lat) * np.cos(Lon)
```

## Camera pitch tilt (rotate around X-axis)

To tilt the camera view upward/downward by `pitch` degrees:

```python
cp, sp = math.cos(pitch), math.sin(pitch)
cam_dy = cp*dir_y + sp*dir_z    # tilted Y
cam_dz = -sp*dir_y + cp*dir_z   # tilted Z
```

This elevates the gaze above/below the equatorial plane without changing longitude mapping.

## World-space rotation (scene spins, camera fixed)

```python
def rotY(angle_deg):
    theta = np.radians(angle_deg)
    c, s = math.cos(theta), math.sin(theta)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])

R = rotY(angle)
wx = R[0,0]*dx + R[0,1]*dy + R[0,2]*dz
wy = R[1,0]*dx + R[1,1]*dy + R[1,2]*dz
wz = R[2,0]*dx + R[2,1]*dy + R[2,2]*dz
```

## Sphere intersection (analytical)

```python
def intersect_sphere(dx, dy, dz, cx, cy, cz, r):
    ocx=-cx; ocy=-cy; ocz=-cz
    b = 2.0*(ocx*dx + ocy*dy + ocz*dz)
    c = ocx*ocx + ocy*ocy + ocz*ocz - r*r
    disc = b*b - 4.0*c
    t = np.full_like(b, np.inf)
    ok = disc >= 0
    if np.any(ok):
        t[ok] = (-b[ok] - np.sqrt(np.maximum(disc[ok], 0))) / 2.0
    t[t <= 0.1] = np.inf
    return t
```

## Triangle intersection (Möller–Trumbore, vectorized)

```python
def intersect_tri(dx,dy,dz, v0x,v0y,v0z, v1x,v1y,v1z, v2x,v2y,v2z):
    e1x=v1x-v0x; e1y=v1y-v0y; e1z=v1z-v0z
    e2x=v2x-v0x; e2y=v2y-v0y; e2z=v2z-v0z
    Hx=dy*e2z-dz*e2y; Hy=dz*e2x-dx*e2z; Hz=dx*e2y-dy*e2x
    a=e1x*Hx+e1y*Hy+e1z*Hz
    t = np.full_like(Hx, np.inf)
    ok = np.abs(a) > 1e-8
    f = np.zeros_like(Hx); f[ok] = 1.0/a[ok]
    sx=-v0x; sy=-v0y; sz=-v0z
    u_ = -f*(sx*Hx+sy*Hy+sz*Hz)
    qx=sy*e2z-sz*e2y; qy=sz*e2x-sx*e2z; qz=sx*e2y-sy*e2x
    v_ = -f*(dx*qx+dy*qy+dz*qz)
    tw = f*(sx*e1x+sy*e1y+sz*e1z)
    valid = ok & (u_>=0) & (v_>=0) & ((u_+v_)<=1.0)
    t[valid] = tw[valid]; t[t <= 0.1] = np.inf
    return t
```

## Ground plane (y=constant)

```python
ground_y = -0.5
ok_g = wy < -0.01                        # rays going down only
t_g = np.where(ok_g, ground_y/np.where(ok_g, wy, 1.0), np.inf)
hit_g = (t_g > 0.5) & (t_g < best_t - 0.01)  # z-buffer test
```

## ⚠️ CRITICAL PITFALLS

### NaN from `inf * direction` — THE QUIET KILLER

Mixed hit/non-hit pixels leave `inf` in `t`. Any arithmetic like `hit_pos = ray_dir * t + origin` produces **NaN** at the inf positions. The NaN propagates through shading and corrupts output silently.

**Fix:** Use safe fallback before hit-position math:
```python
ts_safe = np.where(hit_mask, t_intersection, 1.0)
hit_pos = ray_dir * ts_safe + center       # no NaN
```

### Star placement must use per-channel writes

`frame[y,x] = (r,g,b)` writes a tuple to the wrong axis on numpy arrays. Use indexed channels:
```python
# WRONG
frame[sy, sx] = (1.0, 0.9, 1.0)           # sets entire row/col
# RIGHT
frame[sy, sx, 0] = 1.0; frame[sy, sx, 1] = 0.9; frame[sy, sx, 2] = 1.0
```

### Variable naming: rotate vertices as a tuple

When rotating triangle vertices `(v0,v1,v2)`, bind as `rv0, vr1, vr2` — consistent prefix prevents the `v1r`/`vr1` NameError at runtime.

### Ground plane inf distance attenuation

Ground hit positions `wx * t_g` produce inf for non-hit pixels. Mask or clip before computing distances:
```python
tg_safe = np.where(hit_mask, t_g, 1.0)
gx = np.clip(wx * tg_safe, -LIM, LIM)
```

### Triangle face normals must rotate with the mesh

For flat-shaded triangles, compute the face normal ONCE in object space, then `rn = R @ n` each frame. Do NOT recompute from rotated vertices — slower and can flip for degenerate rotations.

## Performance notes

- 2048×1024 frames ~1s/frame first pass (imports + seed), drops to ~0.35s on cache warm
- Triangle count scales linearly — keep meshes below ~20 faces per frame for interactive speeds
- For videos >3s, consider dropping to 1920×960 or reducing FPS

## FFmpeg encode pattern

```python
cmd = ["ffmpeg", "-y", "-framerate", str(FPS), "-i", "frame_%05d.png",
       "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast",
       "-crf", "18", "-movflags", "+faststart", "output.mp4"]
subprocess.run(cmd, capture_output=True)  # check returncode != 0
```

## Related skills

- `360-equirectangular-rendering` — cube-specific wireframe renderer (user-owned)
- `blender5-headless` — higher-fidelity but slower rendering pipeline