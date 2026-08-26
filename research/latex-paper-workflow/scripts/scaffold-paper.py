#!/usr/bin/env python3
"""
Scaffold a multi-file LaTeX paper project from scratch.
Usage: python3 scripts/scaffold-paper.py <project-name>

Creates:
  <project-name>/
    Makefile
    README.md
    img/
    src/
    doc/
      main.tex
      chapters/
        abstract.tex
        introduction.tex
        data_pipeline.tex
        results.tex
        discussion.tex
        conclusion.tex
      references.bib
"""

import argparse
import sys
from pathlib import Path


TEMPLATES = {
    "Makefile": """\
# SH26 — StarHORSE 2026 Data
# Makefile for paper production and analysis pipeline

.PHONY: all pdf clean latex clean-bib help \\
        analysis clean-analysis \\
        src/%.py

# ── Defaults ──────────────────────────────────────────────────────────
BUILDDOC  := doc
OUTDIR    := doc/_build
IMG_DIR   := img
LATEX     := xelatex
LATEXOPTS := -interaction=nonstopmode -halt-on-error
BIBTOOL   := biber
PYTHON    := python3
SRC_DIR   := src

# ── Paper compilation ─────────────────────────────────────────────────
all: pdf

pdf: $(OUTDIR)/paper.pdf
	@echo "✓ PDF built: $@"

latex: pdf

$(OUTDIR)/paper.pdf: $(BUILDDOC)/main.tex $(wildcard $(BUILDDOC)/*.bib $(BUILDDOC)/chapters/*.tex)
	@mkdir -p $(OUTDIR)
	cd $(BUILDDOC) && $(LATEX) $(LATEXOPTS) main.tex -output-directory=$(OUTDIR)
	@if [ -f $(BUILDDOC)/main.bcf ]; then \\
		cd $(BUILDDOC) && $(BIBTOOL) main.bcf -c -d $(OUTDIR); \\
		cd $(BUILDDOC) && $(LATEX) $(LATEXOPTS) main.tex -output-directory=$(OUTDIR); \\
		cd $(BUILDDOC) && $(LATEX) $(LATEXOPTS) main.tex -output-directory=$(OUTDIR); \\
	fi
	@echo "✓ LaTeX PDF generated"

# ── Analysis ──────────────────────────────────────────────────────────
analysis:
	@echo "Running full analysis pipeline..."
	@for f in $(SRC_DIR)/*.py; do \\
		echo "→ $$f"; \\
		$(PYTHON) $$f || { echo "✗ Failed: $$f"; exit 1; }; \\
	done
	@echo "✓ Analysis pipeline complete"

# Pattern rule: make src/foo.py → runs that single script
$(SRC_DIR)/%.py:
	@echo "→ Running $<"
	@$(PYTHON) $<
	@echo "✓ Done: $<"

# ── Cleaning ──────────────────────────────────────────────────────────
clean:
	rm -rf $(OUTDIR)
	@echo "✓ Cleaned LaTeX build files"

clean-analysis:
	@echo "Remove generated figures in img/?"
	@read -p "> " && if [ "$$REPLY" = "y" ]; then \\
		rm -f $(IMG_DIR)/*.png $(IMG_DIR)/*.pdf $(IMG_DIR)/*.svg; \\
		echo "✓ Cleaned analysis figures"; \\
	fi

clean-bib:
	rm -f $(BUILDDOC)/*.aux $(BUILDDOC)/*.bcf $(BUILDDOC)/*.blg $(BUILDDOC)/*.bbl

# ── Help ──────────────────────────────────────────────────────────────
help:
	@echo "SH26 Makefile targets:"
	@echo "  make pdf             Compile the paper LaTeX to PDF"
	@echo "  make analysis        Run all Python scripts in src/"
	@echo "  make src/foo.py      Re-run a single analysis script"
	@echo "  make clean           Remove LaTeX build artifacts"
	@echo "  make clean-analysis  Remove analysis output files"
	@echo "  make help            Show this help"
""",

    "README.md": """\
# {TITLE} — {SHORT_NAME}

[![Language](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

{DESCRIPTION}

## Project structure

```
{PROJECT}/
├── Makefile          # Build & analysis targets
├── README.md         # This file
├── LICENSE           # MIT
├── img/              # Generated figures (one image per script)
├── src/              # Python analysis scripts
└── doc/              # Paper & references
    ├── main.tex      # LaTeX manuscript (entry point)
    ├── chapters/     # One .tex per paper section
    └── references.bib   # Bibliography
```

## Quick start

```bash
# Install dependencies
pip install -r requirements.txt   # TODO: add requirements file

# Compile the paper
make pdf

# Run the full analysis pipeline
make analysis

# Re-run a single script
make src/my_analysis.py

# Clean up
make clean        # LaTeX build artifacts
make clean-analysis  # Analysis output files
```

## Adding a new analysis

1. Copy `src/template_analysis.py` → `src/your_name.py`
2. Customize the script
3. Add figures to `img/`
4. Reference them in `doc/chapters/results.tex`

## Citation

TODO: Add paper citation here.

## Contributors

TODO: Add contributors.
""",

    "main.tex": r"""\documentclass[11pt,a4paper]{article}

% ── Packages ─────────────────────────────────────────────────────────
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{geometry}
\usepackage{graphicx}
\usepackage{amsmath,amssymb}
\usepackage{hyperref}
\usepackage{booktabs}
\usepackage{caption}
\usepackage{subcaption}
\usepackage[style=apa]{biblatex}

\geometry{margin=1in}

% ── Metadata ─────────────────────────────────────────────────────────
\title{{TITLE}}
\author{{AUTHORS}}
\date{\today}

% ── Bibliography ─────────────────────────────────────────────────────
\addbibresource{references.bib}

\begin{document}

\maketitle

\input{chapters/abstract}

\input{chapters/introduction}

\input{chapters/data_pipeline}

\input{chapters/results}

\input{chapters/discussion}

\input{chapters/conclusion}

\printbibliography

\end{document}
""",

    "chapters/abstract.tex": """\
\begin{abstract}
  % TODO: Write abstract — problem, method, results, conclusion
\end{abstract}
""",

    "chapters/introduction.tex": r"""\
% ── SH26 ── Introduction ────────────────────────────────────────────
% TODO: Background, motivation, related work

\section{Introduction}
\label{sec:introduction}

% TODO: Fill in content
""",

    "chapters/data_pipeline.tex": r"""\
% ── SH26 ── Data Pipeline ───────────────────────────────────────────
% TODO: Describe the pipeline, data sources, processing steps

\section{Data Pipeline}
\label{sec:data_pipeline}

% TODO: Fill in content
""",

    "chapters/results.tex": r"""\
% ── SH26 ── Results ─────────────────────────────────────────────────
% TODO: Key findings, figures, tables

\section{Results}
\label{sec:results}

% TODO: Fill in content

\begin{figure}[t]
  \centering
  \includegraphics[width=0.8\textwidth]{../../img/example.png}
  \caption{TODO: Figure description}
  \label{fig:example}
\end{figure}
""",

    "chapters/discussion.tex": r"""\
% ── SH26 ── Discussion ──────────────────────────────────────────────
% TODO: Interpretation, context, limitations

\section{Discussion}
\label{sec:discussion}

% TODO: Fill in content
""",

    "chapters/conclusion.tex": r"""\
% ── SH26 ── Conclusion ──────────────────────────────────────────────
% TODO: Summary of findings, future work

\section{Conclusion}
\label{sec:conclusion}

% TODO: Fill in content
""",

    "references.bib": r"""\
% ── {TITLE} — references ─────────────────────────────────────────
% Add your .bib entries here

% TODO: Add key references
""",

    "src/template_analysis.py": """\
#!/usr/bin/env python3
\"\"\"
{TITLE} — Analysis template
Copy to src/your_analysis.py and customize.
\"\"\"

import argparse
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# ── Configuration ───────────────────────────────────────────────────
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "img"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    parser = argparse.ArgumentParser(description="{TITLE} analysis pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be done without running")
    args = parser.parse_args()

    if args.dry_run:
        log.info("DRY RUN — skipping actual computation")
        return

    # ── Step 1: Load data ───────────────────────────────────────────
    log.info("Loading data...")
    # TODO: Replace with actual data loading logic

    # ── Step 2: Process / analyze ───────────────────────────────────
    log.info("Running analysis...")
    # TODO: Replace with actual analysis logic

    # ── Step 3: Generate figures ────────────────────────────────────
    log.info("Generating figures...")
    # TODO: Add matplotlib figure creation and save

    log.info("✓ Analysis complete")


if __name__ == "__main__":
    main()
""",

    ".gitignore": r"""\
*.aux
*.log
*.out
*.toc
*.bbl
*.blg
*.bcf
*.pdf
__pycache__/
*.pyc
.DS_Store
""",
}

# Map of chapter keys that exist in TEMPLATES
CHAPTER_KEYS = [
    "chapters/abstract.tex",
    "chapters/introduction.tex",
    "chapters/data_pipeline.tex",
    "chapters/results.tex",
    "chapters/discussion.tex",
    "chapters/conclusion.tex",
]


def main():
    parser = argparse.ArgumentParser(description="Scaffold a multi-file LaTeX paper project")
    parser.add_argument("project_name", help="Project name (used for directory and titles)")
    parser.add_argument("--authors", default="", help="Author list (default: to be filled)")
    parser.add_argument("--description", default="", help="Short description for README")
    args = parser.parse_args()

    project = Path(args.project_name)
    if project.exists():
        print(f"Error: {project} already exists. Remove it first.")
        sys.exit(1)

    project.mkdir(parents=True)

    # Substitute placeholders
    title = args.project_name.replace("_", " ").title()
    short = args.project_name[:20].upper()
    authors = args.authors or "TBD"
    desc = args.description or ""

    for name, content in TEMPLATES.items():
        target = project / name
        target.parent.mkdir(parents=True, exist_ok=True)
        final = content.format(
            TITLE=title,
            SHORT_NAME=short,
            AUTHORS=authors,
            DESCRIPTION=desc,
            PROJECT=args.project_name,
        )
        target.write_text(final)
        print(f"  ✓ {target}")

    print(f"\nProject {project} scaffolded with {len(TEMPLATES)} files.")
    print("Next steps:")
    print("  1. Fill in doc/chapters/*.tex with content")
    print("  2. Create analysis scripts in src/")
    print("  3. Run 'make pdf' to compile")


if __name__ == "__main__":
    main()
