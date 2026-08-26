# tabularx X-column limit + "compiles standalone but not in-document" diagnosis

Discovered 2026-08-23 while merging vision sections into the drp-paper
journal manuscript. Two distinct, durable lessons.

## 1. `tabularx` allows exactly ONE X-type column (documented, rock-solid)

A `tabularx` table may contain **at most one** X-type column (`X` or a
custom `>{...}X` such as the journal style's `Y`). Writing two — e.g.

```latex
% WRONG: two Y columns
\begin{tabularx}{\linewidth}{@{}l l Y Y@{}}
```

— is invalid and produces a hard error near the first rule after the header
row. In this session it surfaced as:

```
! Misplaced \noalign.
\midrule ->\noalign ...
l.300 \end{tabularx}
! ==> Fatal error occurred, no output PDF file produced!
```

The reported line (`\end{tabularx}`) is misleading — the real fault is the
column preamble, not the end environment.

**Fix:** keep one X column, give the other wide columns fixed `p{...}`
widths that sum (with the natural `l` columns) to ≤ `\linewidth`:

```latex
% RIGHT: one Y, rest fixed
\begin{tabularx}{\linewidth}{@{}l p{3.2cm} p{4.4cm} Y@{}}
...
\end{tabularx}
```

If you genuinely need two flexible columns, drop `tabularx` and use a plain
`tabular` with explicit `p{}` widths on every wrapping column (sum them so
they fit the text block, or you'll trade the fatal error for overfull `\hbox`).

## 2. "Compiles standalone but not in-document" ⇒ patch corruption elsewhere

After fixing the two-Y column to a single Y, the **identical** table
definition compiled cleanly in a standalone `\documentclass` test (exit 0)
yet the full-document build **still** failed at the same line. Same source,
different result ⇒ the fault is **contextual**, i.e. a stray/duplicated token
in the surrounding document — classic signature of a fuzzy `patch` that
doubled a line or left a duplicated `\begin{...}`/`\end{...}`/`\\` from a
prior edit (this file had been partially-read + patched several times).

Diagnostic recipe:
1. Isolate the table in a minimal standalone doc → if it compiles, the table
   is NOT the cause.
2. `grep -n 'begin{\|end{' file.tex | sed -n '250,320p'` (around the failing
   line) looking for a duplicated `\begin{tabularx}`/`\end{table}` or an
   orphaned rule.
3. `grep -n '\\\\\\\\' file.tex` for doubled backslashes from patching.
4. Re-read the whole edited region with `read_file` (do NOT trust partial
   offset/limit reads after multiple patches) and reconcile by hand.

Note for honesty: this session's build was **left broken** at the cap — the
two-X cause was fixed, but the secondary contextual cause was diagnosed, not
yet resolved. Do not treat "switched to one Y" as a complete fix.
