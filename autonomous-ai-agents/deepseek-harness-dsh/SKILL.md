---
name: deepseek-harness-dsh
description: "Use when running coding tasks via dsh (DeepSeek Harness)."
version: 1.0.0
author: Arman Khalatyan / Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [dsh, deepseek-harness, coding-agent, cli]
    related_skills: [opencode-workflow, claude-code, codex]
---

# DeepSeek Harness (`dsh`) as a Coder

DeepSeek Harness (`dsh`) is DeepSeek AI's open-source agent harness ("everything is a plugin", Cordis runtime). Repo: https://github.com/deepseek-ai/deepseek-harness. **Developer preview — expect breaking changes; re-verify on upgrade.**

Installed on this host: `dsh` in `~/.local/bin` (npm, `~/.local` global prefix; plain `npm i -g` without prefix fails with EACCES; `pnpm add -g` fails with NO_GLOBAL_BIN_DIR). Version 0.1.1-rc.2.

## Install

```sh
npm config set prefix ~/.local   # once, so npm -g writes to ~/.local
npm i -g @deepseek-ai/dsh
dsh --version
```

Requires Node ^22.19 || >=24.

## Architecture (what matters)

- Entry modes: `dsh web` (Web UI, port 3080), `dsh --profile headless "task"` (one fresh persisted session, prints final answer, exits), `dsh --profile <name>` (other profiles).
- Profiles live in `~/.dsh/profiles/<name>/`: `package.json` (`dsh.profile.bundles` list), `cordis.yml` (root, read-only), **`cordis.patch.yml` (the user's editable patch layer)**.
- Provider/model defaults come from plugin ids: `llm-pi-ai` (provider routes) and `agent-default-model` (`provider` + `model`). Default headless profile is DeepSeek-locked: `deepseek-official` / `deepseek-v4-flash`.
- Settings YAML is `$DSH_HOME/settings.yaml` (default `~/.dsh/settings.yaml`); keys via `$DSH_HOME/.credentials.yaml` or **`apiKeyEnv: <ENV_VAR_NAME>`** in the provider route.
- Inspect composed config: `dsh --profile headless --dump-config`.
- Web UI provider config: Settings → Models → "Add a custom provider" (Provider ID, base URL, protocol, credential, models).

## Custom OpenAI-compatible provider (local vLLM recipe — VERIFIED WORKING)

Write `~/.dsh/profiles/headless/cordis.patch.yml`:

```yaml
- id: llm-pi-ai
  config:
    providers:
      myvllm:
        name: My local vLLM
        api: openai-completions
        baseURL: http://<your-vllm-host>:8000/v1
        apiKeyEnv: MY_VLLM_KEY
        models:
          - id: my-model
- id: agent-default-model
  config:
    provider: myvllm
    model: my-model
```

- `apiKeyEnv` takes the NAME of an env var, never a literal key. For no-auth endpoints: `export MY_VLLM_KEY=*** (in ~/.bashrc and in the launching shell).
- Using `apiKey: empty` (literal) instead of `apiKeyEnv` fails: `PI_AI_ERROR: No API key for provider`.
- Vision models on custom providers need `input: [text, image]` on the model entry.

## Usage

One-shot coding task in a repo directory:

```sh
dsh --profile headless "Refactor auth module and run the tests"
```

- The invoking cwd is the workspace root; sandbox defaults to `workspace-write` with `approval: ask`. For headless runs that must act unattended, set `DSH_PERMISSION_MODE=danger-full-access` (approval becomes `never`) — use deliberately, per workspace.
- Bash tool default timeout 60s; long jobs need the task phrased/looped accordingly.
- Web UI: `dsh web` → http://127.0.0.1:3080.
- **Context-window death on long sessions (hit 2026-08-25):** against the local 262K-token vLLM model, a single headless session running >~1.5h with many tool outputs died with `CONTEXT_WINDOW_EXCEEDED` (400 BadRequest, input 229K+output 32K > 262144) — usually AFTER most file edits were already written to disk, at the final test-iteration/reporting phase. Mitigations: keep each stage prompt tightly scoped, split big stages in two, and after ANY non-zero exit, diff the working tree to salvage landed work instead of re-running the whole stage; finish the tail yourself.
- **Orchestrated multi-stage work (verified pattern):** run each stage as a FRESH `dsh --profile headless` background terminal process (notify_on_complete), one bounded prompt per stage, with ground rules in the prompt: no git commit/push (orchestrator commits), don't touch pre-existing dirty files, tests must stay green (give the exact test command), report changed files + pytest line in the final message. On the local ~14–18 tok/s vLLM a full-repo audit took ~30 min; a bounded edit stage runs 20–40 min. Session transcripts persist at `~/.dsh/sessions/<--cwd-->/<session-id>/session.jsonl.zstd` (zstd-compressed JSONL — zstd is NOT installed on this host by default; read via `python3 -c "import zstandard"` only if available, otherwise tail the process log).

## Pitfalls

- First headless run auto-initializes the profile from shipped templates (creates `~/.dsh/profiles/headless/`).
- Without a provider patch it fails: `MISSING_CREDENTIAL: llm-deepseek: no API key for provider route "deepseek-official"` — export `DEEPSEEK_API_KEY` or patch a custom provider.
- npm global install needs `~/.local` prefix on this host; `pnpm add -g` unusable (no global bin dir).
- Security scanner flags: raw-IP baseURL and dotfile writes (expected for this config; user-approved).
- Telemetry plugin exists (`session-telemetry-otel`); default mode DISABLED; can be disabled in the patch if desired.

## Verification (smoke test)

```sh
dsh --profile headless "Respond with exactly: DSH_SMOKE_OK"
# expect output: DSH_SMOKE_OK
```

Verified 2026-08-25 against a local vLLM endpoint (27B open-weight model): returned `DSH_SMOKE_OK`.
