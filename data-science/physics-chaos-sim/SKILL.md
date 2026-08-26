---
name: physics-chaos-sim
description: Interactive physics & chaos simulations as single-file HTML/JS apps. Covers double pendulum, coupled oscillators, N-body gravity, fluid dynamics, Ising model, reaction-diffusion, and more.
version: 1.0.0
author: Hermes Agent
---

# Physics & Chaos Simulations

Build interactive physics simulations as single self-contained HTML files. Dark theme with user palette.

## When to use

- User asks for a simulation, visualization, or animated physics demo
- User says "show me how [physics concept] works"
- Building interactive demos of nonlinear dynamics, wave phenomena, statistical mechanics

## Visual conventions

- **Background:** `#0D1117` (user's dark theme)
- **Palette:** `#58C4DD` (blue), `#83C167` (green), `#FFFF00` (yellow), `#FF6B6B` (red/dprhub), `#C792EA` (purple), `#FF922B` (orange)
- **Font:** `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`
- **UI text color:** `#484f58` (muted), `#c9d1d9` (primary)
- **Border/accent:** `#21262D` / `#30363D`
- **Single HTML file** with inline CSS and JS — no build step, no dependencies

## Code structure

### 1. Layout — 4-panel grid

For multi-panel simulations, use a 2×2 CSS grid:

```html
<div class="grid">
  <div class="panel"><div class="panel-title"><span>Title</span><span class="val">—</span></div><canvas id="c1"></canvas></div>
  <div class="panel"><div class="panel-title"><span>Title</span><span class="val">—</span></div><canvas id="c2"></canvas></div>
  <div class="panel"><div class="panel-title"><span>Title</span><span class="val">—</span></div><canvas id="c3"></canvas></div>
  <div class="panel"><div class="panel-title"><span>Title</span><span class="val">—</span></div><canvas id="c4"></canvas></div>
</div>
```

```css
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 2px;
  padding: 2px;
  height: calc(100vh - 140px);
  min-height: 500px;
}
.panel { background: #0D1117; position: relative; display: flex; flex-direction: column; overflow: hidden; }
.panel-title { font-size: 10px; color: #484f58; text-transform: uppercase; letter-spacing: 1px; padding: 4px 8px; background: #161B22; border-bottom: 1px solid #21262D; display: flex; justify-content: space-between; align-items: center; }
canvas { flex: 1; display: block; }
```

For single-panel sims, just put one canvas in the center.

### 2. Controls bar

Fixed at bottom, outside the grid:

```html
<div id="controls" style="position:fixed;bottom:0;left:0;right:0;background:rgba(13,17,23,0.98);border-top:1px solid #30363D;padding:10px 16px;display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:center;z-index:100;">
  <button id="btn-slow">0.25×</button>
  <button id="btn-normal" class="active">1×</button>
  <button id="btn-fast">4×</button>
  <button id="btn-pause">Pause</button>
  <div class="ctrl-group">
    <label>Param:</label>
    <input type="range" id="paramSlider" min="0" max="10" step="0.1" value="1">
    <span class="val" id="paramVal">1.0</span>
  </div>
  <button id="btn-reset">Reset</button>
</div>
```

**Critical: use `onclick` handlers directly (or `addEventListener` after DOM loads). Never nest controls inside the grid — they'll be covered by canvases.**

### 3. Canvas sizing (DPR-aware)

```javascript
function resize() {
  const dpr = window.devicePixelRatio || 1;
  [c1, c2, c3, c4].forEach(c => {
    const r = c.getBoundingClientRect();
    if (r.width > 0 && r.height > 0) {
      c.width = r.width * dpr;
      c.height = r.height * dpr;
      c.getContext('2d').setTransform(dpr, 0, 0, dpr, 0, 0);
    }
  });
}
window.addEventListener('resize', resize);
window.addEventListener('load', resize);
setTimeout(resize, 200); // fallback
```

### 4. IIFE wrapper

Always wrap the entire JS in an IIFE to avoid global namespace pollution:

```javascript
(function() {
  "use strict";
  // all code here
})();
```

### 5. Physics integration

- Use **RK4** (Runge-Kutta 4th order) for ODE integration — much better than Euler for oscillators
- Use **sub-stepping** (8 substeps per frame) for stability at high speeds
- Clamp `dt` to prevent explosion on tab-switch: `Math.min((now - lastTS)/1000, 0.05)`

```javascript
function rk4(state, dt) {
  let [t1,o1,t2,o2] = state;
  const k1 = derivs(t1,o1,t2,o2);
  const k2 = derivs(t1+dt*k1[0]*0.5, ...);
  const k3 = derivs(t1+dt*k2[0]*0.5, ...);
  const k4 = derivs(t1+dt*k3[0], ...);
  return [t1+(k1[0]+2*k2[0]+2*k3[0]+k4[0])*dt/6, ...];
}
```

### 6. Main loop pattern

```javascript
function frame(now) {
  const dt = Math.min((now - lastTS)/1000, 0.05) * speedMul;
  lastTS = now;
  if (!paused && dt > 0) {
    const sub = 8, subDt = dt/sub;
    for (let j=0; j<sub; j++) { /* integrate */ }
    simTime += dt;
  }
  try { render1(); render2(); render3(); render4(); } catch(e) { console.error(e); }
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
```

## Chaos visualization patterns

When simulating chaotic systems, include these diagnostic panels:

### Lyapunov divergence plot
Track |δ| between a reference and perturbed trajectory. Plot log₁₀(|δ|) vs time. A straight line rising = exponential divergence = positive Lyapunov exponent = chaos.

```javascript
const dx = th1 - pTh1, dy = th2 - pTh2;
const dist = Math.sqrt(dx*dx + dy*dy);
const logD = Math.log10(Math.max(dist, 1e-15));
divHistory.push({ t: simTime, v: logD });
// Lyapunov estimate: slope of log(distance) vs time
if (divHistory.length > 200) {
  const slope = (logD - divHistory[0].v) / (simTime - divHistory[0].t);
  lyapHistory.push({ t: simTime, v: slope });
}
```

### Poincaré section
Record state at a fixed phase condition (e.g., every time ω₁ crosses zero with positive slope). For periodic motion: finite set of points. For chaos: fractal structure. This is one of the most powerful visual tests for chaos.

```javascript
if (Math.sign(om1) !== Math.sign(om1_prev) && om1 > 0) {
  poincare.push({ th1, th2 });
}
```

### Phase space trajectory
Plot (θ, ω) — if it forms closed loops, the system is periodic. If it never repeats and fills a region, it's chaotic.

### Chaos comparison panel
Show reference vs. perturbed system side-by-side with a divergence line between them. Color-code: SYNC (green), DRIFT (orange), CHAOS (red).

## Color by velocity

Map speed to the user's palette for intuitive physics visualization:

```javascript
function velColor(v, max = 12) {
  const t = Math.min(Math.abs(v)/max, 1);
  if (t < 0.5) return lerp([88,196,221],[131,193,103], t*2);   // blue → green
  return lerp([131,193,103],[255,146,43], (t-0.5)*2);            // green → orange
}
```

## Chaos badge pattern

```css
.badge.sync { background: rgba(131,193,103,0.2); color: #83C167; border: 1px solid rgba(131,193,103,0.4); }
.badge.drift { background: rgba(255,146,43,0.2); color: #FF922B; border: 1px solid rgba(255,146,43,0.4); }
.badge.chaos { background: rgba(255,107,107,0.2); color: #FF6B6B; border: 1px solid rgba(255,107,107,0.4); }
```

```javascript
const badge = document.getElementById('chaosBadge');
if (logD < -2) { badge.className='badge sync'; badge.textContent='SYNC'; }
else if (logD < 0) { badge.className='badge drift'; badge.textContent='DRIFT'; }
else { badge.className='badge chaos'; badge.textContent='CHAOS'; }
```

## Periodic boundary visualization (3×3 tiling)

When rendering particles with periodic boundary conditions, the minimum image convention must be handled in TWO places:

### 1. Physics: minimum image convention

```javascript
function minImage(dx, dy) {
  dx = dx - Math.round(dx / SIM_SIZE) * SIM_SIZE;
  dy = dy - Math.round(dy / SIM_SIZE) * SIM_SIZE;
  return [dx, dy];
}
```

Apply before every distance computation (forces, energy, halo detection).

### 2. Rendering: 3×3 tiling

Particles near a box edge must be drawn on the opposite side too, otherwise they "teleport" visually. **Standard technique:** draw each particle in all 9 tiles of a 3×3 grid of box copies.

```javascript
// For each particle, draw in 3×3 tiling
for (const p of particles) {
  for (let ti = -1; ti <= 1; ti++) {
    for (let tj = -1; tj <= 1; tj++) {
      const tx = p.x + ti * SIM_SIZE;
      const ty = p.y + tj * SIM_SIZE;
      // Map to screen coords for this tile
      const sx = boxCX - halfL + (tx + halfL) / SIM_SIZE * boxSize;
      const sy = boxCY - halfL + (ty + halfL) / SIM_SIZE * boxSize;
      // Alpha: central tile at 1.0, others at 0.35
      const alpha = (ti === 0 && tj === 0) ? 1.0 : 0.35;
      drawParticle(p, sx, sy, alpha, key);
    }
  }
}
```

### 3. Trails: key by tile

**Critical pitfall:** if you don't key trails by tile, a particle wrapping will create a trail stretching across the entire screen. Use a per-particle map of `trail_key → trail_points`.

```javascript
// In drawParticle:
const key = `${tileX},${tileY}`;
p.trails = p.trails || {};
if (!p.trails[key]) p.trails[key] = [];
const trail = p.trails[key];
trail.push({x: sx, y: sy});

// Detect discontinuity (trail crossing >70% of box width)
if (trail.length >= 2) {
  const last = trail[trail.length - 1];
  const prev = trail[trail.length - 2];
  if (Math.abs(last.x - prev.x) > boxSize * 0.7 ||
      Math.abs(last.y - prev.y) > boxSize * 0.7) {
    trail.length = 0; // clear on wrap
    trail.push({x: sx, y: sy});
  }
}
```

### Why 3×3 and not more?

A particle can be at most one box-length away from any other particle that interacts with it (minimum image convention). So only 3×3 tiles can contain visible particles that should be near each other visually. This is optimal — N² direct summation is O(N²) in the physics, but the rendering stays O(N) in canvas operations.

### Coordinate mapping

Physical coords: `[−SIM_SIZE/2, SIM_SIZE/2]` in each axis.
Screen box: centered at `(boxCX, boxCY)`, pixel size `boxSize × boxSize`.

```javascript
function physToScreen(val, halfL, boxCX, boxCY, boxSize) {
  return boxCX - boxSize/2 + (val + halfL) / (2*halfL) * boxSize;
  // equivalently: boxCX - halfL + (val + halfL)/SIM_SIZE * boxSize
}
```

See `references/periodic-bc-rendering.md` for a full worked example and common pitfalls.

## Upload to S3

After building, upload via the S3 script:

```bash
python3 ~/.hermes/scripts/s3_media_upload.py /path/to/simulation.html
```

Then share the URL: `![name](https://s3.data.aip.de:9000/scr4agent/hermes/UUID.html)`

## Troubleshooting

- **Buttons not working:** Controls MUST be outside the grid (fixed position, `z-index: 100`). Canvases can absorb clicks if they overlap controls.
- **Canvas too small:** Use `getBoundingClientRect()` for dimensions (not `offsetWidth` which can be 0 on init). Add `setTimeout(resize, 200)` as fallback.
- **Tab blur slowdown:** Clamp `dt` to 0.05s max. Use `performance.now()` (not `Date.now()`).
- **Memory leak:** Clear history arrays on reset — don't just truncate, set `.length = 0`.
- **No globals:** Wrap everything in IIFE, use `let`/`const`, avoid `var`.

## Simulation ideas

| Category | Simulations |
|----------|------------|
| Chaos | Double pendulum, Lorenz attractor, Duffing oscillator, Henon-Heiles, Rössler |
| Waves | Coupled oscillators, wave interference, vibrating membrane, sound synthesis |
| Fluids | 2D Navier-Stokes, vortex shedding, Rayleigh-Bénard convection |
| Statistical | Ising model, reaction-diffusion (Gray-Scott), diffusion-limited aggregation |
| Gravity | N-body, restricted 3-body, Lagrange points, figure-8 orbit |
| Mechanical | Rope/cloth Verlet, spring mesh, granular matter, rigid body |
| Quantum | Wave packet tunneling, harmonic oscillator, particle in a box, double-slit |

## File path convention

Store simulation files at:
```
/home/hermes/.hermes/skills/creative/assets/<name>.html
```
