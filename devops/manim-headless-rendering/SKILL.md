---
name: manim-headless-rendering
description: "Guidelines for rendering Manim animations in a headless Linux environment (no GUI). Includes troubleshooting common errors, choosing correct renderer, managing long renders, and concatenating partial video files produced by Manim.
"
version: 1.0.0
---

# Overview
When running Manim on a server or CI environment without a display, the default OpenGL renderer may fail or hang. Use the `cairo` renderer, which works without an X server.

```bash
manim -qh --renderer=cairo path/to/script.py SceneName
```

If the animation is long, run it in the background to avoid the 600 s foreground timeout:

```bash
manim -qh --renderer=cairo path/to/script.py SceneName \
    --media_dir /tmp/manim_media \
    &> /tmp/manim.log &
```

You can also use the built‑in background mode:

```bash
manim -qh path/to/script.py SceneName --background --notify_on_complete
```

# Common Errors & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| `NameError: ShowCreation is not defined` | Script used `ShowCreation` which was removed in recent Manim versions. | Replace with `Create` (or `Write`/`FadeIn`). |
| `Invalid value for --renderer: software` | Wrong renderer name. | Use `cairo` or `opengl`.
| Process times out after 600 s | Foreground render exceeded limit. | Run in background with `notify_on_complete` or split animation into smaller scenes. |
| `ffmpeg concat file error: string required` | Concatenation list file had empty lines or missing quotes. | Generate the list with: `ls *.mp4 | sort | while read f; do echo "file '$f'"; done > concat.txt` and ensure no stray empty lines. |

# Managing Partial Movies
Manim writes each animation chunk as a separate *partial_movie_files* MP4. To combine them:
1. Locate the directory, e.g. `/home/hermes/media/videos/YourScene/480p15/partial_movie_files/YourScene/`.
2. Create a concat list:
   ```bash
   find . -name "*.mp4" | sort | while read f; do echo "file '$PWD/$f'"; done > /tmp/concat.txt
   ```
3. Run ffmpeg:
   ```bash
   ffmpeg -y -f concat -safe 0 -i /tmp/concat.txt -c copy output.mp4
   ```
   Ensure the `concat.txt` contains lines like `file '/full/path/video.mp4'` with no blank lines.

# Tips for Quick Render
- Use low resolution (`-ql`) for drafts, high (`-qh`) for final.
- Keep scene length under a minute; split longer videos into multiple Scene classes.
- Avoid heavy vector graphics; raster images load faster.
- Pre‑define colours and fonts globally to reduce object creation overhead.

# Example Minimal Script
```python
from manim import *

class Demo(Scene):
    def construct(self):
        self.camera.background_color = "#0D1117"
        txt = Text("4MOST", font="DejaVu Sans Mono", color=WHITE)
        self.play(Write(txt))
        self.wait(1)
```
Render with:
```
manim -qh --renderer=cairo demo.py Demo
```

# References
- Manim documentation: https://docs.manim.community/en/stable/
- Manim GitHub issues on headless rendering.
- FFmpeg concat demuxer docs.
---
