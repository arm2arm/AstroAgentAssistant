---
name: rave-dr6-public-talk-visualizations
description: Turn a nearest-100 RAVE DR6 query into dark-theme, public-talk-ready PNG visualizations with clear titles, readable scaling, and presentation-friendly styling.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [astronomy, rave-dr6, visualization, public-talk, presentation, plotting]
    category: astronomy
    related_skills: [rave-dr6, rave-dr6-nearest-100-plot]
---

# RAVE DR6 Public Talk Visualizations

## When to Use
Use this skill when the user wants RAVE DR6 outputs suitable for talks, outreach slides, or clean presentation graphics rather than only a research-style quicklook.

## Procedure

### 1. Start from the canonical query workflow
Use `rave-dr6` for generic querying, or `rave-dr6-nearest-100-plot` if the task is already specifically about the nearest 100 stars.

### 2. Save the nearest-100 subset locally
```python
df.to_parquet('rave_dr6_closest100.parquet', index=False)
```

### 3. Use a dark presentation theme
```python
import matplotlib.pyplot as plt
plt.rcParams.update({
    'figure.facecolor': '#0D1117',
    'axes.facecolor': '#0D1117',
    'savefig.facecolor': '#0D1117',
    'text.color': 'white',
    'axes.labelcolor': 'white',
    'xtick.color': 'white',
    'ytick.color': 'white',
})
```

### 4. Produce two public-ready PNGs
Recommended outputs:
- `rave_dr6_publictalk_galactic.png`
- `rave_dr6_publictalk_radec.png`

Use:
- larger markers than the research quicklook
- clear title and subtitle wording
- colorbar with readable label
- no cluttered legends
- consistent dark background and high contrast

### 5. Suggested styling choices
- Figure size: `8x6` or `10x6`
- DPI: `300`
- Marker size: `40–100` depending on overlap
- Highlight the Sun in Galactic plots with a gold marker
- Prefer concise titles, e.g.:
  - `100 nearest RAVE DR6 stars`
  - `Galactic projection`
  - `RA vs Dec sky distribution`

### 6. Deliverables
- the parquet table for reuse
- two PNGs for presentation use
- optional one-sentence captions for slide insertion

## Pitfalls
- Do not mix this presentation-oriented skill with generic TAP debugging; start from `rave-dr6` if the query itself is uncertain.
- Do not overload the figure with too many annotations.
- Keep outputs as PNG for easy slide insertion.
- If the scientific plot is the priority rather than presentation quality, use `rave-dr6-nearest-100-plot` instead.

## Verification
- Both PNGs open correctly and are readable on a dark slide background.
- Titles and labels are legible in presentation scale.
- The parquet table and PNG files are all written successfully.
