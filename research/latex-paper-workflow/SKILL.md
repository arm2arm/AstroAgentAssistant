---
name: latex-paper-workflow
title: LaTeX Research Paper — Creation, Iteration, Compilation, and Submission
description: >-
  Complete guide to writing, iterating, compiling, and packaging LaTeX research papers.
  Covers monolithic paper generation, multi-round improvement, merging papers, figure generation,
  MNRAS/journal submission formatting, and portability fixes on Ubuntu/Debian.
author: Hermes Agent
date: 2026-04-30
tags: [latex, paper, academic-writing, compilation, submission, mnras]
---

# LaTeX Research Paper Workflow

This umbrella covers the full lifecycle of a LaTeX research paper: creation, iterative improvement, compilation, and journal submission packaging.

---

## 1. Paper Creation

### Directory Structure
```
/home/hermes/<titleslug>/
├── main.tex              ← entry point (monolithic or \input{} chapter files)
├── Makefile              ← build system (optional but recommended)
├── references.bib        ← BibTeX references
├── img/                  ← generated figures (NOT doc/figures/)
├── src/                  ← Python analysis scripts
└── doc/
    ├── main.tex          ← entry point
    ├── chapters/         ← OPTIONAL (only if \input{}ed from main.tex)
    │   ├── abstract.tex
    │   ├── introduction.tex
    │   ├── data_pipeline.tex
    │   ├── results.tex
    │   ├── discussion.tex
    │   └── conclusion.tex
```

Title slug: lowercase, hyphens, remove special chars (only `[a-z0-9-]`).

**Figure directory convention**: Use `img/` at project root for generated figures, referenced via `../../img/fig.png` from `doc/`. Do NOT use `doc/figures/`.

### Mandatory Paper Sections
1. **Title** and **Author(s)** — derive from context or use reasonable placeholder
2. **Abstract** — problem, method, results, conclusion
3. **Introduction** — problem statement, motivation, contributions
4. **Related Work** — survey of relevant literature (`\cite{}` placeholders)
5. **Methodology** — approach, methods, experiments
6. **Results** — findings, quantitative outcomes
7. **Discussion** — interpretation, limitations, implications
8. **Conclusion** — summary, future work
9. **References** — `\bibliographystyle{plain}` + `\bibliography{references}`

### Minimum Preamble
```latex
\usepackage{amsmath, amssymb}    % Math
\usepackage{graphicx}            % Figures — use [draft] if images aren't real files
\usepackage{hyperref}            % Links
\usepackage{booktabs}            % Tables
\usepackage{microtype}           % Typography
\usepackage{geometry}            % Margins
\geometry{margin=1in}
```

### Writing Style
- Formal academic tone throughout
- No conversational language, first-person plural preferred
- Precise technical terminology
- Explicit transitions between sections
- Include equations (`equation` or `align` environments) where appropriate
### Slide Styling Preference (session-derived)

Per-user defaults: some users prefer a light deck by default while others (notably this user) prefer a dark, high-contrast deck. Embed per-user style choices into edits rather than hardcoding one global default.

Default for general audiences (when no per-user override exists):
- clean white-background Beamer style
- dark body text
- restrained blue/green accent colors
- light gray footer/panel backgrounds if needed
- preserve readability over branding-heavy styling

User-specific override (arm2arm):
- the user prefers a dark background: background color #0D1117
- palette: Blue #58C4DD, Green #83C167, Yellow #FFFF00
- use high-contrast white or off-white body text and avoid low-contrast accent tints on dark slides
- keep slides readable; avoid tiny fonts on dark backgrounds and prefer split slides over shrinking text

Rules when applying styles:
1. Honor an explicit per-user preference when present (do not silently revert it). If a deck already used a different theme, ask only if the change materially affects layout or meaning.
2. Change the theme in the preamble, not the slide body, unless the new theme forces layout adjustments.
3. Preserve content first, then restyle — avoid mixing a theme migration with a large content rewrite in the same edit unless the user asked for both.
4. Recompile twice after every theme/date/preamble change to stabilize navigation, outlines, and title-page metadata.
5. Check for overfull `\\vbox` warnings after adding architecture-heavy or content-heavy slides. If a slide becomes dense, split it rather than shrink fonts.
6. Mark Beamer frames as `fragile` whenever they contain `verbatim`, repository trees, or other literal blocks; otherwise compilation errors look unrelated.

Theme substitution policy:
- If the user explicitly requests a named theme (e.g. `Antibes`, `Metropolis`), switch to that theme when it is available. If it is not installed, prefer `Metropolis` as the practical material-like substitute and note the substitution in the commit message or provenance manifest.
- If the user later asks to revert theme naming (remove an agent or named framework), follow the explicit removal procedure in this skill (search-and-rewrite, preserve technical substance, recompile).

Polish sequence (when told to “make slides nicer”):
1. identify the most text-dense or visually weak slide first;
2. replace a low-information overview diagram with a cleaner external figure (for dark decks, prefer figures with transparent or dark-friendly backgrounds and high-contrast labels);
3. shorten bullets before shrinking fonts;
4. use `\\small` only on the specific dense frames that still overflow after text tightening;
5. recompile twice and inspect overfull `\\vbox` warnings by line number to target remaining crowded slides.

For maturity-model or workflow-progression slides, a robust visual pattern is a horizontal sequence of rounded cards with:
- one short title per level,
- one short subtitle per level,
- directional arrows between levels,
- a single bottom caption expressing the progression in plain language.

When the user provides slide content in another presentation format (for example Marp frontmatter plus bullet content) but the working project is already a functioning LaTeX/Beamer deck, prefer **translating the content into the existing Beamer source** instead of switching toolchains mid-stream. Preserve the requested structure/content while keeping the established compilation path.

See also `references/beamer-slide-polish-patterns.md` for a concise slide-polish checklist derived from a DRP/REANA/PUNCH4NFDI deck revision session.

For infrastructure talks with maturity models, a robust slide sequence is:
1. system/infrastructure overview
2. execution layer / workflow system
3. example scientific workload
4. maturity model overview
5. one slide each for major maturity levels or grouped levels
6. registry/discovery layer
7. takeaway

4. **Appendix Selection & Layout (Multi-target Compilation):** When a manuscript exceeds a page limit due to extensive appendices, provide the user with a "Main Body" PDF for submission (no appendix) and a "Full" PDF (body + appendix).
5. **Section Reframing:** For "Agentic" papers, avoid generative AI hype. Position the AI assistant (e.g. Hermes) as an observer/operator of a deterministic **Grounding Substrate** (FAIR metadata, execution logs, RO-Crate). This fulfills the requirement for deterministic provenance in agentic astronomy.

### Handling Model/Provider Switches mid-session
When the user announces a change to the active LLM or provider (e.g. \"model was just switched from gpt-5-mini to claude-opus-4.8 via GitHub Copilot\"), treat this as **contextual routing**, not an action item. 
- **Acknowledge seamlessly**: Adjust your self-identification and capabilities to match the new model.
- **Do not attempt to run tools to switch the model**: The model is user-configured out-of-band (e.g., via the Copilot UI or gateway config).
- **Do not stall**: Reply briefly acknowledging the identity shift, then immediately resume or prompt for the next step of the active task.

### Agent-Assisted Writing Disclosure
When the user wants the paper to explicitly say it was written with an agent or writing pipeline, do not leave that only in chat. Reflect it in the manuscript and companion slides.

Practical pattern:
1. Update the author line, title-page note, or subtitle to name the writing scaffold if requested.
2. Add one explicit paragraph or short section in the paper body describing the role of the writing system (literature discovery, critique, style passes, etc.).
3. Add an acknowledgement sentence that separates tool assistance from manual scientific curation.
4. If slides exist, add a dedicated slide or title-page note so the presentation matches the paper.
5. Recompile both paper and slides after the wording change.

Important caveat: make the tool's role auditable but not overstated. Prefer wording like "used as a structured writing/review scaffold" over claims that the system independently established correctness. When the workflow includes multiple submodules or personas, spell out the composition clearly and distinguish automated critique from final human/source curation.

### Removing a named agent/framework while preserving content
If the user later says to remove a named framework, writing pipeline, or agent stack from a paper or companion slides (for example: "remove mentioning X"), treat this as a full-content cleanup rather than a wording tweak.

Use this pattern:
1. search all paper/slide sources for the framework name and lowercase variants;
2. remove the dedicated named section, named tables/figures, acknowledgements, and stray mentions in abstract/introduction/conclusion;
3. preserve the underlying technical substance by rewriting named examples into **generic assistant / agentic-system language** when the concept is still useful;
4. re-run the search to verify zero matches remain;
5. recompile and deliver the cleaned artifacts.

This user specifically prefers generic agentic-assistant framing in reproducibility papers unless they explicitly request a named framework.

### Quality Checklist
- [ ] All 9 mandatory sections present
- [ ] Uses `draft` mode for graphicx (unless images are real files)
- [ ] No `\textquote{}` (requires `csquotes` — use ``quotes'' instead)
- [ ] Compiles without errors (clean aux → pdflatex → bibtex → pdflatex ×2)
- [ ] Citations in text match entries in `references.bib`
- [ ] Figures/tables have captions, labels, and are referenced in text

---

## Git + Makefile Project Setup for LaTeX Papers

When a user asks to "convert to a local git project" or "add a Makefile so we can build with make all":

### Git initialization
```bash
cd /path/to/paper
git config user.name "Author Name"
git config user.email "author@institution.de"
git init
# Add .gitignore FIRST, then add files
git add -A
git commit -m "chore: initial commit — full paper project"
```

**Pitfall**: `git init && git add -A && git commit` in one shot fails if `user.name`/`user.email` are not configured — `git commit` exits with "Author identity unknown". Always configure identity before the first commit.

### .gitignore for LaTeX
Track only source files and final PDFs. Never commit aux/log/nav/snm/toc/vrb:
```
*.aux *.bbl *.blg *.log *.out *.nav *.snm *.toc *.vrb
*.fls *.fdb_latexmk *.synctex.gz
__pycache__/ *.pyc .DS_Store
```
Apply this with `git rm -r --cached . && git add -A` after adding .gitignore to a repo that already tracked these files.

### Commit discipline
After every meaningful change (Makefile, template update, figure fix) commit immediately:
```bash
git add -A && git commit -m "feat/fix/build: short description"
```

### Makefile for multi-target LaTeX + figures
Standard targets for a paper repo with Python-generated figures:

| Target | Action |
|---|---|
| `make all` | figures + all PDFs |
| `make pdf` | main paper only (3-pass) |
| `make epj` | journal submission PDF |
| `make slides` | Beamer presentation |
| `make figures` | `cd figures && python make_*.py` |
| `make clean` | remove aux files |
| `make distclean` | clean + remove PDFs |
| `make watch` | auto-rebuild on `.tex`/`.bib` changes (`entr`) |

**Critical Beamer pitfalls:**
- Beamer slides usually have **no `\cite` commands** — do NOT run `bibtex` on slides target, it will exit with error "I found no `\citation` commands". Only run bibtex on targets that actually cite.
- **`xelatex` resolves `\includegraphics{}` relative to CWD, not the `.tex` file's directory** — this differs from `pdflatex` behavior and is a common cause of "image not found" failures when the image is generated in a different directory than the `.tex`. Fix: use absolute paths in `\includegraphics{}`, OR `cp` the image to CWD before compiling. Verify with `pdfimages -list <pdf>` — empty list means the image wasn't found.
- Figure scripts that hard-code absolute paths (e.g. `plt.savefig('/home/user/project/figures/fig.pdf')`) break when the Makefile does `cd figures && python script.py`. Fix: use relative paths (`plt.savefig('fig.pdf')`) in the script.
- Makefile recipe lines **must use tabs**, not spaces.
- Build figure dependencies **before** LaTeX targets in `make all`.

### Makefile template skeleton
```makefile
LATEX      = pdflatex
LATEXFLAGS = -interaction=nonstopmode -halt-on-error
PYTHON     = python3

.PHONY: all pdf epj slides figures clean distclean

all: figures main.pdf main-webofc.pdf slides.pdf

figures:
	cd figures && $(PYTHON) make_drp_fig.py

main.pdf: main.tex references.bib
	$(LATEX) $(LATEXFLAGS) main.tex
	bibtex main
	$(LATEX) $(LATEXFLAGS) main.tex
	$(LATEX) $(LATEXFLAGS) main.tex

slides.pdf: slides.tex          # NO bibtex — slides rarely cite
	$(LATEX) $(LATEXFLAGS) slides.tex
	$(LATEX) $(LATEXFLAGS) slides.tex

clean:
	rm -f main.aux main.bbl main.blg main.log main.out \
	      main-webofc.aux main-webofc.bbl main-webofc.blg \
	      main-webofc.log main-webofc.out \
	      slides.aux slides.log slides.nav slides.out slides.snm slides.toc slides.vrb
```

---

## EPJ Web of Conferences (webofc) conversion

This section captures lessons and a repeatable recipe from a recent session where we converted an existing LaTeX manuscript into the EPJ Web of Conferences (webofc) template. Use this whenever a user requests porting a paper to the EPJ Web of Conferences format.

Key additions from recent session:
- Always create a local backup git branch before any destructive or bulk edits (e.g. bibliography sweep, style conversion). Name pattern: backup/<task>-YYYYMMDD. Commit immediately with a clear message.
- When editing files, always stage and commit each change with a small, descriptive message. The agent must not make uncommitted edits.
- For automated BibTeX lookups, write candidates to references/_autofetch_candidates.bib and commit that file before manually vetting entries.
- Add a small deterministic script `scripts/append_bib_from_candidates.py` that appends vetted entries from `_autofetch_candidates.bib` to `references.bib` with provenance comments, and requires explicit confirmation before writing (interactive by default). The script lives under the skill's `scripts/` directory and is documented in `references/autofetch-bib.md`.

Recent session-specific fixes to embed (2026-06-08 agentic-astronomy rebuild):
- Compilation and timeout handling: prefer background builds or multi-step foreground runs; capture pdflatex_pass*.txt logs; commit logs and backups on the backup branch for auditing.
- Patch-safety: after any `patch` touching preamble or document skeleton, run a quick grep for doubled backslashes and correct them before a full compile.
- Escaped-underscore markers: if the cleanup process introduces placeholder markers such as `<<ESC_UNDERSCORE>>`, handle them consistently: replace with `_` in verbatim/JSON blocks and `\_` in normal text mode; verify with a single pdflatex pass before committing.
- Large write_file safety: break large writes into parts, write parts, then concatenate or use `\input{}` to avoid write_file truncation failures.

Action items added to the skill's references/ and scripts/ directories:
- references/compile-timeouts-and-patch-pitfalls.md (summarizes the above fixes and safe patterns)
- scripts/latex_build_bg.sh (helper compile script: pdflatex → bibtex → pdflatex ×2; recommended for agent background runs)
- Note: these are conservative, class-level additions — they codify how the agent should behave across LaTeX rebuild sessions to match the user's preference (backup-first, commit logs, avoid silent write failures).
- Add a template `templates/append_bib_README.md` describing safe interactive usage and the repository backup policy for bib sweeps.
\nKey additions from recent session:
- Always include webofc.cls and woc.bst in the project root. If the class references auxiliary style files (e.g. doiEDPS.sty) that are not present on the build host, create a minimal local shim (see templates/doiEDPS.sty) rather than attempting global texmf installs on behalf of the user.
- Workflow observation: when converting, produce a working copy (main-webofc.tex) and extract the original manuscript body into a separate include (main-body-epj.tex). This keeps the conversion reversible and makes patch generation clean.
- Bibliography/authorship pitfall discovered: BibTeX may report "I found no \citation commands" if the project uses an include/wrapper pattern where the \cite commands end up in a different .aux file. Practical remedies:
  - Ensure the include is active (not commented) and that the main wrapper writes citations into the wrapper's .aux. If citations are in an included file, run `pdflatex` once and inspect the produced `.aux` files for `\citation{...}` lines to find the correct basename for `bibtex`.
  - If needed, move the body into an `\input{main-body-epj.tex}` pattern (as we do) so all citations appear in the wrapper's .aux and `bibtex <basename>` works predictably.
  - Clean stale aux files before the canonical compile sequence to avoid phantom missing-citation warnings.
- Create a diff/patch file (webofc.patch) between original main.tex and main-webofc.tex and deliver it to the user for review before overwriting originals.
- If the class complains about missing doiEDPS.sty, prefer to add a minimal doiEDPS.sty (from templates/doiEDPS.sty) that implements \doiEDPS{<doi>} as a DOI hyperlink. This is a small, low-risk shim and prevents build failures on CI or containerized environments.
- Build script recommendation: add an automated script `scripts/epj_compile.sh` that
  - Deliverables that users expect after conversion: main-webofc.pdf, main-webofc.tex, main-body-epj.tex, webofc.patch, main-webofc.log, build_run.log, and a submission ZIP containing webofc.cls, woc.bst, the sources, minimal shims (doiEDPS.sty), and a build script.
  - Layout warnings: if `fancyhdr` warns that `\\\\footskip is too small (0.0pt)`, add `\\\\setlength{\\footskip}{3.60004pt}` to the wrapper preamble to silence it.
  - Unescaped underscores in LaTeX text mode (e.g. file names like `license_info.yaml`) will fail compilation with math-mode errors (e.g. missing `$`). Always escape underscores as `\\\\_` in standard text blocks of the LaTeX paper body.
  - Beamer Slide Dimension Overflows: Beamer tables or figures often trigger `Overfull \\vbox` or `Overfull \\hbox` warnings and slide overflows if dimensions are set using widths alone.
    - To prevent vertical slide overflows, scale figures using height constraints relative to text height: `height=0.75\\textheight,keepaspectratio`.
    - For tables, ensure fonts are set to `\\small` or `\\footnotesize` and prefer split frames over overly dense slides.
  - Synchronizing Acronyms & Project Metadata: Always audit and synchronize funding agencies and institution names across both the manuscript paper and the companion presentation slides (e.g., updating outdated or mixed identifiers such as `BMFTR` to the standardized federal acronym `BMBF`). Do not allow acronym mismatch between the slides and paper.
  - Single-user, Single-assistant Profile Model: Implement isolated workspaces/profiles for assistants to enforce security/privacy boundaries and avoid cross-project credential leaks.
  - Guided Reproducibility Surface: Position the assistant as an artifact-generating companion (producing Dockerfiles, `reana.yaml`, `CITATION.cff`, and git patches) rather than offering conversational advice.
  - Automated Debugging Loops: Implement a "compile-sandbox" loop on the execution backend (such as REANA) where the assistant executes, captures logs, patches configuration errors, and reiterates automatically to accelerate the transition from L2 (Citable) to L3 (Validated) maturity.

Recommended support files (added to this skill):
- references/webofc-conversion.md — session-specific notes, errors encountered (doiEDPS missing), and exact commands used.
- `references/overfull-hbox-remediation.md` — systematic recipe to reach 0 overfull warnings >2pt across multi-target builds: verbatim JSON line-breaking, p{}-table width/tabcolsep math, the duplicated-appendix gotcha, and EPJ/arXiv tarball standalone verification
- scripts/epj_compile.sh — deterministic compile script (pdflatex → bibtex → pdflatex ×2), logs to build.log, and produces a submission ZIP.
- templates/webofc-main.tex — minimal webofc starter template that imports the paper body via an include.
- templates/doiEDPS.sty — minimal helper style to define doi macros.

Minimal safety and verification checks:
- Run pdflatex once, then bibtex, then pdflatex twice; inspect the .log for undefined citations and rerun as needed.
- If bibtex reports missing .aux entries, ensure the included body file (main-body-epj.tex) contains the citation commands and that the main-webofc.tex \include or \input is active (not commented out).
- After adding a local shim (doiEDPS.sty), re-run the full compile chain and check the .log for unresolved package errors. If deeper class support is missing (rare), ask the user for the full macro zip from EDP Sciences and include it in the submission package.

Pointer: see the new support files added under this skill for concrete examples and an automated compile script.

When to use
- Target journal: EPJ Web of Conferences / Web of Conferences series.
- **Author instructions page:** https://www.epj-conferences.org/for-authors#anchor_Instructions-ffor-authors
- **Author instructions page:** https://www.epj-conferences.org/for-authors#anchor_Instructions-ffor-authors
- Official macro ZIP (2025-03-28): https://www.epj-conferences.org/doc_journal/instructions/macro/web-conf/macro-latex-web-conf.zip
- Files required: webofc.cls, woc.bst, cuted.sty, doiEDPS.sty (all in the official ZIP). Keep all four in the paper directory root.

**Always download fresh from the official URL** rather than reusing cached copies — the package was updated 2025-03-28 and earlier copies (e.g. from 2024) may differ.

Quick checklist
1. Download and unpack the official ZIP:
   ```bash
   curl -sL https://www.epj-conferences.org/doc_journal/instructions/macro/web-conf/macro-latex-web-conf.zip -o /tmp/webofc.zip
   unzip -o /tmp/webofc.zip -d /tmp/webofc_official/
   cp /tmp/webofc_official/macro-latex-web-conf/{webofc.cls,woc.bst,cuted.sty,doiEDPS.sty} ./
   ```
2. Create a working copy: main-webofc.tex (do not overwrite original until verified).
3. Replace the documentclass line with: `\documentclass{webofc}`
4. **Add `\usepackage[varg]{txfonts}` — this is MANDATORY** in the official 2025 template. Missing it produces wrong fonts and may cause class warnings.
5. Adopt the webofc preamble: add other packages (amsmath, graphicx, hyperref, etc.) AFTER txfonts.
6. Use the official author macros — `\firstname{}`, `\lastname{}`, `\inst{}`, `\fnsep\thanks{\email{}}`:
   ```latex
   \author{
     \firstname{Arman} \lastname{Khalatyan}\inst{1}\fnsep\thanks{\email{email@inst.de}}
     \and
     \firstname{E.} \lastname{Sacchi}\inst{2}
   }
   \institute{Institution 1 \and Institution 2}
   ```
7. Ensure woc.bst is present; bibliography call: `\bibliography{references}` (BibTeX required; woc.bst is loaded by the class).
8. Compile sequence: pdflatex → bibtex → pdflatex ×2.
9. Verify figures: webofc supports standard figure environments and figure* for two-column floats; use `\sidecaption` only if the class supports it (see shipped template for examples).

Pitfalls and mitigations
- **Author block `\inst{}` is mandatory when `\thanks{}` is present (webofc.cls):** dropping `\inst` from authors (e.g. after collapsing to a single shared affiliation) makes `\maketitle` fail with the cryptic `! Use of \reserved@a doesn't match its definition`. Even with ONE institute, tag every author `\inst{1}` and keep a single `\institute{...}` entry. Fastest diagnosis for this class of opaque class-macro errors: build 2–3 minimal variant docs in /tmp (copy the cls/sty in, change ONE variable per variant), compile each — isolates the offending syntax in seconds instead of guessing.
- Duplicate packages: remove font packages such as txfonts/newtx* if template already loads fonts. Duplicate font packages cause font substitution warnings or fatal errors.
- Bibliography: do NOT mix biblatex + biber with the class unless you have adapted the class; prefer traditional BibTeX with woc.bst for the simplest path.
- Overfull/underfull boxes: the webofc template uses specific margins; if you see overfull boxes after conversion, check figure widths and table column widths first.
- Missing class/bst: If webofc.cls or woc.bst are missing on build servers (e.g. CI), include them in the submission ZIP or add them to the project's texmf folder for CI.
- Backslash escapes when patching: prefer writing a fresh main-webofc.tex via templates rather than many small patch operations.

Minimal workflow (commands)

cp /path/to/webofc.cls /path/to/paper/
cp /path/to/woc.bst /path/to/paper/
cp /path/to/template-image-files /path/to/paper/figures/  # optional

# make a working copy
cp main.tex main-webofc.tex
# edit main-webofc.tex: change documentclass, adapt preamble and title block

# compile
pdflatex -interaction=nonstopmode main-webofc.tex || true
bibtex main-webofc || true
pdflatex -interaction=nonstopmode main-webofc.tex || true
pdflatex -interaction=nonstopmode main-webofc.tex || true

What to deliver to the user
- main-webofc.pdf (compiled EPJ-formatted PDF)
- A diff/patch showing exact edits to main.tex (or main-webofc.tex if you did not overwrite main.tex)
- A short notes file describing non-trivial replacements (references/webofc-conversion.md)

User preference embedding
- If the user has a per-user style preference (e.g., dark background slides, palette), do NOT silently change paper style. For slide decks, the user prefers a dark theme (#0D1117 background) — preserve that for slides and document that preference in the skill's per-user notes. Paper-level styling must follow the journal class rules; do not attempt dark-paper styling unless the user explicitly asks and the journal allows it.

See also:
- templates/webofc-main.tex (a minimal starting point)
- scripts/epj_compile.sh (automated compile + basic checks)
- references/webofc-conversion.md (session notes and commands)


## 2. Iterative Improvement

### Build System with Makefile
For projects combining LaTeX papers with Python-generated figures, use a Makefile at the project root:

```makefile
IMG_DIR   := latex/images
PYTHON    := python3

.PHONY: all compile run clean thesis expose plots

all: run latex

plots:
	@echo "[1/3] Running simulations..."
	$(PYTHON) src/ml_rms_sim.py --img-dir $(IMG_DIR)
	$(PYTHON) src/ml_rms_sim_refined.py --img-dir $(IMG_DIR)
	@echo "[✓] plots generated"

run: plots
	@echo "[✓] all simulations done"

latex: thesis expose

thesis:
	@echo "[2/3] Compiling thesis..."
	cd latex && pdflatex -interaction=nonstopmode thesis.tex
	cd latex && pdflatex -interaction=nonstopmode thesis.tex
	@echo "[✓] thesis.pdf"

expose:
	@echo "[3/3] Compiling exposé..."
	cd latex && pdflatex -interaction=nonstopmode expose.tex
	cd latex && pdflatex -interaction=nonstopmode expose.tex
	@echo "[✓] expose.pdf"

compile: thesis

clean:
	@echo "Cleaning..."
	cd latex && rm -f *.aux *.log *.out *.toc *.pdf
	rm -f $(IMG_DIR)/thesis_*.png
	@echo "[✓] cleaned"
```

**Key rules for this pattern:**
- Makefile recipe lines MUST use tabs (not spaces) — `make` requires tabs
- Run Python plots BEFORE LaTeX compilation (figures must exist before `\includegraphics`)
- Use `--img-dir` argument in Python scripts to write figures to the correct directory
- Always compile LaTeX twice per document (first pass for references, second for resolution)
- LaTeX paths for figures must match the directory structure: `\includegraphics{images/figure.png}`
- Keep build artifacts (`.aux`, `.log`, `.out`, `.toc`, `.pdf`) in `.gitignore`

### Project Structure with Combined Python + LaTeX
```
project/
├── .gitignore          # ignore *.aux *.log *.out *.toc *.pdf __pycache__/
├── Makefile            # build system (all, compile, run, clean)
├── README.md           # documentation
├── src/                # Python simulation/analysis code
│   ├── __init__.py
│   ├── simulation.py        # main pipeline
│   └── plotting.py          # figure generation (--img-dir arg)
└── latex/              # LaTeX papers
    ├── expose.tex
    ├── thesis.tex
    └── images/             # figures referenced by LaTeX
        ├── figure1.png
        └── figure2.png
```

### Mandatory .gitignore Entries
```
*.aux
*.log
*.out
*.toc
*.pdf
__pycache__/
*.pyc
.DS_Store
```

---

## 2. Iterative Improvement

### Preferred: Single-File Rewrite for Major Changes
For substantial rewrites (10+ changes, new sections, structural overhaul), write the entire `main.tex` in one `write_file()` call. Patching LaTeX is fragile due to `\`, `%`, `&` escaping.

### Monolithic vs Multi-file Structure
See the **Directory Structure** section above for full details.

**Quick guide:**
- **Monolithic** `main.tex`: Short papers, rapid iteration, single author
- **Multi-file** `doc/chapters/*.tex`: Long papers, parallel work, individual section review. Directory: `doc/chapters/` (not `sections/`). Files: `abstract.tex`, `introduction.tex`, `data_pipeline.tex`, `results.tex`, `discussion.tex`, `conclusion.tex`, etc.
- **Figure directory**: Always `img/` at project root, referenced via `../../img/fig.png` from `doc/`
- **Scaffold**: Use `scripts/scaffold-paper.py` to create a new multi-file project (see `references/multi-file-paper-structure.md`)
- **Clean stale files** — remove unused `chapters/` files not referenced by `main.tex`

### Iteration Pattern
1. **Read** current `main.tex` with `read_file` (full, no pagination)
2. **Plan** improvements (structural, prose, figures, references)
3. **Apply** — `patch` for small changes, full `write_file` for major changes
4. **Compile** — run `pdflatex` twice for bibliography resolution
5. **Verify** output page count and check `.log` for errors

### Multi-Round 10-Cycle (Standard Improvement)
Each round targets specific improvements:
- **Round 1**: Structural fixes — remove duplicate packages, unused packages, biblatex→BibTeX, add missing figures
- **Round 2**: Academic prose — improve introduction flow, strengthen thesis statements, formalize language
- **Round 3**: Related work — contextualize literature, strengthen reproducibility narrative
- **Round 4**: Practical sections — add concrete examples, expand step-by-step guides
- **Round 5**: Method/technical — improve technical precision, explain tool integration
- **Round 6**: Governance/quality — tighten quality checklists, improve role definitions
- **Round 7**: Language tightening — remove redundant phrases, eliminate wordiness
- **Round 8**: Captions/formatting — improve table/figure captions, consistent citations
- **Round 9**: Future outlook — expand roadmap, improve community growth section
- **Round 10**: Final polish — consistency checks, strengthen conclusion

### Multi-Phase Iteration (X figure rounds + Y text rounds)
When user requests "iterate 7 times on images, 25 times on text":
1. **Figure iterations FIRST** — write/rewrite matplotlib scripts, execute, iterate
2. **Text iterations SECOND** — write comprehensive `main.tex` with ALL improvements in one shot
3. **Compile at the end** — no need to compile after every single iteration

### Merging Multiple Papers
1. **Read all source papers** — `read_file` each `main.tex` fully
2. **Plan merged structure** — identify unique sections, overlapping content, logical flow
3. **Write monolithic main.tex** — one `write_file()` with all merged content
4. **Generate figures** — new architecture diagrams, combined models
5. **Compile and iterate** — 10+ rounds of refinement

---

## 3. Figure Generation

### Scientific Figure Style Guide
- **Professional color palettes** — use hex codes, avoid rainbow gradients
  - Blues: `#2C5F8A`, `#4A90A4`, `#1E4D7A`
  - Greens: `#5BA06B`, `#4BA05A`, `#1B5E20`
  - Reds: `#C8374B`, `#D94F5C`
  - Oranges: `#D4872C`, `#E8913A`
  - Purples: `#7B68AE`, `#9B7DB8`
- **White background** — `facecolor='white'`
- **Clear layer labels** — use `FancyBboxPatch` for rounded boxes, `FancyArrowPatch` for arrows
- **Consistent font sizes** — 7-11pt for labels, 13-15pt for titles
- **Proper legends** — include legend for color-coded elements
- **High DPI** — `dpi=200` minimum
- **Use `plt.close()`** after saving to free memory
- **Use `bbox_inches='tight'`** for clean borders
- **Use `plt.tight_layout()`** before saving

### Figure Generation Pattern
```python
# 1. Write Python script
write_file('figures/generate_fignname.py', python_code)

# 2. Execute script
terminal('cd /path/to/figures && python3 generate_fignname.py')

# 3. Reference in LaTeX
# \includegraphics[width=0.95\textwidth]{figures/fignname.png}

# 4. Recompile
terminal('pdflatex -interaction=nonstopmode main.tex')
```

### Common Figure Pitfalls
- **FancyArrowPatch**: Does NOT accept `style=` or `linestyle=` — these are `matplotlib.lines` parameters. Use `arrowstyle=` only.
- **SyntaxError with repeated kwargs**: `arrowstyle='->', arrowstyle='-|>'` — remove duplicates
- **matplotlib.use('Agg')**: Must be set BEFORE any other matplotlib imports for headless rendering
- **FancyBboxPatch**: Use `facecolor='none'` NOT `facecolor='transparent'` — matplotlib's `colors.to_rgba` throws ValueError on `'transparent'`
- **Multi-Model Grid Sizing**: When plotting N models, use at least N columns. Putting 4 models in a 3-column grid (`plt.subplots(4, 3, ...)`) causes index errors. Always size the grid to accommodate all models.
- **Figure replacement breaks cross-references**: When replacing an old figure with a new one, update ALL `\\ref{}` and `\label{}` references in the .tex file. Search the entire file for the old label name before patching.
- **Float specifier behavior**: `!h` is unreliable — LaTeX often auto-converts to `!ht` and still moves it. Use `[t]` (top) for figures that should sit above surrounding text, or `[!ht]` for more flexibility.
- **Orphaned figure floats**: After adding or moving a `\\begin{figure}` block, verify that the float is placed in (or immediately before) the section whose prose first calls `\\ref{fig:X}`. If the figure is defined below the referencing paragraph, LaTeX will defer it far downstream in the PDF, which looks like a broken layout. Always do a paired search: find `\\label{fig:name}` and the matching `\\ref{fig:name}` and confirm they are in the same or adjacent sections. When restructuring sections (e.g. moving the Hermes diagram into the L0→L4 section), also remove any redundant duplicate subsection that described the same figure/content in the old location.
- **Duplicate Discussion section header**: When patching large multi-section papers and a `\\section{...}` near the old patch location accidentally remains with the *same name* as the Discussion section (e.g. from an old "Hermes as a user-facing assistant" block that was refactored), it renders as a phantom duplicate section. After every structural patch, scan for `\\section{` tags and confirm each section name appears exactly once.
- **Compilation requires 3 passes after figure changes**: First pass generates new labels, second resolves references, third stabilizes any shifts. Always check `.log` for "Label(s) may have changed" warnings.
- **`draft` mode fallback**: When image files aren't ready yet, use `\\usepackage[draft]{graphicx}` so missing images fall back to placeholder boxes instead of erroring.

---

## 4. Compilation Rules

### Compilation Chain
```bash
cd /home/hermes/<article-slug>/
rm -f main.aux main.log main.out main.toc main.bbl main.blg  # clean stale files first
pdflatex main.tex              # Pass 1: generates .aux, .toc, bibliography entries
bibtex main                    # Run BibTeX to resolve citations
pdflatex main.tex              # Pass 2: resolves cross-references, citation numbers
pdflatex main.tex              # Pass 3 (optional): fixes TOC, cross-reference shifts
```

### Practical Compilation Pitfalls
- **Missing images**: Always use `\\usepackage[draft]{graphicx}` so missing images fall back to draft boxes
- **`\\textquote{}` is NOT standard LaTeX**: Requires `csquotes` package — use standard LaTeX ``quotes'' or `\\textit{}` instead
- **At least 2 pdflatex passes + bibtex** are required for citations to resolve
- **Clean stale aux files** before compiling to avoid phantom "undefined reference" warnings
- **Use `\\bibliographystyle{plainnat}`** + `\\bibliography{references}` for traditional BibTeX
- **Don't mix biblatex and traditional BibTeX** — pick one and remove the other
- **Journal class not found**: Custom journal classes (e.g. `aa.cls`, `mnras.cls`) are often not installed on fresh systems. Install to `/home/hermes/texmf/tex/latex/` after verifying with `kpsewhich <class>.cls`. For `aa.cls`, use NASA mirror: `curl -sL https://fits.gsfc.nasa.gov/standard30/aa.cls -o /home/hermes/texmf/tex/latex/aa.cls` (A&A server at aanda.org frequently returns 504).
- **BibTeX vs biblatex mismatch**: Some journal classes (e.g. `aa` v7.0) are designed for traditional BibTeX. Using `\\usepackage[style=aa]{biblatex}` will fail with "Style 'aa' not found." Always check the class documentation — if it uses `\\bibliographystyle{}`, use BibTeX with `bibtex` in Makefiles, NOT biber.
- **texmf home location**: On this system, `kpsewhich -var-value=TEXMFHOME` returns `/home/hermes/texmf` (NOT `~/.texlive/`). Place custom classes in `/home/hermes/texmf/tex/latex/`.

### Compilation Verification
Check `tail -5` for "Output written on main.pdf (N pages)". For large papers, check the `.log` file for warnings.

---

### Exposé Page-Count Control
For exposés and other short documents where a specific page count matters:

1. **Use `article` class, NOT `report`** — `report` auto-creates page breaks for every `\chapter`, making page count control nearly impossible. `article` with manual `\newpage` commands gives precise control.

2. **Remove the TOC** — `\tableofcontents` consumes a full page. For exposés, omit the TOC entirely.

3. **Use `\vspace*{-2cm}`** before the title block to compress the first page.

4. **Delete unnecessary `\newpage`** — Start with your usual section breaks, compile, then remove `\newpage` commands one at a time until the target page count is reached. Each removal merges two sections onto the same page.

5. **Tighten title block spacing** — Reduce `\\vspace{}` and `\\[mm]` values in the title block; every 1mm saved matters when you're one page over.

6. **Verify with compilation** — `pdflatex expose.tex` → check "Output written on expose.pdf (N pages)".

### Minimal Exposé Template
```latex
\documentclass[11pt, a4paper, oneside]{article}
\usepackage{geometry}
\geometry{margin=2cm}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.5ex}

\begin{document}
\pagestyle{empty}
\vspace*{-2cm}
\begin{center}
{\huge\textbf{Exposé}}\\[2mm]
{Masterarbeit / Bachelorarbeit}\\\\[4mm]
\textbf{\Large Title Here}
\end{center}
\newpage
\section{Content}
...
\end{document}
```

### Common LaTeX Pitfalls

- **Duplicate packages**: `\\usepackage{hyperref}` often duplicated via patches — check full file before patching
- **Package conflicts**: `biblatex` vs traditional BibTeX — pick one
- **Unused packages**: Remove unused `tcolorbox`, `mdframed`, `siunitx`, `csquotes` if not referenced
- **Missing `\\usepackage{titlesec}`**: If using `\\titleformat`, must include `titlesec`
- **Sibling overwrites**: If another agent touched the same file, always `read_file` first
- **Pagination on read_file**: Always read full file before writing — partial reads + `write_file` can corrupt
- **Section files not used**: If you create `sections/*.tex` but don't `\\input{}` them, they're dead weight — clean them up
- **Subprocess encoding**: When automating LaTeX compilation, use `errors='replace'` for stderr

- **Polish Strategy:** When refining introduction/conclusion sections for maturity-model papers, focus on making the operational context explicit: preserve the computational path, define the DRP tuple strictly, and remove conversational filler. Each revision should bring the prose closer to the high-density professional standard of the "Rising Cards" diagrams.
- **Journal-grade upgrade:** when the user asks to turn a conference-style manuscript into a refereed-journal paper, follow `references/journal-upgrade-checklist.md` — verified refs (CrossRef API recipes) → formal numbered definitions → shipped reference implementation in `code/` → real measured evaluation with machine-readable `results/*.json` → results figures generated only from that JSON → prose keyed to measurable claims + limitations + availability/AI-disclosure statements. Also covers: webofc `amsthm`/`\openbox` clash (drop amsthm), pifont `\ding{192}`+ Unicode ①–⑤ circled-numeral pairing between figure and caption, and the linear-pipeline → swim-lane figure redesign recipe with renderer-bbox verification.
- **Large-File write_file Stream Timeout (CRITICAL)**
`write_file` calls with body > ~8 K tokens will time out mid-stream and produce **no output** (no file written, no error returned to the agent). This is the single most common silent failure when writing full paper bodies.

**Pattern to avoid**: one giant `write_file` with the entire merged LaTeX body.

**Safe pattern**:
1. Split the body into 2–4 logically coherent chunks, each < ~8 K tokens (~600 lines of dense LaTeX).
2. Write each chunk as a separate file (`main-body-part1.tex`, `main-body-part2.tex`, …).
3. Concatenate: `cat main-body-part1.tex main-body-part2.tex ... > main-body-merged-full.tex`
4. Point the wrapper via `\input{main-body-merged-full}` (no `.tex` extension needed).
5. Delete the part files once the merged file compiles cleanly.

```bash
# Step 3 example (3-part body):
cat main-body-merged.tex main-body-merged-part2.tex main-body-merged-part3.tex \
    > main-body-merged-full.tex
wc -l main-body-merged-full.tex  # sanity check
```

This pattern is always safe: even if some parts are small, splitting never breaks anything; a single oversized write_file silently discards the entire file.

### Patch-Induced Corruption (CRITICAL)
When using `skill_manage(action='patch')` or `patch` on LaTeX files:
- **Doubled backslashes**: The patch tool can mangle `\\` — a single `\` in the old_string may produce `\\` in the result (escaped literal backslash). Always verify the patched lines with `read_file` immediately after patching.
- **`\begin`, `\maketitle`, `\input` lines are especially vulnerable**: Even a simple replacement of `\begin{document}` in a wrapper file can turn into `\\begin{document}`, causing a LaTeX "Missing \begin{document}" fatal error that looks completely unrelated. After any patch that touches the LaTeX preamble or document skeleton lines, immediately run `grep -n 'begin\|maketitle\|input' file.tex | head -20` to confirm the backslashes are single. Fix with `sed -i 's/\\\\begin{document}/\\begin{document}/'` etc. — sed is safe here because you are replacing exact literal double-backslash sequences, not doing regex expansion.
- **Mangled escape sequences**: `\\_` for underscore in text mode can become `\\\\_`. `\\item` can become `\\\\item`. `\\textbf` inside `$...$` produces compilation errors.
- **Mitigation**: After any `patch` on LaTeX, scan the affected lines for `\\` and fix with a post-patch Python cleanup script. For major changes, prefer `write_file` over patching.
- **Python cleanup pattern**:
  ```python
  content = content.replace('\\\\_', '\\_')
  content = content.replace('\\\\item ', '\\item ')
  content = content.replace('\\\\textbf{', '\\textbf{')
  content = content.replace('user\\\\_A', 'user\\_A')
  ```
- **Beamer-specific note**: If the patched frame contains `verbatim` or ASCII tree content, also convert the frame to `\\begin{frame}[fragile]{...}` before recompiling, otherwise the first compile error may look unrelated to the actual content change.

### Math in Paragraph Text

- **`\text{}` is NOT standard** without `amsmath` — use `\mathrm{}` for upright text in math mode, or wrap the entire phrase in `$\mathrm{...}$`.
- **`\textbf{}` inside `$...$` fails** in many contexts — use `\mathbf{}` or `\boldsymbol{}` instead, or restructure to avoid bold inside math mode.

### Float Specifiers
- **`!h` is unreliable** — LaTeX often refuses to place floats exactly where requested. Use `!ht` or `!ht!` instead. The `!` override can cause overfull pages if the float cannot fit at the original position.
- **`[t]` (top) and `[b]` (bottom)** are more flexible than `[h]` (here) for figures/tables in long documents.

### Compilation Verification
- **2 pdflatex passes required** — first pass generates cross-references, second pass resolves them. If you see "undefined reference" warnings on pass 1, rerun.
- **Check for "Output written on main.pdf (N pages)"** in the last 5 lines of the log to confirm successful compilation.

---

## 6. MNRAS / Journal Submission Package

### MNRAS Class
```latex
\documentclass[fleqn,usenatbib,useAMS]{mnras}
```

### Portable Preamble (no newtxtext/newtxmath for portability)
```latex
\usepackage[T1]{fontenc}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{tabularx}
\usepackage{array}
\usepackage{enumitem}
\usepackage{xcolor}
\usepackage{hyperref}
```

### Key MNRAS Pitfalls

**1. Avoid `newtxtext,newtxmath` for portability** unless you know they are installed.
Common failure on Ubuntu: `! LaTeX Error: File 'newtxtext.sty' not found.`
Remove both `ae,aecompl` and `newtxtext,newtxmath` for portability.

**2. `longtable` is NOT valid in MNRAS two-column mode**
Error: `Package longtable Error: longtable not in 1-column mode.`
Replace with `table*` + `tabularx`:
```latex
\begin{table*}
\centering
\caption{...}
\label{tab:...}
\small
\begin{tabularx}{\textwidth}{...}
...\end{tabularx}
\end{table*}
```

**3. Convert inline bibliography to BibTeX**
```latex
\bibliographystyle{mnras}
\bibliography{references}
```
Place entries in `references.bib`. For arXiv-heavy drafts, pragmatic entries are acceptable.

### Submission Package Layout
```
mnras_submission_package/
  main.tex
  references.bib
  compile.sh          # latexmk -pdf main.tex fallback to pdflatex/bibtex
  README.txt          # compile instructions
  figures/
    README.txt
  notes/
    manifest.json
    package_notes.txt
```

### Ubuntu Package Requirements
```bash
sudo apt update && sudo apt install -y \
  latexmk texlive-latex-base texlive-latex-extra texlive-fonts-recommended \
  texlive-publishers biber texlive-science
```

### Build Commands
Preferred:
```bash
latexmk -pdf -interaction=nonstopmode main.tex
```
Fallback:
```bash
pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```

### arXiv Metadata Pitfall
The arXiv API returns IDs like `2603.26953v1`, not bare `2603.26953`.
Strip version suffix: `re.sub(r'v\d+$', '', arxiv_id)`

### Non-Fatal Warnings (OK to ignore)
- Font size substitutions
- Underfull/overfull boxes
- Duplicate destination warnings for tables

### Fatal Blockers (Must Fix)
- Missing `.sty` files
- `longtable not in 1-column mode`
- Unresolved bibliography (missing `.bbl` generation)

---

### Citation Rules

- Never invent references, DOIs, page numbers, or experimental results
- If a citation is needed but not provided, insert a clear placeholder: `% TODO: add citation`
- Keep factual claims appropriately qualified when sources are missing
- For arXiv entries, pragmatic BibTeX entries are acceptable
- Use `plainnat` or `mnras` bibliography style depending on target journal
#### Handling undefined citation keys (recommended safe procedure)

When a LaTeX build reports "undefined citation" warnings for specific citation keys (for example placeholder or 2026-preprints), follow this conservative, auditable sequence. This expands the previous guidance with robust fallbacks for automated tool timeouts, provenance capture, and a small, interactive append script.

1. Reproduce and capture the failure
   - Run a clean, deterministic build: `make clean && make -j1 main.pdf` and save the `main.log` and `main.aux` files.
   - Inspect the last 150 lines of `main.log` for `Citation `...` undefined` messages and the list of keys.

2. Search local bibliography
   - `rg "<KEY>" references.bib || true` to confirm the key is absent. If present but duplicated, report it instead of sweeping.

3. Conservative automated lookups (OPTIONAL, run only with user approval)
   - Use the provided helper workflow: run an automated sweep that queries CrossRef, arXiv, and ADS (public endpoints) for likely matches, but DO NOT let the sweep write directly to `references.bib`.
   - The sweep MUST write its results to `references/_autofetch_candidates.bib` and include per-entry provenance comments (timestamp, source URL or DOI, and the search query).
   - Practical robustness: the automated steps should tolerate network/timeouts by (a) retrying a small fixed number of times, (b) falling back to a minimal placeholder entry when no canonical record is found, and (c) never overwriting existing entries.
   - If web-based lookups (web_extract / execute_code) time out or fail, the sweep should still produce a candidates file with conservative placeholders so the project can build and the user can review suggestions.

4. Inspect candidates and vet manually
   - Open `references/_autofetch_candidates.bib` and verify each candidate's authors, title, year, DOI/arXiv id, and entry type (article, inproceedings, misc).
   - Correct escaped characters and author lists; the automated transform often needs minor cleanup (commas, accent marks, braces).
   - For ambiguous matches, prefer the DOI or arXiv id as the authoritative anchor.

5. Backup and commit policy (user-preference embedded)
   - Before applying any automated or bulk edits to `references.bib`, create a local backup git branch: `git checkout -b backup/bib-sweep-YYYYMMDD` and commit current state: `git add references.bib && git commit -m "chore: backup before bib sweep"`.
   - Append vetted entries using the interactive helper script `scripts/append_bib_from_candidates.py` (see skill `scripts/`) — the script prompts per-entry and writes provenance comments above each inserted BibTeX entry.
   - Commit with a descriptive message: `git add references.bib && git commit -m "chore: add N automated bib entries (provenance in-file)"`.
   - Do NOT push or rewrite history without explicit user approval. The user (arm2arm) prefers a preserved local backup branch before any destructive history edits.

6. Rebuild and verify
   - Re-run `make clean && make main.pdf` (or the Makefile targets you normally use). Confirm `main.log` no longer contains the undefined-citation warnings and that the paper compiles successfully.
   - If some keys remain undefined, either (a) the lookup failed and manual sourcing is required (ask the user), or (b) the citation was a stray / placeholder — remove or replace it.

7. Deliverable and changelog
   - Produce a short changelog entry describing which keys were added, their provenance URLs/DOIs, the backup branch name, and the commit hashes. Store that under `references/autofetch-bib.md` and attach it to the commit message.
   - Keep the `_autofetch_candidates.bib` file as an auditable record — do not delete it automatically. It should remain in the repo for provenance.

Robust fallback rules and tool-timeout behaviour
- If a networked lookup (CrossRef, arXiv, ADS) fails or times out when executed by `execute_code` or `web_extract`, the tool should:
  1. Retry at most 2 more times with exponential backoff (2s → 6s).
  2. If still failing, write a conservative placeholder entry into `_autofetch_candidates.bib` with a `% TODO` comment and the attempted query string and timestamp.
  3. Commit the candidates file on a new backup branch (see Step 5) so the user can inspect what the sweep produced.
- Never auto-append fetched entries to `references.bib` without explicit human approval.

Small helper script (recommended)
- `scripts/append_bib_from_candidates.py` — interactive script that reads `references/_autofetch_candidates.bib`, shows each candidate with provenance, prompts the user to (A) accept and append to `references.bib`, (B) edit inline before appending, (C) skip, or (D) mark as manual (leave as TODO). The script writes provenance comments above each appended entry and backs up `references.bib` to `references.bib.bak` before editing. The helper script is now installed as `scripts/append_bib_from_candidates.py` and a README `templates/append_bib_README.md` is included in the skill to explain safe usage and the recommended backup branch policy.

Notes / Pitfalls
- Automated lookups may return multiple candidate works for ambiguous keys: prefer manual confirmation. Treat all automated additions as suggestions until the user approves the commit.
- Do not assume the presence of ADS or CrossRef credentials; the template script uses public endpoints and gracefully degrades if rate-limited.
- If a missing-citation key is a future preprint (e.g. 2026 keys) and the canonical BibTeX is not yet published, annotate the key with a temporary pragmatic entry and mark it `% TODO: replace with canonical entry when available`.
- When merging a large merged body into the driver `main.tex`, prefer the include/wrapper pattern (driver `\input{main-body-merged-full}`) rather than embedding the entire body inline. This avoids oversized write_file calls, reduces risk of timeouts, and keeps the driver small and auditable.

Pointers added in this skill:
- `references/_autofetch_candidates.bib` — canonical location for automated suggestions (do not overwrite; keep for provenance)
- `scripts/append_bib_from_candidates.py` — interactive appender (see skill `scripts/`)
- `references/autofetch-bib.md` — short changelog template and example (see skill `references/`)


### Supported Reference Files

The skill's `references/` directory contains domain-specific knowledge and session notes:

- references/agentic-astronomy-session-2026-06-04.md — session notes, commands, and artifacts for the "agentic-astronomy-paper" project (path: /home/hermes/tmp/agentic-astronomy-paper).
- references/appendix-json-formatting.md — handling long JSON verbatim blocks in appendices: fvextra, breakable verbatim, listings/minted options, and conversion-to-image fallback with example commands.
- references/drp-paper-session-guidance.md — short session-specific guidance for DRP paper workflows and screenshot capture.
- `references/agent-assisted-paper-disclosure.md` — How to disclose agent-assisted writing consistently across paper, acknowledgements, and slides without overstating automation
- `references/aa-class-pitfalls.md` — A&A journal class gotchas: 5-part abstract format, `\\mail{}` for correspondence, no biblatex, `\\thanks` pitfalls, error transcript from session SH26
- `references/multi-file-paper-structure.md` — When to use multi-file vs monolithic paper structure, directory conventions, and pitfall checklist
- `references/journal-class-troubleshooting.md` — Custom journal class installation, class location on this system
- `references/ml-model-comparison-hpc.md` — Guidelines for comparing ML models on tabular HPC data
- `references/python-pandas-pitfalls.md` — Common pandas/matplotlib/Python installation pitfalls
- `references/webofc-conversion.md` — EPJ Web of Conferences conversion details and doiEDPS shims

The skill's `scripts/` directory contains:

- `scripts/scaffold-paper.py` — Create a new multi-file LaTeX paper project with Makefile, chapters, and analysis template
- `scripts/epj_compile.sh` — Automated EPJ compilation workflow script

The skill's `templates/` directory contains:

- `templates/aa-paper.tex` — A&A journal template with 5-part abstract, `\\mail{}`, traditional bibliography, and chapter structure
- `templates/expose-article.tex` — Minimal exposé template for short academic documents
- `templates/webofc-main.tex` — Minimal EPJ Web of Conferences template
- `templates/doiEDPS.sty` — Helper DOI macros style template

---

## 7. Conversation-to-Report Synthesis

When the user says "wrap up our discussion into a report/paper" or similar, the conversation may be in a past session JSONL file, not in the current context. This section covers the full pattern.

## 8. Session-derived updates (2026-06-04 — agentic-astronomy-paper)

Lessons captured from a recent edit cycle while preparing the "agentic-astronomy-paper" (branch: backup/appendix-l0l4-20260604). These are class-level, reusable practices that should be consulted whenever performing bibliography sweeps, large LaTeX edits, or repository-level packaging for reproducible-research papers.

Key additions (why this matters)
- Memory API limits can interrupt long agent sessions. When persistence via the memory tool fails or is unreliable, write a small SESSION metadata file into the project repo (SESSION_DRPHUB26.txt) so the session state is auditable and reproducible by humans and future agents.
- Always create a local backup git branch *before* any bulk or destructive edits (naming pattern: backup/<purpose>-YYYYMMDD). Commit the current references.bib and any build artifacts that the sweep might touch. This preserves a rollback point and satisfies reviewers who expect non-destructive provenance.
- Bib sweep workflow: never write automated candidate BibTeX entries straight into references.bib. Instead:
  1. Write automated results to references/_autofetch_candidates.bib with per-entry provenance comments (query, source URL/DOI/arXiv id, timestamp).
  2. Commit the candidates file on a backup branch so the candidates are auditable independently of the main bibliography.
  3. Vet entries manually or via an interactive script (scripts/append_bib_from_candidates.py) and append vetted entries into references.bib with provenance comments.
  4. Commit the updated references.bib to the same backup branch with a clear message.
- Do not leave malformed BibTeX stubs in references.bib. During a sweep we observed stub blocks (partial @article stubs) cause BibTeX parsing errors. Remove or fully replace stubs before running bibtex. The safe pattern is to (a) clean stubs, (b) run a single pdflatex → bibtex → pdflatex ×2 cycle, (c) inspect /tmp/bibtex.log, and (d) fix any remaining parse/format errors.
- Long-running CLI commands called from the agent can hit foreground timeouts. Prefer background=true with notify_on_complete=true for long jobs, or split the compile chain into shorter sequential commands the agent can run and check between steps. Capture logs (/tmp/pdflatex1.log, /tmp/bibtex.log, etc.) and attach them to the commit or session file for auditing.

Minimal checklist to apply when doing a bib sweep or large structural edit
- [ ] Create backup branch: git checkout -b backup/<purpose>-YYYYMMDD
- [ ] Commit current references.bib and _autofetch_candidates.bib if present
- [ ] Run automated sweep (if requested), write to references/_autofetch_candidates.bib
- [ ] Commit candidates file on the backup branch
- [ ] Vet candidates interactively (scripts/append_bib_from_candidates.py)
- [ ] Merge vetted entries into references.bib; remove any malformed stubs
- [ ] Run pdflatex → bibtex → pdflatex ×2 and inspect logs in /tmp
- [ ] Commit references.bib and logs with a descriptive message

Pitfalls / gotchas
- Patching LaTeX preamble lines is dangerous: escaped backslashes can double and break compilation. After any patch touching `\begin{document}`, `\input{}`, `\maketitle`, or package lines, run a short post-patch sanity check and a single pdflatex pass.
- If bibtex reports "I was expecting a `,' or a `}'" lines, it usually means a malformed or truncated BibTeX entry is present. Search for incomplete `@` entries and remove or correct them before continuing.
- Keep `_autofetch_candidates.bib` in the repo for provenance — do not delete it automatically.

Where to look in the skill for tools that implement these patterns
- scripts/append_bib_from_candidates.py — interactive appender (use this to vet & append candidates)
- references/autofetch-bib.md — changelog template and provenance example

These updates are intentionally short and prescriptive: they convert recurring manual judgments (backup-first, candidates-commit, session-file fallback) into a small checklist that agents and human collaborators can follow reliably.


### Step 1: Locate the Relevant Session

The current session may have zero prior messages. Check for the most relevant session file:

```bash
# List recent session files sorted by modification time
ls -lt /home/hermes/.hermes/sessions/*.jsonl | head -10

# If you know the date, narrow it down
ls -lt /home/hermes/.hermes/sessions/20260508_*.jsonl
```

### Step 2: Parse the JSONL Session File

Session files are line-delimited JSON with roles (`user`, `assistant`, `tool`, `session_meta`). Use Python to extract content:

```python
import json

with open('/home/hermes/.hermes/sessions/<session-file>.jsonl', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    entry = json.loads(line)
    role = entry.get('role', 'unknown')
    content = entry.get('content', '')
    # role tells you who spoke; 'tool' entries contain MCP/API responses
```

**Key pitfall**: `read_file` on a JSONL file returns raw JSON lines, which are not human-readable. Always parse with Python first to extract structured content.

### Step 3: Identify Key Discussion Points

Look for:
- **User's initial question/request** (Line 1 or near start) — this is the goal
- **Assistant's analysis/answers** — core content to synthesize
- **Tool outputs** (arXiv results, API responses, web search) — these are factual anchors
- **User corrections or follow-ups** — show where the assistant revised its reasoning
- **Final state** — what was the last agreed-upon conclusion?

### Step 4: Synthesize into LaTeX

Structure the report around the discussion flow:

1. **Abstract** — one-paragraph summary of the problem and conclusion
2. **Introduction** — the user's original question/motivation
3. **Analysis / Discussion** — the core technical content (equations, physics, reasoning)
4. **Practical Recommendations** — actionable next steps, frameworks, or plans
5. **Conclusions** — final summary of findings

**Use a minimal preamble** (no citations needed for a discussion summary):
```latex
\documentclass[11pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{amsmath, amssymb}
\usepackage{geometry}
\usepackage{enumitem}
\usepackage{booktabs}
\usepackage{hyperref}
\usepackage{microtype}
\geometry{a4paper, margin=1in}
\hypersetup{colorlinks=true, linkcolor=blue, urlcolor=blue}
```

**Avoid**: BibTeX references (the session itself is the source), complex figure generation (unless the discussion contained plots), multi-file structure (monolithic is best for reports).

### Step 5: Compile and Deliver

```bash
cd /home/hermes/<report-slug>/
rm -f *.aux *.log *.out *.toc *.bbl *.blg
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

Upload the resulting PDF via S3:
```bash
python3 ~/.hermes/scripts/s3_media_upload.py /home/hermes/<report-slug>/main.pdf
```

Then send the S3 URL in the response.

### Pitfalls Specific to This Pattern

- **Fresh session with no context**: If the conversation is in a previous session, don't try to guess the content. Parse the JSONL file directly.
- **Tool output truncation**: Session JSONL may contain truncated tool responses (especially arXiv web extract results). Don't include truncated content in the report — synthesize only what is fully visible.
- **Session files can be large**: Some sessions are 1MB+. Use `tail` or Python iteration to read only what you need; don't load the entire file into memory at once if it's very large.
- **Role confusion**: `session_meta` entries have empty content. Skip them. `tool` entries may contain long API responses — distinguish between the tool output and the assistant's interpretation of it.
- **No discussion to summarize**: If the most recent session is from a different topic, double-check before proceeding. The session metadata includes a message count — a session with only 2-3 messages may not have enough content.