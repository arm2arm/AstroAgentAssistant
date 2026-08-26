Agentic-astronomy-paper: workflow notes & policy

Purpose
- Capture the policy and reproducible workflow for editing and polishing LaTeX papers that include agentic/LLM literature checks and citation insertion. Encapsulated under the latex-paper-workflow skill so future sessions inherit the policy.

Key policy additions (June 2026)
- When performing literature checks and citation updates in a LaTeX repo, follow this sequence:
  1. Add BibTeX entries to references.bib and commit them. Do not modify the manuscript prose first. (Rationale: avoids introducing uncommitted references that the manuscript may fail to find and creates a safe, verifiable step.)
  2. Present the user with the choice to auto-insert \cite{}s or to apply suggested insertion patches. Do NOT auto-replace textual placeholders without explicit user confirmation. (Rationale: user may want to control phrasing / blind-review constraints.)
  3. If the user authorises auto-insert, make conservative non-destructive edits: replace textual placeholders like "[IVOA VOTable spec — add citation]" with an inline citation and add a short parenthetical if the original text included bracketed explanation.
  4. Recompile the paper (pdflatex → bibtex → pdflatex x2). If compilation reports missing citations, roll back the commit and present the errors to the user.
  5. Commit the manuscript edits with a descriptive message and produce a changelog + annotated diff.

- When adding standards/registry citations (IVOA, DataCite, Zenodo), prefer @misc entries with stable URLs in references.bib and use clear BibTeX keys (e.g. IVOAVOTable2023, IVOAObsCore2017, DataCiteKernel2024, ZenodoGuide2023).

- Do NOT overwrite references.bib wholesale in one write operation. Instead use targeted append/patch operations to avoid losing pre-existing curated entries.

- Use `make -C <repo> main.pdf` for compilation after changes. If make fails due to environment differences, fallback to the explicit pdflatex → bibtex → pdflatex sequence.

- Preserve local commit history. Before applying any destructive rewrite (history rewrite, force-push), create a local backup branch named `backup/<timestamp>-pre-rewrite` and push only after explicit user approval.

- Always check for explicit placeholder strings (\[.*add citation.*\]) across the repository before finishing. Replace them only with user consent.

Repro commands
- Search for placeholders: `grep -R "add citation" . || true`
- Compile: `make -C /home/hermes/tmp/agentic-astronomy-paper main.pdf`
- Create backup branch: `git checkout -b backup/$(date -Iseconds)-pre-rewrite`
- Generate BibTeX for arXiv ID: `curl -s "https://arxiv.org/bibtex/<id>"`

Linked reference files
- references/webofc-conversion.md (webofc conversion guidance)
- references/webofc-session-arm2arm-2026-06-03.md (session notes)

