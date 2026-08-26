# Beamer Slide Polish Patterns

Condensed guidance from a session revising a PUNCH4NFDI / DRP / REANA deck.

## When to apply
Use when the user says things like:
- make the slides nicer
- improve readability / legibility
- change the diagram
- too dense / too text heavy
- make it look more polished

## Practical sequence
1. **Find the weakest visual anchor first**
   - Usually this is an overview or maturity-model slide with a generic diagram or crowded bullets.
   - Replacing one weak diagram often improves the deck more than editing several minor bullets.

2. **Prefer a custom external figure over TikZ for quick iteration**
   - Use a small matplotlib script that writes both PDF and PNG.
   - Keep the background white for light decks; use high-contrast outlines for dark decks.
   - Save with `bbox_inches='tight'` and close the figure.

3. **Tighten wording and fix common syntax typos before shrinking fonts**
   - Look out for double-word typos in slide text (such as `"and and"`, `"the the"`, `"is is"`).
   - Ensure agency funding acronyms match exactly across paper acknowledgements and slide footers (e.g., verifying `"BMBF"` instead of `"BMFTR"` or other variants).
   - Replace long phrases like “one- to two-sentence description” with “short description”.
   - Remove redundant geographic qualifiers if already implied elsewhere.

4. **Eliminate Layout Overflows and Box Clipping**
   - Avoid setting wide horizontal constraints (`width=0.92\\linewidth`) for tall figures inside slides. Tall layout figures should be bounded by vertical limits (`height=0.75\\textheight,keepaspectratio`) to eliminate `Overfull \\vbox` warnings of 20pt+ and prevent vertical text clipping.
   - Mark Beamer frames as `fragile` whenever they contain `verbatim`, repository trees, or code blocks.

5. **Use local font reduction, not global deck shrinkage**
   - Add `\\small` or `\\footnotesize` only on frames that still overflow after trimming text.
   - Good candidates are architecture slides, registry slides, and two-column summary slides.

6. **Compile twice and use warnings diagnostically**
   - Run `pdflatex` compilation twice to propagate navigation data, slide counts, and outline structures cleanly.
   - Overfull `\\vbox` warnings identify the exact dense frames. Fix the flagged slides, then rebuild again.

## Good progression-diagram pattern
For L0→L4 or similar workflow maturity diagrams:
- horizontal row of rounded cards
- one short tag (`L0`, `L1`, ...)
- one short title (`Minimal`, `Documented`, `Citable`, ...)
- one short subtitle (`workflow + URL`, `README + example`, ...)
- arrows between cards
- one bottom caption stating the conceptual progression

## Design heuristics
- improve hierarchy, not decoration
- one key message per slide
- use block environments to group related steps/stages
- shorten bullets before adding columns
- if a slide remains crowded after `\small`, split it instead of compressing further

## Example figure style
Useful palette for clean scientific deck diagrams:
- neutral gray-blue text: `#263238`, `#607D8B`
- light card fills with stronger edge colors
- progression accent in blue or coral only where emphasis matters

## Outcome pattern
A successful polish pass usually produces:
- one upgraded figure asset
- 3–5 tightened dense slides
- fewer or smaller overflow warnings
- same content, better scanability
