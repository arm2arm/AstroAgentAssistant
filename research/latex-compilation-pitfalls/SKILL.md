---
name: latex-compilation-pitfalls
description: >-
  Common LaTeX compilation errors, debugging patterns, and fixes — especially
  for agent-generated Beamer decks, TikZ/pgfplots variable mismatches,
  block/column nesting issues, and systematic error diagnosis workflows.
version: 1.0.0
author: Hermes Agent
tags: [latex, beamer, tikz, pgfplots, debugging, compilation]
---

# LaTeX Compilation Pitfalls & Debugging

This class covers the most common LaTeX compilation failures that arise when
working with agent-generated documents (OpenCode, Claude Code, Codex, etc.)
and the systematic patterns for diagnosing and fixing them.

## When to Use

- User asks to create LaTeX/Beamer/PPTX from a description
- An agent tool generates LaTeX that fails to compile
- Compilation errors mention `beamercolorbox`, `pgfmath`, or `minipage` nesting
- Need to debug "Fatal error occurred, no output PDF produced" from pdflatex

## Debugging Workflow

### Step 1: Clean and Compile
```bash
cd /path/to/project
rm -f *.aux *.log *.nav *.snm *.toc *.out *.vrb *.fls *.fdb_latexmk
pdflatex -interaction=nonstopmode slides.tex 2>&1 | tail -10
```

### Step 2: Extract Error Lines
```bash
grep -n "^!" slides.log | head -30
```

### Step 3: Categorize and Fix
See the **Common Pitfalls** section below for the most frequent failures.

### Step 4: Verify
```bash
grep "Output written on.*\.pdf" slides.log
# Should show: Output written on slides.pdf (N pages, XXXXX bytes).
```

## Beamer-Specific Pitfalls (Agent-Generated Content)

### Pitfall 1: pgfmath variable mismatch in TikZ `\draw plot`

**Error:** `Package PGF Math Error: Unknown function 'x'`

Agent code often writes `{sin(deg(x*0.5))}` where `x` is not a pgfmath variable.

**Root cause:** Inside TikZ `\draw plot`, the loop variable is `\x` (with
backslash), not bare `x`. Inside pgfplots `\addplot` within an `axis`
environment, `x` (no backslash) IS valid — pgfplots injects it.

**Fix:**
```latex
% Wrong (TikZ draw plot):
\draw plot (\x, {2.5*sin(deg(x*0.5))});
% Correct:
\draw plot (\x, {2.5*sin(deg(\x*0.5))});

% Correct (pgfplots addplot — x IS valid here):
\addplot {2.5*sin(deg(x*0.5))};
```

### Pitfall 2: `\block{}` inside `columns`

**Error:** Cascading `! LaTeX Error: \begin{beamercolorbox} on input line X
ended by \end{minipage}` followed by `ended by \end{column}`.

`\begin{block}{title}{content}` internally uses `\begin{beamercolorbox}`
wrapped in a `\begin{minipage}`. Inside a `\begin{column}`, this nesting
breaks because beamercolorbox does not stack cleanly inside column.

**Fix:** Replace `\block{}` with `\textbf{}` + body text:
```latex
% Before (breaks inside columns):
\begin{column}{0.5\textwidth}
  \block{\accenttext{Title}}{content goes here}
\end{column}

% After (works):
\begin{column}{0.5\textwidth}
  \textbf{\accenttext{Title}}

  Content goes here.
\end{column}
```

### Pitfall 3: Beamer Background Color Not Applying (2026-07-19)

**Error:** Background stays white (`#FFFFFF`) despite setting `\setbeamercolor{background canvas}{bg=bg}` or similar.

**Root cause:** Beamer's native background canvas mechanism does NOT properly resolve custom color names defined via `\definecolor{HTML}{...}`. The color definition exists but isn't applied to the canvas.

**Common failed attempts:**
```latex
% These DO NOT work — background stays white:
\setbeamercolor{background canvas}{bg=bg}
\setbeamercolor{background canvas}{bg=0A1628}
\setbeamercolor{background}{bg=bg}
```

**The ONLY working pattern:** Use `\usebackgroundtemplate` with an explicit TikZ fill:

```latex
% Define the background color FIRST
\definecolor{mybgcolor}{HTML}{0A1628}

% Then set background using template with TikZ fill
\usebackgroundtemplate{\tikz\fill[mybgcolor] (0,0) rectangle (\paperwidth,\paperheight);}
```

**Placement:** Must be in preamble, AFTER `\definecolor` and BEFORE `\begin{document}`.

**Verification:** After compiling, check the PDF:
```bash
convert -density 150 slides.pdf[0] txt:- | head -5
# Background pixels should show your hex value (e.g., #0A1628), not #FFFFFF
```

**Example: Ocean Blue theme**
```latex
\definecolor{mybgcolor}{HTML}{0A1628}
\definecolor{accentBlue}{HTML}{0EA5E9}
\definecolor{electricBlue}{HTML}{38BDF8}
\definecolor{txt}{HTML}{F0F9FF}
\usebackgroundtemplate{\tikz\fill[mybgcolor] (0,0) rectangle (\paperwidth,\paperheight);}
\setbeamercolor{normal text}{fg=txt}
\setbeamercolor{frametitle}{fg=electricBlue}
```

This pitfall was discovered when creating a dark-themed Beamer deck for the sine-wave-drp project — multiple standard approaches failed silently before the TikZ fill pattern succeeded.

## Common Figure/Plot Pitfalls

### TikZ plot syntax
- Always use `\x` (backslash-x) for loop variables in TikZ `\draw plot`
- pgfplots `\addplot` inside `axis` uses bare `x` — do NOT add backslash
- Use `deg()` for degree input in trig functions: `sin(deg(\x))`

### FancyArrowPatch (matplotlib)
- Uses `arrowstyle=` NOT `style=` or `linestyle=`
- Cannot repeat kwargs: `arrowstyle='->', arrowstyle='-|>'` is invalid

### FancyBboxPatch
- Use `facecolor='none'` NOT `facecolor='transparent'` (ValueError)

## Patch-Induced Corruption

When using `patch` on LaTeX files:

1. **Doubled backslashes**: A single `\` in old_string may produce `\\` in
   the result. Always verify patched lines with `read_file` after patching.

2. **Vulnerable lines**: `\begin{document}`, `\begin{frame}`,
   `\input{}`, `\maketitle` are especially prone to doubling.
   Quick check: `grep -n 'begin\|input' file.tex | head -20`

3. **Post-patch cleanup** if needed:
   ```python
   content = content.replace('\\\\_', '\\_')
   content = content.replace('\\\\item ', '\\item ')
   content = content.replace('\\\\begin{document}', '\\begin{document}')
   ```

4. **Beamer fragile frames**: If a patched frame contains verbatim or
   ASCII content, add `[fragile]` to the frame:
   `\begin{frame}[fragile]{Title}`

## Quick Reference

| Error pattern | Likely cause | Fix |
|---------------|-------------|-----|
| `Unknown function 'x'` in pgfmath | `\draw plot` using `x` not `\x` | Change to `\x` |
| `beamercolorbox ended by minipage` | `\block{}` inside `\column` | Use `\textbf{}` instead |
| `Missing } inserted` | Unbalanced braces or `\` doubling | Check patch results |
| `File 'xxx.sty' not found` | Missing package | `\usepackage{xxx}` or install |
| `Label(s) may have changed` | Figure/section reorder | Run pdflatex once more |
| `Overfull \vbox` | Slide too dense | Split frame or use `\small` |

## File Structure

Support files under this skill:
- `references/beamer-agent-pitfalls.md` — Error transcripts and session notes from agent-generated Beamer debugging
