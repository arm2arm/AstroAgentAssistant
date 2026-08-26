# Short changelog template for bib sweeps

When we run an automated bibliographic sweep and vet candidates interactively, record a short changelog entry like this in references/autofetch-bib.md

- Date: 2026-06-08
- Backup branch: backup/bib-sweep-2026-06-08
- Files committed: references/_autofetch_candidates.bib, references.bib, build_logs/pdflatex_pass1.txt
- Keys added: smith2024, doe2025
- Provenance:
  - smith2024: CrossRef query 'Smith 2024 fair data', DOI:10.1234/example (source: crossref API) — accepted after manual vetting
  - doe2025: arXiv query 'Doe 2025 reproducible pipeline' — candidate arXiv:2501.01234v1 — accepted with note '% TODO: replace with final journal entry if available'
- Notes: one candidate (lee2026) was ambiguous and left in candidates file. Commit: 7a8b9c (append with provenance comments)
