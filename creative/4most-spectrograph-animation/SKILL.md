---
name: 4most-spectrograph-animation
description: Manim CE animation explaining the 4MOST spectrograph for 11th-grade physics class. Full optical path from starlight through telescope, collimator, slit, dispersion element, fibre positioner, spectrographs, to CCD detectors.
category: creative
---
# 4MOST Spectrograph Animation — Manim CE

## Context
Educational animation for an 11th-grade physics class explaining how the 4MOST (4-Metre Multi-Object Spectrograph) works.

## Scene Requirements
1. Distant star field / single bright star emitting white light
2. Telescope collecting light (VLT-style or simple primary + secondary)
3. Collimating optics
4. Entrance slit
5. Dispersion element (prism OR diffraction grating) producing rainbow spectrum
6. Fibre positioner grid (many fibres feeding multiple spectrograph channels)
7. Three spectrograph modules receiving fibres
8. CCD detectors recording the final spectra

## Colour Palette
| Name   | Hex       | Manim constant |
|--------|-----------|----------------|
| BLUE   | #58C4DD   | BLUE_E         |
| GREEN  | #83C167   | GREEN          |
| YELLOW | #FFFF00   | YELLOW         |
| WHITE  | #EAEAEA   | WHITE          |
| DIM    | #7A8599   | LIGHT_GREY     |
| RED    | #FF6B6B   | RED_E          |
| PURPLE | #C792EA   | PURPLE_E       |
| BG     | #0D1117   | BLACK          |

Set scene background to dark: `self.camera.background_color = BLACK`

## Script Structure
```python
# /home/hermes/animations/4most_detailed.py
from manim import *

class FourMOSTDetailed(Scene):
    def construct(self):
        # 1. Title card
        # 2. Star / starlight rays entering telescope
        # 3. Telescope optics (simple lens/mirror)
        # 4. Collimating lens producing parallel beam
        # 5. Entrance slit mask
        # 6. Prism/grating dispersing into 7+ colour rays
        # 7. Fibre positioner grid (30 dots)
        # 8. Fibre lines connecting to 3 spectrograph channels
        # 9. CCD detector panels showing final spectra
        # 10. Labels and captions for each stage
        # 11. Fade out
```

## Rendering
```bash
mkdir -p /home/hermes/animations
manim -qh /home/hermes/animations/4most_detailed.py FourMOSTDetailed
```
- Render at 1080p60 if possible, otherwise 480p15
- Output: `media/videos/4most_detailed/1080p60/FourMOSTDetailed.mp4`

## Delivery
- User prefers direct Telegram file attachments, not external links
- Send short preview first (~10s), then full version (30-60s) on request

## Common Pitfalls
- Arrow tip cannot be coloured with hex values — use Manim arrow constants
- Long renders (>600s) — use background rendering with `notify_on_complete: true`
- Use `self.wait()` between stages for pacing
- Include brief explanatory text labels for each stage

## References
- 4MOST instrument: https://www.eso.org/sci/facilities/vlt/instrument/4most/