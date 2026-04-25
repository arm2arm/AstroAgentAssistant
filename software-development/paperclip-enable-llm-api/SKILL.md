---
title: Enable OpenAI-compatible API in Paperclip
name: paperclip-enable-llm-api
description: Configure the top-level LLM provider block in Paperclip so the instance recognizes the OpenAI backend in current Paperclip versions.
author: Hermi (hermes-agent)
---

## When to use
Use this skill whenever a Paperclip instance is running but `paperclipai doctor` reports **No LLM provider configured**, even though you previously added OpenAI settings. In current Paperclip versions, the usual cause is that `llm` was placed under `server` instead of at the top level of `config.json`.

## Preconditions
- Paperclip is installed and the wrapper script (`run-paperclip-bg.sh`) is available.
- You have filesystem access to `~/.paperclip/instances/<instance>/config.json`.
- The desired LLM provider is already installed (e.g., the local `oss-120b` model).

## Steps
1. **Stop the running server** (replace `<pid>` with the actual PID):
   ```bash
   kill $(lsof -t -i :3101)   # or kill <pid>
   ```
2. **Open the instance config** (use any editor you like):
   ```bash
   nano ~/.paperclip/instances/default/config.json
   ```
3. **Add/Update the `llm` block** if it is missing:
   ```json
   "llm": {
     "provider": "openai",
     "apiKey": "",
     "model": "oss-120b"
   },
   ```
4. **Ensure `llm` is a top-level key** (not nested under `server`):
   ```json
   "llm": {
     "provider": "openai",
     "apiKey": ""
   },
   "server": {
     "deploymentMode": "authenticated",
     "exposure": "public",
     "bind": "custom",
     "host": "0.0.0.0",
     "customBindHost": "0.0.0.0",
     "port": 3101,
     "allowedHostnames": [],
     "serveUi": true
   },
   ```
5. **Save the file** and exit the editor.
6. **Restart Paperclip** using the wrapper script (or the command you normally use):
   ```bash
   ~/run-paperclip-bg.sh
   ```
7. **Verify startup logs** by watching the log:
   ```bash
   tail -f ~/.paperclip/paperclip-daemon.log
   ```
   You should see lines similar to:
   ```
   ✓ LLM provider: openai configured but no API key set (optional)
   Server listening on 0.0.0.0:3101
   ```
8. **Verify health and config recognition**:
   ```bash
   npx paperclipai doctor
   curl -s http://<IP>:3101/api/health
   ```
   `doctor` should report the OpenAI provider as configured, and `/api/health` should return status JSON.

## Pitfalls & Gotchas
- In current Paperclip builds, `llm` must be a **top-level** config block. If you place it under `server`, `paperclipai doctor` reports **No LLM provider configured**.
- Do **not** rely on `source ~/.bashrc` from a non-interactive start script; many default `.bashrc` files return early. Export `OPENAI_API_BASE`, `OPENAI_API_KEY`, and `OPENAI_MODEL` directly in the background start script instead.
- If you set an `apiKey` value, remember to provide the same key to the backend or client using that backend.
- The firewall must allow inbound TCP 3101; otherwise external clients will see a timeout.

## Verification
- `npx paperclipai doctor` → reports `LLM provider: openai configured ...`
- `curl http://<IP>:3101/api/health` → `{"status":"ok",…}`
- `tr '\0' '\n' </proc/<paperclip-node-pid>/environ | grep OPENAI_` → shows the expected OpenAI-compatible backend environment variables when using the background start script.

---
*Skill created by Hermi on 2026‑04‑19.*