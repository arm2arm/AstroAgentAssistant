# `Misplaced \noalign` from over-escaped table row terminators

A recurring, easy-to-misdiagnose failure when an agent (or the `patch` tool)
inserts a LaTeX table.

## Symptom
Fatal:
```
! Misplaced \noalign.
\midrule ->\noalign
l.300 \end{tabularx}
! ==> Fatal error occurred, no output PDF file produced!
```
- Reported line is the `\end{tabularx}`/`\end{tabular}` line (misleading).
- Booktabs rules (`\toprule`/`\midrule`/`\bottomrule`) are `\noalign` commands;
  TeX complains one is "misplaced."
- The build produces **no PDF** even though the document otherwise compiled
  fine up to that table.

## Root cause (verified)
A table **data row ends in 3 or 4 trailing backslashes instead of exactly 2.**
Each `\\` pair is one `\cr` row-break. A 3rd/4th stray backslash emits an
extra `\cr`, so the *next* booktabs rule (itself `\noalign`) lands where TeX
expects a cell → `Misplaced \noalign`.

How it got there: the **`patch` tool over-escaped the `\\` row terminators**
when inserting the table (the fuzzy/replace path doubled them). Not the column
spec.

## Red herring (real constraint, NOT the cause here)
`tabularx` allows **exactly one X-type column**. A spec with two `Y`/`X`
columns is itself invalid, but it does **not** produce `Misplaced \noalign` at
a rule line. Fixing the column spec alone will not clear this error. (Both bugs
can coexist; the row-terminator one is the one that stops the build at a rule.)

## Diagnosis (the sequence that actually worked)
1. **Isolate first — does the committed good version still compile?**
   ```bash
   git checkout -- main.tex
   pdflatex -interaction=nonstopmode -halt-on-error main.tex 2>&1 | tail -5
   ```
   If the restored version compiles and the working tree does not, **your edit
   introduced the bug** and the TeX installation is fine. This single test
   separates "my change broke it" from "the environment changed" and avoids
   hours of environment red-herrings (missing packages, font changes, etc.).
2. **Byte-diff the failing table against a known-good table** in the same
   document. Compare the trailing bytes of each data row.
3. **Count trailing backslashes per row in Python** — use `chr(92)`, NOT a
   shell-escaped backslash (shell `printf`/heredocs mangle `\u`/`\\` and give
   false reads):
   ```python
   def trail(s):
       n = 0
       while s and s[-1] == chr(92):   # chr(92) == backslash
           n += 1; s = s[:-1]
       return n
   ```
   Any data row with `trail != 2` is the culprit.
4. Confirm the good rows in the same file show `trail == 2`.

## Fix (byte-safe — the verified pattern)
**Do NOT fix the backslashes in place with a naive join/replace script.** In
this session that approach dropped newlines and turned the error into
`! Undefined control sequence. l.2 \midruleL0 & Capture...` (worse). Instead:

1. `git checkout -- <file>.tex` to restore the known-good file.
2. **Re-apply the whole set of edits with a raw-string Python script** (zero
   escaping ambiguity). Build row strings with:
   ```python
   BS = chr(92)
   ROW = BS + BS   # exactly two backslashes = one row break
   row = f"{a} & {b} & {c} & {d} {ROW}\n"
   ```
3. **Assert** before writing that every table data row ends in exactly two
   backslashes, and that the file's brace balance is 0.
4. Re-run the full 3-pass build (pdflatex → bibtex → pdflatex ×2) and check the
   fresh `.log` for overfull/undefined.

The in-repo example that landed: `apply_vision_merge.py` (raw-string
`str.replace` edits + `trail()` assertion) → 16 pp, 0 errors, `make verify`
green.

## Companion tool
`scripts/check_table_row_terminators.py <file.tex>` scans every `tabular*`
environment and flags any line with trailing backslashes that is not exactly 2
(and any `&`-row missing its terminator). Exit 1 on problems. Run it in `make
verify` to prevent regressions.
