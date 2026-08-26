# Human-First vs Agent-First Comparison Slide Pattern

**Use case:** Create paradigm-shift comparison slides showing transition from linear single-turn workflows to circular multi-turn agent workflows.

---

## Visual Structure

### Left Column: "FROM HUMAN-FIRST"
- **Header:** Grey pill with "FROM" text
- **Title:** "HUMAN-FIRST" in navy blue
- **Linear workflow:** 4 icons in a row (User → Search → Docs → Chat)
- **Data layer:** Rounded box with 4 icons (DB, Globe, Book, Cloud)
- **Input layer:** "SINGLE TURN" box with user icon
- **Arrows:** Dashed arrows pointing UP from data → search, input → data

### Center Transition
- Large purple arrow pointing right

### Right Column: "TO AGENT-FIRST"
- **Header:** Purple pill with "TO" text
- **Title:** "AGENT-FIRST" in purple
- **Agent hub:** Central robot icon labeled "Agent"
- **Surrounding nodes:** 6 nodes in hexagon pattern (Retrieve, Reason, Goal, Act, Analyze, Verify)
- **Circular arrows:** Curved arrows connecting nodes clockwise
- **Dashed lines:** From agent hub to each surrounding node
- **Data layer:** Same 4 icons but purple
- **Input layer:** "MULTI-TURN • ITERATIVE • GOAL-DRIVEN" box with robot icon
- **Arrows:** Dashed arrows pointing UP from data → analytics, input → data

---

## Color Palette

```python
from pptx.dml.color import RGBColor

NAVY = RGBColor(0x1A, 0x2B, 0x4C)      # Dark Navy Blue
PURPLE = RGBColor(0x62, 0x00, 0xEA)    # Vibrant Purple
GREY_PILL = RGBColor(0x94, 0xA3, 0xB8)  # Muted Blue-Grey
GREY_FOOTER = RGBColor(0x6B, 0x72, 0x80) # Medium Grey
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
```

---

## Key Implementation Details

### 1. Linear Workflow (Left Side)

```python
wf_y = Inches(1.9)
icon_sz = Inches(0.6)
wf_x = [Inches(0.9), Inches(1.7), Inches(2.5), Inches(3.3)]
icons = ["👤", "🔍", "📄", "💬"]

for i, (x, icon) in enumerate(zip(wf_x, icons)):
    circle(slide, x, wf_y, icon_sz, WHITE, icon, 18, NAVY)
    if i < 3:
        shape(slide, MSO_SHAPE.RIGHT_ARROW, x + icon_sz + Inches(0.12), wf_y + Inches(0.2),
              Inches(0.25), Inches(0.12), NAVY)
```

### 2. Hexagon Node Layout (Right Side)

```python
import math

# Center agent
center_x, center_y = 10.5, 2.0  # inches
radius = 0.55  # inches from center

# 6 nodes at angles: 90°, 30°, 330°, 270°, 210°, 150°
node_angles = [90, 30, 330, 270, 210, 150]
node_icons = ["🔍", "🧠", "🎯", "⚡", "📊", "✅"]
node_labels = ["Retrieve\n(continuous)", "Reason", "Goal", "Act", "Analyze", "Verify"]

nodes = []
for angle, icon, label in zip(node_angles, node_icons, node_labels):
    rad = math.radians(angle)
    nx = center_x + radius * math.cos(rad)
    ny = center_y + radius * math.sin(rad)
    nodes.append((Inches(nx), Inches(ny), icon, label))

for nx, ny, icon, label in nodes:
    circle(slide, nx, ny, Inches(0.48), PURPLE, icon, 14, WHITE)
    # Label below each node
    lines = label.split("\n")
    for j, line in enumerate(lines):
        tb(slide, nx - 0.15, ny + 0.52 + j * 0.15, 0.45, 0.18, line, 7, PURPLE, False, PP_ALIGN.CENTER)
```

### 3. Curved Arrows Between Nodes

```python
arrow_pairs = [(0,1), (1,2), (2,3), (3,4), (4,5), (5,0)]
for i, j in arrow_pairs:
    x1, y1, _, _ = nodes[i]
    x2, y2, _, _ = nodes[j]
    mx = (x1.inches + x2.inches) / 2
    my = (y1.inches + y2.inches) / 2
    shape(slide, MSO_SHAPE.RIGHT_ARROW, Inches(mx - 0.08), Inches(my - 0.04),
          Inches(0.12), Inches(0.06), PURPLE)
```

### 4. Dashed Lines from Agent to Nodes

```python
for nx, ny, _, _ in nodes:
    cx = center_x
    cy = center_y
    dx = nx.inches + 0.24 - cx
    dy = ny.inches + 0.24 - cy
    dist = (dx**2 + dy**2)**0.5
    if dist > 0:
        shape(slide, MSO_SHAPE.RECTANGLE,
              Inches(cx + dx * 0.35), Inches(cy + dy * 0.35),
              Inches(0.03), Inches(0.03), PURPLE)
```

### 5. Footer Banner

```python
shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(5.5), Inches(12.3), Inches(0.6), GREY_FOOTER)
tb(slide, Inches(0.6), Inches(5.6), Inches(12.1), Inches(0.45),
   "typically serving humans through single-turn interactions", 11, WHITE, False, PP_ALIGN.CENTER)
```

---

## Common Pitfalls

1. **Node spacing:** Don't manually calculate positions — use trigonometry for even hexagon spacing
2. **Label positioning:** Labels must be below nodes (y + 0.5"), not overlapping
3. **Arrow direction:** Curved arrows should flow clockwise
4. **Dashed line visibility:** Use small rectangles (0.03") as dashed line segments
5. **Text wrapping:** Multi-line labels need split("\n") and loop for proper positioning

---

## Example Build Script

See `build_comparison_slide.py` in `/home/hermes/projects/synthetic_plasma_deck/` for a complete working example.

---

## Verification

After generating:
```bash
libreoffice --headless --convert-to pdf comparison_slide.pptx
ls -lh comparison_slide.pdf
```

Deliver to Telegram:
```
MEDIA:/home/hermes/projects/synthetic_plasma_deck/comparison_slide.pdf
```
