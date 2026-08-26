---
name: webxr-hit-test-pitfalls
description: Debug hit-test failures and placement marker issues.
version: 1.0.0
author: Hermes Agent + Dr. Arman Khalatyan
---

# WebXR Hit-Test Pitfalls and Reticle Visibility

Use this skill when debugging AR placement marker issues in Three.js WebXR portals.

## When to Use
- Reticle/cyan ring doesn't appear during scanning
- Hit-test returns empty results on Android Chrome
- User sees passthrough but no placement marker
- `matrix.decompose()` throws "cannot assign to readonly property 'position'"

## Quick Checklist

### 1. Reticle Visibility Pattern (STABILITY DEBOUNCE)

- ✅ Reticle is a **Group**, not a Mesh
- ✅ `reticle.matrixAutoUpdate = true` (never `false`)
- ❌ DO NOT show reticle immediately — this causes flicker during ARCore calibration
- ✅ `reticle.visible = false` initially, positioned far away (`set(0, -100, 0)`)
- ✅ Use **stability debounce**: require ≥3 consecutive valid hit-test frames before showing:

```javascript
let hitStabilityCount = 0;         // consecutive stable hit count
const HIT_STABLE_THRESHOLD = 3;    // N consistent hits before showing
let groundDetected = false;

// In render loop — only flip to visible after threshold met:
if (results.length > 0 && pose && pose.transform.position) {
    hitStabilityCount++;
    reticle.position.set(pose.transform.position.x, ...);
    if (hitStabilityCount >= HIT_STABLE_THRESHOLD && !groundDetected) {
        groundDetected = true;
        reticle.visible = true;
        scanningOverlay.classList.remove('active');  // hide DOM scan overlay
    }
} else {
    hitStabilityCount = Math.max(0, hitStabilityCount - (results.length > 0 ? 1 : 2));
}
```

- ✅ After `groundDetected`, if tracking is lost (`hitStabilityCount → 0`), keep reticle visible at last known position — don't hide again unless explicitly resuming scan mode

**Anti-pattern:** Showing/hiding reticle every frame based on single hit-test result. This flickers during calibration and makes the marker appear/disappear as user moves phone, causing "scan grid disappears when I turn head" reports.

### 2. Hit-test Reference Space
- ✅ `referenceSpace` obtained FIRST (local-floor or viewer fallback)
- ✅ `requestHitTestSource({ space: referenceSpace })` uses the SAME space
- ✅ `frame.getHitTestResults()` pose extraction uses same `referenceSpace`

### 3. Position Updates (NOT Matrix)
- ✅ `reticle.position.set(pose.transform.position.x, ...)` 
- ✅ NEVER `reticle.matrix.fromArray(hitPose.transform.matrix)` — destroys rotation
- ✅ NEVER `matrix.decompose()` — throws on Three.js r160+ Groups

### 4. Reading Back (NOT Matrix)
- ✅ `reticle.getWorldPosition(pos)` — safe
- ✅ `reticle.getWorldQuaternion(quat)` — safe
- ❌ `matrix.decompose(pos, quat, scale)` — throws exception

## Correct Pattern (v2 — with stability debounce)

```javascript
// Build reticle as Group, HIDDEN initially
const reticleGroup = new THREE.Group();
const ringMesh = new THREE.Mesh(
  new THREE.RingGeometry(0.35, 0.55, 48),
  new THREE.MeshBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 1, side: THREE.DoubleSide })
);
ringMesh.rotation.x = -Math.PI / 2;
reticleGroup.add(ringMesh);

// ... add innerDisc and outerGlow ...

reticle = reticleGroup;
reticle.matrixAutoUpdate = true;
reticle.visible = false;  // HIDDEN — only shown after stable ground detection
scene.add(reticle);

// Scan particles: ALWAYS parent to reticle (NOT scene) so they inherit world matrix.
// Spread in a circle around origin (reticle space), not random scene coordinates.
const particleCount = 120;
const positions = new Float32Array(particleCount * 3);
for (let i = 0; i < particleCount; i++) {
    const r = Math.random() * 0.9;
    const theta = Math.random() * Math.PI * 2;
    positions[i*3]   = r * Math.cos(theta);
    positions[i*3+1] = 0.01;  // just above floor surface (local Y)
    positions[i*3+2] = r * Math.sin(theta);
}
const particleGeo = new THREE.BufferGeometry();
particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
scanParticles = new THREE.Points(particleGeo, particleMaterial);
reticle.add(scanParticles);  // CRITICAL: child of reticle, not scene

// State for stability debounce (declare in outer scope)
let hitStabilityCount = 0;
let groundDetected = false;
const HIT_STABLE_THRESHOLD = 3;

// Request reference space + hit-test with SAME space
let referenceSpace = null;
try { referenceSpace = await session.requestReferenceSpace('local-floor'); }
catch(e) { referenceSpace = await session.requestReferenceSpace('viewer'); }

session.requestHitTestSource({ space: referenceSpace }).then(source => {
  hitTestSource = source;
});

// In render loop — stability debounce:
const results = frame.getHitTestResults(hitTestSource);
if (results.length > 0) {
    const pose = results[0].getPose(referenceSpace);
    if (pose && pose.transform.position) {
        hitStabilityCount++;
        reticle.position.set(pose.transform.position.x, pose.transform.position.y, pose.transform.position.z);

        // Show reticle + particles only after N consecutive stable hits
        if (hitStabilityCount >= HIT_STABLE_THRESHOLD && !groundDetected) {
            groundDetected = true;
            reticle.visible = true;  // This also makes child particles visible via inheritance
            scanningOverlay.classList.remove('active');  // hide DOM overlay
        }
    } else {
        hitStabilityCount = Math.max(0, hitStabilityCount - 1);
    }
} else {
    // Tracking lost — decrement faster
    hitStabilityCount = Math.max(0, hitStabilityCount - 2);
}

// Read back via getWorldPosition (NOT matrix.decompose)
const pos = new THREE.Vector3();
reticle.getWorldPosition(pos);
```

## Files Modified (webxr-portal-door)
- `/home/hermes/projects/webxr-portal-door/index.html`
- `/home/hermes/projects/webxr-portal-door/Dockerfile`

## Mobile Cache-Busting Pitfall

**Problem:** `cache-busted ?v=` query params fail to force reload on Android Chrome despite correct nginx headers (`Cache-Control: no-cache, no-store`). Browser uses aggressive same-origin disk cache or socket pooling that ignores cache headers.

**Fix — apply ALL three layers:**
1. **Nginx config** (in Dockerfile):
   ```nginx
   add_header Cache-Control "no-cache, no-store, must-revalidate" always;
   etag off;
   add_header Last-Modified "" always;
   ```
2. **HTML `<meta>` tag** (inside `<head>`, before body content can cache):
   ```html
   <meta http-equiv="Cache-Control" content="no-cache, no-store">
   ```
3. **Testing instruction:** Tell user to:
   - Use incognito/private browser window (most reliable)
   - OR clear Chrome socket pools: `chrome://net-internals/#http-cache` → "Clear socket pools"
   - OR open Android Settings → Apps → Chrome → Storage → Clear

**Verification:** Check Content-Length of both localhost and remote URL — if lengths match, new code IS served and the issue is client-side caching.

## Related Skills
- `webxr-portal` — main WebXR portal implementation