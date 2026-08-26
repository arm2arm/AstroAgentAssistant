---
name: terminal-bench
description: Benchmarking LLM agents in terminal environments using Harbor and Terminal-Bench datasets (2.0, 2.1, Pro). Covers installation, custom endpoint configuration, oracle smoke tests, dataset selection, ARM64 pitfalls, and result interpretation.
version: 1.0.0
author: Hermes Agent
metadata:
  hermes:
    tags: [benchmarking, terminal, evaluation, harbor, agent-evals]
---

# Terminal-Bench Benchmarking

## Overview

Terminal-Bench evaluates AI agents on realistic, multi-step terminal tasks in sandboxed Docker containers. The official harness is **Harbor** (by the same Stanford/Laude team).

**Datasets:**
- **terminal-bench 1.0** — 80 tasks (original)
- **terminal-bench 2.0** — 89 tasks across software engineering, ML, security, data science, sysadmin
- **terminal-bench 2.1** — Improved 2.0 (Harbor v2.1+)
- **terminal-bench-pro** (Alibaba) — separate registry, different format
- **terminal-bench-science** — in development, scientific computing focus

**Leaderboard:** https://www.tbench.ai/
**Paper:** Merrill et al. (ICLR 2026)

## Prerequisites

```bash
# Install Harbor (NOT 'pip install harbor' — that's a different package)
uv tool install harbor

# Verify
harbor --help
```

**Platform check before running:**

```bash
uname -m
# x86_64 = fine
# aarch64 / arm64 = PROBLEM — see Pitfalls below
```

## CLI Versions (Important)

There are **two** CLI tools — they use DIFFERENT datasets and are NOT interchangeable:

| CLI | Package | Use for | Status |
|---|---|---|---|
| `harbor run` | `uv tool install harbor` | TB 2.1, 2.0 (Harbor) | **CURRENT / USE THIS** |
| `tb run` | `uv tool install terminal-bench` (v0.2.x) | TB 1.0, 2.0 (legacy) | **SUPSEDED** |

**Always prefer `harbor run`** for v2.1. The `tb` CLI:
- Only supports older dataset formats (no v2.1)
- Its remote registry returns **empty responses** (dataset downloads fail silently)
- See "Registry Failure Workaround" below

### Registry Failure Workaround (tb CLI)

If the `tb` CLI's remote registry returns empty (common), download the dataset directly from HuggingFace:

```bash
# Clone from HF (each task is a top-level dir, not wrapped in 'tasks/')
git clone --depth 1 https://huggingface.co/datasets/camel-ai/terminal-bench-core_migrated.git

# Create expected structure
mkdir -p /tmp/tb-dataset/tasks
cp -r terminal-bench-core_migrated/* /tmp/tb-dataset/tasks/

# Run locally
tb run -p /tmp/tb-dataset/tasks -a oracle -t "hello-world"
```

## Quick Start

### 1. Oracle smoke test

```bash
harbor run \
  -d terminal-bench/terminal-bench-2 \
  -a oracle \
  -l 1 \
  -y \
  -o /tmp/tb-smoke
```

If this fails, the environment is misconfigured before touching your model.

### 2. Run against an agent

```bash
harbor run \
  -d terminal-bench/terminal-bench-2 \
  -a terminus-2 \
  -m "openai/gpt-5" \
  -k 3 \
  -n 4
```

### 3. Run a specific task only

```bash
harbor run \
  -d terminal-bench/terminal-bench-2 \
  -a terminus-2 \
  -m "openai/gpt-5" \
  --include-task-name "hello-world"
```

## Custom Endpoint Configuration

For OpenAI-compatible endpoints (LiteLLM proxy, vLLM, Ollama, etc.), use `--agent-kwarg`:

```bash
harbor run \
  -d terminal-bench/terminal-bench-2 \
  -a terminus-2 \
  -m "your-model-name" \
  --agent-kwarg api_base=http://localhost:4000/v1 \
  --agent-kwarg max_turns=100 \
  -k 3
```

### Register model info (required for unrecognized models)

Harbor uses LiteLLM internally. Custom/unrecognized models need `model_info` for metrics tracking and context summarization:

```bash
--agent-kwarg 'model_info={"max_input_tokens": 128000, "max_output_tokens": 4096}'
```

Or via config:

```python
from harbor.models.trial.config import AgentConfig
from harbor.models.agent_name import AgentName

agent_config = AgentConfig(
    name=AgentName.TERMINUS_2,
    model_name="your-model",
    kwargs={
        "api_base": "http://localhost:4000/v1",
        "temperature": 0.7,
        "max_turns": 100,
        "model_info": {
            "max_input_tokens": 128000,
            "max_output_tokens": 4096,
            "input_cost_per_token": 0.0,
            "output_cost_per_token": 0.0,
        },
    }
)
```

Then: `harbor run --agent-import-path "my_config:agent_config"`

### Common agent kwargs

| kwarg | Purpose | Default |
|---|---|---|
| `api_base` | Custom OpenAI-compatible URL | (none) |
| `temperature` | Sampling temp | 0.7 |
| `max_turns` | Max conversation turns per task | 1,000,000 |
| `parser_name` | `"json"` or `"xml"` | `"json"` |
| `enable_summarize` | Context summarization during long tasks | `True` |
| `proactive_summarization_threshold` | Free-token threshold for summarization | 8000 |
| `reasoning_effort` | `"none"|"low"|"medium"|"high"|"xhigh"|"max"` | (none) |
| `max_thinking_tokens` | Anthropic extended thinking mode | (none) |
| `model_info` | Token limits + cost for metrics | (none, required for custom models) |
| `collect_rollout_details` | RL training / SFT trace generation | `False` |

## Supported Agents (built-in)

`claude-code`, `terminus-2`, `terminus-1`, `openhands`, `codex`, `swe-agent`, `mini-swe-agent`, `oracle`, `hermes`, `opencode`, `aider`, `cline-cli`, `cursor-cli`, `copilot-cli`, `devin`, `dspy-rlm`, `goose`, `kimi-cli`, `langgraph`, `nemo-agent`, `pi`, `qwen-coder`, `rovodev-cli`, `trae-agent`, `vibe`, and ACP registry shorthands.

Custom agent: `--agent-import-path "module.path:AgentClass"`

## Platform Pitfalls

### ARM64 / Apple Silicon (CRITICAL)

Terminal-Bench Docker images are **x86_64-only**. On ARM64 hosts (Apple Silicon, AWS Graviton, NVIDIA Grace, ARM servers):

**The real problem is QEMU user-mode SEGFAULTS on complex programs.**
- ✅ Containers START under QEMU emulation (`uname -m` returns `x86_64`)
- ✅ Simple binaries work (busybox, echo, uname)
- ❌ Python, uv, pytest, any C-extension → SEGFAULT ("signal 11")
- ❌ Oracle agent gets 0.0 score (execution too fast, no output)

**Fix options:**
1. **Run on an x86_64 host** (best — Newton: 141.33.4.144)
2. **QEMU-in-Docker (ARM64 workaround)** — spawn ARM64 container with `--privileged`, mount Docker socket, entrypoint registers QEMU in binfmt_misc. Container then creates x86_64 containers via QEMU. See `references/arm64-docker-emulation.md`.
3. **Root + QEMU system registration** — `apt install qemu-user-static`, register via `docker run --privileged multiarch/qemu-user-static --reset -p yes`
4. **Cloud sandbox** — `--env daytona`, `--env modal`, `--env e2b`
2. **Root + QEMU system registration** — `apt install qemu-user-static`, register via `docker run --privileged multiarch/qemu-user-static --reset -p yes`
3. **Cloud sandbox** — `--env daytona`, `--env modal`, `--env e2b`

### Docker not running

```bash
docker ps  # check
# Start Docker daemon if needed
systemctl start docker
```

### Network issues

Harbor downloads Docker images and task definitions from the registry. Ensure outbound HTTP access. Use `--debug` to trace failures.

## Result Inspection

```bash
harbor view /path/to/results
# or manually:
cat /path/to/results/*/result.json | python3 -m json.tool
```

Result JSON structure:
```json
{
  "id": "...",
  "stats": {
    "n_completed_trials": 5,
    "n_errored_trials": 2,
    "evals": {
      "terminus-2__terminal-bench/terminal-bench-2": {
        "n_trials": 5,
        "n_errors": 2,
        "metrics": [{"mean": 0.6}],
        "exception_stats": {"RuntimeError": [...]}
      }
    }
  }
}
```

## Benchmark Categories (Terminal-Bench 2.0)

| Category | Examples |
|---|---|
| Software engineering | Bug fixing, feature implementation |
| System administration | Git server setup, webserver config |
| Security | Certificate generation, hash cracking |
| Data science | Data resharding, model training |
| Scientific workflows | MIPS interpreter, fasttext training |
| Model training | fasttext classifier, kernel compilation |

Task difficulty levels: easy, medium, hard.

## Debugging

```bash
# Enable verbose logging
harbor run ... --debug

# Check Harbor version
harbor --version  # should be v0.20+ (not the old pip 'harbor')

# List available datasets
harbor datasets list

# Print resolved config (helps debug agent kwargs)
harbor run ... --print-config
```

Common error patterns:
- **RuntimeError + "platform does not match"** → ARM64 host, see above
- **Container exited (255)** → container build/start failed, check logs with `--debug`
- **Network timeout** → registry unreachable or slow download
- **Missing API key** → set env vars (ANTHROPIC_API_KEY, OPENAI_API_KEY, etc.)

## Related Benchmarks

| Benchmark | What it measures |
|---|---|
| Terminal-Bench | End-to-end terminal task completion in Docker containers |
| AgentBench (DBBench) | SQL/database query generation |
| SWE-Bench | Real-world GitHub patch correctness |
| τ-Bench | Multi-turn tool-use + policy adherence |
| Cline Bench | Local editor-embedded workflows |
| OSWorld | GUI/desktop automation |

## References

- Harbor docs: https://harborframework.com/docs
- Terminal-Bench paper: https://arxiv.org/abs/2601.11868
- Leaderboard: https://www.tbench.ai/
- Alibaba Terminal-Bench Pro: https://github.com/alibaba/terminal-bench-pro