# Beamer Background Color Pitfall — Session Notes (2026-07-19)

## Context

Session: Creating a dark-themed Beamer presentation for the `sine-wave-drp` project (Ocean Blue theme). User requested a dark background with high-contrast text and ocean blue accent colors.

## Problem

Multiple standard approaches for setting a solid background color in Beamer **failed silently** — the background remained white (`#FFFFFF`) despite correct-looking LaTeX code.

## Failed Attempts

### Attempt 1: Standard `\setbeamercolor{background canvas}`
```latex
\definecolor{bg}{HTML}{0A1628}
\setbeamercolor{background canvas}{bg=bg}
```
**Result:** Background stayed white. No error, just ignored.

### Attempt 2: Hex value directly
```latex
\setbeamercolor{background canvas}{bg=0A1628}
```
**Result:** Same — white background.

### Attempt 3: `\setbeamercolor{background}`
```latex
\setbeamercolor{background}{bg=bg}
```
**Result:** Still white.

### Attempt 4: `\usebackgroundtemplate` with `\fill[bg]`
```latex
\usebackgroundtemplate{\fill[bg] (0,0) rectangle (\paperwidth,\paperheight);}
```
**Result:** Black background (`#000000`), not the defined navy blue. The `[bg]` color specifier wasn't resolving the custom color name.

## Working Solution

The **ONLY** pattern that worked was using `\usebackgroundtemplate` with an **explicit TikZ fill** and a separately defined color:

```latex
% Define the background color FIRST
\definecolor{mybgcolor}{HTML}{0A1628}

% Then set background using template with TikZ fill
\usebackgroundtemplate{\tikz\fill[mybgcolor] (0,0) rectangle (\paperwidth,\paperheight);}
```

### Why This Works

- `\definecolor{HTML}` creates a color name that TikZ can use
- `\tikz\fill[mybgcolor]` explicitly invokes TikZ's color resolution
- `\usebackgroundtemplate` places the fill on every slide
- The rectangle covers the full paper size

### Why Other Approaches Fail

Beamer's native `\setbeamercolor{background canvas}{bg=...}` mechanism uses a different color resolution path that doesn't properly handle custom colors defined via `\definecolor{HTML}{...}`. The color exists but isn't applied to the canvas rendering.

## Verification Command

After compiling, verify the background color with ImageMagick:

```bash
convert -density 150 slides.pdf[0] txt:- | head -5
# Look for your hex value (e.g., #0A1628) in the pixel output
# If you see #FFFFFF, the background template isn't working
```

## Theme Examples

### Ocean Blue (Deep Navy Background)
```latex
\definecolor{mybgcolor}{HTML}{0A1628}
\definecolor{accentBlue}{HTML}{0EA5E9}
\definecolor{electricBlue}{HTML}{38BDF8}
\definecolor{warmAccent}{HTML}{FB923C}
\definecolor{txt}{HTML}{F0F9FF}
\usebackgroundtemplate{\tikz\fill[mybgcolor] (0,0) rectangle (\paperwidth,\paperheight);}
\setbeamercolor{normal text}{fg=txt}
\setbeamercolor{frametitle}{fg=electricBlue}
```

### Berlin Tech (Dark Red-Pink Accent)
```latex
\definecolor{mybgcolor}{HTML}{1A1A2E}
\definecolor{accentBlue}{HTML}{E94560}
\definecolor{electricBlue}{HTML}{00D4FF}
\definecolor{warmAccent}{HTML}{FF6B35}
\definecolor{txt}{HTML}{FFFFFF}
\usebackgroundtemplate{\tikz\fill[mybgcolor] (0,0) rectangle (\paperwidth,\paperheight);}
\setbeamercolor{normal text}{fg=txt}
\setbeamercolor{frametitle}{fg=electricBlue}
```

## Project Context

- **Project:** `/home/hermes/projects/sine-wave-drp`
- **File:** `sine-wave-lecture.tex` (renamed from `slides.tex`)
- **GitLab:** https://gitlab-p4n.aip.de/arm2arm/sine-wave-drp
- **DRP Hub:** https://drphub-p4n.aip.de/share/7cfd7561-51c6-477c-a353-bcf6cc5c5251

## User Preference

User `arm2arm` prefers dark-themed Beamer presentations with:
- Deep navy or dark gray backgrounds
- High-contrast white or off-white text
- Vibrant accent colors (ocean blue, red-pink, electric cyan)
- Clean, professional aesthetic

Always use the `\usebackgroundtemplate{\tikz\fill[...]}` pattern for reliable dark backgrounds with this user.

## Related Pitfalls

See also:
- `latex-paper-workflow` skill — Slide Styling Preference section
- `latex-compilation-pitfalls` skill — Pitfall 3: Beamer Background Color Not Applying
