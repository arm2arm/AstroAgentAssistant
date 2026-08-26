---
name: coding-agent-troubleshooting
description: "Use when Claude Code, Codex, or OpenCode fail to connect."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---

# Coding Agent Troubleshooting

Diagnose issues when connecting external coding agents to API endpoints. Covers format mismatches, vLLM quirks, smoke testing, and installation problems.

## Common Failure Modes

### 1. API Format Mismatch

Claude Code requires Anthropic's API format (`POST /v1/messages`). OpenAI-compatible endpoints (OpenAI API, vLLM, LiteLLM) use `POST /v1/chat/completions`. They are NOT interchangeable.

**Signs:** `claude` commands fail with connection/auth errors even though the endpoint works for other clients.

**Fix:** Run a proxy like LiteLLM that translates between formats:
```bash
pip install litellm
litellm --model openai/<model_name> --host <vllm-endpoint> --port 4000
# Point claude at: ANTHROPIC_BASE_URL=http://127.0.0.1:4000
```

### 2. vLLM Reasoning Field Misrouting (CRITICAL)

When vLLM serves a reasoning-capable model, output may go to the `reasoning` field instead of `content`:

```json
{
  "message": {
    "content": null,           // ← Claude Code reads this — EMPTY
    "reasoning": "Here's a thinking process..."  // ← Output goes here
  }
}
```

**Signs:** Agent connects, responds, but returns empty/no output. The `content` field is `null` while `reasoning` contains text.

**Diagnose:**
```bash
curl -s http://ENDPOINT/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"MODEL","messages":[{"role":"user","content":"Reply with: TEST_OK"}],"max_tokens":20}' \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(repr(d['choices'][0]['message'].get('content')))"
```

If output is `None`, the server misroutes output.

**Fix on vLLM:**
```bash
# Add to vLLM startup args
--disable-reasoning
```

### 3. Installation Permissions

Global npm install often fails in restricted environments.

**Fallback:**
```bash
npm install -g @anthropic-ai/claude-code --prefix ~/.local
# Binary at: ~/.local/bin/claude
```

### 4. Provider/Model Resolution

OpenCode requires providers to be configured. `opencode models` lists available providers:
```bash
opencode auth list          # check configured providers
opencode providers          # manage providers
```

For custom OpenAI-compatible endpoints:
```bash
# Usually via OPENAI_API_BASE / OPENAI_API_KEY env vars
# Or add provider: opencode providers add <name> --url <endpoint> --key <key>
```

## Smoke Test Checklist

Before deploying any coding agent, run these checks:

### Endpoint Health
```bash
# 1. Models endpoint responds
curl -s http://ENDPOINT/v1/models | python3 -c "import json,sys; d=json.load(sys.stdin); print('Models:', [m['id'] for m in d.get('data',[])])"

# 2. Chat completions works AND content field is populated
curl -s http://ENDPOINT/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"MODEL","messages":[{"role":"user","content":"Reply with: SMOKE_OK"}],"max_tokens":20}' \
  | python3 -c "
import json,sys
d=json.load(sys.stdin)
content = d['choices'][0]['message'].get('content','')
if content == 'SMOKE_OK':
    print('PASS: endpoint working correctly')
elif content == '' or content is None:
    print('FAIL: content field empty — check vLLM reasoning config')
else:
    print(f'GOT: {repr(content)}')
"
```

### Agent Readiness
```bash
claude --version        # Claude Code
opencode --version      # OpenCode
codex --version         # Codex (if installed)
```

## When to Use Which Agent

| Agent | Best For | Format Needed | Sandbox |
|-------|----------|---------------|---------|
| Claude Code | Complex refactoring, multi-turn, PR review | Anthropic (`/v1/messages`) | `--dangerously-skip-permissions` |
| Codex | One-shot fixes, clean git repos | OpenAI (`/v1/chat/completions`) | `--sandbox workspace-write` |
| OpenCode | Provider-agnostic, TUI sessions | OpenAI (`/v1/chat/completions`) | Manual |

## Pitfalls

1. **Never assume API compatibility** — Anthropic ≠ OpenAI format. Test with curl first.
2. **vLLM reasoning output is the #1 silent failure** — always smoke-test the `content` field.
3. **npm global install often fails** — have the `--prefix ~/.local` fallback ready.
4. **OpenCode requires provider config** — env vars may not be enough; use `opencode providers` to add.
5. **Claude Code needs Anthropic API format** — even if your endpoint speaks OpenAI format, Claude Code won't work without a proxy.