---
name: reana-client-config
description: Configure REANA client authentication with multi-profile `.reana/config.yaml` or `~/.reana/config.yaml`, store tokens safely, and select dev/prod back-ends reproducibly.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [reana, authentication, config, access-token, workflow]
    category: workflows
    related_skills: [reana-aip, reana-serial-python, reana-shboost24]
---

# REANA Client Config

## When to Use
Use this skill when a task requires authenticated access to one or more REANA back-ends and the user needs a simple, repeatable way to provide `server_url` and `access_token` values safely.

## Procedure

### 1. Create the REANA config directory
Choose one of these layouts:

**Home-level config (recommended):**
```bash
mkdir -p ~/.reana
```

**Project-local config:**
```bash
mkdir -p .reana
```

### 2. Write `config.yaml` with named profiles
Use top-level profile names like `dev`, `prod`, or any nickname:

```yaml
dev:
  server_url: https://reanadev.example.org
  access_token: <DEV_ACCESS_TOKEN>

prod:
  server_url: https://reana.example.org
  access_token: <PROD_ACCESS_TOKEN>

nickname:
  server_url: https://another-reana.example.org
  access_token: <ACCESS_TOKEN>
```

Save it as either:
- `~/.reana/config.yaml`
- `.reana/config.yaml`

### 3. Protect the secrets
```bash
chmod 600 ~/.reana/config.yaml 2>/dev/null || true
chmod 600 .reana/config.yaml 2>/dev/null || true
```

### 4. Select a profile when running `reana-client`
If using a home-level config:
```bash
export REANA_PROFILE=dev
reana-client ping
```

If using a project-local config, point REANA to it explicitly or mount it for container usage.

### 5. Dockerized `reana-client` pattern
```bash
docker run --rm \
  -v "$HOME/.reana/config.yaml:/root/.reana/config.yaml:ro" \
  -e REANA_PROFILE=dev \
  ghcr.io/reana/reana-client:latest ping
```

Project-local variant:
```bash
docker run --rm \
  -v "$(pwd)/.reana/config.yaml:/root/.reana/config.yaml:ro" \
  -e REANA_PROFILE=dev \
  ghcr.io/reana/reana-client:latest ping
```

### 6. Use the selected profile in workflows
Examples:
```bash
REANA_PROFILE=dev reana-client list
REANA_PROFILE=prod reana-client run -w my-workflow
REANA_PROFILE=nickname reana-client status -w my-workflow
```

### 7. AIP-style usage notes
- Keep the config outside public git repositories when possible.
- Prefer one named profile per REANA environment.
- Pair this skill with `reana-aip` or `reana-serial-python` when writing or running workflows.

## Pitfalls
- Do not commit real `access_token` values to Git.
- Do not mix different servers under one unnamed profile.
- Do not leave permissions world-readable.
- Use `server_url`, not ad-hoc key names, to stay compatible with normal REANA client expectations.

## Verification
- `REANA_PROFILE=<name> reana-client ping` succeeds.
- `config.yaml` contains the intended profiles and valid keys.
- File permissions are restricted (`600`).
