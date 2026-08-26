# A&A (Astronomy & Astrophysics) Class — Pitfalls & Patterns

## Abstract Format (CRITICAL — session SH26, 2026-05-15)

The `aa` class (v7.0+) requires a **5-part abstract** as a **preamble command**, NOT as a LaTeX environment:

```latex
% WRONG — will cause "Environment abstract undefined" error:
\begin{abstract}
  This is the abstract.
\end{abstract}

% CORRECT — 5 arguments in the preamble:
\abstract{
  Context. Background sentences here.
}{
  Aims. Objective statement here.
}{
  Methods. Approach description here.
}{
  Results. Key findings with numbers.
}{
  Conclusions. Implications statement.
}
```

The 5 mandatory parts are: **Context**, **Aims**, **Methods**, **Results**, **Conclusions**.
Abstract must be ~300 words; >400 words triggers an error.

## Correspondence / Email (CRITICAL)

The `aa` class redefines `\thanks` to do nothing in the author field and `\url` is not available in preamble context. Use `\mail{}` instead:

```latex
\author{F. Anders\inst{2,3,4}}
% ...
\mail{fanders@icc.ub.edu}  % <-- correspondence email, rendered as footnote
```

Do NOT use `\thanks{Corresponding author: \url{...}}` inside `\author{}` — it breaks compilation.

## Bibliography (CRITICAL)

The `aa` class has its own built-in bibliography system. Do NOT use `biblatex` with this class:

```latex
% WRONG — "Style 'aa' not found" or "Style 'natbib' not found":
\usepackage[style=aa]{biblatex}
\addbibresource{references.bib}
\printbibliography

% CORRECT — traditional thebibliography environment:
\begin{thebibliography}{}
\bibitem[Author et al.(Year)]{key}
Author, A., Coauthor, B. \& Third, C. Year, Journal, Volume, Page
\end{thebibliography}
```

Also check: the class may use `\bibliography{references}` as a preamble command in some versions. Test first.

## Class Location

The `aa.cls` class is installed at `/home/hermes/texmf/tex/latex/aa.cls` (user texmf), NOT in the system texlive tree. Version 7.0+.

## Compilation Notes

- XeTeX works fine (`xelatex`), but traditional `pdflatex` is the standard
- No biblatex integration — use the built-in `thebibliography` environment
- `\maketitle` must come AFTER `\date{}` in preamble
- `\date{}` with empty argument suppresses the date on the first page

## Common Error Transcript

Session SH26 hit these errors in order:
1. "Environment abstract undefined" — tried `\begin{abstract}` environment
2. "Style 'aa' not found" — tried `\usepackage[style=aa]{biblatex}`
3. "Style 'natbib' not found" — tried `\usepackage[style=natbib]{biblatex}`
4. "Missing \begin{document}" — `\thanks{}` inside `\author{}` broke preamble parsing
5. "File `../../img/example.png' not found" — figure referenced before generated

The fix sequence was: switch to `\abstract{}` preamble command → replace biblatex with `thebibliography` → replace `\thanks` with `\mail{}` → comment out missing figures with `\usepackage[draft]{graphicx}` fallback.
