# Overfull \hbox remediation — systematic recipe (session 2026-07-04, EPJ DRP paper)

Goal: 0 overfull warnings > 2pt in ALL build targets (main + journal wrapper). Achieved from 7 warnings (up to 103pt) in ~4 patch/rebuild cycles.

## 1. Triage: rank by severity, locate by line

```bash
grep -n "Overfull \\\\hbox" main.log | awk -F'[()]' '{print $2, $0}' | sort -rn | head
sed -n '<line>p' main.tex   # log line numbers refer to SOURCE lines in the paragraph message
```

Treat < 2–3pt as noise; fix everything above.

## 2. Fix by cause (three classes cover ~all cases)

**(a) Long verbatim/JSON lines (biggest offenders, 29–103pt).**
Verbatim never wraps — break the source lines at JSON syntax boundaries with hanging indent:

```
# before (103pt over):
    {"@type": "SoftwareSourceCode","name": "counts.py","encodingFormat": "text/x-python"},
# after:
    {"@type": "SoftwareSourceCode", "name": "counts.py",
     "encodingFormat": "text/x-python"},
```

Keep JSON valid (break after commas/braces). ~72 chars is a safe max line width for single-column; find offenders with `awk 'length($0)>72' file.tex`.

**(b) p{}-column tables that sum too wide (~17–19pt).**
Column fractions + default `\tabcolsep` (6pt × 2 × ncols) overflow. Fix: `\setlength{\tabcolsep}{4pt}` inside the table env + shave 0.01–0.02 off the widest `p{}` fractions. For header-row overflow of a few pt, abbreviate the widest header cell (e.g. "Implementation" → "Impl.").

**(c) Free-width `lll` tables with long text cells.**
Convert to fixed `p{}` columns: `\begin{tabular}{@{}l p{0.46\linewidth} p{0.34\linewidth}@{}}` — `@{}` trims outer padding, text cells wrap.

## 3. Multi-target gotcha (cost a full cycle)

The same verbatim content may exist TWICE: inlined in `main.tex` AND in an appendix file input by the journal wrapper (`appendix-l0l4.tex` via `main-webofc.tex`). Fixing main.tex only moves the warning to the other log. Fix all copies, and `grep` both logs:

```bash
grep "Overfull .hbox" main.log main-webofc.log | grep -vE "\(([0-2])\."   # empty = clean
```

Also: `make` may not track appendix deps — `touch main-webofc.tex` to force rebuild after editing an appendix.

## 4. Submission packaging verification (EPJ + arXiv)

- **EPJ tarball:** sources + `webofc.cls`, `woc.bst`, `cuted.sty`, `doiEDPS.sty` + only the figure PDFs actually `\includegraphics`'d. Include appendix files `\input` by the wrapper — easy to miss since they're not in Makefile deps.
- **arXiv tarball:** replace `references.bib`+`.bst` with the precompiled `main-webofc.bbl` (arXiv runs pdflatex only, no bibtex) + `00README.txt` naming the main file. Non-standard cls/sty MUST ship in the arXiv source.
- **Verify standalone:** extract each actual tarball into a clean temp dir, compile from there (pdflatex[+bibtex]×3), assert same page count, 0 errors, 0 undefined citations. Record sha256 of both tarballs.
