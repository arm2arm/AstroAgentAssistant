---
name: sin-unit-circle-animation
description: >
  Create animations showing the Unit Circle → Sine Wave connection.
  Uses ValueTracker + always_redraw for smooth rotating point that traces out the sine wave.
  Perfect for educational content (11th grade math, trigonometry).
version: 1.0.0
---

# Unit Circle → Sine Wave Animation

## Core Approach

The key pattern: use `ValueTracker` + `always_redraw` for smooth, real-time animation of a rotating point on a unit circle, where the y-coordinate traces out a sine wave.

### Why ValueTracker + always_redraw?

- **Smooth animation** — Manim interpolates the ValueTracker smoothly over the run_time
- **Automatic synchronization** — point position, radius line, wave, and projection line all update together
- **No manual frame building** — avoids fragile manual VMobject point arrays
- **Clean code** — all dependencies expressed as `always_redraw` lambdas

## Step-by-Step

### 1. Set up ValueTracker for angle

```python
theta = ValueTracker(0)  # θ starts at 0 radians
```

### 2. Create always_redraw mobjects

```python
point = always_redraw(lambda: Dot(
    2 * np.array([np.cos(theta.get_value()),
                  np.sin(theta.get_value()), 0]),
    color=GREEN, radius=0.08
))

radius = always_redraw(lambda: Line(ORIGIN,
    2 * np.array([np.cos(theta.get_value()),
                  np.sin(theta.get_value()), 0]),
    color=YELLOW, stroke_width=2))

arc = always_redraw(lambda: Arc(radius=0.5, start_angle=0,
    angle=theta.get_value(), color=ORANGE, stroke_width=2))
```

### 3. Build the sine wave (also driven by ValueTracker)

```python
wave_points = ValueTracker(0)  # 0 to 1 controls how much wave is revealed

def build_wave():
    n_points = 200
    max_t = wave_points.get_value() * 2 * PI
    pts = []
    for j in range(int(n_points * max_t / (2 * PI)) + 1):
        t = j * 2 * PI / n_points
        x_w = wave_origin[0] - 0.5 + j * 7.0 / n_points
        y_w = wave_origin[1] + 2 * np.sin(t)
        pts.append([x_w, y_w, 0])
    wm = VMobject()
    wm.set_points_as_corners(pts)
    wm.set_color(GREEN).set_stroke(width=4)
    return wm

wave_reveal = always_redraw(build_wave)
```

### 4. Animate both together

```python
self.play(
    theta.animate.set_value(2 * PI),
    wave_points.animate.set_value(1),
    run_time=8,
    rate_func=linear,
)
```

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Using `run_time(...)` instead of `run_time=` | Always keyword: `run_time=8` |
| `DOWN_RIGHT` doesn't exist | Use `RIGHT * 2 - DOWN * 1.5` |
| `MathTex` with `font=` parameter | Use `MathTex().scale()` instead |
| `MathTex.get_part_by_tex()` returns None | Use `set_color_by_tex()` |
| ParametricFunction with `t_min`/`t_max` | Use `t_range=(min, max, step)` |
| Manual VMobject point building | Use `always_redraw` + `ValueTracker` |
| `get_part_by_tex()` returns None | Use `set_color_by_tex()` |
| `MathTex` with font parameter | Use `.scale()` instead |

## Color Palette (Dark Background)

```python
BG       = "#0D1117"
GREEN    = "#83C167"   # E field, sin wave, positive
BLUE     = "#58C4DD"   # B field, secondary
YELLOW   = "#FFFF00"   # highlights, radius
ORANGE   = "#FF9F43"   # angle θ
PURPLE   = "#C792EA"   # propagation, tertiary
WHITE_C  = "#EAEAEA"   # body text
DIM      = "#7A8599"   # axes, labels
RED      = "#FF6B6B"   # negative slopes, warnings
```

## Pacing

| Section | Timing |
|---------|--------|
| Title | 1.5s |
| Circle + axes appear | 0.7s |
| Point, radius, arc, labels | 1.2s |
| Wave frame appears | 0.9s |
| Rotation + wave build | 8s (linear) |
| Equation | 2.1s |
| Final note + fade | 1.9s |
| **Total** | **~16s** |

## Verification Checklist

- [ ] `ValueTracker` for angle and wave progress
- [ ] `always_redraw` for all dependent mobjects
- [ ] `theta.animate.set_value(2*PI)` synchronized with wave building
- [ ] `run_time=` keyword (not function call)
- [ ] `set_color_by_tex()` for MathTex coloring (not `get_part_by_tex()`)
- [ ] No `DOWN_RIGHT` or other non-existent direction shortcuts
- [ ] `ParametricFunction` uses `t_range=` tuple, not `t_min`/`t_max`
- [ ] `MathTex` uses `.scale()` not `font_size` parameter
