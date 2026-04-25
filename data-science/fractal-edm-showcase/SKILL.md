---
name: fractal-edm-showcase
title: Fractal EDM Showcase
description: Automated workflow to generate a short fractal showcase video with a synthetic fast‑paced EDM soundtrack, including Seahorse and Elephant valley visual elements.
author: Hermes Agent
created: 2026-04-14
---

# Overview
This skill automates the creation of a short (~55 s) fractal showcase video that includes:
- Mandelbrot set, Sierpinski triangle, Barnsley fern, **Seahorse Valley** (tiny central figure), and **Elephant Valley** (jet‑coloured, slowly zoomed).
- A synthetic, fast‑paced EDM soundtrack (140 BPM) generated entirely in Python.
- Final video‑audio merge using `ffmpeg`.

The workflow is fully script‑driven and works with the local Manim environment (`~/.venvs/manim`).

# Files & Directory Structure
```
~/fractals-animation/
├─ script.py                 # Manim scene (see below)
├─ audio/
│   ├─ generate_edm_track.py   # EDM synthesis script
│   ├─ edm_fast.wav            # generated WAV (temporary)
│   ├─ edm_fast.aac            # AAC‑encoded version
│   └─ edm_fast_trimmed.aac    # 55 s trimmed track
└─ media/videos/script/480p15/
    └─ FractalsShowcase_EDM_fast.mp4   # final output
```

# Step‑by‑Step Procedure

## 1️⃣ Generate PNG fractal assets
The `script.py` contains helper functions that lazily generate and cache the required images in `/tmp/fractals_imgs`:
- `save_mandelbrot`
- `save_sierpinski`
- `save_barnsley_fern`
- `save_barnsley_elephant`
- **`save_seahorse`** – creates a tiny seahorse‑like point cloud (scale ≈ 0.00009).
- **`save_elephant_jet`** – loads the original elephant PNG, converts to grayscale, applies Matplotlib’s `jet` colormap and resizes to 512 × 512.
Run once (or rely on the caching logic in `script.py`).

## 2️⃣ EDM audio synthesis (`audio/generate_edm_track.py`)
Key parameters (easy to tweak):
```python
BPM = 140                # fast, rocking tempo
TOTAL_SEC = 60           # generate a bit longer, will be trimmed to 55 s
SR = 44100               # 44.1 kHz
```
The script builds four tracks:
- **Kick** – decaying sinusoid with pitch drop.
- **Snare** – band‑passed noise burst.
- **Hi‑hat** – short high‑frequency square‑wave burst.
- **Bass** – low‑frequency sinusoid with a 0.25 Hz LFO wobble.
All tracks are mixed to stereo, normalised, written to `edm_fast.wav`, converted to AAC (`edm_fast.aac`), then trimmed to exactly 55 s (`edm_fast_trimmed.aac`).

## 3️⃣ Render the Manim video (draft quality)
```bash
source ~/.venvs/manim/bin/activate
manim -ql ~/fractals-animation/script.py FractalsShowcase
```
The scene order:
1. Title fade‑in/out.
2. Mandelbrot zoom.
3. Sierpinski → Fern.
4. **Elephant Valley** – displayed with `ELEPHANT_JET_IMG`, fade‑in, then a 30 s slow zoom (`scale(0.5)`).
5. **Seahorse Valley** – tiny central image (`scale(0.2)`), brief fade‑in/out.
6. Closing caption.
All fades are non‑overlapping (clear‑before‑next) to respect the visual style.

## 4️⃣ Merge audio & video
```bash
ffmpeg -y -i /home/hermes/media/videos/script/480p15/FractalsShowcase.mp4 \
       -i /home/hermes/fractals-animation/audio/edm_fast_trimmed.aac \
       -c:v copy -c:a aac -b:a 192k -shortest \
       /home/hermes/fractals-animation/media/videos/script/480p15/FractalsShowcase_EDM_fast.mp4
```
Resulting file is ~2.5 MB (15 fps, 854 × 480).

# Pitfalls & Gotchas
- **Variable scope:** `ELEPHANT_JET_IMG` must be defined *before* it is used in the scene (the original script raised a `NameError`). Ensure the image‑generation block runs before the class definition.
- **Caching:** The script checks `os.path.exists` for each PNG; delete the `/tmp/fractals_imgs` folder if you need to regenerate with different parameters.
- **Audio length mismatch:** If you change the video length (e.g., add more scenes), update `TOTAL_SEC` or the `ffmpeg -t` trim duration accordingly.
- **Zoom speed:** Adjust the `run_time` in `self.play(elephant.animate.scale(...))` to achieve the desired visual pacing.
- **Manim version:** Tested with Manim 0.20.1; newer versions may require minor syntax tweaks.

# Re‑use
You can drop the whole `~/fractals-animation` folder into a new project, tweak the `BPM`, scaling factors, or replace the fractal set with your own images. The workflow works on any Linux machine with Python 3.11, Manim, NumPy, Matplotlib, Pillow, and `ffmpeg` installed.
