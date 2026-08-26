---
name: webxr-portal
description: Build WebXR portal AR apps for 3D browser portals.
version: 1.0.0
author: Hermes Agent + Dr. Arman Khalatyan
---

# WebXR Portal Door

Build interactive 3D portal experiences with WebXR AR/VR support in browsers.

## When to Use
- Creating browser-based AR/VR portal experiences
- Three.js + WebXR projects requiring camera/AR access
- Docker + HAProxy deployment for HTTPS WebXR apps

## Project Structure
```
project/
├── index.html          # Landing page with WebXR entry button
├── css/style.css       # Dark themed styling
├── js/app.js           # Three.js + WebXR logic (main)
├── Dockerfile          # Nginx container, HTTP-only
├── .dockerignore       # Excludes certs and node_modules
└── ssl/                # Pre-generated SSL (not in image)
```

## Project Structure

For production projects, inline JS in index.html is simpler than split files — the working project at `/home/hermes/projects/webxr-portal-door/` uses this:

```
project/
├── index.html          # Landing page + inline Three.js AR logic
├── css/style.css       # Modern glass-morphism, animated gradient bg, ocean blue theme
├── js/app.js           # Legacy/optional (not used when inline)
└── Dockerfile          # Nginx container, port 8123
```

See `references/scanning-visualization.md` for adding visible feedback (wireframe floor plane + particle dots) during AR scanning phase.

Ocean blue theme palette: `0x0ea5e9`, `0x06b6d4`, `0x0284c7`, `0x22d3ee`, `0x38bdf8`, `0xf0f9ff`

### 1. AR Flow (Recommended)
The production flow uses a state machine: `scanning → ground-detected → tap-place → drop-animate → placed`

```
1. User enters AR → show scanning overlay (animated scan lines, expanding waves, grid)
2. Hit-test detects ground plane → hide scanning overlay, show reticle, status "Tap to place"
3. User taps → portal drops from above (ease-out cubic, 1.2s), opacity builds 0.3→0.7
4. Landed → particles, glow, cube rotation activate
```

**State variables:**
```javascript
let groundDetected = false;      // hit-test found ground?
let portalPlaced = false;         // user tapped?
let portalAnimating = false;      // drop animation running?
let hitTestSource = null;
let hitTestSourceRequested = false;
```

### 2. Three.js Setup (inline in index.html)
**CRITICAL: Create renderer BEFORE `requestSession()`** — the XR compositor must see the canvas when the session starts. Creating renderer after session = no passthrough.

```html
<!-- Use three@0.160.0+ — 0.126.0 has broken XR passthrough -->
<script src="https://unpkg.com/three@0.160.0/build/three.min.js"></script>
```

```javascript
// 1. Renderer FIRST (before session)
renderer = new THREE.WebGLRenderer({
    canvas: canvas,
    antialias: true,
    alpha: true
});
renderer.setPixelRatio(window.devicePixelRatio);
renderer.xr.enabled = true;
renderer.xr.setReferenceSpaceType('local-floor');
renderer.setClearColor(0x000000, 0);

camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.01, 100);

scene = new THREE.Scene();

// 2. Reticle — HIDDEN by default (reticle.visible = false), shown ONLY after stable hit-test
// finds floor ≥3 consecutive frames. Showing it immediately causes flicker as ARCore recalibrates.
// After ground detected the reticle appears at floor level with scan particles attached as children.
// CRITICAL for Three.js r160+: use a Group, NOT a single Mesh, to preserve rotation.
const reticleGroup = new THREE.Group();

// Outer glowing ring (large enough to see on mobile)
const ringMesh = new THREE.Mesh(
    new THREE.RingGeometry(0.35, 0.55, 48),
    new THREE.MeshBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 1, side: THREE.DoubleSide })
);
ringMesh.rotation.x = -Math.PI / 2;  // face ground
reticleGroup.add(ringMesh);

// Inner solid disc (visible even when viewed from edge-on)
const innerDisc = new THREE.Mesh(
    new THREE.CircleGeometry(0.35, 32),
    new THREE.MeshBasicMaterial({ color: 0x22d3ee, transparent: true, opacity: 0.7, side: THREE.DoubleSide })
);
innerDisc.rotation.x = -Math.PI / 2;
reticleGroup.add(innerDisc);

// Outer glow halo (wider, fainter)
const outerGlow = new THREE.Mesh(
    new THREE.RingGeometry(0.58, 0.7, 48),
    new THREE.MeshBasicMaterial({ color: 0x0ea5e9, transparent: true, opacity: 0.35, side: THREE.DoubleSide })
);
outerGlow.rotation.x = -Math.PI / 2;
reticleGroup.add(outerGlow);

reticle = reticleGroup;
reticle.matrixAutoUpdate = true;   // Three.js handles rotation — never set to false
reticle.visible = false;            // HIDDEN — only shown after stable ground threshold met
scene.add(reticle);

// Reticle initial position: hidden until hit-test finds floor, so no need to pre-position.
// Place far-away to avoid accidental visibility if a frame renders before scanning starts.

// 3. Portal door group
const portalGroup = new THREE.Group();
portalGroup.visible = false;
scene.add(portalGroup);

// 4. THEN request session and bind
session = await navigator.xr.requestSession('immersive-ar', { ... });
renderer.xr.setSession(session);
```

**CRITICAL SETTINGS (must match or passthrough fails):**
- Creating renderer AFTER `requestSession()` — XR compositor never sees canvas → **black screen**
- Manual `gl.clear()` in render loop — overwrites XR compositor frame
- `camera.matrixAutoUpdate = false` — XR renderer manages camera matrices. Do NOT set this when scene is parented to ARHitTestResult or using XR reference space.
- Manual `camera.projectionMatrix` / `camera.matrixWorld` overrides — remove them

### 3. Hit-test + Tap-to-place
```javascript
// Request hit-test source
// CRITICAL: use 'viewer' space for hit-test, NOT 'local-floor', which fails on many devices
session.requestReferenceSpace('viewer').then(viewerSpace => {
  session.requestHitTestSource({ space: viewerSpace }).then(source => {
    hitTestSource = source;
  });
});

// HIT-TEST EACH FRAME — set position from pose.transform.position (NOT raw matrix!)
const hitTestResults = frame.getHitTestResults(hitTestSource);
if (hitTestResults.length > 0 && !portalPlaced) {
  const hit = hitTestResults[0];
  const hitPose = hit.getPose(referenceSpace); 
  if (hitPose) {
    reticle.position.set(
      hitPose.transform.position.x,
      hitPose.transform.position.y,
      hitPose.transform.position.z
    );
    if (!groundDetected) {
      groundDetected = true;
      // Hide scanning overlay, show reticle
    }
  }
}

// Tap handler
session.addEventListener('select', (event) => {
  if (!portalPlaced && groundDetected && reticle.visible) {
    placePortal();
  }
});

// Place portal at reticle position with drop animation — DO NOT use matrix.decompose!
function placePortal() {
  portalPlaced = true;
  portalAnimating = true;
  portalDropStart = performance.now();
  reticle.visible = false;
  
  // READ BACK: getWorldPosition/getWorldQuaternion (NOT matrix.decompose — throws on Groups in r160+)
  const reticlePos = new THREE.Vector3();
  const reticleQuat = new THREE.Quaternion();
  reticle.getWorldPosition(reticlePos);
  reticle.getWorldQuaternion(reticleQuat);
  
  portalGroup.visible = true;
  portalGroup.position.set(reticlePos.x, reticlePos.y + 4, reticlePos.z);
}
```

### 4. Portal drop animation (in render loop) — UPDATED for Groups
```javascript
if (portalAnimating) {
  const elapsed = performance.now() - portalDropStart;
  const t = Math.min(elapsed / 1200, 1);
  const ease = 1 - Math.pow(1 - t, 3);    // ease-out cubic
  // READ BACK reticle position via getWorldPosition — NOT matrix.decompose
  const reticlePos = new THREE.Vector3();
  reticle.getWorldPosition(reticlePos);
  portalGroup.position.y = reticlePos.y + 4 * (1 - ease);
  portal.material.opacity = 0.3 + ease * 0.4;
  if (t >= 1) {
    portalAnimating = false;
    portalGroup.position.y = reticlePos.y;
    portal.material.opacity = 0.7;
  }
}
```

### 5. Particle system (edge orbiting)
200 particles distributed along 4 frame edges, orbiting with sinusoidal drift. Use custom shaders for glow:
```javascript
// Vertex shader: circular point sprites
const particleVertexShader = `
  attribute float size;
  varying vec3 vColor;
  void main() {
    vColor = color;
    vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
    gl_PointSize = size * (300.0 / -mvPosition.z);
    gl_Position = projectionMatrix * mvPosition;
  }
`;
// Fragment shader: soft glow circle
const particleFragmentShader = `
  varying vec3 vColor;
  void main() {
    float d = length(gl_PointCoord - vec2(0.5));
    if (d > 0.5) discard;
    float glow = 1.0 - smoothstep(0.0, 0.5, d);
    glow = pow(glow, 1.5);
    gl_FragColor = vec4(vColor, glow);
  }
`;
```

### 6. WebXR Initialization (Correct Pattern)
```javascript
async function activateXR() {
  if (!navigator.xr) { setStatus('WebXR not supported'); return; }
  const supported = await navigator.xr.isSessionSupported('immersive-ar');
  if (!supported) { setStatus('AR not supported'); return; }

  // Get xr-compatible context BEFORE creating renderer
  const glContext = canvas.getContext('webgl2', { xrCompatible: true }) ||
                    canvas.getContext('webgl', { xrCompatible: true });
  if (!glContext) { setStatus('WebGL not available'); return; }

  // Create renderer with xr-compatible context
  renderer = new THREE.WebGLRenderer({
    canvas: canvas,
    context: glContext,
    antialias: true,
    alpha: true
  });
  renderer.xr.enabled = true;
  renderer.xr.setReferenceSpaceType('local-floor');
  renderer.autoClear = false;  // REQUIRED for passthrough
  renderer.setClearColor(0x000000, 0);

  // Request session with MINIMAL required features
  session = await navigator.xr.requestSession('immersive-ar', {
    requiredFeatures: [],
    optionalFeatures: ['hit-test', 'local-floor', 'dom-overlay'],
    domOverlay: { root: uiLayer }
  });
  renderer.xr.setSession(session);
  renderer.setAnimationLoop(render);  // wire to render() function, NOT inline
}
```

## Docker Deployment

### Dockerfile (HTTP-only, nginx:alpine)
```dockerfile
FROM nginx:alpine
COPY index.html /usr/share/nginx/html/
COPY css/ /usr/share/nginx/html/css/
COPY js/ /usr/share/nginx/html/js/
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    find /usr/share/nginx/html -type d -exec chmod 755 {} \; && \
    find /usr/share/nginx/html -type f -exec chmod 644 {} \;
RUN rm -f /etc/nginx/conf.d/default.conf
RUN cat > /etc/nginx/conf.d/portal.conf << 'EOF'
server {
    listen 8123;
    server_name _;
    add_header Cache-Control "no-cache, no-store, must-revalidate" always;
    add_header Cross-Origin-Embedder-Policy require-corp always;
    add_header Cross-Origin-Opener-Policy same-origin always;
    add_header Cross-Origin-Resource-Policy cross-origin always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=(self)" always;
    root /usr/share/nginx/html;
    index index.html;
    location / { try_files $uri $uri/ =404; }
}
EOF
EXPOSE 8123
CMD ["nginx", "-g", "daemon off;"]
```

### Rebuild and redeploy
```bash
cd project/
docker stop webxr-portal-door 2>/dev/null; docker rm webxr-portal-door 2>/dev/null
docker build -t webxr-portal-door .
docker run -d --name webxr-portal-door -p 8123:8123 webxr-portal-door
```

### Portal visual effects

For sci-fi portal effects showing an alien planet view from space, use either textured materials or custom GLSL shaders:

**Option 1: Texture-based portal (stable, performant)**
```javascript
const textureLoader = new THREE.TextureLoader();
const planetTexture = textureLoader.load('https://www.solarsystemscope.com/textures/download/8k_earth_daymap.jpg');
planetTexture.wrapS = THREE.RepeatWrapping;
planetTexture.wrapT = THREE.RepeatWrapping;

const portalMaterial = new THREE.MeshStandardMaterial({
    map: planetTexture,
    transparent: true,
    opacity: 0.8,
    side: THREE.DoubleSide,
    emissive: 0x0ea5e9,
    emissiveIntensity: 0.3
});

// In render loop - animate texture rotation
if (portal.material.map) {
    portal.material.map.rotation -= 0.0005;  // slow planet spin
}
```

Add atmospheric glow ring:
```javascript
const glowGeometry = new THREE.RingGeometry(0.76, 0.82, 64);
const glowMaterial = new THREE.MeshBasicMaterial({
    color: 0x0ea5e9,
    transparent: true,
    opacity: 0.6,
    side: THREE.DoubleSide
});
const glowRing = new THREE.Mesh(glowGeometry, glowMaterial);
glowRing.position.set(0, 1.4, -0.01);
portalGroup.add(glowRing);

// Pulse animation in render loop
if (glowRing && portalPlaced) {
    const pulse = 0.6 + Math.sin(timestamp * 0.003) * 0.15;
    glowRing.material.opacity = pulse;
    glowRing.scale.setScalar(1 + Math.sin(timestamp * 0.002) * 0.05);
}
```

**Option 2: GLSL shader portal (complex, may hang on mobile)**
For procedural planet surfaces with animated noise:

```javascript
const portalMaterial = new THREE.ShaderMaterial({
    uniforms: {
        time: { value: 0.0 },
        color1: { value: new THREE.Color(0x0a0a20) }, // deep space
        color2: { value: new THREE.Color(0x1a4a2e) }, // alien planet surface
        color3: { value: new THREE.Color(0x0ea5e9) }  // atmosphere glow
    },
    vertexShader: `...`,
    fragmentShader: `...`,  // noise-based terrain generation
    transparent: true,
    side: THREE.DoubleSide
});

// Update time uniform in render loop
if (portal.material.uniforms && portal.material.uniforms.time) {
    portal.material.uniforms.time.value = timestamp * 0.001;
}
```

**WARNING:** Complex GLSL shaders with noise functions can cause hangs/freezes on mobile WebXR. If the scene freezes, revert to texture-based approach (Option 1).

## Portal Step-Through (Step-Through Pattern)

For step-through portals (walk through door into another world), use **explicit tap-based navigation** — NOT automatic walking detection. Auto proximity detection is fundamentally unreliable on mobile AR:
- Camera pose tracking, reticle quaternion roll/tilt, and hit-test matrices vary by device
- Auto-detection causes false positives: the door "appears then disappears" when the scene dumps into the inside world
- Never use `camera.getWorldPosition()` + zone checks to trigger mode changes automatically

**Correct pattern:**
```javascript
// Mode transitions are EXPLICIT via tap
function onSelect() {
    if (mode === 'door' && !transitioning) {
        // Tap to enter
        triggerTransition('inside');
    } else if (mode === 'inside' && !transitioning) {
        // Tap to return
        triggerTransition('door');
    }
    // ... scanning/placement logic ...
}
```

Status messages must be clear:
- "Door placed — tap the screen to step through" (not "walk toward it")
- "You entered the other world — tap to return"

To make portal 20% smaller:
```javascript
portalGroup.scale.set(0.8, 0.8, 0.8);  // instead of (1, 1, 1)
```

### Writing code for this project

**Use direct file editing (write_file + patch) — NOT opencode.** Opencode times out at 300s on large refactors and produces truncated output. It once partially rewrote `index.html` in a way that left it at 676 lines (from ~1000+), requiring restoration from backup. Direct editing is reliable for all changes to this project.

OpenCode (opencode.ai) can be used as an autonomous coding agent for this project. Configure with custom OpenAI-compatible provider:

### Config (`~/.config/opencode/opencode.jsonc`)
```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "model": "aip/aip-best",
  "provider": {
    "aip": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "AIP",
      "options": {
        "baseURL": "http://141.33.165.84:8000/v1",
        "apiKey": "empty"
      },
      "models": {
        "aip-best": { "name": "aip-best" }
      }
    }
  }
}
```

### Usage patterns
- **One-shot:** `opencode run 'Add feature X'` — works for single-file edits, use `--format json` for machine-readable output. Timeout at 300s; if it exceeds, the task was too large.
- **Large refactors:** Split into focused single-file tasks. Opencode is slow on multi-file changes in one-shot mode.
- **CSS-only tasks:** Explicitly say "modify ONLY css/style.css" or it will try to also change HTML/JS.
- **Always scope to the project dir:** `cd project && opencode run '...'`
- **Git init required:** opencode won't track changes without a git repo.

### Pitfall: One-shot timeout on large diffs
If `opencode run` times out after 300s, the task is too large for one-shot. Break into smaller, single-file tasks or use interactive TUI mode (`pty=true`).

### Pitfall: Opencode edits wrong file
Opencode may edit `js/app.js` even when told to modify `index.html`. Always explicitly state "Modify only index.html" in the prompt, and verify the changes afterward.

### Pitfall: Opencode one-shot timeout (300s)
If `opencode run` times out after 300s, falling back to direct `patch` calls is acceptable — do not retry endlessly. The model endpoint may be slow or unavailable. For this project, targeted `patch` edits are reliable for single-line or small-block fixes (renderer settings, CSS rules, inline JS tweaks). Reserve opencode for larger multi-file refactors where the patch tool would be unwieldy.

### Pitfall: Opencode prompt corruption
When passing code blocks in `opencode run '...'`, shell interpretation of backticks and quotes can corrupt the prompt. If you see bash errors like "command not found" in output, use direct `patch` instead.

## Pitfalls

### domOverlay Feature
**Problem:** `domOverlay: { root: document.body }` causes session failures on most Android devices including Chrome with ARCore.

**Fix:** Omit domOverlay entirely or pass a specific UI layer element, not `document.body`.

### Session requiredFeatures blocking startup
**Problem:** Putting `hit-test` or `local-floor` in `requiredFeatures` causes `requestSession()` to fail silently on devices that support AR but lack those specific features. User sees button click with no error.

**Fix:** Move `hit-test` and `local-floor` to `optionalFeatures` — request them separately after session starts:
```javascript
// REQUIRED features should be empty or minimal
session = await navigator.xr.requestSession('immersive-ar', {
    requiredFeatures: [],
    optionalFeatures: ['hit-test', 'local-floor', 'dom-overlay'],
    domOverlay: { root: uiLayer }
});

// Request features separately after session starts
try {
    referenceSpace = await session.requestReferenceSpace('local-floor');
} catch(e) {
    console.warn('[AR] local-floor not available, falling back to viewer');
    referenceSpace = await session.requestReferenceSpace('viewer');
}

session.requestReferenceSpace('viewer').then(viewerSpace => {
    session.requestHitTestSource({ space: viewerSpace }).then(source => {
        hitTestSource = source;
    });
});
```

### Scanning overlay positioning
**Problem:** Scanning overlay inside `#ui-layer` gets hidden when AR hides the UI layer, leaving no visual feedback during scanning phase.

**Fix:** Place `#scanning-overlay` OUTSIDE `#ui-layer` in the HTML so it stays visible during AR mode:
```html
<div id="ui-layer">
    <header class="header">...</header>
    <div id="status"></div>  <!-- Status INSIDE ui-layer for domOverlay visibility -->
</div>
<!-- Scanning overlay OUTSIDE ui-layer -->
<div id="scanning-overlay">...</div>
```

### Status bar visibility in AR domOverlay
**Problem:** Status/debug elements placed OUTSIDE `domOverlay.root` (`#ui-layer`) are NOT composited into the XR view — invisible to the user during AR.

**Fix:** Place `#status` inside `#ui-layer` and add explicit AR-mode CSS:
```css
body.ar-active #status {
    display: block !important;
    background: rgba(0, 0, 0, 0.6) !important;
    color: #38bdf8 !important;
    position: fixed !important;
    bottom: 20px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    z-index: 100 !important;
    pointer-events: none !important;
}
```

### ARCore Requirement
**Problem:** WebXR AR requires ARCore on Android. Not all devices support it.

**Fix:** Check `navigator.xr.isSessionSupported('immersive-ar')` first. Provide clear error message.

### Browser Compatibility
**Problem:** Brave, Firefox, and Safari have limited or no WebXR AR support.

**Fix:** Only Chrome for Android supports WebXR AR reliably. Document this.

### HTTPS Required
**Problem:** WebXR AR requires HTTPS. Self-signed certs are blocked by browsers.

**Fix:** Use reverse proxy (HAProxy, nginx) with trusted SSL cert. The internal nginx container is HTTP-only.

### Three.js version pinning
**Problem:** Three.js 0.126.0 has **broken XR passthrough** — camera shows dark screen.

**Fix:** Use `three@0.160.0+` for reliable AR passthrough:
```html
<script src="https://unpkg.com/three@0.160.0/build/three.min.js"></script>
```

### Renderer initialization order + xrCompatible context
**Problem:** Two blockers cause dark passthrough:
1. Creating renderer AFTER `requestSession()` — XR compositor never sees canvas
2. Three.js creates a WebGL context WITHOUT `xrCompatible: true` — browser silently refuses to composite camera video onto it

**Fix:** Get an xr-compatible WebGL context FIRST, create renderer with it, THEN request session:
```javascript
// 1. Get xr-compatible context — prefer webgl (not webgl2) for better Android passthrough
const glContext = canvas.getContext('webgl', { xrCompatible: true }) ||
                  canvas.getContext('webgl2', { xrCompatible: true });
if (!glContext) { return; /* WebGL not available */ }

// 2. Create renderer with that context
renderer = new THREE.WebGLRenderer({
    canvas: canvas,
    context: glContext,  // pass the xr-compatible context
    antialias: true,
    alpha: true
});
renderer.setPixelRatio(window.devicePixelRatio);
renderer.xr.enabled = true;
renderer.xr.setReferenceSpaceType('local-floor');
renderer.autoClear = false;  // REQUIRED — let XR compositor manage frames
renderer.setClearColor(0x000000, 0);
renderer.toneMapping = THREE.NoToneMapping;  // avoid tone mapping artifacts in AR
// preserveDrawingBuffer: false (Three.js default) causes BLACK SCREEN on Android.
// The XR compositor cannot access frame buffer contents without it.
```html
<!-- In the renderer creation, add preserveDrawingBuffer: true -->
```
```javascript
renderer = new THREE.WebGLRenderer({
    canvas: canvas,
    context: glContext,
    antialias: true,
    alpha: true,
    preserveDrawingBuffer: true  // CRITICAL: false causes black screen on Android AR
});
```

// 3. THEN request session
session = await navigator.xr.requestSession('immersive-ar', { ... });
renderer.xr.setSession(session);
```

**Pitfall: `alert()` / `confirm()` / `prompt()` blocks XR passthrough**
Calling `alert()` in a button handler (or anywhere during XR init) blocks JavaScript execution and can cause the XR compositor to fail to initialize — user sees black screen. **Never use blocking dialogs during AR initialization.** Replace with `console.log()` or visible status messages via `setStatus()`.

**Pitfall: `environmentBlendMode === 'opaque'` means hardware doesn't support passthrough**
After session starts, check `session.environmentBlendMode`. If it's `opaque` instead of `alpha-blend`, the device does not support camera passthrough (e.g., some Samsung devices). User will see a dark background regardless of renderer settings. Add diagnostic:
```javascript
console.log('[DIAG] environmentBlendMode:', session.environmentBlendMode);
if (session.environmentBlendMode === 'opaque') {
    console.warn('[AR] Passthrough NOT available on this device');
    setStatus('⚠️ Passthrough unavailable (opaque mode)');
}
```

**Pitfall: Dead/unused render loop functions**
Having an unused function like `startRenderLoop()` with an inline `renderer.setAnimationLoop()` that only does `renderer.render()` is dangerous — if accidentally called it overrides the correct `render()` function that contains hit-test and animation logic. Remove unused render loop functions. Always wire to the named `render` function: `renderer.setAnimationLoop(render);`

### Reticle visibility + Three.js r160 readonly position pitfall

**Problem:** Reticle ring too small to see on mobile (0.1/0.12 radius). More critically, `matrixAutoUpdate = false` with manual `reticle.matrix.fromArray(hitPose.transform.matrix)` DESTROYS the reticle's rotation — if the ring has `-PI/2` X rotation to face the ground, overwriting the entire matrix each frame removes it entirely, rendering the ring edge-on and invisible.

**Even worse in Three.js r160+:** `reticle.matrix.decompose(pos, quat, scale)` throws **"cannot assign to readonly property position"** because Object3D.position is a getter-only property in recent Three.js versions. Calling decompose on any Group/Mesh triggers this crash.

**Fix (r160+ compatible):** Use a Group with `matrixAutoUpdate = true`, set position from hit-test pose's transform.position, and use `getWorldPosition()`/`getWorldQuaternion()` to read back:

```javascript
// Build reticle as a Group so rotation is preserved by Three.js
const reticleGroup = new THREE.Group();

// Outer glowing ring (large enough to see on mobile)
const ringMesh = new THREE.Mesh(
    new THREE.RingGeometry(0.35, 0.55, 48),
    new THREE.MeshBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 1, side: THREE.DoubleSide })
);
ringMesh.rotation.x = -Math.PI / 2;  // face ground
reticleGroup.add(ringMesh);

// Inner solid disc (visible even when viewed from edge-on)
const innerDisc = new THREE.Mesh(
    new THREE.CircleGeometry(0.35, 32),
    new THREE.MeshBasicMaterial({ color: 0x22d3ee, transparent: true, opacity: 0.7, side: THREE.DoubleSide })
);
innerDisc.rotation.x = -Math.PI / 2;
reticleGroup.add(innerDisc);

// Optional outer glow halo
const outerGlow = new THREE.Mesh(
    new THREE.RingGeometry(0.58, 0.7, 48),
    new THREE.MeshBasicMaterial({ color: 0x0ea5e9, transparent: true, opacity: 0.35, side: THREE.DoubleSide })
);
outerGlow.rotation.x = -Math.PI / 2;
reticleGroup.add(outerGlow);

reticle = reticleGroup;
reticle.matrixAutoUpdate = true;   // CRITICAL — Three.js handles rotation
reticle.visible = false;
scene.add(reticle);
reticle.userData = { ringMesh, innerDisc, outerGlow };

// HIT-TEST: set position from pose.transform.position (NOT the raw matrix)
const pose = results[0].getPose(referenceSpace);
reticle.position.set(
    pose.transform.position.x,
    pose.transform.position.y,
    pose.transform.position.z
);
reticle.visible = true;

// READ BACK: use getWorldPosition/getWorldQuaternion (NOT matrix.decompose)
const pos = new THREE.Vector3();
const quat = new THREE.Quaternion();
reticle.getWorldPosition(pos);
reticle.getWorldQuaternion(quat);
```

**Pulse children in render loop** (since reticle is a Group, not a Mesh):
```javascript
if (reticle && reticle.visible && reticle.userData) {
    const pulse = 0.5 + Math.sin(timestamp * 0.006) * 0.5;
    const ud = reticle.userData;
    if (ud.ringMesh) ud.ringMesh.material.opacity = 0.7 + pulse * 0.3;
    if (ud.innerDisc) ud.innerDisc.material.opacity = 0.5 + pulse * 0.25;
}
```

**Anti-patterns to avoid:**
- `reticle.matrixAutoUpdate = false` — breaks rotation inheritance on Groups
- `reticle.matrix.fromArray(hitPose.transform.matrix)` — overwrites ALL transform including rotation → ring appears edge-on and invisible
- `reticle.matrix.decompose(pos, quat, scale)` — throws "cannot assign to readonly property position" on Groups in Three.js r160+

### Hit-test reference space mismatch

**Problem:** Requesting hit-test with `local-floor` space fails, or requesting with `viewer` space but then using `referenceSpace` (which could be `local-floor`) to extract pose causes `getPose()` to return `null` silently — no reticle appears even though the session started successfully.

**Fix:** Use the **SAME** reference space that was obtained for the hit-test source. If you fall back to `viewer` when `local-floor` fails, request hit-test with `viewer` space:

```javascript\n// Request reference space — fall back to viewer if local-floor unavailable
let referenceSpace = null;
try {
  referenceSpace = await session.requestReferenceSpace('local-floor');
} catch(e) {
  console.warn('[AR] local-floor not available, falling back to viewer');
  referenceSpace = await session.requestReferenceSpace('viewer');
}

// Hit-test MUST use the same reference space that was obtained
session.requestHitTestSource({ space: referenceSpace }).then(source => {
  hitTestSource = source;
});

// HIT-TEST EACH FRAME: use the SAME referenceSpace
const results = frame.getHitTestResults(hitTestSource);
if (results.length > 0) {
  const pose = results[0].getPose(referenceSpace); // ← same space used above
  if (pose && pose.transform.position) {
    reticle.position.set(pose.transform.position.x, pose.transform.position.y, pose.transform.position.z);
  }
}
```

See `webxr-hit-test-pitfalls` skill for comprehensive debugging checklist.

### Session management
**Problem:** "There is already an active, immersive XRSession" error on repeated button taps.

**Fix:** Guard at top of `activateXR()`:
```javascript
if (session) return;  // already active
```

### Variable scope for portal elements

**Problem:** New portal elements (glow ring, particles, etc.) cause "glowRing is not defined" errors in render loop.

**Root cause:** Variables declared inside `activateXR()` without outer scope declaration are not accessible in the `render()` function.

**Fix:** Declare all portal element variables in the outer scope with `let`:
```javascript
// At top of activateXR() scope
let cube = null;
let portal = null;
let reticle = null;
let glowRing = null;  // MUST declare here, not just inside activateXR()
let hitTestSource = null;
```

Then assign inside the setup code:
```javascript
const glowRing = new THREE.Mesh(glowGeometry, glowMaterial);  // WRONG - creates local variable
glowRing = new THREE.Mesh(glowGeometry, glowMaterial);        // CORRECT - assigns to outer scope
```

Always declare new portal elements (rings, particles, effects) in the outer scope before they're used in the render loop.

### JavaScript syntax errors prevent entire script from running

**Problem:** Button click does nothing, no alerts, no console logs — entire script is blocked.

**Root cause:** Duplicate variable declarations (e.g., `const glowGeometry` declared twice, `const glowMaterial` declared twice) cause syntax errors that prevent the entire `<script>` from executing.

**Detection:**
```bash
cd project && sed -n '/<script>/,/<\/script>/p' index.html | sed '1d;$d' > /tmp/script.js
node --check /tmp/script.js
```

**Fix:** Use unique variable names for different geometries/materials:
```javascript
// First glow ring (atmospheric)
const glowGeometry = new THREE.RingGeometry(0.76, 0.82, 64);
const glowMaterial = new THREE.MeshBasicMaterial({ ... });

// Later: glow plane (background bloom) - MUST use different names
const glowPlaneGeometry = new THREE.PlaneGeometry(2.0, 3.1, 1, 1);  // NOT glowGeometry
const glowPlaneMaterial = new THREE.ShaderMaterial({ ... });        // NOT glowMaterial
```

**Common duplicates to watch for:**
- `glowGeometry` (ring vs plane)
- `glowMaterial` (basic material vs shader material)
- `particleMaterial` (multiple particle systems)
- `portalMaterial` (if switching approaches)

Always verify syntax after adding new visual elements.

### Cache-busting for mobile testing

**Problem:** Mobile browsers aggressively cache HTML/JS, showing old code after redeploy.

**Fix:** Add cache-control headers in three places:

1. **HTML meta tags** in `<head>`:
```html
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
```

2. **Nginx config** in Dockerfile:
```nginx
add_header Cache-Control "no-cache, no-store, must-revalidate" always;
add_header Pragma "no-cache" always;
add_header Expires "0" always;
```

3. **Version query strings** on static assets:
```html
<link rel="stylesheet" href="css/style.css?v=20260730">
```

**Mobile force-reload:** Add `?v=2` to URL: `https://ar.aip.de?v=2`

### Mobile debugging with visible status messages

**Problem:** Users on Android cannot access browser console to see errors or debug logs.

**Fix:** Add visible status messages for every step in the AR initialization flow:
```javascript
async function activateXR() {
    console.log('[AR] activateXR called');
    setStatus('WebXR detected, initializing...');
    
    if (!navigator.xr) {
        console.error('[AR] navigator.xr not available');
        setStatus('❌ WebXR not supported. Use Chrome on Android.');
        return;
    }
    console.log('[AR] navigator.xr available');
    setStatus('✓ WebXR available, checking AR...');

    if (session) {
        console.warn('[AR] session already active');
        setStatus('AR session already active');
        return;
    }

    try {
        const supported = await navigator.xr.isSessionSupported('immersive-ar');
        console.log('[AR] immersive-ar supported:', supported);
        if (!supported) {
            console.error('[AR] AR not supported');
            setStatus('❌ AR not supported. Install Chrome + ARCore on Android.');
            return;
        }
        setStatus('✓ AR supported, starting session...');

        // ... session request ...
        console.log('[AR] requesting immersive-ar session...');
        session = await navigator.xr.requestSession('immersive-ar', { ... });
        console.log('[AR] session acquired:', session);
        setStatus('✓ AR session started, setting up...');

        // ... reference space ...
        session.requestReferenceSpace('local-floor').then((space) => {
            referenceSpace = space;
            console.log('[PORTAL] referenceSpace acquired');
            setStatus('✓ Reference space ready, scanning floor...');
        }).catch(e => {
            console.error('[PORTAL] referenceSpace FAILED:', e);
            setStatus('❌ Reference space failed: ' + e.message);
        });
    }
}
```

**Status flow:**
1. "WebXR detected, initializing..."
2. "✓ WebXR available, checking AR..."
3. "✓ AR supported, starting session..."
4. "Requesting AR session..."
5. "✓ AR session started, setting up..."
6. "✓ Reference space ready, scanning floor..."

Each step shows ✓ success or ❌ error with message. Users can screenshot and report exact failure point.

### Inline animation loop bypassing render() function

**Problem:** `renderer.setAnimationLoop()` given an inline anonymous function skips ALL hit-test logic, portal animations, and scene updates — only a raw static render fires. Hit-test results are computed but never consumed, portal drop animation never runs, particles never move. The user sees a frozen scene or missing reticle even though session appears active.

**Root cause:** An inline callback that looks correct at first glance:
```javascript
// WRONG — hit-test + animation logic in render() NEVER fires
renderer.setAnimationLoop((timestamp, frame) => {
    renderer.render(scene, camera);  // only renders, no hit-test, no animations
});
```

**Fix:** Always wire to the named `render` function:
```javascript
renderer.setAnimationLoop(render);  // CORRECT — runs full render(timestamp, frame) with all logic
```

### Duplicate `renderer.xr.setSession(session)` call

**Problem:** `renderer.xr.setSession()` called twice on the same session object. The second call silently fails or resets state, causing passthrough issues (black screen, frozen camera).

**Root cause:** Copy-paste or refactoring leaves `setSession` in two places — e.g., once after renderer creation AND again inside a portal setup block.

**Fix:** Call `renderer.xr.setSession(session)` ONCE per session lifecycle:
```javascript
// After renderer setup, before requestSession OR immediately after acquiring session
renderer.xr.setSession(session);  // only ONE call
```

If you see a second call like `renderer.xr.setSession(session)` elsewhere in activateXR() or a setup function, remove it.

### Complex alien portal scene generation

**For impressive sci-fi portal scenes showing alien worlds**, use procedural generation instead of textures:

**Components:**
1. **Starfield background** (2000+ colored stars)
2. **Procedural terrain** with height-based vertex colors (purple valleys, pink mid-levels, cyan peaks)
3. **Floating crystals** (icosahedrons with emissive materials, orbiting and rotating)
4. **Nebula clouds** (500+ particle points with additive blending)
5. **Dynamic colored point lights** (cyan + magenta, flickering intensity)

**Example structure:**
```javascript
const portalSceneGroup = new THREE.Group();
portalSceneGroup.position.z = 0.05;
portalGroup.add(portalSceneGroup);

// 1. Starfield
const starGeometry = new THREE.BufferGeometry();
const starPositions = new Float32Array(starCount * 3);
const starColors = new Float32Array(starCount * 3);
// ... populate with random positions and HSL colors ...
const starField = new THREE.Points(starGeometry, starMaterial);
portalSceneGroup.add(starField);

// 2. Procedural terrain with sine wave heights
const terrainGeometry = new THREE.PlaneGeometry(30, 30, 128, 128);
// ... generate heights with Math.sin() combinations ...
// ... color vertices based on normalized height ...
const terrain = new THREE.Mesh(terrainGeometry, terrainMaterial);
portalSceneGroup.add(terrain);

// 3. Floating crystals (12 icosahedrons)
const crystals = [];
for (let i = 0; i < 12; i++) {
    const crystal = new THREE.Mesh(
        new THREE.IcosahedronGeometry(0.3 + Math.random() * 0.5, 0),
        new THREE.MeshStandardMaterial({
            color: new THREE.Color().setHSL(i / 12, 0.9, 0.6),
            metalness: 0.9, roughness: 0.1,
            emissive: new THREE.Color().setHSL(i / 12, 0.9, 0.3),
            emissiveIntensity: 0.5
        })
    );
    crystal.userData = { rotationSpeed: {...}, orbitAngle, orbitRadius, orbitSpeed };
    portalSceneGroup.add(crystal);
    crystals.push(crystal);
}

// 4. Nebula particles
const nebulaGeometry = new THREE.BufferGeometry();
// ... 500 particles with positions, colors, sizes ...
const nebula = new THREE.Points(nebulaGeometry, nebulaMaterial);
portalSceneGroup.add(nebula);

// 5. Dynamic lights
const mainLight = new THREE.PointLight(0x0ea5e9, 2, 50);
const secondaryLight = new THREE.PointLight(0xff00ff, 1.5, 50);
portalSceneGroup.add(mainLight);
portalSceneGroup.add(secondaryLight);

// Store for animation
portalSceneGroup.userData = { stars, terrain, crystals, nebula, lights: [mainLight, secondaryLight] };
```

**Animation in render loop:**
```javascript
if (portalSceneGroup && portalPlaced) {
    const sceneData = portalSceneGroup.userData;
    sceneData.stars.rotation.z += 0.0001;
    sceneData.crystals.forEach(crystal => {
        crystal.rotation.x += crystal.userData.rotationSpeed.x;
        crystal.userData.orbitAngle += crystal.userData.orbitSpeed;
        // ... update position from orbit ...
    });
    sceneData.nebula.material.opacity = 0.4 + Math.sin(timestamp * 0.001) * 0.1;
    sceneData.lights[0].intensity = 2 + Math.sin(timestamp * 0.003) * 0.5;
}
```

### Texture loading with error handling

**Problem:** Texture loads can fail silently or block execution on mobile with CORS or network issues.

**Fix:** Add callbacks to texture loader:
```javascript
const textureLoader = new THREE.TextureLoader();
const planetTexture = textureLoader.load(
    'https://www.solarsystemscope.com/textures/download/8k_earth_daymap.jpg',
    () => console.log('[PORTAL] Texture loaded'),
    undefined,
    (err) => console.error('[PORTAL] Texture load failed:', err)
);
```

This logs success/failure and prevents silent blocking.
### DOM overlay cleanup

**Problem:** Header and UI elements remain visible during AR, blocking camera view.

**Fix:** Add `body.ar-active` CSS class and hide non-essential elements:
```css
body.ar-active .header { display: none !important; }
body.ar-active #ui-layer > :not(#scanning-overlay) { display: none !important; }
```

In JavaScript, add the class when AR starts:
```javascript
document.body.classList.add('ar-active');
document.querySelector('.header').style.display = 'none';
```

And restore on session end:
```javascript
document.body.classList.remove('ar-active');
document.querySelector('.header').style.display = '';
```

### Portal placement transform
**Problem:** Copying the reticle's live transform directly to the portal makes it track the reticle. Replacing `Object3D.position` via `Object.assign(..., { position: new THREE.Vector3(...) })` throws `Cannot assign to read only property 'position'` and can abort all AR setup.

**Fix:** Read the marker position, then mutate the portal's existing transform. Do not replace transform fields:
```javascript
const pos = new THREE.Vector3();
reticle.getWorldPosition(pos);
portalGroup.position.set(pos.x, pos.y + dropHeight, pos.z);

// Never: Object.assign(mesh, { position: new THREE.Vector3(...) })
```
Use `.position.set(...)`, `.quaternion.copy(...)`, and `.scale.set(...)` for all Three.js scene objects.

### AR Camera Passthrough (black screen)

**Problem:** In `immersive-ar`, camera shows dark/black — no passthrough visible.

**Root causes (all block passthrough):**
- Renderer created **AFTER** `requestSession()` — XR compositor never sees canvas, always black
- `autoClear = true` with Three.js XR renderer — 3D scene clears the color buffer each frame, destroying composited video. **FIX: set `renderer.autoClear = false`.**
- Dark CSS body background (`background: var(--bg-dark)`) or pseudo-elements (`::before`, `::after`) visible during AR mode
- Manual `gl.clear()` in render loop — overwrites XR compositor frame. Remove manual clears.
- DOM scanning overlays outside `domOverlay.root` are not composited in XR
- `alert()` / `confirm()` / `prompt()` during XR init — blocks JS and compositor setup
- `environmentBlendMode === 'opaque'` — device hardware does not support passthrough (e.g., some Samsung devices)
- WebGL context order: prefer `webgl` over `webgl2` for Android Chrome passthrough compatibility
- `html` element background not cleared — set both `document.body` AND `document.documentElement` to transparent
- Unused/dead `renderer.setAnimationLoop()` override functions that bypass the main `render()` logic
- **`autoClear = false` in opaque mode** — in opaque AR mode, autoClear=false prevents the color buffer from being cleared, so scene.background and setClearColor are ignored → black screen. **Fix: set `autoClear = true` for opaque mode, `autoClear = false` for alpha-blend mode.**
- **`scene.background` doesn't render in XR opaque mode** — even with autoClear=true, scene.background is ignored by the XR compositor. **Fix: add a large BackSide sphere as the background:**
  `const bgSphere = new THREE.Mesh(new THREE.SphereGeometry(50, 32, 32), new THREE.MeshBasicMaterial({color: 0x0a1929, side: THREE.BackSide})); scene.add(bgSphere);`
- **`preserveDrawingBuffer` does NOT fix opaque mode** — the blend mode is determined by browser/OS, not renderer options. Setting `preserveDrawingBuffer: true` does not enable passthrough on devices that only support opaque.
- **Dynamic autoClear + setClearColor based on blend mode:**
  `if (opaque) { renderer.autoClear = true; renderer.setClearColor(0x0a1929, 1); } else { renderer.autoClear = false; renderer.setClearColor(0x000000, 0); }`

**Diagnosis priority: CHECK `session.environmentBlendMode` FIRST.** A black screen is most often caused by opaque blend mode (hardware limitation), NOT renderer settings. If opaque, no amount of renderer tweaking will enable camera passthrough. Optimize the opaque mode experience instead.

**Session retry strategy to coax alpha-blend:**
Only retry a session configuration if camera passthrough is the sole goal. For a placement workflow, **do not end an opaque session and retry with `{}`**: that bare session omits `hit-test`, so `requestHitTestSource()` fails and no placement marker can appear. Keep the first session requested with `optionalFeatures: ['hit-test', 'local-floor']`; configure opaque rendering separately.

**Full fix checklist (apply ALL):**
```javascript
// 1. NO blocking dialogs — use console.log or setStatus()
// 2. Prefer webgl for AR passthrough
const glContext = canvas.getContext('webgl', { xrCompatible: true }) ||
                  canvas.getContext('webgl2', { xrCompatible: true });
// 3. Create renderer with xr-compatible context, set autoClear=false
renderer = new THREE.WebGLRenderer({ canvas, context: glContext, alpha: true });
renderer.autoClear = false;
renderer.setClearColor(0x000000, 0);
// 4. Make ALL backgrounds transparent (body + html)
document.body.style.background = 'transparent';
document.documentElement.style.background = 'transparent';
// 5. Hide decorative elements
document.querySelectorAll('.bg-animation, .particle-field, .bg-orb, #loading')
    .forEach(el => el.style.display = 'none');
// 6. Check blend mode AFTER session starts — handle opaque gracefully
if (session.environmentBlendMode === 'opaque') {
    scene.background = new THREE.Color(0x0a1929);  // dark bg for opaque mode
    renderer.autoClear = true;  // REQUIRED: false causes black screen in opaque mode
    renderer.setClearColor(0x0a1929, 1);  // opaque clear matches background
    // Add scene lighting so 3D objects are visible in opaque mode
    scene.add(new THREE.AmbientLight(0x404060, 0.5));
    const dirLight = new THREE.DirectionalLight(0x38bdf8, 1);
    dirLight.position.set(2, 5, 3);
    scene.add(dirLight);
    // Add large BackSide sphere — scene.background doesn't render in XR opaque mode
    const bgSphere = new THREE.Mesh(
        new THREE.SphereGeometry(50, 32, 32),
        new THREE.MeshBasicMaterial({ color: 0x0a1929, side: THREE.BackSide })
    );
    scene.add(bgSphere);
    setStatus('Blend: opaque | 3D only (no camera passthrough)');
} else {
    scene.background = null;  // CRITICAL: must be null for alpha-blend passthrough
    setStatus('Blend: alpha-blend | Camera: active');
}
// 7. Remove dead render loop functions; use renderer.setAnimationLoop(render);
```

Also add CSS:
```css
body.ar-active { background: transparent !important; }
body.ar-active .bg-animation,
body.ar-active .bg-animation::before,
body.ar-active .bg-animation::after { display: none !important; }
body.ar-active .particle-field { display: none !important; }
body.ar-active .bg-orb { display: none !important; }
body.ar-active .header { display: none !important; }
```

### Touch placement and render isolation

**Problem:** AR scan works but tapping does not drop the door, or a portal texture error makes the entire door disappear.

**Fix:** Mobile WebXR can omit XR `select` for touchscreen taps. Route both `select` and canvas `pointerdown` to one idempotent placement handler; use a short front-of-camera fallback if hit-test never resolves. Clear the timer/listener on session end.
```javascript
session.addEventListener('select', onSelect);
canvas.addEventListener('pointerdown', onCanvasPointerDown, { passive: true });
function onCanvasPointerDown() {
  if (session && renderer.xr.isPresenting) onSelect();
}
// onSelect must guard: mode === 'scanning' && !doorPlaced
```

Render the offscreen portal texture in `try/catch/finally`; always restore `renderer.setRenderTarget(null)`. If it fails, disable the decorative texture but continue with the final `renderer.render(scene, camera)` so the physical door remains visible.

### Scanning overlay z-index
**Problem:** DOM overlays in AR need `pointer-events: none` to let taps reach the session.

**Fix:** Always set `pointer-events: none` on scanning overlays, reticles, and guides during AR sessions.
