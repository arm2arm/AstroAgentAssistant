DRP‑Hub session notes (drphub26)

Summary
- Session date: 2026-06-04
- Repo: /home/hermes/tmp/agentic-astronomy-paper
- Branch: backup/appendix-l0l4-20260604 (HEAD after edits)
- Key artifacts created: appendix-l0l4.tex, SESSION_DRPHUB26.txt, references/_autofetch_candidates.bib

What we did (useful reproducible steps)
1. Create a non-destructive backup branch before edits:
   git checkout -b backup/<purpose>-$(date +%Y%m%d)
2. Add appendix-file and commit:
   git add appendix-l0l4.tex main-body-merged-full.tex
   git commit -m "feat(appendix): add L0--L4 DRP examples and DRP card JSON appendix"
3. Build check (Makefile):
   make -C /home/hermes/tmp/agentic-astronomy-paper -j1 main.pdf
   (If long builds are required, run background jobs with notify_on_complete=true via automation.)
4. Bib sweep: collect candidate BibTeX entries into references/_autofetch_candidates.bib, vet manually, then append to references.bib on a new backup branch and rebuild.

Pitfalls & lessons learned
- Always create a local backup branch before destructive changes (user preference). Skill enforces this as a checklist item.
- Automated long-running scripts hit tool timeouts (execute_code 300s max, terminal foreground 600s). Use background=true with notify_on_complete=true for operations expected to take >5–10 minutes.
- Shell helper scripts can fail due to quoting or stray `fi`/`then` mismatches. Keep scripts small and test locally before batching into a long helper.
- Memory API (persistent memory) has size limits. When saving session metadata programmatically, prefer writing a session file to the repo (SESSION_DRPHUB26.txt) as a durable fallback.
- Do not auto-append auto-discovered BibTeX into the canonical references.bib without manual vetting; write candidates to references/_autofetch_candidates.bib and require human approval.

Recommended verification checklist for DRP appendices
- Appendix file present and included via \appendix+\input in main .tex driver
- DRP card JSON examples exist under appendix and a machine-readable template exists in templates/
- references/_autofetch_candidates.bib contains provenance comments for each candidate
- main.pdf and main-webofc.pdf build without "undefined citation" warnings after vetted BibTeX entries are appended

Pointers to public standards to cite
- RO‑Crate: Soiland‑Reyes et al., 2022 (Data Science / ro-crate.org)
- Workflow‑Run RO‑Crate: Leo et al., 2024 (PLOS ONE)
- Snakemake: Köster & Rahmann, 2012; Mölder et al., 2021
- REANA: Šimko et al., 2019/2021

When to update this reference note
- Add canonical BibTeX entries to references/_autofetch_candidates.bib when automated fetch succeeds
- Add a short script under scripts/ to fetch canonical BibTeX with retries and CrossRef/ADS APIs
