# LaTeX build checklist

1. Run `pdflatex main.tex` and capture output.
2. Run `bibtex main` (if using BibTeX) or `biber` as required.
3. Run `pdflatex main.tex` twice to resolve references.
4. Inspect .log for Overfull/Underfull \hbox warnings.
5. If Overfull boxes caused by inline verbatim/JSON, move the block to `.fair-metadata/` and include with `\lstinputlisting`.

