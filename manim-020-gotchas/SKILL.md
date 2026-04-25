---
name: manim-020-gotchas
title: Manim CE 0.20.1 Common Pitfalls
description: >-
  Gotchas and API changes specific to Manim Community Edition 0.20.1.
  Includes ImageMobject, animation names, and font handling.
author: Hermi
date: 2026-04-16
tags: [manim, animation, gotchas, 0.20]
---

## Overview

Common pitfalls discovered when building Manim animations with CE v0.20.1.
Prevents runtime errors during render.

## Pitfalls & Fixes

### 1. ImageMobject cannot go in VGroup

```python
# WRONG — raises TypeError
VGroup(title, ImageMobject("plot.png"), caption)

# CORRECT — use Group instead
Group(title, ImageMobject("plot.png"), caption)
```

`VGroup` only accepts `VMobject` subclasses. `ImageMobject` is a `PixelArtMobject`,
not a `VMobject`. Use `Group` (which accepts any `Mobject`) when mixing images with text/shapes.

### 2. `GrowIn` does not exist in 0.20.1

Available animation aliases for images:
- `FadeIn(mob)` — fade from transparent
- `FadeOut(mob)` — fade to transparent
- `GrowFromPoint(mob, point)` — grow from a specific point
- `GrowFromCenter(mob)` — grow from center

`GrowIn` was removed/renamed. Use `FadeIn` for image appearances.

### 3. Font name fallback

Manim 0.20.1 warns if a requested font is not installed. Common fallback:
```python
# Instead of font="Courier" (may warn)
font="DejaVu Sans Mono"  # usually available

# Or use default (no font= parameter, uses DejaVu Sans)
Text("Hello")  # Uses default sans-serif
```

### 4. `partial_movie_files` cache corruption

If a render crashes mid-way, the next render may use corrupted cached animations.
Fix: delete the specific partial file or the whole cache:
```bash
rm -rf media/videos/*/partial_movie_files/SCENE_NAME/
```

### 5. `run_time` vs `wait` for scene pacing

Use explicit `wait()` between animated sections instead of inflating `run_time`
on the last animation — `wait()` is more predictable and easier to debug timing:
```python
self.play(Write(text), run_time=2.0)
self.wait(2.0)  # clear separation of animation and reading time
```

### 6. Random state in animations

If using `np.random` in animation loops, seed it at the scene level:
```python
def construct(self):
    np.random.seed(42)  # reproducible star positions, etc.
```

### 7. `ParametricFunction` uses `t_range`, NOT `t_min`/`t_max`

```python
# WRONG — raises TypeError: Mobject.__init__() got an unexpected keyword argument 't_min'
ParametricFunction(
    lambda t: np.array([t, np.sin(t), 0]),
    t_min=-PI, t_max=PI, color=GREEN
)

# CORRECT — tuple of (min, max, step)
ParametricFunction(
    lambda t: np.array([t, np.sin(t), 0]),
    t_range=(-PI, PI, 0.05),
    color=GREEN
)
```

### 8. `MathTex` does NOT accept `font` or `font_size` parameters

```python
# WRONG — raises TypeError: Mobject.__init__() got an unexpected keyword argument 'font'
MathTex(r"\frac{a}{b}", font="DejaVu Sans Mono", font_size=30)

# CORRECT — use .scale() for sizing
formula = MathTex(r"\frac{a}{b}")
formula.scale(0.8)
```

`MathTex` inherits from SVG objects — it uses system LaTeX fonts. For custom fonts/size, use `Text()` instead.

### 9. `MathTex.get_part_by_tex()` often returns `None`

```python
# WRONG — may return None, then .set_color() crashes
eq.get_part_by_tex("sin(\\theta)").set_color(GREEN)
eq.get_part_by_tex("y").set_color(GREEN)

# CORRECT — use set_color_by_tex() which searches all submobjects
eq.set_color_by_tex("sin", GREEN)
eq.set_color_by_tex("y", GREEN)
eq.set_color_by_tex("r", YELLOW)
```

`get_part_by_tex()` looks for exact tex string matches in submobjects, which often fail because Manim splits the equation into many individual submobjects. `set_color_by_tex()` is more reliable.

### 10. `DOWN_RIGHT` does NOT exist in Manim 0.20.1

```python
# WRONG — raises NameError
Line(ORIGIN, DOWN_RIGHT * 2.5, color=DIM)

# CORRECT — compose from unit vectors
Line(ORIGIN, RIGHT * 2 - DOWN * 1.5, color=DIM)
```

Available direction shortcuts: `UP`, `DOWN`, `LEFT`, `RIGHT`, `UP_LEFT`, `UP_RIGHT`, `DOWN_LEFT`, `DOWN_RIGHT` — **NONE of these exist** in Manim CE. Always compose: `RIGHT * 2 - DOWN * 1.5`.

### 11. `run_time(...)` syntax error (function-call style)

```python
# WRONG — run_time is a keyword argument, not a function call
self.play(Create(mob), run_time(0.3))

# CORRECT — keyword argument
self.play(Create(mob), run_time=0.3)
```

Common typo from copying/manually editing. Always check `run_time=`, not `run_time(...)`.

### 12. `Text()` does NOT accept `font_weight` parameter

```python
# WRONG — raises TypeError: unexpected keyword argument 'font_weight'
Text("Hello", font_size=44, font_weight=8)

# CORRECT — no font_weight
Text("Hello", font_size=44)
```

Manim 0.20.1's `Text` class (Pango-based) does not support `font_weight`. For bold text, use `Text("Hello", font="DejaVu Sans Bold")` or just rely on default rendering.

### 13. `Arc` does NOT accept `start_position` parameter

```python
# WRONG — raises TypeError: unexpected keyword argument 'start_position'
Arc(radius=0.5, start_angle=0, angle=theta, start_position=LEFT * 3)

# CORRECT — use .add_updater() or .move_to() to position
arc = Arc(radius=0.5, start_angle=0, angle=theta)
arc.add_updater(lambda m: m.move_to(LEFT * 3))
# OR just create it at the right position after creation
```

The `start_position` parameter is not part of Manim CE's Arc API. Use `move_to()` or an updater to position.

### 14. Frame rate limits minimum `wait()` duration

```python
# At 15 FPS, self.wait(0.03) → Manim warns and uses 0.067s minimum
self.wait(0.03)  # WARNING: too short for current frame rate

# At 60 FPS (high quality render), self.wait(0.03) works fine
```

Low-quality draft renders (`-ql`) use 15 FPS, so `wait()` under ~0.067s gets silently extended. High-quality renders (`-qh`) use 60 FPS where 0.03s is fine. **Design animations assuming `-ql` pacing if you want draft renders to look correct.**

### 15. `MathTex` does NOT accept `color` in `.scale()`

```python
# WRONG — raises TypeError: unexpected keyword argument 'color'
MathTex("+", color=RED).scale(0.6, color=RED)

# CORRECT — set color in constructor OR use .set_color()
MathTex("+", color=RED).scale(0.6)
# OR
MathTex("+").scale(0.6).set_color(RED)
```

`.scale()` only accepts sizing arguments. Pass `color=` to the constructor, or call `.set_color()` after scaling.

### 16. `CYAN` does NOT exist in Manim 0.20.1

```python
# WRONG — raises NameError: name 'CYAN' is not defined
Text("minus", color=CYAN)

# CORRECT — use TEAL, TEAL_A..E, or PURE_CYAN
Text("minus", color=TEAL)
# OR
Text("minus", color=PURE_CYAN)
```

Check available color names with: `python3 -c "from manim import *; print(dir())" | tr ',' '\n' | grep -iE "cyan|teal|blue"`

### 17. Unicode minus `−` (U+2212) crashes `MathTex` LaTeX compilation

```python
# WRONG — raises ValueError: latex error converting to dvi
#          "! LaTeX Error: Unicode character − (U+2212) not set up for use with LaTeX."
MathTex(r"−", color=WHITE)

# CORRECT — use plain ASCII dash, or use Text() instead
MathTex(r"-", color=WHITE)
# OR
Text("-", color=WHITE)
```

`MathTex` goes through LaTeX which has no Unicode minus support. Use ASCII `"-"` in MathTex, or use `Text()` (Pango-based, no LaTeX) for arbitrary Unicode characters.

### 18. `Arrow` does NOT accept `tip_width_factor`

```python
# WRONG — raises TypeError: unexpected keyword argument 'tip_width_factor'
Arrow(start, end, tip_width_factor=0.4)

# CORRECT — use max_tip_length_to_length_ratio and stroke_width
Arrow(start, end, stroke_width=5, max_tip_length_to_length_ratio=0.3)
```

Check Arrow's signature: `python3 -c "from manim import Arrow; import inspect; print(inspect.signature(Arrow.__init__))"`
Relevant params: `stroke_width`, `buff`, `max_tip_length_to_length_ratio`, `max_stroke_width_to_length_ratio`.

## Verification Checklist

- [ ] `ImageMobject` in `Group`, not `VGroup`
- [ ] `FadeIn` instead of `GrowIn`
- [ ] Fonts exist on system (check with `fc-list | grep fontname`)
- [ ] Partial cache cleaned after any crash
- [ ] `wait()` calls between major sections
- [ ] `np.random.seed()` set for reproducible elements
- [ ] `color=` in constructor, NOT in `.scale()`
- [ ] `TEAL`/`PURE_CYAN` not `CYAN`
- [ ] ASCII `"-"` in `MathTex()`, use `Text()` for Unicode
- [ ] `max_tip_length_to_length_ratio` not `tip_width_factor` in `Arrow()`
- [ ] No `Polyline` — use `VGroup` of `Line` segments
- [ ] No `side_length` on `Triangle` — use `.scale()` after creation
- [ ] `VGroup()` already groups, no need to wrap again

## Additional Pitfalls

### 19. `Polyline` does NOT exist in Manim 0.20.1

```python
# WRONG — raises NameError: name 'Polyline' is not defined
Polyline(points, color=GREEN, stroke_width=4)

# CORRECT — use VGroup of Line segments
segments = VGroup()
for i in range(len(points)-1):
    segments.add(Line(points[i], points[i+1], color=GREEN, stroke_width=4))
```

For zigzag resistors or any polyline, build it from individual `Line` objects in a `VGroup`.

### 20. `Triangle(side_length=...)` is NOT supported

```python
# WRONG — raises TypeError: unexpected keyword argument 'side_length'
Triangle(side_length=0.3, color=RED)

# CORRECT — create and scale, or use Dot/regular polygon
Triangle().scale(0.15).set_color(RED)
# OR
Dot(radius=0.15, color=RED, fill_opacity=0.8)
```

`Triangle` (which is a `RegularPolygram`) only accepts `**kwargs` for styling. For triangles use `.scale()` after creation. For LED-like indicators, `Dot` is often simpler.

### 21. `VGroup` unpacking confusion

```python
# WRONG — VGroup already takes items, not unpacked list
wires = VGroup(L1, L2, L3, L4)
self.play(Create(v_group(*wires)))  # 'v_group' undefined, and * doesn't apply here

# CORRECT
wires = VGroup(L1, L2, L3, L4)
self.play(Create(wires))
```

`VGroup()` takes items directly as arguments. There is no `v_group()` — it's `VGroup`. And `wires` is already a single Mobject, so just pass `wires`, not `*wires`.

### 22. `Arrow` `stroke_width` affects both line and arrowhead

If you want a thick line but proportional arrowhead, use `stroke_width` together with `max_tip_length_to_length_ratio`. The `stroke_width` sets both the shaft and the arrowhead bar thickness.

### 23. `set_color_by_tex()` on a copy doesn't affect original

```python
# WRONG — modifying the copy doesn't highlight the original
formula_red = formula.copy()
formula_red.set_color_by_tex("V", RED)
# formula is still yellow!

# CORRECT — modify in place or re-render with the colored version
formula.set_color_by_tex("V", RED)
```

When highlighting parts of a MathTex, either call `set_color_by_tex()` on the original or use the copy for the entire animation replacing the original.

### 25. `tip_width_ratio` does NOT exist on `Arrow()`

```python
# WRONG — raises TypeError: unexpected keyword argument 'tip_width_ratio'
Arrow(start, end, tip_width_ratio=0.3)

# CORRECT — Arrow supports these tip-related params:
#   stroke_width, buff, tip_length, max_tip_length_to_length_ratio,
#   max_stroke_width_to_length_ratio
Arrow(start, end, stroke_width=4, max_tip_length_to_length_ratio=0.3)
```

`tip_width_ratio` is NOT a valid Arrow parameter in Manim CE. The closest alternatives are `max_tip_length_to_length_ratio` and `tip_length`. See also pitfall 18 (`tip_width_factor` also invalid).

### 26. Degenerate Arrow (start == end) crashes deep in numpy

```python
# WRONG — start and end are the same point, crashes with
#        ValueError: At least one array has zero dimension
line = DashedLine(ORIGIN, ORIGIN, color=DIM)
# OR
line = Arrow(P, P, color=DIM)  # P is any Mobject position

# CORRECT — ensure start != end
# Use a non-zero distance, or use a different mobject entirely
line = Line(ORIGIN, RIGHT * 0.1, color=DIM, stroke_width=1.5)
```

When start and end are identical, `Arrow.put_start_and_end_on()` calls `np.cross(zero_vector, zero_vector)` which raises. Even `DashedLine(ORIGIN, ORIGIN)` crashes. If you need a zero-length decorative element, use `Dot()` or a short `Line()` instead.

### 27. `FadeOut(Group(...))` can crash with assertion errors

```python
# WRONG — may crash: AssertionError in updater
self.play(FadeOut(Group(mob1, mob2, mob3)))

# CORRECT — fade individually
self.play(FadeOut(mob1), FadeOut(mob2), FadeOut(mob3))
# OR use AnimationGroup
self.play(AnimationGroup(FadeOut(mob1), FadeOut(mob2), FadeOut(mob3)))
```

`FadeOut` on a `Group` can trigger assertion errors inside Manim's updater system, especially when the group contains mobjects with conflicting states. Fade individual mobjects or use `AnimationGroup` instead.

### 24. `Axes.get_tick_labels()` does NOT exist

```python
# WRONG — raises AttributeError: 'Axes' object has no attribute 'tick_labels'
x_ticks = axes.get_tick_labels()
self.play(FadeIn(x_ticks))

# CORRECT — Manim renders axis ticks by default
# No extra call needed
```

Manim's `Axes` renders tick marks and labels automatically. If you need custom tick labels, use `axes.get_axis_labels()` or create them manually with `MathTex`/`Text` and `axes.c2p()`.