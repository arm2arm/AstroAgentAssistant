---
name: reana-client-multi-backend
title: Configure REANA client for multiple back‑ends (dev & prod)
description: Re-homed reference: instructions to set up ~/.reana/config.yaml with dev and prod profiles and run reana-client via Docker using REANA_PROFILE.

## Summary
Create a reusable `~/.reana/config.yaml` with profiles `dev` and `prod` and run the Dockerized reana-client with `-v "$HOME/.reana/config.yaml:/root/.reana/config.yaml:ro" -e REANA_PROFILE=dev`.

## Key commands
```bash
mkdir -p ~/.reana
# write ~/.reana/config.yaml with keys `dev:` and `prod:` containing server_url and access_token

docker run --rm \
  -v "$HOME/.reana/config.yaml:/root/.reana/config.yaml:ro" \
  -e REANA_PROFILE=dev \
  reanahub/reana-client:0.95.0-alpha.3 ping
```

## Pitfalls
- Keep config permission 600. Do not commit tokens.
- Mount the file read-only into the container.
