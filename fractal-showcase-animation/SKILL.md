---
name: fractal-showcase-animation
title: Fractal Showcase Animation with Music
description: |
  Generate a short Manim video showcasing famous fractals (Mandelbrot set, Sierpinski triangle, Barnsley fern, Barnsley elephant) and add a simple background music track. The process includes on‑the‑fly generation of fractal PNGs using matplotlib, assembling them in a Manim scene, rendering, creating a clean audio track, and merging with ffmpeg.
category: data-science
---
## Overview
This skill automates the creation of a ~1 minute fractal demonstration video with smooth transitions and background music. It is reusable for any set of fractal images and works in a standard Manim Python virtual environment.

## Prerequisites
- A Manim community installation (preferably in a virtualenv, e.g. `~/.venvs/manim`).
- `matplotlib` and `numpy` available in the same environment (`pip install matplotlib`).
- `ffmpeg` installed for audio/video processing.

## Directory Structure
```
~/fractals-animation/
│   script.py          # Manim scene (see below)
│   generate_fractals.py  # optional helper Python script to pre‑generate images
└───media/videos/script/480p15/   # rendered video output
```
All generated PNGs are stored in a temporary directory (`/tmp/fractals_imgs`).

## Step‑by‑Step Procedure
1. **Prepare the working directory**
   ```bash
   mkdir -p ~/fractals-animation && cd ~/fractals-animation
   ```
2. **Create the Manim script** (`script.py`).  The script:
   - Imports `matplotlib` to generate the fractal PNGs the first time it runs (caches them in `/tmp/fractals_imgs`).
   - Defines a `FractalsShowcase` scene that:
     * Shows a title.
     * Presents each fractal image with `FadeIn` → hold → `FadeOut`.
     * Includes a brief Mandelbrot zoom animation.
     * Ends with a closing caption.
3. **Install required Python packages** (once):
   ```bash
   source ~/.venvs/manim/bin/activate
   pip install matplotlib
   ```
4. **Render the draft video** (quick quality):
   ```bash
   ~/.venvs/manim/bin/manim -ql script.py FractalsShowcase
   ```
   Output will be at `media/videos/script/480p15/FractalsShowcase.mp4`.
5. **Create a simple background music track** (pure sine tone, 55 s):
   ```bash
   ffmpeg -y -f lavfi -i sine=frequency=440:duration=55 \ 
          -c:a pcm_s16le -ar 44100 -ac 2 /tmp/tone.wav
   ffmpeg -y -i /tmp/tone.wav -c:a aac -b:a 192k -ar 44100 /tmp/bg_music.aac
   ```
   (Any other royalty‑free audio can replace `tone.wav` – just ensure the format is AAC or MP3.)
6. **Merge audio and video** (ensure they have the same length):
   ```bash
   ffmpeg -y -i media/videos/script/480p15/FractalsShowcase.mp4 \ 
          -i /tmp/bg_music.aac \ 
          -c:v copy -c:a aac -b:a 192k -shortest \ 
          media/videos/script/480p15/FractalsShowcase_with_music.mp4
   ```
7. **Optional: High‑quality render** (if needed):
   ```bash
   ~/.venvs/manim/bin/manim -qh script.py FractalsShowcase
   ```
   Then repeat step 6 with the higher‑resolution MP4.

## Pitfalls & Gotchas
- **Broadcast errors** when positioning `Dot` objects: always supply a 3‑element coordinate (use `np.append(..., 0)`).
- **Malformed audio files**: some downloaded MP3s from free archives may lack proper headers. Generating a tone with ffmpeg guarantees a valid track.
- **Matplotlib image caching**: the script checks `os.path.exists` before re‑generating images, avoiding unnecessary computation.
- **Manim background colour**: set `self.camera.background_color = "#0D1117"` for a dark‑theme consistent with other visual assets.
- **Audio length mismatch**: use `-shortest` flag in ffmpeg to truncate the longer stream automatically.

## Example `script.py`
```python
"""
Famous Fractals Animated with Music
~2 min video, ~60 animations, no overlapping captions.
"""
from manim import *
import numpy as np, matplotlib.pyplot as plt, os

FRAC_DIR = "/tmp/fractals_imgs"
os.makedirs(FRAC_DIR, exist_ok=True)

# -----------------------------------------------------------------
# Helper functions to generate fractal PNGs (full implementations omitted
# for brevity – they are the same as in the original live implementation)
# -----------------------------------------------------------------
def save_mandelbrot(fname, width=800, height=800, max_iter=200):
    xs = np.linspace(-2.0, 1.0, width)
    ys = np.linspace(-1.5, 1.5, height)
    X, Y = np.meshgrid(xs, ys)
    C = X + 1j * Y
    Z = np.zeros_like(C)
    M = np.full(C.shape, True, dtype=bool)
    img = np.zeros(C.shape, dtype=int)
    for i in range(max_iter):
        Z[M] = Z[M] * Z[M] + C[M]
        diverged = np.greater(np.abs(Z), 2, out=np.full(C.shape, False), where=M)
        img[diverged & M] = i
        M[diverged] = False
    plt.figure(figsize=(4,4), dpi=200)
    plt.axis('off')
    plt.imshow(img, cmap='magma', extent=[-2,1,-1.5,1.5])
    plt.tight_layout(pad=0)
    plt.savefig(fname, bbox_inches='tight', pad_inches=0)
    plt.close()

def save_sierpinski(fname, depth=7):
    def triangle(ax, a, b, c, depth):
        if depth == 0:
            ax.fill([a[0],b[0],c[0]],[a[1],b[1],c[1]],color='blue')
        else:
            ab = (a+b)/2
            bc = (b+c)/2
            ca = (c+a)/2
            triangle(ax,a,ab,ca,depth-1)
            triangle(ax,ab,b,bc,depth-1)
            triangle(ax,ca,bc,c,depth-1)
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    ax.axis('off')
    a=np.array([0,0])
    b=np.array([1,0])
    c=np.array([0.5,np.sqrt(3)/2])
    triangle(ax,a,b,c,depth)
    plt.tight_layout(pad=0)
    plt.savefig(fname, bbox_inches='tight', pad_inches=0)
    plt.close()

def save_barnsley_fern(fname, n=100000):
    x=np.zeros(n); y=np.zeros(n)
    for i in range(1,n):
        r=np.random.random()
        if r<0.01:
            x[i]=0; y[i]=0.16*y[i-1]
        elif r<0.86:
            x[i]=0.85*x[i-1]+0.04*y[i-1]
            y[i]= -0.04*x[i-1]+0.85*y[i-1]+1.6
        elif r<0.93:
            x[i]=0.2*x[i-1]-0.26*y[i-1]
            y[i]=0.23*x[i-1]+0.22*y[i-1]+1.6
        else:
            x[i]=-0.15*x[i-1]+0.28*y[i-1]
            y[i]=0.26*x[i-1]+0.24*y[i-1]+0.44
    plt.figure(figsize=(4,6),dpi=200)
    plt.scatter(x,y,s=0.1,c='green',marker='.',alpha=0.7)
    plt.axis('off')
    plt.tight_layout(pad=0)
    plt.savefig(fname,bbox_inches='tight',pad_inches=0)
    plt.close()

def save_barnsley_elephant(fname, n=200000):
    x=np.zeros(n); y=np.zeros(n)
    for i in range(1,n):
        r=np.random.random()
        if r<0.1:
            x[i]=0; y[i]=0.2*y[i-1]
        elif r<0.2:
            x[i]=0.5; y[i]=0.25*y[i-1]+0.1
        elif r<0.3:
            x[i]=0.85*x[i-1]+0.04*y[i-1]-0.15
            y[i]= -0.04*x[i-1]+0.85*y[i-1]+0.1
        else:
            x[i]=0.2*x[i-1]-0.26*y[i-1]+0.12
            y[i]=0.23*x[i-1]+0.22*y[i-1]+0.25
    plt.figure(figsize=(5,3),dpi=200)
    plt.scatter(x,y,s=0.1,c='purple',marker='.',alpha=0.7)
    plt.axis('off')
    plt.tight_layout(pad=0)
    plt.savefig(fname,bbox_inches='tight',pad_inches=0)
    plt.close()

# -----------------------------------------------------------------
# Ensure images are cached
MAN_IMG = f"{FRAC_DIR}/mandelbrot.png"
if not os.path.exists(MAN_IMG):
    save_mandelbrot(MAN_IMG)
SIE_IMG = f"{FRAC_DIR}/sierpinski.png"
if not os.path.exists(SIE_IMG):
    save_sierpinski(SIE_IMG)
FERN_IMG = f"{FRAC_DIR}/barnsley_fern.png"
if not os.path.exists(FERN_IMG):
    save_barnsley_fern(FERN_IMG)
ELEPHANT_IMG = f"{FRAC_DIR}/barnsley_elephant.png"
if not os.path.exists(ELEPHANT_IMG):
    save_barnsley_elephant(ELEPHANT_IMG)

# -----------------------------------------------------------------
class FractalsShowcase(Scene):
    def construct(self):
        self.camera.background_color = "#0D1117"
        # Title
        title = Text("Famous Fractals", font_size=48, color=YELLOW, weight=BOLD, font="DejaVu Sans Mono")
        self.play(Write(title), run_time=2)
        self.wait(1)
        self.play(FadeOut(title), run_time=1)
        self.wait(0.5)
        # Mandelbrot zoom
        mandelbrot = ImageMobject(MAN_IMG).scale(2)
        self.play(FadeIn(mandelbrot, scale=0.8), run_time=2)
        self.play(mandelbrot.animate.scale(1.5).move_to([-0.75,0.1,0]), run_time=8, rate_func=linear)
        self.wait(2)
        self.play(FadeOut(mandelbrot, scale=0.8), run_time=2)
        self.wait(0.5)
        # Helper to show static images
        def show(img_path, hold=5):
            img = ImageMobject(img_path).scale(2)
            self.play(FadeIn(img, scale=0.8), run_time=2)
            self.wait(hold)
            self.play(FadeOut(img, scale=0.8), run_time=2)
            self.wait(0.5)
        show(SIE_IMG)
        show(FERN_IMG)
        show(ELEPHANT_IMG)
        # Closing caption
        closing = Text("Fractals: simple rules, infinite complexity", font_size=30, color=GREEN, weight=BOLD, font="DejaVu Sans Mono")
        self.play(Write(closing), run_time=2)
        self.wait(4)
        self.play(FadeOut(closing), run_time=1.5)
```
The full script (including the four image‑generation functions) is stored in `~/fractals-animation/script.py`.

## How to Invoke the Skill
Run the skill via the Hermes CLI:
```
skill_manage(action='run', name='fractal-showcase-animation')
```
or follow the steps manually. The final video will be at:
`~/fractals-animation/media/videos/script/480p15/FractalsShowcase_with_music.mp4`.

---
**Version**: 1.0 (created 2026‑04‑14)
**Author**: Hermes (Hermi)
**Maintainer**: you (the user) – feel free to adjust image parameters, replace the background tone, or extend the scene with more fractals.
