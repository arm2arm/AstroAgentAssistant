---
name: stellar-catalog-comparison
description: Use when comparing matched stellar-catalog parameters.
version: 1.0.0
author: Hermes Curator
license: MIT
---

# Stellar-catalog comparison plots

## Purpose

A reusable workflow for comparing matched stellar-catalog estimates (for example, SH21 versus SH26) across several parameters and scientifically meaningful subgroups. The goal is an exploratory figure that answers the comparison question directly, rather than a crowded dashboard that mixes unrelated diagnostics.

## 1. Make the scientific request explicit

Record, before coding:

- the catalog pair and exact columns;
- the spatial/geometric selection and its expected order-of-magnitude count;
- convergence/quality criteria;
- subgroup definition and interpretation;
- requested parameters and units;
- residual convention, normally `Delta = new_catalog - reference_catalog`.

Check the expected selection count against the live data. Similar names such as “inner box” can refer to materially different boxes; never silently substitute a conventional cut for the cut implied by the requested count.

## 2. Selection strategy

Apply the base convergence and spatial selection once. Then select finite pairs independently for each parameter:

```text
base = converged AND inside requested spatial region
pair_ok(parameter) = finite(new_parameter) AND finite(reference_parameter)
```

Do not require every unrelated parameter to be finite for every row unless a complete-case sample is scientifically intended. This preserves the requested base population and makes per-parameter N transparent.

## 3. Recommended exploratory layout

For five parameters, prefer a 5 x 2 layout:

- left column: normalized distributions of reference and new catalog values;
- right column: distribution of `Delta = new - reference`.

Encode the subgroup with color and the catalog with line style. Use one global legend, not a repeated legend in every panel. Keep titles short; place N, median residual, and MAD in a compact annotation or in the provenance sidecar.

This layout directly shows population differences and agreement/bias. Add scatter or residual-versus-distance panels only when they answer an additional explicit question; they should not displace the primary comparison or create an unreadable 5 x 3 grid.

## 4. Robust plotting conventions

- Use common ranges within each parameter for the reference/new distributions.
- Derive display limits robustly (for example, central 0.5–99.5 percentiles) but state that tails are clipped for display.
- Keep all finite residuals for statistics; do not let display clipping change the reported median/MAD.
- Use a zero reference line in residual panels.
- Use distinct, colorblind-conscious colors for subgroup states and distinct line styles for catalogs.
- Avoid light-on-white density maps; for 2-D density plots use a high-contrast colormap and `LogNorm(vmin=1)`.
- Use `bbox_inches='tight'` only after checking the figure-level title and legend margins.

## 5. Numeric and visual QA

Verify all of the following from the rendered artifact and provenance:

- requested selection, coordinates, and base N are printed;
- subgroup counts sum to the base N (apart from explicitly handled missing subgroup values);
- all requested parameters appear, with units;
- each parameter has both catalog curves and both subgroup curves;
- residual sign and units are stated;
- each residual panel reports N, median, and MAD for both subgroups;
- no panel is empty;
- no title, legend, or statistics box overlaps another text element or is clipped.

When vision inspection is unreliable, use PDF text extraction plus renderer-level bounding-box checks and simple image-size/border checks. A plot that renders successfully is not necessarily legible.

## 6. Bundle revision

When a figure already exists in a multi-page PDF, replace the old page in place rather than appending a duplicate. Verify the final page count and extract the revised page’s title, selection, and sample count from the PDF.

## Pitfalls

- A “27M” request may indicate a larger box than an existing “standard inner box”; validate counts first.
- A complete-case filter across all five parameters can turn a 27M base sample into a much smaller and scientifically different sample.
- Long per-panel titles and repeated legends cause collisions even when the underlying data are correct.
- A single color dimension is insufficient when both subgroup and catalog identity must be shown; use color plus line style and document the mapping.
- Plot-specific display ranges must not be confused with the sample-selection range.

## Reference

See `references/sh21-sh26-exploratory.md` for a concrete, session-derived recipe and QA checklist.
