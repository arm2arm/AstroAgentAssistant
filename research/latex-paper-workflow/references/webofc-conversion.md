EPJ Web of Conferences conversion notes
Last updated: 2026-06-03 (session: git+Makefile+webofc refresh)

---

## Official macro package

URL (2025-03-28 version):
  https://www.epj-conferences.org/doc_journal/instructions/macro/web-conf/macro-latex-web-conf.zip

Contents:
  webofc.cls, woc.bst, cuted.sty, doiEDPS.sty, template.tex, README.txt,
  webofc-doc.pdf, pdf_guidelines.pdf, sample figures

Download + install command:
  curl -sL https://www.epj-conferences.org/doc_journal/instructions/macro/web-conf/macro-latex-web-conf.zip -o /tmp/webofc.zip
  unzip -o /tmp/webofc.zip -d /tmp/webofc_official/
  cp /tmp/webofc_official/macro-latex-web-conf/{webofc.cls,woc.bst,cuted.sty,doiEDPS.sty} ./

---

## Mandatory preamble (2025 template)

\documentclass{webofc}
% Optional: \documentclass[twocolumn]{webofc}

\usepackage[varg]{txfonts}   % MANDATORY — Web of Conferences font
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{microtype}
\usepackage{url}
\usepackage{hyperref}
\hypersetup{colorlinks=true,citecolor=blue,urlcolor=blue,linkcolor=blue}

---

## Author block syntax (official)

\author{
  \firstname{Arman} \lastname{Khalatyan}\inst{1}\fnsep\thanks{\email{khalatyan@aip.de}}
  \and
  \firstname{E.} \lastname{Sacchi}\inst{2}
  \and
  \firstname{H.} \lastname{Enke}\inst{1}
}
\institute{
  Leibniz Institute for Astrophysics Potsdam (AIP), An der Sternwarte 16, 14482 Potsdam, Germany
  \and
  Second affiliation
}

---

## Compile sequence

pdflatex -interaction=nonstopmode main-webofc.tex
bibtex main-webofc
pdflatex -interaction=nonstopmode main-webofc.tex
pdflatex -interaction=nonstopmode main-webofc.tex

---

## Pitfalls encountered

### Missing txfonts
The 2025 official template REQUIRES \usepackage[varg]{txfonts}. Without it, fonts
are wrong and you may see class warnings. Add it as the FIRST usepackage after
\documentclass{webofc}.

### Missing doiEDPS.sty
If the build host lacks it, add a minimal local doiEDPS.sty implementing
\doiEDPS{#1} as a hyperlink to https://doi.org/#1. The official ZIP now includes
doiEDPS.sty — just copy it from there.

### Undefined citations
Ensure the manuscript body contains citation commands. Run pdflatex once to
generate the .aux, then bibtex, then pdflatex ×2. If bibtex reports missing
entries, inspect main-webofc.aux for lines like "\citation{...}".

### Class/package duplication
Remove duplicate font packages (newtx*, txfonts if repeated) when the class
already manages fonts. Only include txfonts once in the preamble.

### Escape underscores in file names/code terms
Unescaped underscores inside document bodies (such as `license_info.yaml`) will
be interpreted as math subscript and throw confusing "missing $" errors.
Escape all plain text underscores as `\_`.

### Synchronize acronyms
When resolving acronyms or funding indicators (such as correcting "BMFTR" to
"BMBF"), ensure corrections propagate to main.tex, main-body-epj.tex, AND
slides.tex. Keep all outputs compiled and consistent.

---

## Deliverables to produce after conversion

- main-webofc.tex (working copy)
- main-body-epj.tex (extracted body, included via \input{})
- doiEDPS.sty (if a shim was added, or copy from official ZIP)
- webofc.patch (diff between main.tex and main-webofc.tex)
- main-webofc.pdf
- main-webofc.log

Submission ZIP should contain:
  webofc.cls, woc.bst, cuted.sty, doiEDPS.sty, all source .tex files,
  figures/, references.bib, scripts/epj_compile.sh, README

---

## Verification steps

1. Confirm "Output written on main-webofc.pdf (N pages)" in the last 5 lines of log.
2. Inspect main-webofc.log for fatal errors and missing .sty warnings.
3. Ensure main-webofc.bbl is created by bibtex; if not, re-run compile chain and
   verify .aux contains citation entries.

---

## Notes for future automation

- scripts/epj_compile.sh should create a clean build, copy in required class/bst
  files, run the compile chain, capture build.log, and create the submission ZIP.
  It should not attempt privileged system installs.
- Prefer creating a working copy and producing a patch (webofc.patch) rather than
  editing the user's original file in-place without review.
- When project uses a Makefile, add an `epj` target that does NOT run bibtex on
  slides (only on the paper targets that have citations).
