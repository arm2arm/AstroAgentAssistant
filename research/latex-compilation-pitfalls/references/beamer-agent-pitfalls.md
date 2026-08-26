# Beamer Compilation Pitfalls from Agent-Generated Content

Session: 2026-07-19, sine-wave Beamer deck via OpenCode.

## Pitfall 1: pgfmath variable mismatch in TikZ `\draw plot`

**Error:** `Package PGF Math Error: Unknown function 'x'`

OpenCode generated:
```latex
\draw[accentBlue, very thick, domain=0:12.6, samples=300, smooth]
  plot (\x, {2.5*sin(deg(x*0.5))});
```

The `x` inside `sin(deg(...))` is not a pgfmath variable — inside a TikZ `\draw plot`, the loop variable is `\x` (with backslash), not `x`.

**Fix:** Use `\x` consistently:
```latex
  plot (\x, {2.5*sin(deg(\x*0.5))});
```

**Distinction:** Inside `pgfplots` `\addplot` within an `axis` environment, `x` (no backslash) IS valid — pgfplots injects it. Do not confuse the two contexts:

| Context | Variable | Example |
|---------|----------|---------|
| `\draw plot` | `\x` | `\draw plot (\x, {sin(deg(\x))})` |
| `\addplot` inside `axis` | `x` | `\addplot {sin(deg(x))}` |

## Pitfall 2: `\block{}` inside `columns`

**Error:** Cascading `! LaTeX Error: \begin{beamercolorbox} on input line X ended by \end{minipage}`

`\begin{block}{title}{content}` internally wraps in `\begin{beamercolorbox}` → `\begin{minipage}`. Inside a `\begin{column}`, this nesting breaks because `beamercolorbox` does not stack cleanly inside `column`.

**Fix:** Replace `\block{}` with plain formatting:
```latex
% Before (breaks):
\begin{column}{0.5\textwidth}
  \block{\accenttext{Amplitude $A$}}{
    Maximum displacement.
  }
\end{column}

% After (works):
\begin{column}{0.5\textwidth}
  \textbf{\accenttext{Amplitude $A$}}

  Maximum displacement.
\end{column}
```

## Resolution Pattern

When compiling agent-generated Beamer code:

1. Run `pdflatex` and capture all `!` error lines (grep `^!` in `.log`)
2. If `Package PGF Math Error: Unknown function`: check `sin(deg(...))` — ensure loop variable is `\x` not `x` in `\draw plot` contexts
3. If `beamercolorbox ended by minipage` or `beamercolorbox ended by column`: find all `\begin{block}{` inside `\begin{columns}` and convert to `\textbf{}` + body
4. Patch, recompile, verify

## Session Artifacts

- Project: `~/projects/sine-wave-drp/`
- Final files: `drp_card.yaml`, `slides.tex`, `slides.pdf` (7 pages, 185KB)
- OpenCode version: 1.15.6
