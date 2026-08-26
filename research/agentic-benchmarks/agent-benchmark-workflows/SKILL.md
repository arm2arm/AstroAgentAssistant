---
name: agent-benchmark-workflows
description: Class-level guide for running AI agent benchmarks — Terminal-Bench, SWE-Bench, DBBench, and related evaluation frameworks. Includes platform compatibility, container setup, and result interpretation.
version: 1.0.0
author: Hermes Agent
---

# Agent Benchmark Workflows

## When to use
- User asks to benchmark/evaluate an LLM agent (terminal use, coding, SQL generation)
- User wants to compare models on task completion rates
- Setting up reproducible benchmark runs

## Available Benchmarks

| Benchmark | What it tests | Platform | Docker needed? |
|---|---|---|---|
| **Terminal-Bench** (Harbor) | Multi-step CLI tasks in sandboxed containers | x86_64 only | Yes |
| **SWE-Bench** (Verified/Pro) | Real GitHub issue patching | Python-based | No |
| **DBBench** (AgentBench FC) | SQL query generation | Python-based | No |
| **τ-Bench** | Multi-turn tool-use + policy adherence | Varies | Check per variant |
| **OSWorld** | GUI automation | Varies | Sometimes |

## Terminal-Bench / Harbor Setup

### Installation
```bash
uv tool install harbor
```

### Basic run
```bash
harbor run \
  -d terminal-bench/terminal-bench-2 \
  -a terminus-2 \
  -m "openai/gpt-4" \
  -l 2 \
  -y \
  -o /tmp/tb-eval
```

### Custom API endpoint
```bash
harbor run \
  -d terminal-bench/terminal-bench-2 \
  -a terminus-2 \
  -m "your-model-name" \
  --agent-kwarg "api_base=http://localhost:4000/v1" \
  --agent-kwarg "model_info={'max_input_tokens': 128000, 'max_output_tokens': 4096}" \
  -l 5 \
  -y \
  -o /tmp/tb-eval
```

### Dataset options
- `terminal-bench/terminal-bench-2` — 89 tasks (standard)
- `terminal-bench/terminal-bench-2-1` — Improved version
- `terminal-bench-pro@1.0` — Alibaba's variant (also x86_64 only)

### Agent options
Built-in: `terminus-2`, `claude-code`, `openhands`, `codex`, `mini-swe-agent`, `oracle`

Custom agent: `--agent-import-path "module.path:AgentClass"`

## ARM64 Compatibility

### The reality (2026-07-28 confirmed)
TB 2.1 containers **DO run** on ARM64 via Docker's built-in QEMU. The container starts with `/usr/bin/qemu-x86_64 /usr/bin/sh` as PID 1. `docker exec <container> uname -m` returns `x86_64`.

**The real issue is NOT container startup** — it's agent interaction. The oracle agent may execute and get 0.0 reward because:
- Agent execution window may be very short (~0.3s) — agent may not attach properly
- Task complexity exceeds oracle's scope
- Environment setup completes but agent communication breaks

### Verification checklist
1. Smoke-test: `harbor run -d terminal-bench/terminal-bench-2-1 -a oracle -l 1 -o /tmp/tb-smoke`
2. If containers start (check `docker ps --filter name=env`), the platform path works
3. Check `docker exec <container> uname -m` → should return `x86_64`
4. If containers fail to start, platform is truly incompatible
5. If containers start but agent gets 0.0 reward, check `result.json` for exception_stats — empty exception_stats with 0.0 reward means agent ran but produced no output

## Interpreting Results

### Key metrics
- **Resolution rate**: % of tasks completed successfully (0-100%)
- **Mean score**: Aggregated across tasks
- **Exceptions**: Count of failures per error type
- **Cost/usd**: API token costs (if model_info provided)

### Result format
Results saved to `--output-dir/<timestamp>/result.json`. Key fields:
```json
{
  "stats": {
    "n_completed_trials": 5,
    "n_errored_trials": 1,
    "evals": {
      "terminus-2__terminal-bench-2": {
        "metrics": [{"mean": 0.62}],
        "exception_stats": {"RuntimeError": ["task-name"]}
      }
    }
  }
}
```

## Pitfalls

1. **ARM64 + Terminal-Bench** — Containers fail with platform mismatch. Always check `uname -m` first.
2. **Oracle smoke test** — Run it before committing to a full eval. Saves 20+ minutes.
3. **QEMU registration** — Requires `--privileged` + root. Without sudo, it's a chicken-and-egg problem.
4. **model_info required** — Custom models need `model_info` dict in kwargs for metrics tracking to work.
5. **Task timeout** — Long tasks (kernel compilation, etc.) may exceed default timeouts. Use `--timeout-multiplier`.