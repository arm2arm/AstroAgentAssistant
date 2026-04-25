---
name: fractal-preference-mandelbrot-elephant
title: Preference – Mandelbrot → Elephant Valley only
description: |
  When the user asks for a fractal showcase, they want a video that shows ONLY a Mandelbrot zoom transitioning to the Elephant's Valley image. The transition should use a very small scaling factor (~1e-7). No other fractals, titles, or captions should be included. Future requests for fractal videos should honor this minimal‑content, single‑focus style.
---
## Steps
1. Load a Mandelbrot fractal visualisation (Manim).
2. Apply a zoom that ends at scale ≈ 0.0000001 (1e‑7).
3. Fade into the Elephant Valley image (512×512, jet colormap) centred.
4. Keep the video duration short (~10‑15 s) and sync with any requested audio.

## Pitfalls
- Do not render additional fractals (Seahorse, Sierpinski, etc.).
- Ensure the scaling factor is applied correctly; otherwise the Mandelbrot may disappear too early.
- Keep the Elephant image centred throughout the zoom.

## Verification
- Play the resulting MP4 and confirm that the only visible content is a Mandelbrot zoom smoothly transitioning into the Elephant Valley image.
- No extra titles, captions, or other fractal scenes should appear.
