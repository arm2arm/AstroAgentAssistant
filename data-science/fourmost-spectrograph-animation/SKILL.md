---
name: fourmost-spectrograph-animation
title: 4MOST Spectrograph Animation (Manim)
description: >
  Generates a 60-90s educational animation of the 4MOST spectrograph on the VISTA 4-m telescope
  using Manim Community Edition. Follows a schematic-first workflow: static matplotlib plot
  for review, then Manim animation. Includes tilting-spine fibres, three spectrographs (HRS/LRS),
  optical train, and science output.
category: data-science
triggers:
  - "4most animation"
  - "4most manim"
  - "4most spectrograph animation"
---

## Workflow

**Step 1 — Schematic first.** Create a static matplotlib multi-panel figure so the user can review and approve the visual design before committing to animation time.

**Step 2 — Manim animation.** Once the schematic is approved, generate the full Manim script and render.

## Step 1 — Schematic (matplotlib)

### Colours
```python
BG       = "#0D1117"   # dark background
BLUE     = "#58C4DD"
GREEN    = "#83C167"
YELLOW   = "#FFFF00"
ORANGE   = "#F5A623"
WHITE    = "#E6EDF3"
GRAY     = "#8B949E"
```

### Panels (6 total)
A. VISTA dome + 4MOST instrument box at Paranal
B. Wide field cone (≈2.5°) with stars/galaxies
C. Curved focal surface + tilting-spine fibres (2436 fibres)
D. Fibres → 3 spectrographs: HRS (812 fibres) + LRS-1/LRS-2 (1624 fibres total)
E. LRS optical train: slit → collimator → dichroics → VPH gratings → CCDs
F. Spectral grid → science: element lines, velocity shifts, Milky Way spiral

### Rendering
```bash
python3 /home/hermes/4most_schematic.py
# Output: /home/hermes/4most_schematic.png
```

## Step 2 — Manim Animation

### Technical Facts to Respect
- Mounted on VISTA 4-m telescope at ESO Paranal
- Field of view: ≈2.5° diameter at Cassegrain focus
- 2436 science fibres in tilting-spine positioner on curved focal surface
- 3 spectrographs via fibre bundles: HRS (812 fibres) + 2× LRS (1624 total)
- Each spectrograph: 3 wavelength channels (blue/green/red) split by dichroics, VPH gratings, large CCDs

### Colour Palette (dark BG style)
```python
BG     = "#0D1117"
BLUE   = "#58C4DD"
GREEN  = "#83C167"
YELLOW = "#FFFF00"
ORANGE = "#F5A623"
WHITE  = "#E6EDF3"
GRAY   = "#8B949E"
REDB   = "#FF6B6B"
```

### 6 Visual Sequences
1. **VISTA + 4MOST** — dome, slit glow, instrument box, title overlay
2. **Wide field** — cone lines from telescope to sky, random stars/galaxies
3. **Tilting-spine fibres** — curved Arc for focal surface, 16 fibre tip dots + spine lines, one spine tilting to a star
4. **Three spectrographs** — focal plane bar → 3 cables → HRS / LRS-1 / LRS-2 boxes
5. **LRS optical train** — slit dots → collimator circle → dichroics → VPH gratings → CCDs → rainbow dispersion fans
6. **Science output** — spectrum grid → element/velocity labels → final title

### Rendering
```bash
# Low-quality preview first
cd /home/hermes
manim -ql --renderer=cairo -r 1280,720 4most_animation.py FourMOST_Full

# Concatenate partial MP4 files
OUT_DIR=$(find /home/hermes/media/videos/4most_animation -name "partial_movie_files" -type d)
SCENE="FourMOST_Full"
PARTIAL=$(find "$OUT_DIR" -name "*.mp4" | grep "$SCENE" | sort)
echo "$PARTIAL" | awk '{print "file '"'"'" $0 "'"'"'"}' > concat.txt
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy /home/hermes/4most_animation_final.mp4

# High-quality final render (run in background)
manim -qh --renderer=cairo -r 1920,1080 4most_animation.py FourMOST_Full
```

## Pitfalls & Gotchas

- **No `python` binary** — always use `python3`
- **`next_section()` calls** require no setup but produce no visible effect unless using a notebook renderer
- **`FadeOut` + `self.remove`** — when fading out a `VGroup` that includes dynamically added individual mobjects (e.g. stars from `make_stars()`), fade out the VGroup first, then call `self.remove()` separately on individual mobjects
- **`Line` not `Arrow`** — use `Line` for static rays to avoid `VMobject.scale()` errors
- **Hex colour parsing** — Manim CE handles hex fine; don't mix with named constants carelessly
- **Background renders** — use `terminal(background=true, notify_on_complete=true)` for >60s renders
- **Partial files** — Manim splits long scenes; always concatenate with `ffmpeg` after render
- **Old partial files** — check `find ... -newer script.py` to find recently generated files

## Verification
Check final output:
```bash
ls -la /home/hermes/4most_animation_final.mp4
ffprobe /home/hermes/4most_animation_final.mp4 2>&1 | head -10
```