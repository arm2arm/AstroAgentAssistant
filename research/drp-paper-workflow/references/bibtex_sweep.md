BibTeX sweep procedure

1) Search arXiv canonical BibTeX: https://arxiv.org/bibtex/<arXivID> (save payload)
2) For DOIs: use CrossRef API or doi.org content negotiation (curl -LH "Accept:application/x-bibtex" "https://doi.org/<doi>")
3) Normalize bibkey to `AuthorYearShortTitle` (e.g. Wang2026AstroRAG). Prefer author family name + year + short title fragment.
4) Insert into references.bib and run `make` (pdflatex->bibtex->pdflatex x2).
5) If undefined citations remain, inspect main.aux for missing keys and fetch until resolved.
6) Commit references.bib and rebuilt main.pdf locally.

Notes:
- For preprints with multiple authors, prefer the first author family name for the bibkey.
- Avoid overly long bibkeys; keep under ~40 chars.
