# Paradigm Shift Comparison Slides

Pattern for recreating "Human-First vs Agent-First" paradigm shift diagrams with:
- Two-column layout (left: linear workflow, right: circular agent hub)
- Central transition arrow
- Data layer and input layer boxes
- Circular node workflows with curved arrows

## Core Structure

```python
# Left column: Linear workflow (4 icons)
wf_x = [Inches(0.9), Inches(1.7), Inches(2.5), Inches(3.3)]
for i, x in enumerate(wf_x):
    circle(slide, x, wf_y, icon_sz, NAVY, ["👤", "🔍", "📄", "💬"][i], 18)
    if i < 3:
        shape(slide, MSO_SHAPE.RIGHT_ARROW, x + icon_sz + Inches(0.1), wf_y + Inches(0.22),
              Inches(0.35), Inches(0.15), NAVY)

# Right column: Central agent hub with 6 surrounding nodes
agent_x, agent_y = Inches(10.8), Inches(2.0)
circle(slide, agent_x, agent_y, Inches(0.8), PURPLE, "🤖", 24)

nodes = [
    (Inches(10.8), Inches(1.0), "🔍", "Retrieve"),   # Top
    (Inches(11.6), Inches(1.3), "🧠", "Reason"),      # Top-right
    (Inches(11.9), Inches(2.0), "🎯", "Goal"),        # Right
    (Inches(11.6), Inches(2.7), "⚡", "Act"),         # Bottom-right
    (Inches(10.8), Inches(3.0), "📊", "Analyze"),     # Bottom
    (Inches(10.0), Inches(2.7), "✅", "Verify"),      # Left
]

for nx, ny, icon, label in nodes:
    circle(slide, nx, ny, Inches(0.5), PURPLE, icon, 16, WHITE)
    tb(slide, nx - 0.18, ny + 0.55, 0.5, 0.2, label, 8, DARK_TEXT, False, PP_ALIGN.CENTER)
```

## Curved Arrows Between Nodes

```python
# Small arrows at midpoints between adjacent nodes
arrow_pairs = [(0,1), (1,2), (2,3), (3,4), (4,5), (5,0)]
for i, j in arrow_pairs:
    x1, y1, _, _ = nodes[i]
    x2, y2, _, _ = nodes[j]
    mx = (x1.inches + x2.inches) / 2
    my = (y1.inches + y2.inches) / 2
    shape(slide, MSO_SHAPE.RIGHT_ARROW, Inches(mx - 0.1), Inches(my - 0.05),
          Inches(0.15), Inches(0.08), PURPLE)
```

## Data Layer and Input Layer

```python
# Data layer (rounded rectangle with 4 icons)
shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), Inches(2.95), Inches(3.4), Inches(0.85), NAVY)
for i, icon in enumerate(["🗄️", "🌐", "📖", "☁️"]):
    tb(slide, Inches(0.85 + i * 0.8), Inches(3.08), Inches(0.6), Inches(0.55), icon, 22, WHITE, False, PP_ALIGN.CENTER)

# Arrow from data to search/agent
shape(slide, MSO_SHAPE.UP_ARROW, Inches(1.9), Inches(2.8), Inches(0.2), Inches(0.12), NAVY)

# Input layer (single-turn or multi-turn)
shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), Inches(4.0), Inches(3.4), Inches(0.65), NAVY_DARK)
tb(slide, Inches(0.85), Inches(4.1), Inches(0.5), Inches(0.45), "👤", 20, WHITE, False, PP_ALIGN.LEFT)
tb(slide, Inches(1.45), Inches(4.1), Inches(2.5), Inches(0.45), "SINGLE TURN", 13, WHITE, True, PP_ALIGN.LEFT)
```

## Color Palette

```python
NAVY = RGBColor(0x00, 0x25, 0x4A)
NAVY_DARK = RGBColor(0x00, 0x1E, 0x3C)
PURPLE = RGBColor(0x6B, 0x3D, 0xB0)
PURPLE_DARK = RGBColor(0x4B, 0x15, 0x7B)
GREY_HEADER = RGBColor(0xE8, 0xE8, 0xE8)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK_TEXT = RGBColor(0x22, 0x22, 0x33)
FOOTER_BG = RGBColor(0xF5, 0xF5, 0xF5)
```

## Pitfalls

1. **Text positioning inside cards:** Textboxes must have `y >= card.y` to stay inside card boundaries.
2. **Node label overlap:** Use small font sizes (8pt) for node labels to avoid crowding.
3. **Curved arrow flow:** Arrows between nodes should follow clockwise direction for "continuous loop" effect.
4. **Vision timeout on large contact sheets:** Use individual slide renders (~560-820px) for visual QA.

## Example Output

See `build_comparison_slide.py` for a complete working example that recreates the Human-First vs Agent-First slide from screenshot.
