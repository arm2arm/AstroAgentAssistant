# Orchestrator verification after coding-agent stages (validated 2026-08-25, SH26 4-stage plan via dsh)

A coding-agent (e.g. dsh headless) stage ending with exit code 0 and a tidy
self-report is **not** verification. In a 4-stage repo-improvement plan the
orchestrator caught four real defects across stages, all reported "done":

1. **Claimed deletion, still on disk.** Stage reported a .bib file "Removed";
   the file still existed and was still git-tracked. Fix: `git rm` it
   yourself.
2. **Bogus page count in docs.** Stage's self-reported figure needed an
   independent recomputation from the actual includes + pypdf page counts.
3. **Untested branch, dead API.** New code used `Series.notna()` in the
   `dist_cut` branch of an aggregate function — no test exercised that
   branch, so the suite was green while the branch would raise
   `AttributeError` at runtime (dask-expr removed `notna`). Caught by
   hand-running the branch against the fixture.
4. **Tasks silently missing after context-window death.** Stage exited
   non-zero mid-run (262K context wall); the tail tasks (CI workflow,
   `make lint`) were simply never written, and the final self-report never
   existed. Diff the working tree against the task list.

## Checklist after EVERY agent stage (before committing)

1. `git status --short` / `git diff --stat` — compare changed/added/removed
   files against the task list in the prompt. Anything missing, finish it
   yourself; don't relaunch the stage.
2. Re-run the FULL test suite in one process with the exact command given
   in the prompt (report line must match or better).
3. Grep-verify each claimed side effect:
   - deleted files: `git ls-files <path>` (tracked?) and `ls` (on disk?)
   - claimed counts (page counts, column counts, plot counts): recompute
     from the artifacts (pypdf, schema, registry), never trust the report
   - new code paths: grep for the API calls the new code makes
     (`notna` etc.) and hand-run any branch no test touches
4. Lint + CLI smoke (`--help`) as specified.
5. THEN commit (the agent never commits; the orchestrator owns commits) and
   push.

## Test-suite design note

When an agent adds a feature, require **branch coverage of every new
conditional** (quality cuts on/off, dist cut set/unset, raw-column vs
derived fallback) as explicit tests — green suite + untested branch =
silent runtime breakage. The SH26 dist-cut fix above was a 1-line
`.notna()` → `.notnull()` change caught only by a 10-line throwaway
verification script.
