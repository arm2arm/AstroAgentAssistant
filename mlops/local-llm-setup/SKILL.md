---
name: local-llm-setup
description: "Diagnose local LLMs, bridge formats for Claude Code, Codex."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, Local-LLM, Setup, Troubleshooting, Proxy]
---

# Local LLM Setup for Coding Agents

When a user wants a coding agent (Claude Code, Codex, OpenCode) running on a local/self-hosted LLM.

## Quick Diagnosis Flow

### Step 1: Check models endpoint
```bash
curl -s https://<host>/v1/models \
  -H "Authorization: Bearer <key>"
```
Expected: `{"data":[{"id":"<model-name>"}],"object":"list"}`

### Step 2: Test chat completions (CRITICAL)
```bash
curl -s -X POST https://<host>/v1/chat/completions \
  -H "Authorization: Bearer <key>" \
  -H "Content-Type: application/json" \
  -d '{"model":"<model>","messages":[{"role":"user","content":"hi"}],"max_tokens":20}'
```

| Result | Meaning |
|--------|---------|
| 200 OK | OpenAI-compatible, coding agent may work |
| 405 Method Not Allowed | Models endpoint works but chat completions not served — agent WILL fail |
| 404 | Wrong path, service down, or incomplete API |

**A models endpoint returning 200 does NOT mean the service is ready for Claude Code.** Always test `/v1/chat/completions`.

### Step 3: Bridge if needed

#### Pattern A: OpenAI format → Anthropic format (Claude Code)
If the endpoint speaks OpenAI (`/v1/chat/completions`) but Claude Code needs Anthropic format:
```bash
pip install litellm
litellm --model openai/<provider>/<model> --host <host> --port 4000
```
Then:
```bash
ANTHROPIC_API_KEY=*** \
ANTHROPIC_BASE_URL=http://127.0.0.1:4000/v1/messages \
claude -p "task" --max-turns 1
```

#### Pattern B: Local endpoint → any agent
Point the agent directly at the local endpoint using environment variables:
- **Claude Code:** `ANTHROPIC_API_KEY=*** ANTHROPIC_BASE_URL=<host>/v1`
- **Codex:** `OPENAI_API_KEY=*** OPENAI_BASE_URL=<host>/v1`
- **OpenCode:** `--model <provider>/<model>` with appropriate auth

## Pitfalls
- `ANTHROPIC_API_KEY` can be any string for local endpoints — it just needs to be present for auth validation
- Local models are slower; use `--max-turns 1` for smoke tests
- A service that only exposes `/v1/models` but not `/v1/chat/completions` is misconfigured — Claude Code cannot use it. Fix the upstream or add a proxy.
- For Hermes gateway/service contexts (e.g., Telegram sessions), sandboxing may fail with local endpoints — use `--sandbox danger-full-access` for Codex or `--bare` for Claude Code

## Ollama: Pull + Register in Hermes Config

### Pull a model
```bash
ollama pull <model-name>
ollama list | grep <model-name>  # verify
```

### Add to Hermes config (curator-managed config via Python)
```python
import yaml
with open('/home/hermes/.hermes/config.yaml', 'r') as f:
    config = yaml.safe_load(f)
# Add model to provider's model list (don't overwrite)
models = config['providers']['ollama'].setdefault('models', [])
if '<model-name>' not in models:
    models.append('<model-name>')
with open('/home/hermes/.hermes/config.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
```

### Switch current model
```bash
hermes config set model.provider ollama
hermes config set model.default <model-name>
```

### Benchmark Ollama local model (TPS + TTFT)
```python
import requests, time, json

payload = {
    "model": "<model-name>",
    "prompt": "List 50 items quickly.",
    "stream": True,
    "options": {"temperature": 0.7, "num_predict": 80}
}

resp = requests.post("http://localhost:11434/api/generate", json=payload, stream=True, timeout=300)
tokens_count = 0
start = time.time()
ttft = None

for line in resp.iter_lines():
    if line:
        chunk = json.loads(line)
        if "response" in chunk:
            tokens_count += 1
            if ttft is None:
                ttft = time.time() - start

elapsed = time.time() - start
tps = tokens_count / elapsed
print(f"TTFT: {ttft:.1f}s | Tokens: {tokens_count} | Time: {elapsed:.1f}s | TPS: {tps:.1f}")
```

**Expected TPS:** ~10-15 on CPU for 27B models (no GPU). 2-4x faster per token on GPU.

### Pitfalls
- After removing a model from the provider's model list, check `model.default` — it may still point to the removed model. Switch it back to a valid one.
- `ollama pull` can take a long time for large models (17GB+). Set generous timeouts.
- The Ollama `/v1/completions` endpoint may timeout for generation — use `/api/generate` with `stream: True` for reliable measurement.
- Model size matters: 27B on CPU ≈ 11-15 TPS, 70B+ on CPU may be too slow for interactive use.
- **Error 412 ("requires a newer version of Ollama that may be in pre-release")** can mean two things:
  - **Actually needs a dev build** — check `ollama --version` and GitHub releases. Stable lags behind.
  - **Engine-specific quant format not supported on your platform** — e.g., `dflash` quants in Ollama 0.32.7 work only on the MLX engine (Apple Silicon). CUDA/ROCm/Linux ARM64 returns 412 even on latest stable. Check release notes for "coming days" disclaimers before installing pre-release builds. Always check available tags at `https://ollama.com/library/<model>/tags` — non-MLX tags (e.g., `q4_K_M`, `q8_0`, `bf16`) usually work cross-platform immediately.

## Related
- `claude-code` skill for Claude Code orchestration patterns
- `codex` skill for Codex workflow patterns
