# Docker Permission Pitfall

## Problem
Files copied into Docker images get root ownership with restrictive permissions (600). nginx runs as non-root user and gets 403 Forbidden errors.

## Reproduction
1. `COPY index.html /usr/share/nginx/html/`
2. Start container → HTTP 403
3. `docker exec container ls -la /usr/share/nginx/html/` shows `rw-------` files owned by root

## Fix
Add to Dockerfile after COPY commands:
```dockerfile
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    find /usr/share/nginx/html -type d -exec chmod 755 {} \; && \
    find /usr/share/nginx/html -type f -exec chmod 644 {} \;
```

## Why It Happens
Docker COPY preserves source file permissions. Files created by root user get 600 (owner read/write only). nginx worker runs as `nginx` user which can't read them.
