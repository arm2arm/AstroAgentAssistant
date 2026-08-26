---
name: webxr-experience
description: Build WebXR portal doors. Use when creating portal doors.
version: 1.0.0
author: Hermes Agent
---

# WebXR Experience Development

Create WebXR portal doors and AR experiences with camera access, running in browsers behind HAProxy with HTTPS.

## What It Covers

- Three.js + WebXR portal experiences
- Direct camera access (`getUserMedia`) vs WebXR AR
- Docker deployment with nginx
- HAProxy SSL termination with WebXR headers
- Browser compatibility issues

## Workflow

### 1. Project Structure
```
project/
├── index.html          # Landing page with buttons
├── css/style.css       # Styling
├── js/app.js           # Three.js + WebXR logic
├── Dockerfile          # nginx container
├── ssl/                # Pre-generated certs (if building SSL in Docker)
└── .dockerignore
```

### 2. Key Code Patterns

**Direct Camera Access (Universal):**
```javascript
// Works on any browser with HTTPS
async openCamera() {
  const stream = await navigator.mediaDevices.getUserMedia({
    video: { facingMode: 'environment', width: 1920, height: 1080 },
    audio: false
  });
  videoElement.srcObject = stream;
  videoElement.play();
}
```

**WebXR AR (Chrome for Android only):**
```javascript
// Check support first
const supported = await navigator.xr.isSessionSupported('immersive-ar');
if (!supported) return;

// Dynamic feature detection (don't hardcode domOverlay)
const features = ['local-floor'];
// Try optional features one by one
const session = await navigator.xr.requestSession('immersive-ar', {
  requiredFeatures: features,
  optionalFeatures: ['hand-tracking', 'hit-test', 'light-estimation']
});
```

### 3. Browser Compatibility

| Feature | Chrome Android | Brave | Firefox | Desktop Chrome |
|---------|---------------|-------|---------|----------------|
| Direct Camera | ✅ | ✅ | ✅ | ✅ |
| WebXR AR | ✅ | ❌ | ❌ | ❌ |
| WebXR VR | ✅ | Partial | ❌ | ✅ (flags) |

**Requirements for WebXR AR:**
- Chrome for Android (NOT Brave)
- ARCore installed on device
- HTTPS URL (not localhost)
- `crossOriginIsolated` headers

### 4. Docker Deployment

**Critical Permission Fix:**
```dockerfile
# Files copied into Docker get root:root 600 permissions
# This causes 403 errors - nginx can't read them
COPY index.html /usr/share/nginx/html/
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    find /usr/share/nginx/html -type d -exec chmod 755 {} \; && \
    find /usr/share/nginx/html -type f -exec chmod 644 {} \;
```

**Dockerfile Template:**
```dockerfile
FROM nginx:alpine
COPY . /usr/share/nginx/html/
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    find /usr/share/nginx/html -type d -exec chmod 755 {} \; && \
    find /usr/share/nginx/html -type f -exec chmod 644 {} \;
RUN rm -f /etc/nginx/conf.d/default.conf
RUN cat > /etc/nginx/conf.d/portal.conf << 'EOF'
server {
    listen 8123;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;
    location / { try_files $uri $uri/ =404; }
}
EOF
EXPOSE 8123
CMD ["nginx", "-g", "daemon off;"]
```

### 5. HAProxy Configuration

**Frontend (SSL Termination):**
```haproxy
frontend webxr_frontend
    bind *:443 ssl crt /etc/haproxy/certs/webxr.pem
    
    # Required for WebXR
    http-response set-header Cross-Origin-Embedder-Policy require-corp
    http-response set-header Cross-Origin-Opener-Policy same-origin
    http-response set-header Cross-Origin-Resource-Policy cross-origin
    
    # Forward protocol
    http-request set-header X-Forwarded-Proto https
    http-request set-header Host webxr.example.com
    
    use_backend webxr_backend
```

**Backend:**
```haproxy
backend webxr_backend
    mode http
    server webxr 127.0.0.1:8123 check inter 30s
```

### 6. Common Pitfalls

1. **403 errors** - Fix file permissions in Dockerfile (`chown nginx:nginx`)
2. **WebXR not working** - Need Chrome for Android, not Brave. Check browser with Chrome.
3. **`domOverlay` failures** - Don't use `domOverlay` in session request. Many devices don't support it.
4. **Feature detection** - Use `isSessionSupported()` to check each feature before requesting. Don't hardcode.
5. **Camera access** - Requires HTTPS (HAProxy termination). HTTP localhost won't work.
6. **Self-signed certs** - Browsers block WebXR on untrusted certificates. Use proper SSL.
7. **`Permissions-Policy: camera=()` blocks ALL domains** — If HAProxy has a blanket `Permissions-Policy` in the frontend, it blocks camera for `ar.aip.de` too. Fix: use `rspdel` + `rspadd` with `{ ssl_fc_sni ar.aip.de }` to override per-domain. Must set `camera=(self)` not `camera=()`.
8. **Vite + React Three XR** — Modern stack uses `@vitejs/plugin-react` which changed API. Remove `babel` key from plugin config. Run `pnpm config set allow-scripts true` before `pnpm build` to allow esbuild scripts.

### 7. Modern Design Patterns

Use glass-morphism cards, gradient text, animated backgrounds, and hero sections for premium portal landing pages. See `references/css-theming.md` for CSS variable palettes.

**Key patterns:**
- `:root` CSS custom properties for theme variables (primary, accent, bg-dark, bg-card, text-muted, border, glow)
- Animated gradient backgrounds via `radial-gradient` + `repeating-linear-gradient` with `@keyframes`
- Glass-morphism cards: `backdrop-filter: blur(20px)`, semi-transparent backgrounds, colored borders
- Gradient text: `-webkit-background-clip: text` with animated `background-size: 200%`
- Hero section: full-viewport flexbox, badge pill, two action buttons (primary/secondary), stats row
- Navigation: fixed top bar with `backdrop-filter: blur(20px)`, brand icon, gradient text

**Design system:** `references/css-theming.md` — pre-built palettes (ocean blue, purple, green, red)

### 8. React Three XR (Vite + TypeScript)

Modern WebXR stack. Session 2026-07-29 deployed to `/home/hermes/projects/react-xr-portal`.

**Build flow:**
1. `pnpm install`
2. Fix Vite config: remove `babel` key from `@vitejs/plugin-react` (changed API)
3. `pnpm config set allow-scripts true` (allows esbuild postinstall)
4. `pnpm build` → outputs to `dist/`
5. Serve via nginx Docker container

**Common build errors:**
- `babel` key in Vite config → remove it (plugin API changed in v6+)
- esbuild scripts ignored → `pnpm config set allow-scripts true`
- TypeScript config present but not loaded on CLI → ignore, doesn't block build
