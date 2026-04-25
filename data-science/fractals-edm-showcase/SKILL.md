---
name: fractals-edm-showcase
description: Create a high‑energy fractal showcase video with a synthetic EDM soundtrack, including custom Seahorse and Elephant‑jet visuals, a slow zoom, and final audio‑video merge.
version: 1.0
author: Hermes Agent
---

# Purpose
This skill automates the end‑to‑end pipeline for a 55‑second Manim animation that displays several fractals (Mandelbrot, Sierpinski, Barnsley fern, Seahorse Valley, Elephant Valley) and synchronises it with a fast, rock‑inspired EDM track generated entirely in Python.

# Prerequisites
- Python 3.11 with a virtual environment containing `manim`, `numpy`, `matplotlib`, `scipy`, `Pillow`, and `ffmpeg` in the system PATH.
- The project directory `~/fractals-animation/` (created beforehand).
- Sufficient RAM/VRAM for the chosen Manim render quality (480p15 for drafts, 1080p60 for HQ).

# Step‑by‑step Procedure

## 1️⃣ Generate the synthetic EDM track
1. Create `~/fractals-animation/audio/generate_edm_track.py` with the following logic (excerpt):
   - Set `BPM = 140` (fast, rocking).
   - Build four tracks: kick, snare, hi‑hat (16th‑note pattern), synth lead.
   - Apply an exponential decay envelope to the kick, white‑noise burst for snare, short square‑wave bursts for hi‑hat.
   - Add a side‑chain‑style ducking envelope on the synth lead triggered by each kick.
   - Add a low‑frequency LFO wobble to the synth bass for “rock” feel.
   - Mix to a stereo NumPy array, write to `edm_fast.wav` (44.1 kHz, 16‑bit).
2. Convert to AAC for MP4 muxing:
   ```bash
   ffmpeg -y -i edm_fast.wav -c:a aac -b:a 192k edm_fast.aac
   ```
3. Trim to exactly 55 seconds (matches video length) to avoid padding clicks:
   ```bash
   ffmpeg -y -i edm_fast.aac -ss 0 -t 55 -c copy edm_fast_trimmed.aac
   ```

## 2️⃣ Add custom fractal image helpers
Edit `~/fractals-animation/script.py`:
- Insert **`save_seahorse`**: uses a polar parametric equation to produce a magenta point‑cloud PNG.
- Insert **`save_elephant_jet`**: loads the existing `barnsley_elephant.png`, converts to greyscale, resizes to 512×512, applies Matplotlib’s *jet* colormap, and saves `elephant_jet.png`.
- Ensure both helpers are called only if their output files do not already exist (caching).

## 3️⃣ Update the Manim scene
In the `FractalsShowcase` class, replace the original elephant block with:
```python
elephant = ImageMobject(ELEPHANT_JET_IMG).scale(2.0)
self.play(FadeIn(elephant, scale=0.8), run_time=2.0)
# Slow zoom out over ~30 s while staying centred
self.play(elephant.animate.scale(0.5).move_to(ORIGIN),
          run_time=30.0, rate_func=linear)
self.wait(2.0)
self.play(FadeOut(elephant, scale=0.8), run_time=2.0)
self.wait(0.5)
```
- Insert a call to `show(SEAHORSE_IMG, duration=5)` before the elephant block if you want the Seahorse displayed.
- Keep the “clear‑before‑next” caption policy (no overlapping text).

## 4️⃣ Render the draft video
```bash
source ~/.venvs/manim/bin/activate
manim -ql ~/fractals-animation/script.py FractalsShowcase
# Output will appear at:
# ~/fractals-animation/media/videos/script/480p15/FractalsShowcase.mp4
```
If you need a faster preview, you can reduce the camera `frame_width` or lower the DPI inside the image‑saving helpers.

## 5️⃣ Merge audio & video
```bash
ffmpeg -y -i ~/fractals-animation/media/videos/script/480p15/FractalsShowcase.mp4 \
       -i ~/fractals-animation/audio/edm_fast_trimmed.aac \
       -c:v copy -c:a aac -b:a 192k -filter:a "volume=0.9" \
       ~/fractals-animation/media/videos/script/480p15/FractalsShowcase_with_EDM_fast.mp4
```
Verify that the resulting file plays for exactly ~55 s and that the beat lines up with the zoom.

## 6️⃣ Optional high‑quality render
After user approval of the draft:
```bash
manim -qh ~/fractals-animation/script.py FractalsShowcase
# HQ video will be stored under media/videos/script/1080p60/
ffmpeg -y -i ~/fractals-animation/media/videos/script/1080p60/FractalsShowcase.mp4 \
       -i ~/fractals-animation/audio/edm_fast_trimmed.aac \
       -c:v copy -c:a aac -b:a 192k \
       ~/fractals-animation/media/videos/script/1080p60/FractalsShowcase_with_EDM_fast_HQ.mp4
```

# Pitfalls & Work‑arounds
- **Memory blow‑up**: Rendering at 1080p60 with many high‑resolution PNGs can exceed RAM. Reduce the number of points in `save_seahorse` (e.g., `points=100000`).
- **Audio click at cut‑point**: Always use the `-c copy` trim method; never re‑encode a trimmed segment, otherwise a tiny click may appear.
- **Zoom speed mismatch**: The `run_time` for the zoom should be roughly the remaining video duration after previous sections. Adjust `run_time` if you add/remove other clips.
- **FFmpeg version**: Ensure you have FFmpeg ≥ 4.4; older versions mishandle AAC‑in‑MP4 muxing.

# Verification Checklist
- [ ] `edm_fast_trimmed.aac` is exactly 55 seconds (`ffprobe` shows `duration=55.00`).
- [ ] Draft video (`FractalsShowcase.mp4`) plays without stalls and shows Seahorse and Elephant‑jet centred.
- [ ] Final merged video file size ≤ 2 MB (draft) and ≤ 10 MB (HQ).
- [ ] Audio is audible and sync‑locked with the elephant zoom (beat hits on zoom milestones).

# References
- Manim documentation: https://docs.manim.community/
- FFmpeg audio‑video merge guide: https://trac.ffmpeg.org/wiki/Concat
- Simple EDM synthesis example (public domain): https://github.com/karpathy/nnf-synth

---

**End of skill**