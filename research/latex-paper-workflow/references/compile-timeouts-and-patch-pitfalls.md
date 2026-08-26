Session-derived guidance: LaTeX compile timeouts, background builds, and patch-safety

Scope
- Condensed, actionable notes captured from the agentic-astronomy rebuild session (2026-06-08).
- Class-level: applicable to any LaTeX paper workflow where the agent compiles, patches, or runs multi-step builds.

Problems observed
- Long pdflatex runs hit the agent foreground timeout and produced partial or no PDF (exit 124) when run in-foreground.
- Automated escaping passes introduced a literal marker `<<ESC_UNDERSCORE>>` and doubled backslashes in patched LaTeX; these block compilation with Emergency stop.
- Large `write_file` calls risk silent failures when payloads exceed the tool's streaming thresholds.

Recommendations (actionable)
1) Use background builds for long LaTeX runs
   - For multi-pass builds use background execution so the agent is not killed by foreground time limits.
   - Example pattern (agent-run): start a background process or use latexmk in background with notify_on_complete=true, capture stdout/stderr to files, then poll or wait for completion.
   - Minimal reliable sequence (foreground-friendly if short):
     - pdflatex -interaction=nonstopmode main.tex
     - bibtex main
     - pdflatex -interaction=nonstopmode main.tex
     - pdflatex -interaction=nonstopmode main.tex
   - When using the Hermes terminal tool for long runs, prefer background=true + notify_on_complete=true or run smaller steps and check logs between them.

2) Capture full logs and save them in the repo
   - Save pass logs (pdflatex_pass1.txt, pdflatex_pass2.txt, pdflatex_pass3.txt) and the combined pdflatex_full_run.txt.
   - Attach these logs to commits when creating a backup branch so failures are auditable.

3) Backup-first commit discipline (user preference)
   - Always create a local backup branch before bulk or destructive edits: backup/<purpose>-YYYYMMDD (example: backup/rebuild-2026-06-08).
   - Commit current PDFs and metadata files to that branch before attempting builds or automated patches.

4) Patch safety & escaped-backslash pitfalls
   - The patch tool can double backslashes (\\ → \\\\) in LaTeX source, breaking \begin{document}, \input, \label, and \ref lines.
   - After any patch touching the preamble or document skeleton, immediately run a quick grep for doubled backslashes and a single pdflatex pass:
     - grep -n "\\\\begin{document}\|\\\\maketitle\|\\\\input" main.tex
   - If doubled backslashes are found, fix by replacing `\\\\` → `\\` on the affected lines before a full compile.

5) ESC_UNDERSCORE and intentional marker handling
   - If automated tooling injects markers like `<<ESC_UNDERSCORE>>`, restore them to the intended LaTeX (replace with `_` or `\_` depending on context) after confirming the context is a verbatim-like or JSON-literal block.
   - Prefer `\_` in normal text; prefer raw `_` inside `\texttt{}` or `verbatim` frames only when safe.

6) Safe write_file pattern for large writes
   - Avoid single giant write_file for very large LaTeX bodies (agent streaming limits). Use chunking:
     - Split into logical parts: main-body-part1.tex, main-body-part2.tex, ... (each < ~8K tokens).
     - Write each part separately, then cat/concatenate into the final file in the project workspace, or set the wrapper to \input{} the part files.
   - Verify each write with read_file immediately after writing.

7) Automated un/escaping rules
   - When mass-escaping underscores: escape only in text mode, avoid changing inside \label{}, \ref{}, \includegraphics{} keys, or inside verbatim/listing blocks.
   - When unescaping: prefer to unescape only in these syntactic contexts: label keys (e.g. `tab:repo_components`), file names inside JSON-LD fields used in appendix verbatim blocks, and \ref/\label arguments.

8) Commit artifacts and logs
   - After a successful or partially successful build, commit produced PDFs and their metadata on the backup branch with a clear message (e.g., "backup: PDFs before rebuild 2026-06-08").
   - If the build fails, commit logs (pdflatex_pass*.txt) and the modified main.tex (with backups) so debugging is reproducible.

9) Example small helper script (agent-run friendly)
- scripts/latex_build_bg.sh (conceptual)

#!/bin/bash
set -e
# run in project dir
pdflatex -interaction=nonstopmode main.tex 2>&1 | tee pdflatex_pass1.txt
bibtex main 2>&1 | tee bibtex_pass.txt
pdflatex -interaction=nonstopmode main.tex 2>&1 | tee pdflatex_pass2.txt
pdflatex -interaction=nonstopmode main.tex 2>&1 | tee pdflatex_pass3.txt
# final status
if [ -f main.pdf ]; then
  echo "Success: main.pdf created" > build_status.txt
else
  echo "Failed: main.pdf missing; check pdflatex_pass*.txt" > build_status.txt
fi

(Place scripts/latex_build_bg.sh into the skill's scripts/ directory when you want the agent to run it.)

10) When to debug vs. rebuild
   - If pdflatex fails early with a fatal error (Emergency stop, Missing \endcsname, ! Misplaced \noalign), switch to targeted debugging: inspect the log snippet, open the offending lines in main.tex and nearby table/figure environments, and fix structural problems (mismatched & columns, missing \end{tabular}, misplaced \hline/\toprule).
   - If failures are due to many undefined citations, run the bibtex pass and inspect .aux files to ensure citations are emitted in the correct .aux basename (include/wrapper pattern remedy).

Provenance & auditing
- Keep all intermediate run logs in the repository and commit them alongside the backup branch.
- Keep the pre-edit main.tex cleanup backup (main.tex.cleanup_YYYYMMDDT...) in the repo root for immediate diff and revert.

This reference file should be included under the latex-paper-workflow skill as a compact troubleshooting guide for future rebuilds and as a companion to scripts/epj_compile.sh and templates/webofc-main.tex.
