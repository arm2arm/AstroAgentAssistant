---
name: manim-telegram-delivery
description: "Generate a Manim animation, extract a short preview, concatenate full‑resolution fragments, and deliver the MP4 directly via Telegram. Handles common rendering pitfalls (partial movie files, missing renderer options) and provides a workflow for producing both low‑res preview and high‑res final video."
version: 1.0.0
---

## Overview
This skill guides you through creating a Manim animation for educational purposes and sending the resulting video to the user on Telegram as a native file.
It covers:
1. Writing a simple Manim script.
2. Rendering a preview (low‑resolution, quick) and locating the generated MP4.
3. Rendering the full‑resolution version (1080p) — Manim auto‑combines partial files into a single MP4 in newer versions; ffmpeg concat is a fallback.
4. Sending the final MP4 (or a short preview) using the `MEDIA:` syntax.

The process is robust against common errors such as missing renderer flags or empty concat lists.

## Step‑by‑Step Procedure
### 1. Prepare the script
```python
# /home/hermes/animations/your_animation.py
from manim import *
import numpy as np

class MyScene(Scene):
    def construct(self):
        # ... your animation code ...
        self.play(Write(Text('Hello')))
        self.wait()
```
* Use `DejaVu Sans Mono` font for readability.
* Keep the scene short for preview (≈10 s) and longer for full version.
* **Always `import numpy as np`** — you'll need `np.log()`, `np.sin()`, etc.
  Manim does NOT provide `log(x, base)` — use `np.log(x) / np.log(base)` instead.
* Avoid mixed quotes in multi-line strings (`"..."` inside `"..."`) — use triple-quoted strings or escape properly.

### 2. Render a quick preview
```bash
manim -ql /home/hermes/animations/your_animation.py MyScene
```
* `-ql` → low quality (480p, 15 fps) – renders fast.
* The resulting file is placed under:
  `/home/hermes/media/videos/your_animation/480p15/partial_movie_files/MyScene/*.mp4`
* Grab the first file (or any) as a preview.

### 3. Render the full‑resolution version
```bash
manim -qh /home/hermes/animations/your_animation.py MyScene
```
* `-qh` → high quality (1080p, 60 fps).
* **Newer Manim**: auto‑combines partial files into `MyScene.mp4` in
  `/home/hermes/media/videos/your_animation/1080p60/MyScene.mp4`.
  → **Check for this file first — if it exists, skip steps 4–5.**
* If the combined file is missing, Manim produced only *partial* MP4s in:
  `/home/hermes/media/videos/your_animation/1080p60/partial_movie_files/MyScene/`

### 4. Build a concat list for ffmpeg (fallback only — skip if combined MP4 exists)
```bash
find /home/hermes/media/videos/your_animation/1080p60/partial_movie_files/MyScene \\\
    -type f -name '*.mp4' | sort | while read -r f; do
    printf "file '%s'\n" "$f"
done > /home/hermes/concat.txt
```
* Ensure each line starts with `file '` and ends with `'`.
* Do **not** leave blank lines – they cause `ffmpeg` "string required" errors.

### 5. Concatenate into a single MP4 (fallback only)
```bash
ffmpeg -y -f concat -safe 0 -i /home/hermes/concat.txt -c copy /home/hermes/your_animation_full.mp4
```
* `-c copy` preserves original encoding and is fast.
* If you get `Line 1: string required`, double‑check `concat.txt` (no empty entries).

### 6. Send via Telegram
In the final response, include:
```
MEDIA:/home/hermes/media/videos/your_animation/1080p60/MyScene.mp4
```
(or the fallback path from step 5).
* Telegram will render it as a video file.
* If the file is too large, fall back to the preview MP4 (the one from step 2).

## Pitfalls & Tips
* **Renderer flag** – Manim only accepts `cairo` or `opengl`. Do not use `software`.
* **Partial files** – they appear only after a successful high‑quality render; ensure the render finished (`process` status `exited` with exit_code 0) before checking for the combined MP4 or running ffmpeg concat.
* **Empty concat list** – occurs if the `find` command fails or the path is wrong. Verify with `cat /home/hermes/concat.txt`.
* **Telegram size limit** – keep the final MP4 under ~20 MB for smooth delivery. If larger, re‑render with `-ql` or cut the animation.
* **`log(x, base)` not defined** – Manim has no built-in `log` function. Use `np.log(x) / np.log(base)` with `import numpy as np`.
* **Mixed quotes in multi-line strings** – `"text with 'quotes'"` works, but `"text with \"nested \"\"\""` fails. Use triple-quoted strings or avoid inner quotes.
* **Check for auto-combined MP4** – newer Manim versions auto-combine partial files into `SceneName.mp4`. Check the output directory first before falling back to ffmpeg concat.

## Example Usage (as seen in conversation)
1. Created `4most_spectrograph_simple.py`.
2. Rendered low‑res preview → sent first clip.
3. Rendered 1080p fragments → built `concat1080.txt`.
4. Ran `ffmpeg -f concat …` – initial errors fixed by correcting the concat file format.
5. Sent the final `4most_spectrograph_full_1080p.mp4`.

## When to Apply
* Any request for a short animation preview **and** a longer high‑resolution version.
* When the user wants the video delivered directly in Telegram rather than a link.
* When you need to handle Manim’s fragmented output automatically.

---
