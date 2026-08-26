# Galaxy rotation-video extensions — extra axes (rotx / roty)

Follow-up to `galaxy-360-rotating-video.md`. Two more videos delivered
2026-08-22 in the same style as the inclined-XYZ pair:

- `/tmp/gal_rotx_360.mp4` — inclined XYZ (30° camera) rotating 360° about the X axis
- `/tmp/gal_roty_360.mp4` — same, about the Y axis (bulge fixed on screen;
  disk sweeps toward/away from camera; thickness exposed at 90°/270°)

## User style rule (from "the second one is strange, make it similar like the First one")

The first delivered pair was (1) face-on in-plane spin and (2) inclined XYZ
LOS-integrated spin. When asked for a different rotation axis, "similar to
the first [of the XYZ pair]" = **same render style**: 30° camera,
LOS-integrated number density, inferno, fixed global normalization. NOT the
flat 2D in-plane "flip" (gal_flip_360.mp4) — that was the "strange" one and
is retired.

## Implementation

- `gal_render.render_xyz_axis(frames_dir, angle_deg, axis)` (added to
  <compute-node> /tmp/gal_render.py): rotate the scene 360° about "x" or "y" on top
  of the Z spin; same camera basis and 3D bincount as `render_xyz`.
- **Fixed global LogNorm**: probe `vmax = max(grid.max())` over angles
  (0, 30, 90, 150, 180), render all 120 frames with ONE
  `LogNorm(vmin=1, vmax=vmax)` — no brightness flicker. roty probed vmax
  7903. (The original Z-spin pair used per-frame normalization; brightness
  pulses there — accepted, but don't replicate for new axes.)
- Driver scripts: <compute-node> `/tmp/gal_rot2.py` (rotx+flip; canonical pattern —
  vmax probe, inline ffmpeg encode, rename loop) and `/tmp/gal_ry.py`
  (roty, self-contained clone of that pattern).
- Render cost: ~1.4 s/frame → 120 frames ≈ 3 min + ~40 s encode.

## Pitfalls hit

1. **f-string rename bug (bit roty twice conceptually):**
   `os.rename(path, os.path.join(fd, "roty_%03d.png"))` — no f-prefix —
   writes EVERY frame to the literal filename `roty_%03d.png`; each rename
   overwrites the previous → 1 file left. ffmpeg then reads 1 frame and
   "succeeds" (exit 0) with a 0.03 s video. Correct:
   `os.path.join(fd, f"roty_{k:03d}.png")`. Always verify after encode:
   `ffprobe -v error -count_frames -select_streams v:0 -show_entries
   stream=nb_read_frames -of csv=p=0 out.mp4` == 120, and a frame-diff QA
   (0° vs 90° vs 180° frames must differ — mean-abs-diff nonzero; also
   check bright-area fraction shifts across the cycle).
2. **Import-check driver scripts before launch**: `gal_render.py` did NOT
   export `encode` or `render_faceon_grids` (gal_rot2.py defines its own
   inline ffmpeg encode; `render_faceon_grids` was added to gal_render.py
   only mid-session). Two roty launch attempts died with AttributeError
   AFTER 3 min of rendering (frames lost). Pattern: keep drivers
   self-contained (compute vmax, inline ffmpeg) or verify
   `import gal_render; gal_render.<helper>` before nohup-launching.
3. **ffmpeg errors swallowed by `subprocess.run(capture_output=True)`** —
   the crash only showed up as the missing output file. Either don't
   capture, or check `result.returncode` before `os.path.getsize`.
4. **Nested-ssh launch: `echo LAUNCHED $!` got mangled** (escaped `\$!`
   printed literally). Harmless, but confirm launch with a follow-up
   `pgrep -fc <script>` + log tail rather than trusting the echo.

## Verification checklist (both videos)

- ffprobe `nb_read_frames == 120`
- frames 0/30/60 extracted: mean-abs-diff(0,90°) > 0 and
  mean-abs-diff(0,180°) > 0 (genuine rotation, not a static frame loop)
- bright-area fraction (pixels > 20 gray) shifts across the cycle
  (roty measured 0.227 → 0.154 → 0.221)
- video size 5–8 MB (a 1-frame "video" is ~30 KB — instant tell)
