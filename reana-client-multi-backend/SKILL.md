---
name: reana-client-multi-backend
title: "Configure REANA client for multiple back‑ends (dev & prod)"
description: "Reusable instructions to set up a .reana/config.yaml with dev and prod profiles and run reana‑client via Docker using REANA_PROFILE."
summary: "Create a reusable .reana/config.yaml with profiles and run commands via Docker using REANA_PROFILE."
---

## Goal
Provide a reproducible way to work with both a development and a production REANA server from the same `reana-client` Docker image.

## Prerequisites
* Docker installed and the current user in the `docker` group.
* Access tokens for both REANA instances.

## Steps
1. **Create the config directory** (if it does not exist):
   ```bash
   mkdir -p ~/.reana
   ```
2. **Write a `config.yaml` with two profiles** – `dev` and `prod`.  Replace the placeholders with your real tokens later:
   ```yaml
   dev:
     server_url: https://reanadev.kube.aip.de
     access_token: <DEV_TOKEN>

   prod:
     server_url: https://reana-p4n.aip.de
     access_token: <PROD_TOKEN>
   ```
   Save it as `~/.reana/config.yaml`.
3. **Select a profile when running a command**.  Mount the config file read‑only into the container and set `REANA_PROFILE` to the desired profile:
   ```bash
   # Dev profile example
   docker run --rm \
     -v "$HOME/.reana/config.yaml:/root/.reana/config.yaml:ro" \
     -e REANA_PROFILE=dev \
     reanahub/reana-client:0.95.0-alpha.3 <reana-client‑command>

   # Prod profile example
   docker run --rm \
     -v "$HOME/.reana/config.yaml:/root/.reana/config.yaml:ro" \
     -e REANA_PROFILE=prod \
     reanahub/reana-client:0.95.0-alpha.3 <reana-client‑command>
   ```
   Replace `<reana-client‑command>` with any `reana-client` sub‑command, e.g. `ping`, `list`, `run …`.
4. **Optional: use a persistent container for an interactive session**
   ```bash
   docker run -d --name reana_shell \
     -v "$HOME/.reana/config.yaml:/root/.reana/config.yaml:ro" \
     -e REANA_PROFILE=dev \
     reanahub/reana-client:0.95.0-alpha.3 sleep 3600

   docker exec -it reana_shell /bin/bash   # now you have a shell with the config loaded
   ```
   Switch profile inside the shell by changing `REANA_PROFILE` or by editing the config file.

## Pitfalls & Tips
* **Never expose your tokens**: keep the file permission `600` (owner‑read/write only).
* **Do not rely on a single keyword** for destructive actions – the system will ask for multiple confirmations (see memory entry).
* If you need to add more back‑ends, just add another top‑level key (e.g., `staging:`) to the same `config.yaml` and set `REANA_PROFILE=staging`.

## Verification
Run a simple ping against each profile to ensure the tokens are correct:
```bash
# Dev
docker run --rm -v "$HOME/.reana/config.yaml:/root/.reana/config.yaml:ro" -e REANA_PROFILE=dev reanahub/reana-client:0.95.0-alpha.3 ping
# Prod
docker run --rm -v "$HOME/.reana/config.yaml:/root/.reana/config.yaml:ro" -e REANA_PROFILE=prod reanahub/reana-client:0.95.0-alpha.3 ping
```
Both should return `OK` if the credentials are valid.

---
**Category**: data-science
**Author**: Hermes (auto‑generated)
**Version**: 1.0
