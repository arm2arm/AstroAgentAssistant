# HAProxy WebXR Configuration

## Cross-Origin Isolation Headers

WebXR requires these headers to be set correctly. Without them, `navigator.xr.requestSession('immersive-ar')` fails silently.

### Required Headers (must be present):
- `Cross-Origin-Embedder-Policy: require-corp`
- `Cross-Origin-Opener-Policy: same-origin`
- `Cross-Origin-Resource-Policy: cross-origin`

### Permissions-Policy Pitfall (CRITICAL)

A blanket `Permissions-Policy` in the HAProxy frontend applies to ALL domains:

```haproxy
rspadd Permissions-Policy:\ geolocation=(),\ microphone=(),\ camera=()
```

This blocks camera access for `ar.aip.de` and any other domain using the same frontend.

### Fix: Domain-Specific Override

Remove blanket policy for specific domains and add domain-specific headers:

```haproxy
# In frontend section:

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

### X-Forwarded-Proto Header

Must be set for WebXR to detect HTTPS:
```haproxy
http-request set-header X-Forwarded-Proto https
http-request set-header Host ar.aip.de
```

### Verification

```bash
# Check response headers
curl -sI https://ar.aip.de | grep -iE "permissions-policy|cross-origin"

# Expected output:
# Permissions-Policy: geolocation=(), microphone=(), camera=(self)
# Cross-Origin-Embedder-Policy: require-corp
# Cross-Origin-Opener-Policy: same-origin
# Cross-Origin-Resource-Policy: cross-origin
```

### Complete Frontend Example

```haproxy
frontend www-https
    bind 141.33.4.130:443 ssl crt /etc/haproxy/certs/ar.aip.de.pem
    
    # Global security headers (apply to all)
    rspadd X-Frame-Options:\ DENY
    rspadd X-Content-Type-Options:\ nosniff
    rspadd Permissions-Policy:\ geolocation=(),\ microphone=(),\ camera=()
    
    # AR domain overrides
    rspdel ^Permissions-Policy:\ if { ssl_fc_sni ar.aip.de }
    rspadd Cross-Origin-Embedder-Policy:\ require-corp\ if { ssl_fc_sni ar.aip.de }
    rspadd Cross-Origin-Opener-Policy:\ same-origin\ if { ssl_fc_sni ar.aip.de }
    rspadd Cross-Origin-Resource-Policy:\ cross-origin\ if { ssl_fc_sni ar.aip.de }
    rspadd Permissions-Policy:\ geolocation=(),\ microphone=(),\ camera=(self)\ if { ssl_fc_sni ar.aip.de }
    
    # Routing
    use_backend bk_ar if { ssl_fc_sni ar.aip.de }
```

### Session Info
- **Date:** 2026-07-29
- **Domain:** ar.aip.de
- **Host IP:** 141.33.55.137:8123 (Docker container)
- **HAProxy host:** 141.33.4.130
- **Issue:** Permissions-Policy camera=() blocking camera, WebXR AR failing
- **Root cause:** Blanket Permissions-Policy in frontend, missing cross-origin headers, domOverlay causing failures, browser compatibility (Brave vs Chrome)
