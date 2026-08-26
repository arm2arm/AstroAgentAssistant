#!/bin/bash
# scripts/latex_build_bg.sh
# Deterministic 3-pass LaTeX build helper for agent runs.
# Usage: run from project root where main.tex resides.
set -euo pipefail
OUTLOGS_DIR="./build_logs"
mkdir -p "$OUTLOGS_DIR"

# Pass 1
pdflatex -interaction=nonstopmode main.tex 2>&1 | tee "$OUTLOGS_DIR/pdflatex_pass1.txt"
# BibTeX
bibtex main 2>&1 | tee "$OUTLOGS_DIR/bibtex.txt" || true
# Pass 2
pdflatex -interaction=nonstopmode main.tex 2>&1 | tee "$OUTLOGS_DIR/pdflatex_pass2.txt"
# Pass 3
pdflatex -interaction=nonstopmode main.tex 2>&1 | tee "$OUTLOGS_DIR/pdflatex_pass3.txt"

if [ -f main.pdf ]; then
  echo "Success: main.pdf created" | tee "$OUTLOGS_DIR/build_status.txt"
else
  echo "Failed: main.pdf missing; check $OUTLOGS_DIR for logs" | tee "$OUTLOGS_DIR/build_status.txt"
  exit 2
fi
