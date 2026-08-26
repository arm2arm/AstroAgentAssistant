# Synthetic Plasma Deck Case Study

Complete walkthrough of regenerating an AI scientific workflow presentation deck with ocean blue styling and 3-slide summarization.

---

## Context

**Project:** `synthetic_plasma_deck`
**Original deck:** `ai_scientific_workflow_overview.pptx` (12 slides, dark theme)
**Goal:** Regenerate with white background + ocean blue accents, then condense to 3 slides

---

## Step 1: Inspect Existing Deck

```bash
cd /home/hermes/projects/synthetic_plasma_deck
ls -lh *.pptx *.py
```

Found:
- `build_deck.py` — Original deck generator (dark theme, dark background)
- `ai_scientific_workflow_overview.pptx` — Original output

**Lesson:** Always read the existing build script first to understand the deck structure, content patterns, and helper functions.

---

## Step 2: Create Ocean Blue Styled Version

### Color Palette

```python
# White background, ocean blue accent palette
BG = RGBColor(0xFF, 0xFF, 0xFF)
TEXT_DARK = RGBColor(0x1A, 0x2A, 0x3A)
TEXT_GRAY = RGBColor(0x4A, 0x5A, 0x6A)
CARD_BG = RGBColor(0xF0, 0xF9, 0xFF)
CARD_BORDER = RGBColor(0xB3, 0xE5, 0xFC)

# Ocean blue accent colors
OCEAN_DEEP =   RGBColor(0x00, 0x3B, 0x5C)  # Deep
OCEAN_LIGHT =  RGBColor(0x00, 0x6B, 0x8A)  # Light
OCEAN_ACCENT = RGBColor(0x00, 0xA5, 0xCF)  # Cyan
OCEAN_TEAL =   RGBColor(0x00, 0x80, 0x80)  # Teal
OCEAN_PAUSE =  RGBColor(0x48, 0xCA, 0xE4)  # Light cyan
```

**Key change:** From dark background (`0x0F, 0x17, 0x2A`) to white background. Text colors flipped from light-on-dark to dark-on-light.

### Card Helper Update

Added card backgrounds and borders for white-bg decks:

```python
def card(slide, x, y, w, h, c=CARD_BG, border=CARD_BORDER):
    r = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    r.fill.solid(); r.fill.fore_color.rgb = c
    l = r.line; l.color.rgb = border; l.width = Pt(1.5)
    r.shadow.inherit = False; r.adjustments[0] = 0.12
    return r
```

**Lesson:** Dark-theme decks use solid card colors without borders. White-bg decks need both background fill AND border for visual separation.

### Complete Deck Generation

```python
# Create new build script: build_deck_ocean.py
python3 build_deck_ocean.py
# Output: ai_scientific_workflow_ocean_blue.pptx (12 slides)
```

---

## Step 3: Export to PDF

```bash
libreoffice --headless --convert-to pdf ai_scientific_workflow_ocean_blue.pptx
# Output: ai_scientific_workflow_ocean_blue.pdf (51KB → 370KB converted)
```

**Lesson:** LibreOffice headless conversion is reliable on Linux. PDF size grows significantly due to rendering.

### WeasyPrint Markdown → PDF

For README documentation, use WeasyPrint instead of LibreOffice:

```python
import markdown
from weasyprint import HTML

html = markdown.markdown(open('README.md').read(), extensions=['tables', 'fenced_code'])
HTML(string=ocean_blue_wrapped_html).write_pdf('output.pdf')
```

**Requires:** `uv pip install weasyprint markdown`
**Run with:** `~/.venv/bin/python3` (not system Python, which lacks the weasyprint package)
**Result:** 89KB styled PDF with tables, code blocks, accent colors

---

## Step 4: Condense to 3 Slides

### Content Summarization Strategy

**Original 12 slides:**
1. Title
2. Problem
3. Vision
4. Architecture
5. Team
6. Tech Stack
7. Knowledge Extraction
8. Agent Capabilities
9. Benchmarking & QA
10. Roadmap
11. Differentiators
12. Thank You

**Condensed 3 slides:**

#### Slide 1: Problem + Vision + Team
- Title + team names in footer
- Left card: Problem (3 bullet points)
- Right card: Vision (4 bullet points)

**Summary approach:** Combine adjacent slides (Problem + Vision) into single side-by-side layout.

#### Slide 2: Architecture + Tech Stack + Capabilities
- Top: 5-layer architecture (vertical stack on left)
- Right: Data flow + Key capabilities (2 cards)
  - Data flow: 6 steps
  - Key capabilities: 6 features

**Summary approach:** Visual hierarchy showing system layers top-to-bottom, with cross-cutting aspects on right.

#### Slide 3: Roadmap + Differentiators
- Top: 4 roadmap phases (horizontal timeline, each with 4 items)
- Bottom: 4 differentiators (numbered list, plain text)

**Summary approach:** Timeline takes visual space at top, differentiators condensed below.

**What was cut:**
- Detailed team bios (names kept in footer only)
- Tech stack breakdown per category (integrated into architecture)
- Knowledge extraction pipeline diagram
- Individual agent capability cards
- QA metrics detail
- Benchmarking specifics
- Thank you slide

---

## Step 5: Generate PDF

```bash
libreoffice --headless --convert-to pdf ai_scientific_workflow_3slides.pptx
# Output: ai_scientific_workflow_3slides.pdf
```

---

## Common Errors Encountered

### Error 1: `AttributeError: 'RGBColor' object has no attribute 'rgb_val'`

```python
# Wrong
print(f"#{OCEAN_DEEP.rgb_val:06x}")

# Fix: Use direct indexing
print(f"#{OCEAN_DEEP[0]:02x}{OCEAN_DEEP[1]:02x}{OCEAN_DEEP[2]:02x}")
```

### Error 2: `NameError: name 'OCEAN_DARK' is not defined`

```python
# Fix: Define missing color at top of script
OCEAN_DARK = RGBColor(0x00, 0x2D, 0x4A)
```

### Error 3: `NameError: name 'OCEAN_DESK' is not defined` (typo)

```python
# Wrong
tb(s, ..., OCEAN_DESK, False)

# Fix: Correct name
tb(s, ..., OCEAN_DEEP, True)
```

**Lesson:** Color names must match exactly. Typos in `tb()` calls cause NameErrors.

---

## Final Deliverable

3-slide PDF covering:
- Problem + Vision + Team
- Architecture (5 layers) + Data Flow + Key Capabilities
- Roadmap (4 phases) + 4 Differentiators

Style: White background, ocean blue accent palette.

---

## User Preferences Captured

- **Concise responses:** No long explanations, just deliver results
- **Publication-ready style:** White backgrounds, accent color palette
- **Telegram delivery:** Use `MEDIA:/absolute/path.ext` format
- **Project preference:** `synthetic_plasma_deck` for scientific workflow presentations
