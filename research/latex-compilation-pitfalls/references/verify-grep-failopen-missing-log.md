# Verify-check silent bypass: grep fail-open on a missing .log

Found 2026-08-24 while finalizing the DRP-Hub journal paper (agentic-astronomy-paper Makefile).

## Symptom

`make verify` prints "Verification passed" (exit 0), but the output contains:

```
grep: main.log: No such file or directory
grep: main.log: No such file or directory
```

The overfull-box and undefined-citation/reference checks were silently skipped and the
**stale PDF from a previous session was certified as current**.

## Root cause

```make
@if grep -q 'Overfull \hbox' main.log; then echo 'FAIL: overfull boxes'; exit 1; fi
```

- `main.log` is deleted by `make clean` (log is in AUX_EXTS), and the pdf target only
  rebuilds when inputs are newer — after `make clean`, `main.pdf` exists but is newer
  than nothing, so the LaTeX build step can be skipped by make's dependency check
  (or a prior run crashed before writing the log).
- `grep` on a missing file exits 1 with no stdout — indistinguishable from "no match"
  inside an `if grep ...; then FAIL; fi` guard. Fail-open.

## Fix (apply to any Makefile with log-based verify checks)

Add an explicit log-existence guard BEFORE the greps:

```make
@test -f $(MAIN).log || { echo 'FAIL: missing $(MAIN).log - run make distclean first'; exit 1; }
@if grep -q 'Overfull \hbox' $(MAIN).log; then echo 'FAIL: overfull boxes'; exit 1; fi
@if grep -Eq 'undefined citations|undefined references' $(MAIN).log; then echo 'FAIL: unresolved'; exit 1; fi
```

## Verification habit

- For a true clean gate: `make distclean && make verify` (distclean also removes the
  PDF, so a stale artifact cannot masquerade as current).
- After any verify run, scan the output for `No such file or directory` lines.
  **A passing exit code with a missing-log grep is a false green.**
- Generalization: any `if grep -q ... file; then fail; fi` QA gate fails open when the
  input file is missing. Prefer an explicit `test -f` guard, or `grep ... || { [ ! -f file ] && exit 1; }`.
