#!/bin/bash
# scripts/epj_compile.sh -- deterministic build for webofc-converted papers
# Usage: ./scripts/epj_compile.sh <main.tex without extension>

set -euo pipefail
main=${1:-main-webofc}
logdir=build_logs
mkdir -p "$logdir"
{
  echo "=== Build start: $(date -u) ==="
  echo "Main: $main"
  echo "Listing files:"
  ls -1
  echo "---- pdflatex pass 1 ----"
  pdflatex -interaction=nonstopmode "$main.tex"
  echo "---- bibtex ----"
  bibtex "$main" || true
  echo "---- pdflatex pass 2 ----"
  pdflatex -interaction=nonstopmode "$main.tex"
  echo "---- pdflatex pass 3 ----"
  pdflatex -interaction=nonstopmode "$main.tex"
  echo "=== Build end: $(date -u) ==="
} &> "$logdir/${main}_build.log"

# Create submission ZIP
zipfile="${main}_submission.zip"
zip -r "$zipfile" "$main.tex" "${main}.pdf" webofc.cls woc.bst doiEDPS.sty references.bib figures/ || true

echo "Created $zipfile and logs at $logdir/${main}_build.log"
