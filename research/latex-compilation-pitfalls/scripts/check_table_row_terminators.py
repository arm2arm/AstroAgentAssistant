#!/usr/bin/env python3
"""Scan a .tex file for table rows whose trailing-backslash count is not exactly 2.

Detects the class of bug that causes `! Misplaced \\noalign.` from booktabs
rules: data rows ending in 3+ (or 0) backslashes instead of a single `\\`.

Usage:
    python3 check_table_row_terminators.py main.tex
    python3 check_table_row_terminators.py main.tex --strict   # also flag rows missing terminator

Exit 0 = clean, 1 = problems found.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

BACKSLASH = chr(92)  # avoid any shell/JSON escaping ambiguity


def trail(s: str) -> int:
    n = 0
    while s and s[-1] == BACKSLASH:
        n += 1
        s = s[:-1]
    return n


def iter_table_spans(lines):
    """Yield (start, end, name) for each tabular/tabularx/longtable span."""
    open_re = re.compile(r"\\begin\{(tabularx?|longtable)\}")
    i = 0
    while i < len(lines):
        m = open_re.search(lines[i])
        if m:
            name = m.group(1)
            close_tok = f"\\end{{{name}}}"
            end = i
            while end < len(lines) and close_tok not in lines[end]:
                end += 1
            yield i, end, name
            i = end + 1
        else:
            i += 1


def main() -> int:
    strict = "--strict" in sys.argv
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return 2
    path = Path(sys.argv[1])
    lines = path.read_text(encoding="utf-8").splitlines()
    problems = 0
    for start, end, name in iter_table_spans(lines):
        for idx in range(start + 1, end):
            line = lines[idx].rstrip()
            if not line:
                continue
            # skip rule/structure lines and the column-spec line
            if line.strip().startswith(("\\toprule", "\\midrule", "\\bottomrule",
                                        "\\midrule", "\\cmidrule", "\\begin{",
                                        "\\end{", "\\caption", "\\label",
                                        "\\small", "\\renewcommand", "\\centering")):
                continue
            t = trail(line)
            if t > 2:
                print(f"{path}:{idx+1} [{name}] {t} trailing backslashes -> "
                      f"should be 2  (tail: {line[-24:]!r})")
                problems += 1
            elif strict and ("&" in line) and t == 0:
                # a cell row that ends without a row break (may be last row,
                # so only a warning)
                print(f"{path}:{idx+1} [{name}] data row missing row terminator "
                      f"(warn)  (tail: {line[-24:]!r})")
    if problems:
        print(f"\nFAIL: {problems} row-terminator problem(s)")
        return 1
    print(f"OK: no over-escaped row terminators in {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
