# A&A (aa.cls) monolithic → multi-file refactor + compile pitfalls — session 2026-08-23

Working example: /home/hermes/projects/SH26/doc/ (main.tex driver, main_preamble.tex,
chapters/*.tex). All steps verified by a clean 14-page compile.

## Split procedure (proven)

1. Backup branch `backup/<purpose>-YYYYMMDD` first; keep monolith as
   `main_backup_monolithic_YYYYMMDD.tex`.
2. Extract preamble (`\documentclass` .. just before `\begin{document}`) into
   `main_preamble.tex`; split body on top-level `\section{` into
   `chapters/<name>.tex`.
3. Driver = `\input{main_preamble}` + `\begin{document}` + one `\input{chapters/x}`
   per chapter + `\end{document}`. Front matter (`\maketitle`) in its own chapter.

## Pitfalls found (each caused a real failure this session)

- **Duplicate `\appendix`**: if the split leaves `\appendix` both at the end of the
  last content chapter AND at the top of `chapters/appendix.tex`, aa.cls dies with
  `Command \theapsection already defined`. Keep exactly ONE `\appendix` switch.
- **Abstract placement**: aa.cls `\abstract{..}{..}{..}{..}{..}` takes five brace
  groups and must appear in the PREAMBLE. If moved into an `\input` file, that
  file's content must START with `\abstract`. Citations (`\citet/\citep`) inside
  the abstract are fatal: "Citations are not allowed in the abstract" — replace
  with plain-text author-year mentions.
- **Bibliography lost in split**: `\bibliographystyle` + `\bibliography` were inline
  near the end of the old monolith and silently vanish. Symptom: bibtex reports
  "I found no \bibdata command" → ALL citations undefined. Re-add them in the
  conclusions chapter (or driver) and re-run the full chain.
- **Figure existence check BEFORE compiling**: extract all `\includegraphics{...}`
  names from chapters and test each against graphicspath. Renamed plots otherwise
  surface only as LaTeX file-not-found errors mid-compile.

## Compile chain & verification

```
rm -f main.aux main.bbl chapters/*.aux main.toc main.out main.blg
pdflatex -interaction=nonstopmode main.tex   # p1
bibtex main                                   # must exit 0 now
pdflatex × 2                                  # resolve refs
```

Verify: page count, `grep -c 'Warning: Citation|Reference undefined'` = 0, zero
`^!` lines, then render pages (`pdftoppm -png -r 40`) and montage for one vision
QA pass over every page.

## Content-parity check after refactor

Confirm every original section title is present in the rebuilt PDF text and the
figure-reference count matches expectations BEFORE deleting anything. Note:
`python3 -c "import fitz"` prints a deprecation warning — harmless.
