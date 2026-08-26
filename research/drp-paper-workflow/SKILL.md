---
name: drp-paper-workflow
description: "Class-level skill: reproducible paper build, DRP-Hub screenshot capture, BibTeX sweep, and final packaging workflow for agentic-astronomy papers. Use when preparing/finishing a DRP-style manuscript and integrating live registry screenshots or API extracts."
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [research, drp, reproducibility, latex, screenshots, bibtex]
    related_skills: [latex-paper-workflow, multi-section-latex-whitepaper, research:arxiv]
---

# DRP Paper Workflow (DRP-Hub + LaTeX + Screenshots)

## Overview

This skill codifies the end-of-paper checklist and repeatable actions used when preparing a DRP-style manuscript that integrates DRP-Hub registry content, REANA execution metadata, and final submission-ready PDF builds. It focuses on: (a) capturing pixel-accurate DRP-Hub screenshots reproducibly, (b) canonicalizing BibTeX entries for recent preprints and standards, (c) conservative copyedits and LaTeX build steps, and (d) packaging the final PDF + annotated changelog.

The skill provides a small set of reproducible scripts and reference notes for common pitfalls encountered during automated captures and LaTeX rebuilds.

## When to use

- You are finalising a manuscript that references a live registry (DRP-Hub) and want pixel-accurate screenshots.
- You need a reproducible, auditable sequence: fetch metadata → capture screenshots → insert into LaTeX → run pdflatex→bibtex→pdflatex×2 → commit built PDF.
- You want an automated probe script to capture pages for inclusion in figures/ and a short checklist to reduce warnings (undefined citations, missing images).
- You are recovering a paper repo from merge damage or automated-edit artifacts (see references/latex_merge_damage.md).

Do NOT use this skill for interactive GUI-driven screenshot fiddling; it is intended for headless, reproducible captures that can be rerun in CI or by an assistant.

## Quick recipe (one-shot)

1. Fetch landing HTML for the target registry page: `curl -sS -o /tmp/drphub_home.html https://drphub-p4n.aip.de/`
2. Run headless Chromium capture (script provided): `scripts/capture_drphub.sh /tmp/drphub_home.html figures/drphub_home_screenshot.png 1280 800`
3. Copy or move screenshot into paper `figures/` and update LaTeX include line (see template).
4. Run `make main.pdf` (Makefile must implement pdflatex→bibtex→pdflatex×2).
5. Inspect `main.log` for undefined citations; run the BibTeX sweep procedure (see references/bibtex_sweep.md) if needed.
6. Commit generated artifacts and built `main.pdf` locally.

## Files added by this skill

- references/drphub_capture.md — commands, alternate options, common failure modes.
- references/rising_cards_aesthetic.md — palette, geometry, and scaling rules for the "Rising Cards" aesthetic.
- references/bibtex_sweep.md — procedure to fetch canonical BibTeX for arXiv/DOI entries and canonicalize keys.
- references/latex-build-checklist.md — build hygiene checklist.
- references/latex_merge_damage.md — merge/automation damage checklist: artifact greps, structural checks, bib hygiene, EPJ webofc class quirks.
- templates/latex_include_screenshot.tex — LaTeX include snippet to paste into the paper.
- scripts/capture_drphub.sh — reproducible headless capture wrapper using Chromium; falls back to wkhtmltoimage if available.
- scripts/verify_rising_cards.py — deterministic PIL/numpy geometry check for Rising Cards figures (no vision model needed).

## Detailed steps

1. Capture HTML locally with `curl --max-time 20 -sS https://drphub-p4n.aip.de/ -o /tmp/drphub_home.html` to avoid live-interaction timing differences.
2. Preferred capture: headless Chromium (snap path on many systems): `/snap/bin/chromium --headless --disable-gpu --screenshot=/abs/path/to/out.png --window-size=1280,800 file:///abs/path/to/drphub_home.html`
3. Alternative: `wkhtmltoimage` where available (higher-fidelity for some server-side renderings). Command: `wkhtmltoimage --quality 90 /tmp/drphub_home.html out.png`.
4. If the page uses anchor navigation (card detail reachable at `#card`), render the HTML with the fragment or use the `/api/cards/<id>` JSON to populate a LaTeX verbatim example instead of a screenshot.
5. Copy into `figures/` and commit; update LaTeX includes to point to `figures/<name>.png` and re-run the Makefile.

## Aesthetic Standards: The Rising Cards Layout

For DRP-related papers, figures representing maturity or processing levels (L0–L4) must follow the "Rising Cards" aesthetic:
- **Geometry:** Horizontal sequence of cards/boxes, bottom-aligned, with increasing height (e.g., scale 1.0 to 1.8) and increasing width.
- **Background:** White for manuscripts (.pdf, .eps), Dark (#0D1117) only for presentation variants.
- **Palette (Consistent across figures):**
  - **L0:** Light Blue / Azure
  - **L1:** Green / Emerald
  - **L2:** Orange / Amber / Goldenrod
  - **L3:** Periwinkle / Soft Blue
  - **L4:** Purple / Fuchsia
- **Style:** Flat design, clean borders, minimal text overlap. Use vision_analyze to verify center-alignment and legibility.

### Rising Cards implementation notes (matplotlib)

- Bottom-align cards at a fixed `bot`; heights `hts = [h0 + step*i]` (e.g. `0.30 + 0.08*i` in axes fraction).
- Use a FIXED stripe height (`strip_h`), not proportional (`ht*0.28`) — proportional stripes get squashed on short cards.
- Anchor title/subtitle relative to the stripe (`bot + ht - strip_h - offset`), NOT proportionally (`bot + ht*0.48`); proportional anchoring drifts as heights vary across cards.
- Place inter-card arrows at a fixed low y (e.g. `bot + 0.13`) so they connect even the shortest card.

## Figure Audit & Selection Procedure

When the user requests a "better version" of a figure or references a previous iteration:
1. **List candidates:** Find all files matching the pattern (e.g., figures/fig4_*.png).
2. **Visual Audit:** Use vision_analyze on the candidates to identify:
   - Layout: Is it "Rising Cards" (increasing size) or "Flat" (equal size)?
   - Contents: Does it include the required levels (e.g., L0 to L4)?
   - Style: Dark theme vs. White theme.
3. **Cross-check Logic:** Inspect the generation script (e.g., make_all_figs.py). Even if a "Flat" image is on disk, the script may have the correct "Rising" logic commented out or toggleable via a variable.
4. **Programmatic geometry check (preferred first pass, and fallback when vision is slow/unavailable):** run `scripts/verify_rising_cards.py <png> [n_cards]`. It uses PIL+numpy to find, at each card's x-center, the topmost/bottommost non-white pixel (grayscale threshold < 245) and asserts (a) tops decrease monotonically L0→L4 (cards rise) and (b) bottoms are aligned. Deterministic and instant; reserve vision_analyze for legibility/overlap judgement. Tip when vision times out: downscale to ≤900 px JPEG q≈82 before retrying once, then switch to the programmatic route rather than looping.

## Scientific Framing: The Grounding Substrate

When discussing Agentic Astronomy or AI-assisted research in DRP contexts:
- **Avoid:** Framing the agent as an autonomous "generator" of research content or open-ended text.
- **Prefer:** Framing the agent as an observer and maintainer of the **Grounding Substrate**.
- **The Grounding Substrate** consists of deterministic artifacts:
  - Repository structure (FAIR compliance).
  - Validated execution logs (REANA).
  - Machine-readable metadata (JSON-LD RO-Crate).
  - Versioned software environments (OCI images).
- **Core Claim:** Hermes and similar agents operate by inspecting the substrate, generating actions based on deterministic constraints, and recording provenance. This design directly addresses LLM "hallucination" by grounding every agent action in a verifiable scientific state.

## Formatting: High-Density Layouts for 17-page Limits

When a manuscript exceeds a strict page limit (e.g., 23 pages for a 17-page target):
1. **Consolidate Maturity Lists:** Move itemized definitions of L0--L4 into a consolidated roadmap table or high-density paragraph to reduce vertical whitespace.
2. **Unified FAIR Mapping:** Merge separate FAIR mapping tables and artifact checklists into a single "FAIR-DRP Maturity Matrix" (e.g., Table 3).
3. **Appendix Density:** Use two-column layouts or smaller fonts (\small) for technical appendices and JSON-LD snippets.
4. **Table Column Tightening:** Switch from fixed-width `p{...}` columns to `lll` or `rll` alignments where possible to allow LaTeX to compact columns vertically.
5. **Figure Scaling:** Reduce standard `\linewidth` scaling from 0.95 to 0.85-0.90 for multi-panel diagrams.

## Structural sanity for the manuscript

- Section order must be: numbered sections → Conclusion → Acknowledgements → `\bibliography{...}` → `\appendix` → appendix sections. Any `\section` between the bibliography and `\appendix` is stranded content from a bad merge — reintegrate it (Contributions → Intro; Novelty/Limitations → Discussion; Evaluation/Worked-example → numbered sections).
- Never reference sections by hardcoded number ("Section 7"); use `Sect.~\ref{...}` so restructuring cannot rot the roadmap paragraph. Probe: `grep -nE 'Sect(ion)?[.~ ]+[0-9]' main.tex`.
- Orphaned .tex files: content files (e.g. appendix-ui.tex) may sit in the repo but never be input — silently missing from the PDF. Probe: compare `ls *.tex` against `grep -E 'input|include' main.tex`. Either inline the content or add the include; do not keep both copies (drift risk). Strip internal notes (delivery TODOs, placeholder reminders) when inlining.

## Pitfalls and fixes

### User-specific preferences discovered in recent sessions
- When the user requests "work always on main", the agent should switch to branch `main` and create a non-destructive backup branch `backup/<purpose>-YYYYMMDD` before substantive edits.
- Avoid committing generated PDFs or large binaries by default. Deliver PDFs via MEDIA:/absolute/path/to/file when sending to the user.
- For paper edits, create small incremental commits with clear messages: one commit per substantive edit (e.g., "paper: sharpen claim", "paper: add evaluation section").
- When including provenance artifacts, ensure `.fair-metadata/provenance.yaml` records `human_reviewed: true`, `reana_run_id`, `container_digest`, `git_commit`.

### Technical pitfalls
- **"Flat vs. Rising" Overwrites:** Image generation scripts often have a toggle for equal heights. Always check if drp_levels.png has been accidentally overwritten by a flat version from a different script (e.g., make_grid.py).
- **Color Inconsistency:** Ensure Figure 1 (Maturity) and Figure 4 (Data Levels) use the same color for the same level index.
- **Merge/automation damage in .tex:** after any merge or scripted edit pass, run the damage greps BEFORE compiling — full checklist with exact commands and fixes in references/latex_merge_damage.md (escape-marker artifacts, broken macros like `oindent`, escaped underscores inside verbatim, stranded sections, leftover TODO notes).
- **Uncited/duplicate bib entries:** diff the bib keys against actual cite usage (commands in references/latex_merge_damage.md). Cite or delete orphans; dedupe near-identical entries (e.g. Binder2018 vs Jupyter2018Binder) keeping one canonical key. A paper discussing FAIR/RO-Crate/PUNCH at length should actually cite those entries.
- **EPJ webofc class quirks:** the class issues bibliographystyle{woc} internally — adding your own causes a clash; just use `\bibliography{references}`. Silence the fancyhdr warning with `\setlength{\footskip}{3.60004pt}`. Verify `webofc.cls`, `woc.bst`, `txfonts` sit in the repo before building.
- **Tiny main.pdf (few KB) committed in tree** = broken previous build; never trust it, always rebuild from clean aux state (`rm -f main.aux main.bbl main.blg main.log main.out main.toc`).
- **Overfull hboxes in p{}-column tables:** column fractions plus inter-column seps must stay below 1.0 linewidth; shave each fraction slightly (e.g. 0.35→0.33) rather than restructuring. Under ~5 pt overfull is sub-visible and acceptable.
- "No such file or directory: wkhtmltoimage": do not hard-fail. Use Chromium headless as primary; attempt wkhtmltoimage only if present.
- Headless rendering can miss lazy-loaded content. If critical UI elements are absent, prefer fetching API JSON (e.g., `/api/cards`), or increase Chromium window-size and re-render.
- LaTeX can cache PDF builds. Always run `make clean` or `make` that triggers the full pdflatex→bibtex→pdflatex×2 sequence after changing figures or references.
- Do not push commits to remote before creating a local backup branch when performing destructive git history actions. (Follow user preference.)

## Verification checklist

- [ ] Screenshot files exist under `figures/` and are committed.
- [ ] LaTeX include lines updated and compile without missing-file errors.
- [ ] Full build (pdflatex→bibtex→pdflatex×2) completes: `grep -c '^!' main.log` = 0, no undefined citations/references, bibtex clean.
- [ ] No section after `\bibliography` except via `\appendix`; Conclusion exists.
- [ ] Figures pass `scripts/verify_rising_cards.py` (geometry) and a legibility glance.
- [ ] Page count matches target; report it to the user with the delivered PDF.
- [ ] Annotated changelog written (git log --name-only + short descriptions).

## References/support

See the `references/` directory for session-specific notes and the `scripts/` folder for repeatable captures and verification.
