---
name: fourmost-spectrograph-schematic
title: 4MOST Spectrograph Schematic
description: Generate a static schematic illustration of the 4MOST spectrograph system as a precursor to a full Manim animation.
author: Hermi (based on user prompt)
version: 0.1
---

## Overview
This skill provides a step‑by‑step guide to create a static schematic of the 4MOST spectrograph using Matplotlib (or any preferred plotting library). The schematic includes:
1. VISTA telescope with 4MOST mount.
2. Wide‑field cone (≈2.5°).
3. Tilting‑spine fibre positioner on a curved focal surface.
4. Fibre bundles to three spectrograph boxes (HRS, LRS1, LRS2).
5. Optical train of a low‑resolution spectrograph (slit, collimator, dichroics, VPH gratings, CCDs).
6. Final science view (grid of spectra → Milky Way outline).

## Prerequisites
- Python 3.9+
- `matplotlib` (pip install matplotlib)
- Optional: `numpy` (usually installed with matplotlib)

## Step‑by‑step code
```python
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------------
# 1. Figure setup (dark background, user colour palette)
# ---------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 7), facecolor="#0D1117")
ax.set_facecolor("#0D1117")

# User colour palette
BLUE = "#58C4DD"
GREEN = "#83C167"
YELLOW = "#FFFF00"
WHITE = "white"

# ---------------------------------------------------------------------
# 2. VISTA + 4MOST (simple dome)
# ---------------------------------------------------------------------
theta = np.linspace(np.pi, 2 * np.pi, 200)
ax.plot(np.cos(theta), np.sin(theta) + 1, color=BLUE, lw=2)
ax.text(0, 2.2, "VISTA 4‑m telescope with 4MOST", color=WHITE, ha="center")

# ---------------------------------------------------------------------
# 3. Wide‑field cone (≈2.5°)
# ---------------------------------------------------------------------
# Scale factor chosen for visual appeal – not a real angular size.
cone_radius = np.tan(np.deg2rad(2.5 / 2)) * 5
ax.add_patch(plt.Circle((0, 0), cone_radius, edgecolor=GREEN, facecolor="none", lw=1, ls='--'))
ax.text(0, -cone_radius - 0.3, "Wide field ≈ 2.5° – thousands of targets", color=WHITE, ha="center")

# ---------------------------------------------------------------------
# 4. Fibre positioner (top‑down view of curved focal surface)
# ---------------------------------------------------------------------
phi = np.linspace(-np.pi / 3, np.pi / 3, 100)
R = 4
x_f = R * np.cos(phi)
y_f = R * np.sin(phi) - 2
ax.plot(x_f, y_f, color=YELLOW, lw=1)
# Hexagonal grid of fibre modules (small circles)
for i in range(-5, 6):
    for j in range(-3, 4):
        ax.plot(x_f[0] + i * 0.3, y_f[0] + j * 0.26, 'o', color=BLUE, markersize=2)
ax.text(0, -2.5, "2436 tilting‑spine fibres", color=WHITE, ha="center")

# ---------------------------------------------------------------------
# 5. Fibres to spectrograph boxes (three cables)
# ---------------------------------------------------------------------
for idx, x_off in enumerate([-2, 0, 2]):
    ax.plot([x_f[-1], x_f[-1] + x_off], [y_f[-1], -4], lw=4, color=GREEN)
    ax.text(x_f[-1] + x_off, -4.5, ["HRS", "LRS1", "LRS2"][idx], color=WHITE, ha="center")

# ---------------------------------------------------------------------
# 6. Low‑resolution spectrograph optical train (simplified)
# ---------------------------------------------------------------------
sp = -2  # x‑position of the spectrograph box
# Slit
ax.add_patch(plt.Rectangle((sp - 0.4, -4.2), 0.8, 0.3, edgecolor=BLUE, facecolor="none", lw=1))
# Collimator (simple line)
ax.plot([sp, sp], [-4.2, -3.8], color=WHITE, lw=1)
# Dichroics – three coloured lines
colors = [BLUE, GREEN, YELLOW]
labels = ["Blue", "Green", "Red"]
for i, c in enumerate(colors):
    y = -3.8 + i * 0.1
    ax.plot([sp, sp + 0.8], [y, y], color=c, lw=1)
    ax.text(sp + 0.9, y, labels[i], color=c, va='center')
# CCDs – small black rectangles
for i in range(3):
    y = -3.85 + i * 0.1
    ax.add_patch(plt.Rectangle((sp + 0.85, y), 0.15, 0.08, facecolor="black"))

# ---------------------------------------------------------------------
# 7. Science view – grid of tiny spectra leading to a Milky Way outline
# ---------------------------------------------------------------------
for i in range(10):
    for j in range(5):
        x0, y0 = -5 + i * 0.5, -7 + j * 0.3
        ax.plot([x0, x0 + 0.3], [y0, y0 + 0.05], color="#AAAAAA", lw=0.5)
ax.text(0, -8, "Spectra → Milky Way map", color=WHITE, ha="center")

# ---------------------------------------------------------------------
# 8. Final touches
# ---------------------------------------------------------------------
ax.set_xlim(-6, 6)
ax.set_ylim(-9, 3)
ax.axis('off')
plt.show()
```

## Tips & Pitfalls
- **Colour palette** – keep the dark background (`#0D1117`) and the three accent colours from the user profile (`#58C4DD`, `#83C167`, `#FFFF00`).
- **Scale** – the schematic is intentionally abstract; the exact angular size of the cone is not critical, only that it visually conveys a wide field.
- **Readability** – keep text labels short and centred; avoid overlapping with other graphic elements.
- **Extensibility** – each numbered block corresponds to a future Manim `Scene`. When moving to animation, you can reuse the same coordinates and colour constants.

## Next Steps
1. Run the script and inspect the generated figure.
2. Share the image with the user for feedback.
3. Once approved, translate each block into a Manim `Scene` (or a single `MovingCameraScene`) following the same geometry and colour scheme, as described in the original prompt.
---
