# DRP-Hub / REANA conference narrative pattern

Use this reference when preparing DRP-Hub, REANA, or AI-agent reproducibility talks for CERN / open-data / astronomy audiences.

## Opening frame that worked

Start with the collaboration/trust motivation before the architecture:

- CERN represents the courage to ask impossible questions and the discipline to answer them together.
- Large-scale science depends on trust in instruments, data, software, and colleagues one may never meet.
- Reproducibility is not only running code again; it keeps the scientific path visible: what was done, how it was done, and how others can check, challenge, and build on it.
- In astronomy, the path is increasingly hidden under catalogues, containers, pipelines, calibration choices, parameters, and workflow decisions.
- AI agents can help expose and package this hidden work, but evidence, validation, provenance, and human review decide the scientific claim.
- Closing sentence: when we publish a result, we should also publish the path back to it.

## Slide structure

For a projector-friendly research talk, prefer this flow:

1. Title: `AI Agents for Reproducible Astronomy: DRP-Hub Meets REANA` or adapted title.
2. Opening motivation: CERN / collaboration / trust / reproducibility.
3. Hidden-work thesis: paper shows plots and claims; underneath are data releases, filters, pipeline versions, containers, workflow parameters, and human choices.
4. DRP concept: Digital Research Product packages workflow, code, environment, data references, metadata, validation evidence, and outputs.
5. L0-L4 maturity as cumulative evidence gates.
6. Reproducibility depth as a separate axis; plot replay is the minimum reader-facing promise when data and code are published.
7. Examples: LHC-CMS tutorials as tutorial-depth histogram/plot replay; Gaia DR3 / SHBoost-style products as plot-depth or scoped validation before full catalogue rebuild.
8. Architecture and service flow: DRP-Hub registry and card view, REANA execution/provenance, PUNCH4NFDI identity/compute/storage substrate.
9. AI-agent role: inspect, scaffold, draft, configure, validate; never replace evidence gates or human review.
10. Takeaway: publish conclusions plus a visible, executable, reviewable route back to the science.

## Speaker notes pattern

If the user provides a prose opening, do not crowd it onto slides. Put a concise visual summary on 1-2 slides and place the full opening text in speaker notes. This preserves readability while letting the speaker rehearse from the deck.

## Projector readability

Use large visual cards and short phrases:

- title 24-32 pt for scientific headings, larger on title slide;
- section headers around 18-22 pt;
- body bullets around 12-14 pt minimum;
- captions/diagram labels around 10.5-11 pt minimum;
- avoid full paragraphs on the slide face; put prose in speaker notes.

Always render to PDF/images and QA the opening and closing slides after title/footer changes.