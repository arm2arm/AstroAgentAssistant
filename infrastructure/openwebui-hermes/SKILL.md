---
name: openwebui-hermes
description: Connect Hermes Agent to Open WebUI using the OpenAI-compatible API server and document image/file-delivery caveats.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [openwebui, hermes, api-server, infrastructure]
    category: infrastructure
    related_skills: [hermes-api-server]
---

# Open WebUI + Hermes

## When to Use
Use this skill when exposing Hermes behind Open WebUI.

## Procedure
1. Enable the Hermes API server.
2. Start the Hermes gateway/API endpoint.
3. Add an OpenAI-compatible connection in Open WebUI using the `/v1` suffix.
4. Verify `/health` and `/v1/models` before testing the UI.

## Pitfalls
- Missing `/v1` is a common configuration error.
- `MEDIA:/...` paths may work in Telegram but not render as images in Open WebUI.

## Verification
- Open WebUI sees the Hermes model.
- Simple chat requests succeed through the UI.
