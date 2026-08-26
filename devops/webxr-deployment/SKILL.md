---
name: webxr-deployment
title: Deploy WebXR apps via Docker, nginx, and HAProxy
description: >-
  Deploy WebXR apps via Docker, nginx, and HAProxy.
author: Hermes Agent
date: 2026-07-29
tags: [webxr, three.js, chrome, arcore, haproxy, nginx, docker]
---

# WebXR Deployment

## Quick Start

```bash
cd /path/to/webxr-app
docker build -t webxr-app .
docker run -d -p 8123:8123 webxr-app
```

## WebXR AR Requirements Checklist

All must be true for `immersive-ar` to work:

1. **HTTPS** — `location.protocol !== 'https:'` blocks the session
2. **Cross-origin isolation headers** — `COEP: require-corp`, `COOP: same-origin`, `CORP: cross-origin`
3. **Chrome on Android** — Brave/Firefox have no WebXR AR support
4. **ARCore installed** — Google Play Store → "ARCore"
5. **Permissions-Policy allows camera** — `camera=(self)`, no blanket `camera=()`

## Debugging WebXR Session Failures

### Check browser support
```javascript
console.log('WebXR:', 'xr' in navigator);
navigator.xr.isSessionSupported('immersive-ar').then(s => console.log('AR:', s));
navigator.xr.isSessionSupported('immersive-vr').then(s => console.log('VR:', s));
```

### Verify HAProxy headers
```bash
curl -sI https://ar.aip.de | grep -iE "cross-origin|permissions-policy"
```

### Add debug overlay during development
```html
<div id="debug" style="position:fixed;top:70px;right:10px;
  background:rgba(0,0,0,0.85);color:#38bdf8;padding:15px;
  border-radius:8px;font-family:monospace;font-size:12px;z-index:999;">
  <div>WebXR: <span id="dbg-xr">checking...</span></div>
  <div>AR: <span id="dbg-ar">checking...</span></div>
  <div>HTTPS: <span id="dbg-https">checking...</span></div>
</div>
```

## HAProxy Per-Domain Override

When a blanket `Permissions-Policy: camera=()` exists for all domains:

```haproxy
rspdel ^Permissions-Policy:\ if { ssl_fc_sni ar.aip.de }
rspdel ^Cross-Origin-Embedder-Policy:\ if { ssl_fc_sni ar.aip.de }
rspdel ^Cross-Origin-Opener-Policy:\ if { ssl_fc_sni ar.aip.de }
rspdel ^Cross-Origin-Resource-Policy:\ if { ssl_fc_sni ar.aip.de }
rspadd Cross-Origin-Embedder-Policy:\ require-corp\ if { ssl_fc_sni ar.aip.de }
rspadd Cross-Origin-Opener-Policy:\ same-origin\ if { ssl_fc_sni ar.aip.de }
rspadd Cross-Origin-Resource-Policy:\ cross-origin\ if { ssl_fc_sni ar.aip.de }
rspadd Permissions-Policy:\ geolocation=(),\ microphone=(),\ camera=(self)\ if { ssl_fc_sni ar.aip.de }
```

## Docker Nginx — Fix Permissions

Files created on host (e.g., `chmod 600`) retain permissions after `COPY`. nginx gets 403.

```dockerfile
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    find /usr/share/nginx/html -type d -exec chmod 755 {} \; && \
    find /usr/share/nginx/html -type f -exec chmod 644 {} \;
```

## Three.js + WebXR Session Pattern

```javascript
async function startAR() {
    const supported = await navigator.xr.isSessionSupported('immersive-ar');
    if (!supported) return;
    
    const features = ['local-floor'];
    for (const feature of ['hit-test', 'hand-tracking', 'light-estimation']) {
        try {
            await navigator.xr.isSessionSupported('immersive-ar', {
                requiredFeatures: [feature]
            });
            features.push(feature);
        } catch { /* not supported */ }
    }
    
    const session = await navigator.xr.requestSession('immersive-ar', {
        requiredFeatures: features,
        optionalFeatures: featuresList
    });
    renderer.xr.setSession(session);
    renderer.setAnimationLoop(() => { /* render loop */ });
}
```

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `SecurityError` | Missing cross-origin headers | Add COEP/COOP/CORP |
| `NotSupported` | ARCore not installed | Install ARCore |
| `session creation failed` | Required feature unavailable | Drop from requiredFeatures |
| `HTTPS required` | Accessing via HTTP | Use HTTPS endpoint |
| 403 Forbidden | nginx file permissions | Fix chown/chmod in Dockerfile |

## Desktop vs Mobile

| Platform | immersive-ar | immersive-vr |
|----------|-------------|-------------|
| Chrome Android | ✅ (with ARCore) | ✅ |
| Chrome Desktop | ❌ | ✅ (headsets) |
| Brave/Firefox | ❌ | ❌ |

## Browser Cache Pitfall

After Docker rebuild, browser may serve cached CSS/JS. User sees old theme/colors.

**Always verify container content matches source:**
```bash
# Check CSS being served
curl -s http://localhost:8123/css/style.css | grep -oE "0x[0-9a-fA-F]{6}|#[0-9a-fA-F]{6}" | sort -u
# Check HTML being served
curl -s http://localhost:8123 | grep -c "new-section-id"
```

If container has old content, check for file permission issues or stale Docker layers:
```bash
docker stop webxr-portal-door 2>/dev/null
docker rm webxr-portal-door 2>/dev/null
docker build --no-cache -t webxr-portal-door .
docker run -d --name webxr-portal-door -p 8123:8123 webxr-portal-door
```

Force client cache bypass: `Ctrl+Shift+R` or incognito mode.

## Container Serving Wrong Port

Multiple web apps may run on different ports (e.g., port 8123 for custom app, 8124 for React XR).

**Verify which app is live:**
```bash
docker ps | grep webxr-portal
curl -s http://localhost:8123 | head -3   # Custom app
curl -s http://localhost:8124 | head -3   # React portal
```

Update HAProxy backend to point to correct port:
```haproxy
server col 127.0.0.1:8123 check inter 30s  # Custom app
# OR
server col 127.0.0.1:8124 check inter 30s  # React portal
```