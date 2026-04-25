---
name: galaxy-formation-animation
description: Create a concise Manim animation explaining galaxy formation for 11th‑grade students. Includes best‑practice steps, common pitfalls, and reusable code snippets.
---
## Overview
This skill outlines a reproducible workflow for generating a ~1‑2 min Manim animation that covers:
1. Early‑Universe density fluctuations
2. Dark‑matter halo collapse
3. Gas cooling & star formation
4. Mergers → elliptical vs spiral galaxies
5. Summary of key take‑aways

The animation uses **clean transitions** – each textual block is placed in a `VGroup` and fully `FadeOut` before the next appears, preventing overlapping captions.

## Prerequisites
- Python 3.12+ with Manim Community Edition (`pip install manim`).
- A virtual environment (e.g., `~/.venvs/manim`).
- `numpy` for random positioning.

## Common Pitfalls & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| `ValueError: operands could not be broadcast together with shapes (2,) (3,)` | `move_to` called with a 2‑D NumPy array. Manim expects a 3‑D vector. | Use `np.append(np.random.rand(2)*scale‑offset, 0)` or `np.array([x, y, 0])` for all `move_to` calls. |
| Overlapping text between steps | Not clearing previous text groups. | Wrap each step’s text and graphics in a `VGroup` (e.g., `step = VGroup(title, caption)`) and `self.play(FadeOut(step))` before starting the next. |
| Long render times for drafts | Using high‑quality settings unintentionally. | Render drafts with `-ql` (quick low‑res) and only use `-qh` for final export. |

## Template Script (`script.py`)
```python
"""
Galaxy Formation – Simple Manim Explainer
Target: ~1‑2 min, ~70 animations, clean transitions.
"""
from manim import *
import numpy as np

# Colour palette (dark‑theme friendly)
BG = "#0D1117"
BLUE = "#58C4DD"
GREEN = "#83C167"
YELLOW = "#FFFF00"
WHITE = "#EAEAEA"
DIM = "#7A8599"
RED = "#FF6B6B"
PURPLE = "#C792EA"
ORANGE = "#FFB347"
MONO = "DejaVu Sans Mono"

class GalaxyFormation(Scene):
    def construct(self):
        self.camera.background_color = BG
        self._part1_fluctuations()
        self._part2_halo_collapse()
        self._part3_gas_cooling_star_formation()
        self._part4_mergers_and_morphology()
        self._part5_summary()

    # -----------------------------------------------------------------
    def _part1_fluctuations(self):
        title = Text("Galaxy Formation", font_size=56, color=BLUE, weight=BOLD, font=MONO)
        self.play(Write(title), run_time=1.5)
        self.wait(1.5)
        # background dots (need 3‑D coordinates)
        dots = VGroup(*[Dot(radius=0.03, color=WHITE).move_to(np.append(np.random.rand(2)*6-3, 0)) for _ in range(150)])
        self.play(Create(dots), run_time=2.0)
        self.wait(1.0)
        overdense = VGroup(*[dots[i] for i in [12,45,78,101]])
        for d in overdense:
            self.play(d.animate.set_color(YELLOW), run_time=0.5)
        cap = Text("Tiny density fluctuations after the Big Bang", font_size=24, color=YELLOW, font=MONO)
        cap.to_edge(DOWN, buff=0.8)
        self.play(Write(cap), run_time=1.5)
        self.wait(2.0)
        self.play(FadeOut(VGroup(title, dots, overdense, cap)), run_time=1.5)
        self.wait(0.5)

    # -----------------------------------------------------------------
    def _part2_halo_collapse(self):
        title = Text("Dark‑Matter Halo Collapse", font_size=44, color=BLUE, weight=BOLD, font=MONO)
        self.play(Write(title), run_time=1.5)
        halo = Circle(radius=3, color=PURPLE, stroke_width=2).set_opacity(0.2)
        self.play(Create(halo), run_time=1.5)
        self.play(Transform(halo, Circle(radius=3, color=PURPLE, stroke_width=4)), run_time=2.0)
        self.play(halo.animate.set_width(1.0), run_time=2.0)
        particles = VGroup(*[Dot(radius=0.06, color=PURPLE).move_to(np.append(np.random.rand(2)*2-1, 0)) for _ in range(30)])
        self.play(FadeIn(particles, scale=0.5), run_time=1.5)
        cap = Text("Overdense region collapses → dark‑matter halo", font_size=24, color=YELLOW, font=MONO)
        cap.to_edge(DOWN, buff=0.7)
        self.play(Write(cap), run_time=1.5)
        self.wait(2.0)
        self.play(FadeOut(VGroup(title, halo, particles, cap)), run_time=1.5)
        self.wait(0.5)

    # -----------------------------------------------------------------
    def _part3_gas_cooling_star_formation(self):
        title = Text("Gas Cooling & Star Formation", font_size=44, color=BLUE, weight=BOLD, font=MONO)
        self.play(Write(title), run_time=1.5)
        halo = Circle(radius=2.5, color=PURPLE, stroke_width=2).set_opacity(0.15)
        self.play(Create(halo), run_time=1.0)
        gas = Circle(radius=2.2, color=BLUE).set_opacity(0.2)
        self.play(Create(gas), run_time=1.5)
        self.play(gas.animate.set_width(1.5).set_opacity(0.4), run_time=2.5)
        stars = VGroup(*[Dot(radius=0.08, color=YELLOW).move_to(np.append(np.random.rand(2)*0.8-0.4, 0)) for _ in range(25)])
        self.play(FadeIn(stars, scale=0.5), run_time=1.5)
        cap = Text("Gas radiates, loses energy, collapses → stars form", font_size=22, color=YELLOW, font=MONO)
        cap.to_edge(DOWN, buff=0.7)
        self.play(Write(cap), run_time=1.5)
        self.wait(2.0)
        self.play(FadeOut(VGroup(title, halo, gas, stars, cap)), run_time=1.5)
        self.wait(0.5)

    # -----------------------------------------------------------------
    def _part4_mergers_and_morphology(self):
        title = Text("Mergers & Morphology", font_size=44, color=BLUE, weight=BOLD, font=MONO)
        self.play(Write(title), run_time=1.5)
        def disk(radius, centre, arm_angle):
            d = Circle(radius=radius, color=BLUE).move_to(centre)
            arms = VGroup()
            for a in np.linspace(0, 2*np.pi, 4, endpoint=False):
                arm = Arc(radius*1.2, a+arm_angle, a+arm_angle+0.6, color=WHITE, stroke_width=2)
                arm.move_to(centre)
                arms.add(arm)
            return VGroup(d, arms)
        gal1 = disk(1.2, LEFT*2, 0)
        gal2 = disk(1.2, RIGHT*2, 0.3)
        self.play(FadeIn(gal1, scale=0.7), FadeIn(gal2, scale=0.7), run_time=2.0)
        arrow1 = Arrow(gal1.get_center(), ORIGIN, color=RED, buff=0.2)
        arrow2 = Arrow(gal2.get_center(), ORIGIN, color=RED, buff=0.2)
        self.play(Create(arrow1), Create(arrow2), run_time=1.0)
        self.play(gal1.animate.move_to(ORIGIN), gal2.animate.move_to(ORIGIN), run_time=2.0)
        self.play(gal1.animate.scale(1.4), gal2.animate.scale(1.4), run_time=1.5)
        ellipse = Ellipse(width=2.8, height=2.2, color=ORANGE).set_opacity(0.6)
        self.play(FadeIn(ellipse), run_time=1.5)
        cap1 = Text("Major merger → elliptical galaxy", font_size=22, color=YELLOW, font=MONO)
        cap1.to_edge(DOWN, buff=0.6)
        self.play(Write(cap1), run_time=1.5)
        self.wait(2.0)
        self.play(FadeOut(VGroup(gal1, gal2, arrow1, arrow2, ellipse, cap1)), run_time=1.0)
        # Spiral outcome
        disk_big = disk(1.5, ORIGIN, 0)
        self.play(FadeIn(disk_big, scale=0.8), run_time=1.5)
        cap2 = Text("Gentle accretion → spiral galaxy", font_size=22, color=YELLOW, font=MONO)
        cap2.to_edge(DOWN, buff=0.6)
        self.play(Write(cap2), run_time=1.5)
        self.play(FadeOut(VGroup(title, disk_big, cap2)), run_time=1.0)
        self.wait(0.5)

    # -----------------------------------------------------------------
    def _part5_summary(self):
        title = Text("Key Take‑aways", font_size=48, color=BLUE, weight=BOLD, font=MONO)
        self.play(Write(title), run_time=1.5)
        points = [
            ("1.", "Tiny density fluctuations after the Big Bang"),
            ("2.", "Overdensities collapse into dark‑matter halos"),
            ("3.", "Gas cools inside halos, forming stars"),
            ("4.", "Mergers → ellipticals; gentle accretion → spirals"),
            ("5.", "Galaxy evolution is hierarchical and ongoing"),
        ]
        y = 0.8
        for num, txt in points:
            n = Text(num, font_size=28, color=YELLOW, font=MONO, weight=BOLD)
            t = Text(txt, font_size=24, color=WHITE, font=MONO).next_to(n, RIGHT, buff=0.4)
            line = VGroup(n, t).to_edge(LEFT, buff=1.0).shift(DOWN * y)
            self.play(Write(line), run_time=1.2)
            self.wait(0.5)
            y -= 0.6
        closing = Text("From fluctuations to the magnificent galaxies we see today!", font_size=28, color=GREEN, font=MONO)
        closing.to_edge(DOWN, buff=0.8)
        self.play(Write(closing), run_time=1.5)
        self.wait(3.0)
        self.play(FadeOut(VGroup(title, closing)), run_time=1.5)
```

## Execution Steps
1. Save the script as `script.py` inside a project folder (e.g., `~/galaxy-animation/`).
2. Render a quick draft:
   ```bash
   cd ~/galaxy-animation
   ~/.venvs/manim/bin/manim -ql script.py GalaxyFormation
   ```
3. For the final high‑resolution version:
   ```bash
   ~/.venvs/manim/bin/manim -qh script.py GalaxyFormation
   ```
   The output will be in `media/videos/script/480p15/` (draft) and `media/videos/script/1080p60/` (HQ).

## Tips & Extensions
- **Adjust speed**: tweak `run_time` values for each `self.play`.
- **Add voice‑over**: export the MP4 and combine with an audio track using `ffmpeg`.
- **Reuse components**: the `disk` helper function can generate any rotating disk galaxy.
- **Export frames**: `self.add(frame)` inside any step to capture PNGs for slides.

---
**Version**: 1.0 – first release after successful trial‑and‑error fixing of 2‑D coordinate errors.
