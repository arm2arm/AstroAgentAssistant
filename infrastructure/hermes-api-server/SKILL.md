---
name: hermes-api-server
description: Enable and expose the Hermes OpenAI-compatible API server safely for frontends and integrations.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [hermes, api-server, infrastructure, deployment]
    category: infrastructure
    related_skills: [openwebui-hermes]
---

# Hermes API Server

## When to Use
Use this skill when enabling Hermes as an OpenAI-compatible backend for frontends or services.

## Procedure
1. Set `API_SERVER_ENABLED=true`.
2. Configure host, port, key, and optional model name.
3. Start Hermes gateway/API server.
4. Verify `/health` and `/v1/models`.

## Pitfalls
- Non-loopback binding without an API key is unsafe.
- Browser CORS settings are only needed for direct browser access, not server-to-server integration.

## Verification
- Health endpoint returns OK.
- The desired model appears on `/v1/models`.
