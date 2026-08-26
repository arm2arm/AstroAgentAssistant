# Periodic Boundary Conditions — Rendering Reference

## The Problem

In N-body and other periodic simulations, particles exit one side of the box and re-enter the opposite side (minimum image convention). On screen, this creates a visual discontinuity:

- **Before fix:** particle at x=0.99 suddenly appears at x=−0.99 (far left), creating a "teleport" effect
- **Trail artifact:** the trail stretches from right edge to left edge across the entire screen

## The Solution: 3×3 Tiling

The standard technique used in all major N-body visualization code (GADGET, AREPO, ENZO viewer plugins):

1. The physical simulation box has size `SIM_SIZE`, coordinates `[−SIM_SIZE/2, SIM_SIZE/2]`
2. For rendering, tile the box 3×3: `(−L, 0, +L)` in each direction
3. Draw each particle in all 9 tiles
4. Central tile (0,0) at full opacity; 8 surrounding tiles at reduced opacity (~35%)

### Why it works

- A particle that has wrapped to the left side IS physically near particles on the right side (they're connected by the periodic boundary)
- By drawing copies in adjacent tiles, particles flow naturally across boundaries
- No trail artifacts: each tile has its own trail keyed by tile offset

### Implementation details

```javascript
// In the render loop:
for (const p of particles) {
  for (let ti = -1; ti <= 1; ti++) {          // 3 tiles in x
    for (let tj = -1; tj <= 1; tj++) {        // 3 tiles in y
      const tx = p.x + ti * SIM_SIZE;         // offset physical coord
      const ty = p.y + tj * SIM_SIZE;
      const sx = boxCX - halfL + (tx + halfL) / SIM_SIZE * boxSize;
      const sy = boxCY - halfL + (ty + halfL) / SIM_SIZE * boxSize;
      const alpha = (ti === 0 && tj === 0) ? 1.0 : 0.35;
      drawParticle(p, sx, sy, alpha, `${ti},${tj}`);
    }
  }
}
```

### Trail management

Trails MUST be keyed by tile to avoid wrap artifacts:

```javascript
// Per-particle: map of "tileKey" → trail points
p.trails = p.trails || {};
const key = `${ti},${tj}`;
if (!p.trails[key]) p.trails[key] = [];
const trail = p.trails[key];
trail.push({x: sx, y: sy});

// Clear on wrap detection
if (trail.length >= 2) {
  const last = trail[trail.length - 1];
  const prev = trail[trail.length - 2];
  const jump = Math.max(Math.abs(last.x - prev.x), Math.abs(last.y - prev.y));
  if (jump > boxSize * 0.7) trail.length = 0; // wrap detected, reset
}
```

### Optimization

For performance (especially with large N):
- Skip far copies: only draw if screen position is within `±boxSize*0.5` of canvas bounds
- Use a spatial hash / grid for halo detection instead of O(N²) pairwise
- Consider Barnes-Hut tree for O(N log N) force computation

### Common pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Only wrapping position, not rendering | Particles teleport across screen | Draw 3×3 tiles |
| Not keying trails by tile | Trails stretch across entire canvas | Use `p.trails[ti,tj]` |
| Using `Math.floor` instead of `Math.round` in minImage | Wrong wrapped position | Always use `Math.round()` |
| Drawing particles with alpha < 1 without `globalAlpha` | Colors don't blend correctly | Set `ctx.globalAlpha` explicitly |
