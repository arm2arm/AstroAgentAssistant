# CSS Theming Patterns for WebXR Projects

Use CSS custom properties (variables) for easy theme switching. Define all colors, shadows, and backgrounds in `:root`, then reference them throughout stylesheets.

## Pattern

```css
:root {
  --primary: #0ea5e9;         /* Main brand color */
  --primary-light: #38bdf8;   /* Highlight/accent variant */
  --primary-dark: #0284c7;    /* Dark variant */
  --accent: #06b6d4;          /* Secondary accent (gradients) */
  --accent-light: #22d3ee;    /* Accent light variant */
  --bg-dark: #0c1929;         /* Page background */
  --bg-card: rgba(15, 30, 50, 0.7); /* Card backgrounds (glass) */
  --text: #f0f9ff;            /* Primary text */
  --text-muted: #94a3b8;      /* Secondary text */
  --border: rgba(14, 165, 233, 0.2); /* Border color */
  --glow: rgba(14, 165, 233, 0.3);   /* Box shadow glow */
}
```

## Common Theme Palettes

### Ocean Blue (default)
```css
--primary: #0ea5e9; --accent: #06b6d4; --bg-dark: #0c1929;
```

### Purple/Magenta
```css
--primary: #8b5cf6; --accent: #ec4899; --bg-dark: #0c0c1e;
```

### Green/Teal
```css
--primary: #10b981; --accent: #14b8a6; --bg-dark: #0c2919;
```

### Red/Orange
```css
--primary: #ef4444; --accent: #f97316; --bg-dark: #1a0c0c;
```

## Applying to Elements

```css
/* Gradients */
background: linear-gradient(135deg, var(--primary), var(--accent));

/* Text gradients */
background: linear-gradient(135deg, var(--primary-light), var(--accent-light));
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
background-clip: text;

/* Glass cards */
background: var(--bg-card);
backdrop-filter: blur(20px);
border: 1px solid var(--border);

/* Glow effects */
box-shadow: 0 8px 30px var(--glow);

/* Animated backgrounds */
background: 
  radial-gradient(ellipse at 20% 20%, var(--primary) 0%, transparent 50%),
  radial-gradient(ellipse at 80% 80%, var(--accent) 0%, transparent 50%);
```

## Session Reference

Built ocean blue theme for `ar.aip.de` portal door (Jul 2026). Replaces purple/magenta theme.
Project: `/home/hermes/projects/webxr-portal-door`
Container: `webxr-portal-door` running on port 8123 (HTTP, HAProxy terminates SSL).
