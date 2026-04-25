---
name: manim-educational-animation
description: "Creating clean, non-overlapping Manim animations for educational explainers (Gymnasium/school level). Avoids text overlap bugs, guides pacing, and structures single-scene vs multi-scene approaches."
version: 1.0.0
---

# Manim Educational Animation — Best Practices

## Core Lesson Learned (from trial & error)

The #1 bug in educational Manim animations: **old text stays visible while new text is written over it**.
The root cause: Manim renders animations in parallel. `Write` and `FadeOut` in the same `self.play()` overlap.

### The Fix: Step Group Pattern

```python
# Each derivation step: Write → Wait → Group → FadeOut → wait(0.5) → Next
s1_lbl = Text("Schritt 1: Variablen trennen", ...)
s1_eq  = MathTex(r"\frac{dT}{T-20} = -k\,dt", ...)
self.play(Write(s1_lbl), Write(s1_eq), run_time=2.0)
self.wait(3.0)

# CRITICAL: group everything from step 1, then remove completely
s1_grp = VGroup(s1_lbl, s1_eq)
self.play(FadeOut(s1_grp), run_time=1.2)
self.wait(0.5)   # Screen must clear before next Write

# Now screen is clean — write step 2
s2_lbl = Text("Schritt 2: Integrieren", ...)
s2_eq  = MathTex(r"\ln|T-20| = -kt + C", ...)
self.play(Write(s2_lbl), Write(s2_eq), run_time=2.0)
```

**Why wait(0.5)**: Manim's animation queue needs a frame gap to clear the old mobject.
Without it, the next `Write` starts before `FadeOut` finishes.

**Why not ReplacementTransform**: It can leave LaTeX artifacts and bounding-box ghosts.
`FadeOut` of a `VGroup` is reliable.

### Consistent Positioning

All derivation steps should use the same anchor position — otherwise they drift:

```python
# All step labels at the same Y
s1_lbl = Text("Schritt 1: ...", ...).to_edge(LEFT, buff=0.8).shift(DOWN * 2.0)
s2_lbl = Text("Schritt 2: ...", ...).to_edge(LEFT, buff=0.8).shift(DOWN * 2.0)

# All step equations directly below their label
eq.next_to(s1_lbl, DOWN, buff=0.5)
```

## Single-Scene vs Multi-Scene

### Single-scene (one `class` with `_teilN()` methods)
- **Best for**: focused topic, 1-2 minute explainers, school material
- **Pros**: no stitching needed, easier to avoid overlap, simpler code
- **Cons**: long render time for one scene
- **Target**: ~60 animations, ~2 min for a complete topic

### Multi-scene (stitched)
- **Best for**: 5+ min videos, modular content, different visual layouts per section
- **Pros**: scenes render in parallel, each scene has its own visual identity
- **Cons**: more complex pipeline, overlap bugs harder to track across scenes
- **Target**: ~15 animations per scene, ~15 sec/scene

## Pacing for Educational Content

| Audience | Target length | Animations | Per-step wait |
|---|---|---|---|
| Gymnasium/School (Klasse 11) | 1.5–2.5 min | ~60–80 | 2–3 sec |
| University | 3–5 min | ~80–120 | 1.5–2 sec |
| General public | 5–8 min | ~120–200 | 1–1.5 sec |

## Color Palette (Dark Background)

```python
BG      = "#0D1117"   # dark background
BLUE    = "#58C4DD"   # main equations, titles
GREEN   = "#83C167"   # solutions, positive results
YELLOW  = "#FFFF00"   # highlights, key values
WHITE   = "#EAEAEA"   # body text
DIM     = "#7A8599"   # axes, labels, secondary text
RED     = "#FF6B6B"   # negative slopes, warnings
PURPLE  = "#C792EA"   # step indicators (Schritt 1, 2, 3)
MONO    = "DejaVu Sans Mono"  # font for ALL text
```

## Common Bugs

| Bug | Cause | Fix |
|---|---|---|
| Text overlaps | `FadeOut` + `Write` in same `play()` | Add `wait(0.5)` after every `FadeOut` |
| Steps drift vertically | No consistent anchor position | All steps use same `.shift(DOWN * 2.0)` |
| LaTeX artifacts | `ReplacementTransform` on MathTex | Use `FadeOut` + `Write` instead |
| Row-by-row reveals too slow | 6+ reveals per field × 0.2s each | Use `Create(pfeile)` for the whole group at once |
| 9-part video too long | Too many scenes, too much explanation | Target 5 parts max, 2 min total |
| 199 animations for 2 min | Too many `wait()` and small reveals | Combine into fewer, bigger animations |
| `log(x, base)` not defined | Manim has no built-in `log` function | Use `np.log(x) / np.log(base)` with `import numpy as np` |
| `NameError: name 'log' not defined` | Same as above — `log` from math module not available | Same fix: `np.log(x) / np.log(base)` |

## Rendering

```bash
# Draft (iterate fast)
manim -ql script.py SceneName

# Production
manim -qh script.py SceneName

# Preview frame
manim -ql --format=png -s script.py SceneName

# Stitch scenes
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy final.mp4
```