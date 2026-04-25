---
name: manim-telegram-animation
description: "Guide to creating concise educational animations with Manim, handling common errors, rendering in low‑resolution, and delivering the final MP4 via Telegram (including ffmpeg concat handling)."
version: 1.0.0
---

# Purpose
This skill captures the workflow we used to produce a short 4MOST spectrograph animation for an 11th‑grade physics class and deliver it over Telegram.
It is useful whenever you need a quick, low‑resolution Manim animation that can be sent as a single media file.

# Steps
1. **Write a minimal Manim script**
   * Use `Create` or `Write` instead of deprecated `ShowCreation`.
   * Prefer `--renderer=cairo` (software rendering) for headless environments.
   * Keep the scene simple to avoid long render times.
2. **Render in low quality**
   ```bash
   manim -ql --renderer=cairo path/to/script.py SceneName
   ```
   This produces a 480p15 video in `~/media/videos/.../partial_movie_files/SceneName/`.
3. **Locate the rendered MP4**
   ```bash
   find ~/media/videos -type f -name "*.mp4"
   ```
4. **If the animation was split into multiple partial files, concatenate them**
   * Generate a concat list:
   ```bash
   find <directory> -name "*.mp4" | sort | while read f; do echo "file '$f'"; done > /tmp/concat.txt
   ```
   * Run ffmpeg:
   ```bash
   ffmpeg -y -f concat -safe 0 -i /tmp/concat.txt -c copy /tmp/final_animation.mp4
   ```
   * Ensure the concat file contains lines of the form `file '/full/path.mp4'` (no empty lines).
5. **Send the resulting MP4 via Telegram**
   * Use the assistant’s `MEDIA:` prefix with the absolute path, e.g.
   ```
   MEDIA:/tmp/final_animation.mp4
   ```
   Telegram will deliver it as a video bubble.

# Common Pitfalls & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| `NameError: ShowCreation not defined` | Old animation call. | Replace with `Create` or `Write`.
| `Invalid value for '--renderer': 'software'` | Wrong renderer name. | Use `cairo` or `opengl`.
| ffmpeg concat error `Line 1: string required` | Empty or malformed concat file. | Generate the list with the exact `file 'path'` format, no stray quotes.
| Long render times / timeouts | Complex scene or high resolution. | Simplify the scene, use `-ql` (quick low quality) and limit resolution.
| Video not sent (Telegram shows nothing) | File not found at the path given. | Verify the file exists (`ls -lh /path/to/file.mp4`). Use the absolute path.

# Tips for Telegram Delivery
- Keep the final file under ~20 MB for reliable delivery.
- Use 480p15 or 720p30 to balance size and clarity.
- If the file is larger, consider further down‑sampling with ffmpeg:
  ```bash
  ffmpeg -i input.mp4 -vf scale=640:-2 -b:v 500k output.mp4
  ```

# Example
Below is a minimal script we used (saved as `spectrograph_demo.py`):
```python
from manim import *
class SpectrographDemo(Scene):
    def construct(self):
        self.camera.background_color = '#0D1117'
        title = Text('4MOST Spectrograph', font='DejaVu Sans Mono', color=WHITE).scale(0.8).to_edge(UP)
        self.play(Write(title))
        star = Dot(radius=0.12, color=YELLOW).shift(LEFT*4)
        self.play(FadeIn(star))
        beam = Rectangle(height=0.07, width=2, color=YELLOW, fill_opacity=0.8).next_to(star, RIGHT)
        self.play(Create(beam))
        slit = Rectangle(height=0.3, width=0.04, color=WHITE, fill_opacity=0.6).next_to(beam, RIGHT)
        self.play(FadeIn(slit))
        grating = VGroup(*[Line(UP, DOWN, color=PURPLE) for _ in range(8)])
        grating.arrange(RIGHT, buff=0.05).next_to(slit, RIGHT, buff=0.4)
        self.play(FadeIn(grating))
        cols = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]
        rays = VGroup()
        for i, c in enumerate(cols):
            ray = Arrow(start=grating.get_center(), end=grating.get_center() + RIGHT*2 + UP*(i-2)*0.3, color=c, tip_length=0.12)
            rays.add(ray)
        self.play(LaggedStartMap(GrowArrow, rays, lag_ratio=0.2))
        self.wait(0.5)
        self.play(FadeOut(VGroup(star, beam, slit, grating, rays)), run_time=1)
        self.play(FadeOut(title), run_time=0.8)
        self.wait(0.2)
```
Render with:
```bash
manim -ql --renderer=cairo spectrograph_demo.py SpectrographDemo
```
Then locate the MP4 and send it via `MEDIA:/full/path.mp4`.

# References
- Manim documentation: https://docs.manim.community
- ffmpeg concat demuxer: https://ffmpeg.org/ffmpeg-formats.html#concat

---
