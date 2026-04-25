---
name: fourmost-educational-animation
description: "Create a short Manim animation that explains the 4MOST spectrograph for 11th‑grade physics classes. Includes installation, script writing, rendering, common pitfalls, and fallback to external video."
version: 1.0.0
---

# Goal
Generate a concise, visually clear animation of the 4MOST multi‑object spectrograph suitable for a high‑school physics lesson.

# Prerequisites
- Python 3.11+ installed.
- Ability to install Python packages (pip).
- Optional: graphical environment for rendering; otherwise use background rendering.

# Step‑by‑step Procedure
1. **Create a working directory**
   ```bash
   mkdir -p ~/animations && cd ~/animations
   ```
2. **Install Manim** (use `--break-system-packages` if the environment is externally managed)
   ```bash
   pip install manim --break-system-packages
   ```
3. **Write the animation script** (save as `fourmost_spectrograph.py`). Use `Create` instead of the deprecated `ShowCreation`. Example minimal script:
   ```python
   from manim import *

   class FourMOSTSpectrograph(Scene):
       def construct(self):
           self.camera.background_color = "#0D1117"
           title = Text("How the 4MOST Spectrograph Works", font="DejaVu Sans Mono", color=WHITE).scale(0.8).to_edge(UP)
           self.play(Write(title))
           # ... (add star, beam, tube, slit, collimator, grating, spectrum, fibres, modules, detectors) ...
           self.wait(1)
   ```
   Keep the script small (≈ 200‑250 lines) to avoid long render times.
4. **Render the animation**
   - Prefer a quick‑render flag for testing:
     ```bash
     manim -ql fourmost_spectrograph.py FourMOSTSpectrograph
     ```
   - For final quality use `-qh` (high quality) and run in background to avoid blocking the session:
     ```bash
     manim -qh fourmost_spectrograph.py FourMOSTSpectrograph &
     ```
   - Use the Hermes `terminal` tool with `background=true` and `notify_on_complete=true` to get notified when rendering finishes.
5. **Handle common errors**
   - `NameError: ShowCreation is not defined` → replace with `Create`.
   - Attribute errors from missing mobject properties often stem from mismatched Manim versions; ensure the script matches the installed Manim version (check `manim --version`).
   - If rendering times out or hangs, simplify the scene (fewer objects, use `Create`/`FadeIn` instead of complex transforms).
6. **Fallback**
   If local rendering is impossible (e.g., no display, strict time limits), provide an existing public video that covers the same material, such as:
   - YouTube: https://www.youtube.com/watch?v=7i97ZZNsdEM ("Exploring the Universe & the Future of Sky Observation • 4MOST")
   - ESO blog video: https://www.eso.org/public/blog/4most/
   Include the link in the final response.

# Pitfalls & Tips
- **Never mix `Write` and `FadeOut` in the same `self.play`** – it causes overlapping text (see `manim-educational-animation` skill). Insert a short `self.wait(0.5)` after a `FadeOut` before the next `Write`.
- **Use consistent positioning** (`.to_edge`, `.next_to`) to avoid drift.
- **Keep colour palette dark‑background friendly** (see colour constants in the skill). Adjust for classroom projectors if needed.
- **Render in background** to keep the interactive session responsive.
- **If the script fails to locate the file**, double‑check the path (`/home/hermes/animations/...`). Use `ls` or `read_file` to verify.

# Verification
- After rendering, the output video will be in `media/videos/.../FourMOSTSpectrograph.mp4`. Play it locally to confirm the sequence runs smoothly and fits within a 2‑minute classroom slot.
- Ensure the final video has no leftover objects (use a final `FadeOut` of the entire scene).

# References
- Manim Community Documentation: https://docs.manim.community/
- Existing `manim-educational-animation` skill for general best practices.

---
