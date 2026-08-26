# LaTeX merge/automation damage checklist

Damage patterns observed in real paper repos after merges or scripted edit passes
(agentic-astronomy paper, 2026-07). Run these BEFORE compiling — they are cheaper
than parsing a broken main.log.

## 1. Artifact greps (fast probes)

```bash
# Escape-marker leftovers from automated underscore handling
grep -n 'ESC.UNDERSCORE' main.tex            # e.g. <<ESC\_UNDERSCORE>> renders literally

# Broken macros (leading backslash eaten by a script)
grep -nE '(^|[^\\])oindent|(^|[^\\])extbf|(^|[^\\])exttt' main.tex   # \noindent, \textbf, \texttt

# Editorial notes that must not ship
grep -nE 'TODO|FIXME|MEDIA:|placeholder' main.tex

# Escaped underscores inside verbatim blocks (print literally as \_)
awk '/\\begin\{verbatim\}/,/\\end\{verbatim\}/' main.tex | grep -n '\\_'
```

## 2. Structural checks

```bash
# Sections stranded after the bibliography (merge damage): the only thing allowed
# between \bibliography{...} and \end{document} is \appendix + appendix sections.
grep -n 'bibliography{\|\\appendix\|\\section' main.tex
# → verify ordering manually: numbered sections … Conclusion … \bibliography … \appendix … appendix sections

# Empty sections (heading with no body before the next heading) — read the outline:
grep -n '\\section\|\\subsection' main.tex

# Hardcoded section numbers that rot after restructuring
grep -nE 'Sect(ion)?[.~ ]+[0-9]' main.tex     # should be Sect.~\ref{...}

# Orphaned .tex content files never actually included
ls *.tex
grep -nE '\\\\(input|include)\{' main.tex
# any .tex present but not input/included = content silently missing from PDF.
# Fix: inline it (preferred if small) or add \input; never keep both copies.
```

## 3. Bib hygiene

```bash
# Keys defined vs. keys cited
grep -oE '@[a-zA-Z]+\{[^,]+' references.bib | sed 's/@[a-zA-Z]*{//' | sort > /tmp/defined
grep -oE '\\cite[tp]?\{[^}]+\}' main.tex | grep -oE '\{[^}]+\}' | tr -d '{}' | tr ',' '\n' | sort -u > /tmp/cited
comm -23 /tmp/defined /tmp/cited    # defined but never cited → cite or delete
comm -13 /tmp/defined /tmp/cited    # cited but undefined → will break bibtex
```
- Dedupe near-identical entries (same work under two keys, e.g. `Binder2018` vs
  `Jupyter2018Binder`): keep one canonical key, delete the other, re-grep cites.
- A paper that discusses FAIR / RO-Crate / PUNCH4NFDI at length should cite the
  corresponding entries (Wilkinson2016FAIR, Soiland2022ROCrate,
  WorkflowRunROCrate2024, Enke2022PUNCH) — uncited-but-relevant is a review flag.

## 4. EPJ Web of Conferences (webofc) class quirks

- `webofc.cls` issues `\bibliographystyle{woc}` internally. Do NOT add your own
  `\bibliographystyle` — just `\bibliography{references}`.
- Required in repo: `webofc.cls`, `woc.bst`, and `\usepackage[varg]{txfonts}`.
- fancyhdr footskip warning: silence with `\setlength{\footskip}{3.60004pt}` in preamble.
- Author block uses `\firstname{}\lastname{}\inst{}\fnsep\thanks{\email{}}` — not
  the plain `\author{...\\...}` style from article class.

## 5. Clean rebuild protocol

```bash
rm -f main.aux main.bbl main.blg main.log main.out main.toc
pdflatex -interaction=nonstopmode main.tex   # pass 1
bibtex main                                  # check output for Warning/Error
pdflatex -interaction=nonstopmode main.tex   # pass 2
pdflatex -interaction=nonstopmode main.tex   # pass 3 (cross-refs settle)
grep -c '^!' main.log                        # must be 0
grep -E 'Warning.*(undefined|multiply)' main.log   # must be empty
grep -c 'Overfull' main.log                  # investigate anything > ~5pt
pdfinfo main.pdf | grep Pages                # report page count to user
```

- A tiny `main.pdf` (few KB) already committed in the tree = broken previous
  build. Never trust it; always rebuild from clean aux state.
- Overfull hboxes in `p{...}` tables: the column fractions + inter-column seps
  must total < 1.0\linewidth. Shave fractions slightly (0.35→0.33) instead of
  restructuring; ≤5 pt residual overfull is sub-visible and acceptable.
