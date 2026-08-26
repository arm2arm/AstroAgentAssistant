# Rising Cards Aesthetic Standards

This document defines the visual and geometric standards for the "Rising Cards" layout used in DRP/PhysicsLLM publications.

## Geometric Scaling
Cards should increase in scale from left (L0) to right (L4).
- **Height (h):** Linearly or exponentially increasing. Typical sequence: [0.4, 0.48, 0.56, 0.64, 0.72] (normalized units).
- **Alignment:** Always bottom-aligned to the same baseline.
- **Spacing:** Uniform gap between cards or slight overlap if using the "diagonal ascending" variant.

## Color Palette (HEX)
Maintain these colors across ALL figures in a paper to anchor the levels.
- **L0 (Raw):** `#58C4DD` (Blue)
- **L1 (Calibrated):** `#83C167` (Green)
- **L2 (Derived):** `#FFA500` (Orange/Amber)
- **L3 (Aggregated):** `#7B68EE` (Medium Slate Blue)
- **L4 (Synthesized):** `#FF00FF` (Fuchsia/Magenta)

## Theme Variations
- **Manuscript:** Transparent or White (`#FFFFFF`) background. Black text.
- **Presentation/UI:** Dark background (`#0D1117`). White/Light text.

## Verification Checklist (via vision_analyze)
- [ ] Do card heights increase monotonically from L0 to L4?
- [ ] Are colors consistent with the standard palette?
- [ ] Is there sufficient margin for the title and caption?
- [ ] Is card content (e.g., "raw data", "provenance") centered within each card?
