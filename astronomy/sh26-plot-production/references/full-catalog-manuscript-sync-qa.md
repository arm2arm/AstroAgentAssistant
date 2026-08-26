# Full-catalog manuscript synchronization and release QA

Use this checklist when a catalogue paper has already generated many figures but the manuscript may still contain values or interpretations from earlier reduced runs.

## Authority order

1. Treat final full-catalog JSON sidecars as the numerical authority.
2. Use independently validated comparison records for cross-catalogue products.
3. Treat manuscript prose and old plans as stale until reconciled.
4. Distinguish an inferred-catalogue comparison from direct validation.

## Scientific consistency checks

- Map every quantitative manuscript claim to a sidecar key or validation record.
- Report ALL, selection-flag True, selection-flag False, counts, and paired finite denominators where relevant.
- Keep spatial selections distinct even when both are informally called the “inner box.” For SH26:
  - extended SH21–SH26 comparison box: `X[-5,5] × Y[-4,4]` kpc;
  - core bulge plotting box: `X[-4,4] × Y[-3,3]` kpc;
  - P97 Queiroz-style box is separate again: `|X|<5`, `|Y|<3.5`, `|Z|<3` kpc.
- Proper-motion-only velocity transformations with radial velocity fixed to zero are projected velocity proxies, not full `U,V,W` or 6D kinematics. State this in module docs, labels, sidecar caveats, manuscript prose, abstract, and conclusions.
- Very large permutation-null z statistics from huge samples are descriptive diagnostics, not automatically Gaussian detection significances. Record permutation count and estimator disagreements.

## Canonical artifact closure

1. Enumerate registry IDs and require contiguity through the current maximum; never hard-code an obsolete upper ID.
2. Require one JSON/PDF/PNG triple for every registered plot.
3. Verify every sidecar identifies the intended final dataset version.
4. Copy validated temporary products into the canonical figure directory only after confirming provenance and counts.
5. Rebuild the combined bundle and run the bundle audit.
6. Record bundle page count, artifact counts, dataset-version coverage, and SHA-256 in the audit document.

## Visual QA

- Build a contact sheet for broad inspection, then inspect suspicious figures individually at native resolution.
- Contact sheets are useful for blank panels and overflow but can falsely imply unreadable labels because of downsampling.
- Check title/count/colorbar collisions after `PlotContext.save()` appends `P##` and `N = ...`; `tight_layout()` ran before that mutation. If a long single-panel title collides with the colorbar, wrap the title onto two lines and rerender the full-catalog product.
- Verify manuscript pages for clipping and overfull floats. Underfilled appendix float pages are not automatically failures if figures and captions are intact.

## Manuscript build gate

Run a clean sequence:

```bash
rm -f main.aux main.bbl main.blg main.log main.out
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

If labels still changed, run another `pdflatex` pass. Then reject:

- undefined citations or references;
- overfull boxes or oversized floats;
- BibTeX syntax/empty-field warnings;
- placeholders in extracted PDF text.

A malformed BibTeX entry can make later entries appear broken. Fix the first parser line reported, then rerun the complete build.

## Final release gate

- Run the full test suite.
- Run `py_compile` for modified plot modules.
- Verify registry IDs directly from the registry/CLI.
- Run `git diff --check`.
- Confirm clean manuscript logs and visual QA.
- Commit and push only after every gate passes.
- Verify `HEAD == origin/main` and a clean working tree.
