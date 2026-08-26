Session: 2026-06-02 — Agentic astronomy paper + slides

Summary of actions and useful artifacts for future runs:

- Paper and slides were compiled and uploaded to S3 via ~/.hermes/scripts/s3_media_upload.py.
  - main.pdf S3 URL: https://s3.data.aip.de:9000/scr4agent/hermes/e621d115084e473a922bae5241d68844.pdf
  - slides.pdf S3 URL: https://s3.data.aip.de:9000/scr4agent/hermes/df16059a6c2b46a08016c40b23a8156c.pdf

- User preferences (arm2arm):
  - Prefers dark background for slides: #0D1117
  - Palette: Blue #58C4DD, Green #83C167, Yellow #FFFF00
  - Prefers final PDFs delivered over Telegram; expect MEDIA:/ absolute paths to attach via Hermes
  - When editing LaTeX, create a local backup branch before any destructive git history rewrite

- Build notes (local):
  - LaTeX engine: pdfTeX (TeX Live 2023/Debian)
  - Compilation: pdflatex + bibtex (2-3 pdflatex passes). Use Makefile when present.
  - Common warnings seen: underfull \hbox; no fatal errors

- Tools & scripts used:
  - ~/.hermes/scripts/s3_media_upload.py — uploader used to publish PDFs to S3, returns a markdown link

- Patching tips (from this session):
  - After a patch that modifies Beamer theme or fragile frames, recompile twice and inspect overfull vbox warnings.
  - When adding agent-assisted writing disclosure, add parallel entries to both main.tex and slides.tex to keep artifacts consistent.

- Next-step items for the user (left as placeholders in slides/main):
  - Funding/grant numbers for: BMFTR / PhysicsLLM / PUNCH4NFDI / DFG

- Reproducibility checklist for future sessions:
  - Read full files before writing/patching (avoid partial `read_file` + `write_file` combos)
  - For major LaTeX patches, prefer `write_file` over `patch` to avoid doubled-backslash corruption
  - Ensure figures exist before compilation (run plotting scripts first)

- Where to find project files during the session:
  - /home/hermes/tmp/agentic-astronomy-paper/

This reference file is intended to be short and actionable — place it under the skill's `references/` directory so subagents and future sessions find precise, replicable commands and the user's explicit style preferences.
