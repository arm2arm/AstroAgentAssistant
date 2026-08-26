---
name: powerpoint-deck-customization
description: Generate, customize, and export PowerPoint decks with python-pptx — styling, white backgrounds, accent colors, PDF conversion via LibreOffice headless mode.
version: 1.0.0
author: Hermes Agent + Arman Khalatyan
license: MIT
metadata:
  hermes:
    tags: [productivity, presentation, powerpoint, python-pptx, pdf-export]
---

# PowerPoint Deck Customization

Generate and customize PowerPoint presentations programmatically using `python-pptx`. Supports style changes (colors, backgrounds, fonts) and PDF export via LibreOffice headless mode.

---

## When to Use This

- **Regenerate existing slides** with new styling (white background, accent colors)
- **Condense multi-slide decks** into summary versions
- **Create publication-ready presentations** with consistent styling
- **Export decks to PDF** for distribution or Telegram delivery

---

## Core Workflow

### 1. Inspect Existing Deck

```bash
# Check what's in the project
ls -lh *.pptx *.md *.py

# If build script exists, read it to understand structure
read_file build_deck.py
```

### 2. Define Color Palette

```python
from pptx.dml.color import RGBColor

# White background + ocean blue accent example
BG = RGBColor(0xFF, 0xFF, 0xFF)  # White
OCEAN_DEEP = RGBColor(0x00, 0x3B, 0x5C)
OCEAN_LIGHT = RGBColor(0x00, 0x6B, 0x8A)
OCEAN_ACCENT = RGBColor(0x00, 0xA5, 0xCF)
OCEAN_TEAL = RGBColor(0x00, 0x80, 0x80)
OCEAN_PAUSE = RGBColor(0x48, 0xCA, 0xE4)
TEXT_DARK = RGBColor(0x1A, 0x2A, 0x3A)
TEXT_GRAY = RGBColor(0x4A, 0x5A, 0x6A)
CARD_BG = RGBColor(0xF0, 0xF9, 0xFF)
CARD_BORDER = RGBColor(0xB3, 0xE5, 0xFC)
```

### 3. Helper Functions

Copy these patterns from existing build scripts — they provide consistent styling:

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

def bg(slide, c=BG):
    """Set slide background color"""
    r = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    r.fill.solid(); r.fill.fore_color.rgb = c; r.line.fill.background(); r.shadow.inherit = False

def card(slide, x, y, w, h, c=CARD_BG, border=CARD_BORDER):
    """Create rounded rectangle card with border"""
    r = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    r.fill.solid(); r.fill.fore_color.rgb = c
    l = r.line; l.color.rgb = border; l.width = Pt(1.5)
    r.shadow.inherit = False; r.adjustments[0] = 0.12
    return r

def tb(slide, x, y, w, h, text, sz=18, c=TEXT_DARK, bold=False, align=PP_ALIGN.LEFT, fn="Calibri"):
    """Add textbox"""
    t = slide.shapes.add_textbox(x, y, w, h)
    tf = t.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = text; p.font.size = Pt(sz); p.font.color.rgb = c; p.font.bold = bold; p.font.name = fn; p.alignment = align
    return t

def bar(slide, x, y, w, h, c=OCEAN_DEEP):
    """Add color bar"""
    r = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    r.fill.solid(); r.fill.fore_color.rgb = c; r.line.fill.background(); r.shadow.inherit = False
    return r

def bullet(slide, x, y, w, h, items, sz=16, c=TEXT_DARK, bc="\u2022", cc=OCEAN_ACCENT, sp=Pt(8), fn="Calibri"):
    """Add bulleted list with custom bullet color"""
    t = slide.shapes.add_textbox(x, y, w, h)
    tf = t.text_frame; tf.word_wrap = True
    ns = "http://schemas.openxmlformats.org/drawingml/2006/main"
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = item; p.font.size = Pt(sz); p.font.color.rgb = c; p.font.name = fn; p.space_after = sp
        pPr = p._p.get_or_add_pPr()
        buChar = pPr.makeelement(f"{{{ns}}}buChar", {"char": bc})
        pPr.append(buChar)
        buClr = pPr.makeelement(f"{{{ns}}}buClr", {})
        srgb = buClr.makeelement(f"{{{ns}}}srgbClr", {"val": f"{cc[0]:02x}{cc[1]:02x}{cc[2]:02x}"})
        buClr.append(srgb); pPr.append(buClr)
    return t
```

### 4. Export to PDF

**Method: LibreOffice headless mode (Linux)**

```bash
libreoffice --headless --convert-to pdf input.pptx
```

This is reliable on Linux systems with LibreOffice installed. Output filename matches input with `.pdf` extension.

**Alternative: WeasyPrint (Markdown → Styled PDF)**

For README docs and text-heavy content, convert Markdown directly to a styled PDF:

```bash
# Install (uses uv-managed venv)
uv pip install weasyprint markdown
```

```python
import markdown
from weasyprint import HTML

with open('README.md') as f:
    md = f.read()

html = markdown.markdown(md, extensions=['tables', 'fenced_code', 'codehilite'])

# Wrap with ocean-blue themed CSS
styled_html = '''
<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
@page { margin: 1in; }
body { font-family: 'DejaVu Sans', sans-serif; font-size: 11pt; line-height: 1.6; color: #1a2a3a; }
h1 { color: #003B5C; border-bottom: 2px solid #00A5CF; padding-bottom: 8px; }
h2 { color: #003B5C; margin-top: 28px; }
h3 { color: #006B8A; }
code { background: #f0f9ff; border: 1px solid #b3e5fc; padding: 1px 4px; border-radius: 3px; }
pre { background: #f0f9ff; border: 1px solid #b3e5fc; padding: 12px; border-radius: 6px; }
table { border-collapse: collapse; width: 100%; margin: 16px 0; }
th { background: #003B5C; color: white; padding: 8px 12px; }
td { padding: 8px 12px; border-bottom: 1px solid #b3e5fc; }
tr:nth-child(even) td { background: #f0f9ff; }
blockquote { border-left: 4px solid #00A5CF; padding-left: 16px; color: #4A5A6A; }
</style></head><body>
''' + html + '</body></html>'

HTML(string=styled_html).write_pdf('output.pdf')
```

**Run with:** `~/.venv/bin/python3` or `uv run python3 -c "..."` — weasyprint installs to the uv-managed venv at `~/.venv`, not system Python.

**Note:** WeasyPrint requires `DejaVu Sans` font (available on Linux). For Unicode content (arrows, emojis, special chars) this font covers most symbols.

---

## Common Patterns

### Summarizing Multi-Slide Deck

1. Identify core narrative: Problem + Vision → Architecture → Roadmap
2. Extract key content from each section
3. Condense 10-12 slides into 3-4 summary slides
4. Maintain visual hierarchy: titles, bars, cards, bullets

### Style Changes (White Background)

- Replace `BG = RGBColor(0x0F, 0x17, 0x2A)` (dark) with `BG = RGBColor(0xFF, 0xFF, 0xFF)` (white)
- Update text colors: dark text (`TEXT_DARK`) instead of light text on dark backgrounds
- Add card backgrounds (`CARD_BG`) and borders (`CARD_BORDER`) for visual separation
- Use accent colors for bars, headers, and visual highlights

### Ocean Blue Accent Palette

```python
OCEAN_DEEP =   RGBColor(0x00, 0x3B, 0x5C)  # #003B5C
OCEAN_LIGHT =  RGBColor(0x00, 0x6B, 0x8A)  # #006B8A
OCEAN_ACCENT = RGBColor(0x00, 0xA5, 0xCF)  # #00A5CF
OCEAN_TEAL =   RGBColor(0x00, 0x80, 0x80)  # #008080
OCEAN_PAUSE =  RGBColor(0x48, 0xCA, 0xE4)  # #48CAE4
```

Use for:
- Top and bottom accent bars
- Section headers
- Bullet points
- Card left borders
- Layer/phase highlights

---

## Pitfalls

### 1. RGBColor Access Error

**Problem:** `AttributeError: 'RGBColor' object has no attribute 'rgb_val'`

**Fix:** RGBColor objects don't expose hex values directly. Use integer components:
```python
# Wrong
print(f"#{OCEAN_DEEP.rgb_val:06x}")

# Right
print(f"#{OCEAN_DEEP[0]:02x}{OCEAN_DEEP[1]:02x}{OCEAN_DEEP[2]:02x}")
```

### 2. Undefined Color Variables

**Problem:** `NameError: name 'OCEAN_DARK' is not defined`

**Fix:** Define all colors used in the deck at the top of the script:
```python
OCEAN_DARK = RGBColor(0x00, 0x2D, 0x4A)  # Very dark blue
```

### 3. PDF Conversion Failures

**Problem:** LibreOffice not installed or conversion fails

**Fix:**
```bash
# Check LibreOffice availability
which libreoffice

# If missing, install
sudo apt-get install libreoffice  # Debian/Ubuntu
```

### 4. Card vs Textbox Positioning (Text Overlap Pitfall)

**Problem:** Text placed **inside** a card is positioned at absolute slide coordinates, not relative to the card. If textbox `y` is less than card `y`, text floats above the card boundary and overlaps previous content.

**Example (wrong):**
```python
c = card(s, Inches(0.6), Inches(1.5), Inches(2.9), Inches(5.2))
bar(s, x, Inches(1.5), ...)
# These tbs are positioned ABOVE the card (y < card.y):
tb(s, x, Inches(0.25), ...)  # WRONG: y=0.25 above card at y=1.5
tb(s, x, Inches(0.6), ...)   # WRONG: same
# These are INSIDE the card (y >= card.y):
tb(s, x + 0.2, Inches(3.1), ...)  # OK
```
This causes card title/period to appear at the top of the slide, not inside their card.

**Fix:** Always place textbox `y` at or below the card's `y` coordinate. Add an inset from card top:

```python
c = card(s, x, y_c, w, h)
# Title inside card, relative to card
tb(s, x + 0.2, y_c + 0.3, ...)   # 0.3" below card top
tb(s, x + 0.2, y_c + 0.7, ...)   # further down
# Bullet list inside card
bullet(s, x + 0.2, y_c + 1.2, ...)
```

This applies to ALL card-embedded content — titles, periods, bullets — every textbox within a card must have `y >= card.y`.

### 5. Circular Node Positioning (Hexagon Layout)

**Problem:** When creating circular/agent-loop diagrams with surrounding nodes, manual coordinate calculation leads to uneven spacing and misaligned labels.

**Fix:** Use trigonometry for even hexagon spacing:

```python
import math

# Center agent
center_x, center_y = 10.8, 2.0  # inches
radius = 0.55  # inches from center

# 6 nodes at angles: 90°, 30°, 330°, 270°, 210°, 150° (top, top-right, right, bottom, bottom-left, left)
node_angles = [90, 30, 330, 270, 210, 150]
node_icons = ["🔍", "🧠", "🎯", "⚡", "📊", "✅"]
node_labels = ["Retrieve", "Reason", "Goal", "Act", "Analyze", "Verify"]

nodes = []
for angle, icon, label in zip(node_angles, node_icons, node_labels):
    rad = math.radians(angle)
    nx = center_x + radius * math.cos(rad)
    ny = center_y + radius * math.sin(rad)
    nodes.append((Inches(nx), Inches(ny), icon, label))

for nx, ny, icon, label in nodes:
    circle(slide, nx, ny, Inches(0.5), PURPLE, icon, 14, WHITE)
    tb(slide, nx - 0.15, ny + 0.45, 0.4, 0.15, label, 7, PURPLE, False, PP_ALIGN.CENTER)
```

**Curved arrows between nodes:** Place small arrows at midpoints between adjacent nodes.

### 6. Bullet Color XML Errors

**Problem:** Invalid XML namespace or color format in `bullet()` function

**Fix:** Ensure loop variable name doesn't conflict:
```python
# Wrong
for color, items in colors:
    ...  # 'color' shadows the imported 'color' module

# Right
for idx, items in enumerate(items_list):
    c = color_list[idx]
    ...
```

---

## Verification

After generating deck:

```bash
# Check PPTX file size and slides
ls -lh *.pptx

# Generate PDF
libreoffice --headless --convert-to pdf deck.pptx

# Verify PDF exists and has reasonable size
ls -lh *.pdf

# If delivering to Telegram/Messaging:
# Use MEDIA:/absolute/path/to/file.pdf
```

---

## Telegram Delivery Pattern

When user asks to see a PDF in Telegram:

```bash
# Generate PDF from PPTX
libreoffice --headless --convert-to pdf deck.pptx

# Deliver with MEDIA: prefix
MEDIA:/home/user/projects/deck/final.pdf
```

The MEDIA: prefix tells Hermes to attach the file natively to the platform message.

---

## Related Skills

- `brainstorm-to-deck` — Convert brainstorm notes to PowerPoint (different workflow)
- `design-md` — Design system and token specs (for consistent design systems)
- `powerpoint` — Core .pptx operations (reading, editing, QA patterns)

---

## New Techniques (2026-07-13)

### Human-First vs Agent-First Comparison Slides

Pattern for creating paradigm-shift comparison diagrams with:
- Linear workflow (left) vs circular agent loop (right)
- Hexagon node layout using trigonometry
- Curved arrows between nodes
- Dashed connector lines from central hub

See `references/human-first-vs-agent-first-slide-pattern.md` for complete implementation guide.

---

## Examples

See `references/synthetic-plasma-case-study.md` for a complete walkthrough of regenerating a deck with ocean blue styling and 3-slide summarization.

See `references/agent-first-comparison-slide.md` for the pattern of recreating paradigm-shift comparison diagrams (Human-First vs Agent-First) with circular node workflows and curved arrows.

---

## New Techniques (2026-07-13)

### Markdown to PDF via WeasyPrint

For README-style documentation or text-heavy content, convert Markdown directly to styled PDF:

```bash
# Install in uv-managed venv
uv pip install weasyprint markdown
```

```python
import markdown
from weasyprint import HTML

with open('README.md') as f:
    md = f.read()

html = markdown.markdown(md, extensions=['tables', 'fenced_code', 'codehilite'])

# Wrap with themed CSS
styled_html = '''<!DOCTYPE html><html><head><style>
@page { margin: 1in; }
body { font-family: 'DejaVu Sans', sans-serif; font-size: 11pt; }
table { border-collapse: collapse; width: 100%; }
th { background: #003B5C; color: white; }
td { padding: 8px; border-bottom: 1px solid #b3e5fc; }
</style></head><body>''' + html + '</body></html>'

HTML(string=styled_html).write_pdf('output.pdf')
```

**Run with:** `~/.venv/bin/python3` — weasyprint installs to uv venv at `~/.venv`, not system Python.

### Circular Node Diagrams (Agent Workflows)

For "Agent-First" comparison slides with central hub + surrounding nodes:

```python
# Central agent node
agent_x, agent_y = Inches(10.8), Inches(2.0)
circle(slide, agent_x, agent_y, Inches(0.8), PURPLE, "🤖", 24)

# 6 surrounding nodes in hexagon pattern
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
    # Label below each node
    tb(slide, nx - 0.18, ny + 0.55, 0.5, 0.2, label, 8, DARK_TEXT, False, PP_ALIGN.CENTER)
```

**Curved arrows between nodes:** Use small arrows at midpoints between adjacent nodes. For visual QA, render to PDF and check arrow flow.

### Vision Timeout Fallback Pattern

When `vision_analyze` times out on large contact sheets:

1. **Don't keep retrying** — switch to deterministic checks
2. Convert to individual slide images: `pdftoppm -png -r 88 -f N -l N deck.pdf out`
3. Use small thumbnails (~560-820px) for vision inspection
4. Run `scripts/deck_qa.py` for media/background verification
5. Run `scripts/verify_arrows.py` for diagram arrow validation

See `references/white-editable-decks-and-deterministic-qa.md` for full playbook.
