---
name: webxr-dev
description: Build WebXR portals and AR/VR browser apps in Three.js.
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [webxr, threejs, ar, vr, immersive-web, docker, nginx, ssl]
---

# WebXR Portal & Immersive Web Projects

Class-level skill for building WebXR-enabled immersive web experiences — portal doors, AR overlays, VR rooms, and interactive 3D pages that run in the browser.

**Triggers:**
- User wants to build a WebXR/AR/VR web page, portal experience, or 3D browser app
- Need to serve WebXR content with HTTPS (required by browsers for WebXR APIs)
- Building interactive Three.js + WebXR demos with Docker deployment

## Workflow

1. **Scaffold project** — create `index.html`, `css/style.css`, `js/app.js`, `package.json`
2. **Add Three.js** — load from CDN (jsdelivr three@0.150.0) or npm for larger projects
3. **Create 3D scene** — initialize Three.js scene, camera, renderer with `renderer.xr.enabled = true`
4. **Add XR session support** — detect WebXR availability, check `immersive-ar` and `immersive-vr` modes, provide fallbacks
5. **Implement AR/VR** — use `renderer.xr.setSession()`, `renderer.setAnimationLoop()` for XR frame callbacks
6. **Deploy with Docker** — serve on HTTP port + HTTPS port (WebXR requires HTTPS)

## WebXR Requirements (critical)

- **HTTPS is REQUIRED** for WebXR APIs. Both HTTP and HTTPS endpoints needed for dev
- Self-signed certificates work but browsers show warnings — user must click "Proceed anyway"
- WebXR AR (`immersive-ar`) only works on Chrome for Android (mobile AR)
- WebXR VR (`immersive-vr`) works on desktop Chrome with flags enabled (`chrome://flags → WebXR`)
- WebXR is NOT available in Firefox, Safari, or Edge as of 2026

## AR Session Pattern

```javascript
async enterAR() {
  const session = await navigator.xr.requestSession('immersive-ar', {
    requiredFeatures: ['local-floor'],
    optionalFeatures: ['hand-tracking', 'dom-overlay', 'hit-test'],
    domOverlay: { root: document.body }
  });
  this.renderer.xr.setSession(session);
  // Use renderer.setAnimationLoop() for XR frame callbacks
}
```

## VR Session Pattern

```javascript
async enterVR() {
  const session = await navigator.xr.requestSession('immersive-vr', {
    requiredFeatures: ['local-floor'],
    optionalFeatures: ['bounded-floor']
  });
  this.renderer.xr.setSession(session);
}
```

## Detection & Fallback

```javascript
if (!('xr' in navigator)) {
  // No WebXR — show disabled button
} else {
  navigator.xr.isSessionSupported('immersive-ar').then(supported => {
    if (supported) { /* enable AR button */ }
    else {
      // Try VR as fallback
      navigator.xr.isSessionSupported('immersive-vr').then(vrSupported => {
        if (vrSupported) { /* enable VR button instead */ }
        else { /* show not supported */ }
      });
    }
  });
}
```

## Shader Portal Pattern

Use custom GLSL shaders for portal effects — vertex displacement + fragment color mixing with time uniforms:

```glsl
// Vertex: displace Z based on sin/cos of position + time
// Fragment: mix colors based on UV coords + time + spiral distance
```

## Docker + WebXR Deployment

### SSL Certificates
Generate on host, COPY into image. Never generate inside Dockerfile — `openssl` in Alpine exits code 1 silently:
```bash
mkdir -p ssl/
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/server.key -out ssl/server.crt \
  -subj "/CN=localhost" 2>/dev/null
```

### Dual-Port Pattern
Serve both HTTP (for dev) and HTTPS (for WebXR):
```nginx
server { listen 8123; ... }          # HTTP for dev
server { listen 8124 ssl; ... }      # HTTPS for WebXR
```
Dockerfile: `EXPOSE 8123 8124`, run with `-p 8123:8123 -p 8124:8124`

### File Permissions
After COPY, files are root:root with mode 600. Fix:
```bash
docker exec <container> chown -R nginx:nginx /usr/share/nginx/html
docker exec <container> find /usr/share/nginx/html -type d -exec chmod 755 {} \;
docker exec <container> find /usr/share/nginx/html -type f -exec chmod 644 {} \;
```

### Required Headers (Nginx — HTTP only, HAProxy terminates SSL)
```nginx
add_header Cross-Origin-Embedder-Policy require-corp always;
add_header Cross-Origin-Opener-Policy same-origin always;
add_header Cross-Origin-Resource-Policy cross-origin always;
```

### Required Headers (HAProxy — SSL termination, domain-specific)
HAProxy must add cross-origin headers per-domain using `rspdel` + `rspadd`.
CRITICAL: A blanket `Permissions-Policy: camera=()` in frontend config blocks camera for ALL domains.

```haproxy
# Remove blanket headers for ar.aip.de
rspdel ^Permissions-Policy:\ if { ssl_fc_sni ar.aip.de }
rspdel ^Cross-Origin-Embedder-Policy:\ if { ssl_fc_sni ar.aip.de }
rspdel ^Cross-Origin-Opener-Policy:\ if { ssl_fc_sni ar.aip.de }
rspdel ^Cross-Origin-Resource-Policy:\ if { ssl_fc_sni ar.aip.de }

# Add domain-specific headers
rspadd Cross-Origin-Embedder-Policy:\ require-corp\ if { ssl_fc_sni ar.aip.de }
rspadd Cross-Origin-Opener-Policy:\ same-origin\ if { ssl_fc_sni ar.aip.de }
rspadd Cross-Origin-Resource-Policy:\ cross-origin\ if { ssl_fc_sni ar.aip.de }
rspadd Permissions-Policy:\ geolocation=(),\ microphone=(),\ camera=(self)\ if { ssl_fc_sni ar.aip.de }
```

Also set forwarded headers:
```haproxy
http-request set-header X-Forwarded-Proto https
http-request set-header Host ar.aip.de
```

**Verify:** `curl -sI https://ar.aip.de | grep -iE "permissions-policy|cross-origin"`

### React Three XR (modern stack)
For React-based XR, use React Three Fiber + @react-three/xr (Vite build):
```bash
git clone https://github.com/WawasCode/DefaultReactXR.git
cd DefaultReactXR && pnpm install && pnpm build
# Build outputs to dist/ — serve with any static server
```
Key: fix Vite config for newer @vitejs/plugin-react (remove `babel` key).
Set `pnpm config set allow-scripts true` to allow esbuild build scripts.

## Three.js Version (critical)

**Use Three.js 0.160.0+ for WebXR projects.** Older versions (0.126.0, 0.150.0) have unreliable XR passthrough, broken `renderer.xr` handling, and missing features like proper reference space management.

```html
<!-- CORRECT — modern version with full XR support -->
<script src="https://unpkg.com/three@0.160.0/build/three.min.js"></script>
<!-- WRONG — unreliable XR passthrough -->
<script src="https://unpkg.com/three@0.126.0/build/three.js"></script>
```

## AR Camera Passthrough (critical)

**Renderer initialization order is device/browser-dependent.** Some browsers require renderer BEFORE session, others AFTER. If passthrough shows black screen, try the opposite order.

**Pattern A: Renderer BEFORE session (Chrome Android typical):**
```javascript
// Create renderer with XR support
renderer = new THREE.WebGLRenderer({
    canvas: canvas,
    antialias: true,
    alpha: true,
    preserveDrawingBuffer: false,
    powerPreference: 'high-performance'
});
renderer.xr.enabled = true;
renderer.xr.setReferenceSpaceType('local-floor');
renderer.autoClear = false; // XR compositor manages clearing

// THEN request session
session = await navigator.xr.requestSession('immersive-ar', {
    requiredFeatures: ['hit-test', 'local-floor'],
    optionalFeatures: ['dom-overlay'],
    domOverlay: { root: uiLayer }
});

renderer.xr.setSession(session);
```

**Pattern B: Renderer AFTER session (if Pattern A shows black):**
```javascript
// Request session FIRST
session = await navigator.xr.requestSession('immersive-ar', {
    requiredFeatures: ['hit-test', 'local-floor'],
    optionalFeatures: ['dom-overlay'],
    domOverlay: { root: uiLayer }
});

// THEN create renderer with active session
renderer = new THREE.WebGLRenderer({
    canvas: canvas,
    antialias: true,
    alpha: true,
    preserveDrawingBuffer: false
});
renderer.xr.enabled = true;
renderer.xr.setSession(session); // Bind immediately
```

**Critical settings for passthrough:**
- `preserveDrawingBuffer: false` — let XR compositor manage framebuffer
- `autoClear: false` — XR session handles clearing, not Three.js
- `renderer.setClearColor()` — avoid or use with alpha=0
- `scene.background = null` — no background color/texture
- Canvas CSS: `background: transparent !important`

**BLOCKS PASSTHROUGH (do NOT do any of these):**
```javascript
// ❌ Manual camera matrix overrides during XR frame
camera.matrixAutoUpdate = false;
camera.projectionMatrix.fromArray(view.projectionMatrix);

// ❌ Manual framebuffer clear
gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

// ❌ Non-transparent body/canvas backgrounds in CSS
body { background: #0a1929; } // ← leaks through in AR
```

**Transparent background in AR:** Dark CSS body backgrounds leak through the composited view. Use a CSS class toggle + inline styles:
```javascript
// On AR entry:
document.body.style.background = 'transparent';
canvas.style.background = 'transparent';
document.body.classList.add('ar-active');

// In CSS — strip dark backgrounds from DOM overlays:
body.ar-active .header,
body.ar-active #ui-layer {
    background: transparent !important;
    backdrop-filter: none !important;
    box-shadow: none !important;
}

// On session end — restore:
document.body.style.background = '';
document.body.classList.remove('ar-active');
```

**DOM overlays in XR:** Elements that should appear in XR (scanning overlays, reticle guides, status) must be children of the `domOverlay.root` element. Elements outside it are not composited.
```javascript
// WRONG — scanning overlay outside domOverlay root, won't render in XR
<div id="scanning-overlay">...</div>  <!-- sibling of #ui-layer → NOT composited -->

// CORRECT — scanning overlay INSIDE domOverlay root
<div id="ui-layer">
    <header>...</header>
    <div id="scanning-overlay">...</div>  <!-- child of #ui-layer → composited -->
</div>
```

## Development Workflow

**Use opencode as the primary coding agent for WebXR projects.** Configure opencode with a custom OpenAI-compatible provider and run iterative tasks via `opencode run` in the project directory.

## Common Pitfalls

- **SSL cert generation inside Dockerfile FAILS** — `openssl` in Alpine exits code 1 for obscure reasons. Generate on host, COPY into image.
- **`add_header` is NOT allowed inside `if ($request_method = 'OPTIONS')` blocks** in nginx. Move all `add_header` directives to `server {}` or `location {}` level.
- **File permissions cause 403** — nginx runs as `nginx:nginx`. Fix ownership and permissions after COPY.
- **WebXR fails with "not a secure context"** — must use HTTPS (port 8124), not HTTP (port 8123).
- **WebXR AR only on mobile** — `immersive-ar` only works on Chrome for Android. Samsung Browser may not support WebXR — test with Chrome.
- **`alert()` in error handlers is non-UX-friendly** — use styled DOM overlay instead.
- **XR frame callback must use `renderer.setAnimationLoop()`** — not `requestAnimationFrame()` during XR sessions.
- **Healthcheck against HTTPS with self-signed cert fails** — use HTTP port in HEALTHCHECK or pass `-k` to wget.
- **Dark screen in AR mode** — caused by one or more: manual `gl.clear()`, `camera.matrixAutoUpdate = false`, manual camera matrix overrides, non-transparent body background, or DOM elements outside `domOverlay.root`. See "AR Camera Passthrough" section.
- **Browser caching blocks updates** — add `<meta http-equiv="Cache-Control">` tags and nginx `add_header Cache-Control "no-cache"` to force reload on mobile. Use version query strings (`style.css?v=20260730`) for CSS/JS files.
- **Complex GLSL shaders can freeze mobile browsers** — if scene hangs, simplify to `MeshBasicMaterial` or `MeshStandardMaterial` with textures instead of custom fragment shaders. Test on target device early.
- **Variables used in render loop must be declared in outer scope** — `let glowRing = null;` at module level, then assign `glowRing = new THREE.Mesh(...)` inside init function. Three distinct failure modes (all crash AR at runtime, none caught by `node --check`):
  - **Declared but never assigned** — `let portal = null;` at top, but no `portal = new THREE.Mesh(...)` anywhere in setup. Any handler doing `portal.parent` (e.g. tap-to-place) throws `TypeError: Cannot read properties of null (reading 'parent')`. Grep the setup to confirm every outer-scope `let` actually receives an assignment.
  - **`const` shadows the outer `let`** — `const portalSceneGroup = new THREE.Group();` inside `activateXR()` re-declares a new local that shadows the outer `let portalSceneGroup = null;`. The top-level `render()` still reads `null` → `ReferenceError`/`TypeError` once the portal is placed, killing the animation loop. When you intend to fill an outer-scope variable, ASSIGN (`portalGroup = new THREE.Group()`), never `const`-redeclare.
  - **Group referenced via a mesh's `.parent`** — if `portal` (the mesh) is added to `portalGroup`, `portal.parent` works only after `portal` is assigned. Safer: keep a top-level `let portalGroup = null;` and use it directly instead of deriving from `portal.parent`.
  Quick verification after an AR refactor: `grep -nE "let portal|portal = new THREE.Mesh|portalGroup = new|portalSceneGroup = "` and eyeball that each outer `let` has a matching assignment. `node --check` only catches syntax, never scoping/runtime null-derefs.
- **Texture loader callbacks for debugging** — always add load/error callbacks to `TextureLoader.load()` to catch CORS or network issues on mobile.

## Mobile Debugging Strategy

When AR button appears unresponsive on mobile:

1. **Add visible status messages** — don't rely on console.log. Show each step in the DOM:
   ```javascript
   setStatus('WebXR detected, initializing...');
   setStatus('✓ WebXR available, checking AR...');
   setStatus('✓ AR supported, starting session...');
   ```

2. **Add alert() for button click confirmation** — temporary debug to verify event listener works:
   ```javascript
   startButton.addEventListener('click', () => {
       alert('Button clicked! navigator.xr: ' + !!navigator.xr);
       activateXR();
   });
   ```

3. **Force cache refresh** — tell user to:
   - Add `?v=2` to URL: `https://ar.aip.de?v=2`
   - Use Incognito/Private mode
   - Clear browser cache in settings

4. **Check for Samsung Browser vs Chrome** — Samsung Browser may lack WebXR support. Recommend Chrome + ARCore.

5. **Graceful degradation** — if `immersive-ar` fails, try `immersive-vr` fallback or show clear error message with device requirements.

6. **Syntax errors prevent all JavaScript** — duplicate variable declarations (`const glowMaterial` twice) cause silent script failure. Validate with `node --check` before deploying.

7. **Camera passthrough troubleshooting** — if screen stays black after session starts:
   - Try renderer initialization order (BEFORE vs AFTER session request)
   - Check `preserveDrawingBuffer: false` and `autoClear: false`
   - Verify no manual camera matrix overrides in render loop
   - Confirm CSS backgrounds are transparent
   - Test on Chrome (not Samsung Browser) with ARCore installed