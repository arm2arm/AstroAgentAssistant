---
name: agentic-benchmarks
title: Agentic LLM Evaluation Benchmarks
description: >-
  Overview and comparison of benchmarks that evaluate LLMs as autonomous agents:
  GAIA, WebArena, OSWorld, ToolBench, LiveAgentBench, BrowseComp, WebVoyager,
  Tau-Bench. Includes guidance on running AgentBench DBBench SQL generation and
  selecting the right benchmark.
author: Hermes Agent
date: 2026-07-20
tags: [agentic, evaluation, benchmarks, tool-use, multi-step, GAIA, WebArena, OSWorld, ToolBench, DBBench, SQL]
---

# Agentic LLM Evaluation Benchmarks

Benchmarks that test LLMs as **autonomous agents** — multi-step reasoning, tool use, planning, and real-world task completion — as opposed to single-turn QA benchmarks like MMLU or GSM8K.

## Benchmarks

| Benchmark | What it measures | Difficulty | API-runnable |
|-----------|-----------------|------------|--------------|
| **GAIA** | Real-world assistant tasks (browsing, file ops, data analysis) | Hard | ✅ Yes |
| **WebArena** | Web tasks — forms, bookings, shopping, account management | Hard | ❌ Needs browser env |
| **OSWorld** | Desktop OS tasks — install, config, file management | Hard | ❌ Needs OS env |
| **ToolBench** | Tool calling & chaining — 16K+ instruction-tool pairs | Medium | ✅ Partially |
| **LiveAgentBench** | Continuously updated real-world tasks | Hard | ✅ Yes |
| **BrowseComp** | DeepMind web search — finding obscure info via multi-hop | Medium | ✅ Partially |
| **WebVoyager** | Web navigation with memory & planning | Hard | ❌ Needs browser env |
| **Tau-Bench** | Policy compliance (medical, legal domains) | Hard | ⚠️ Limited |
| **DBBench** | SQL generation (single-turn, via AgentBench controller) | Medium | ✅ Yes |

## Selection Guide

### If you want something you can run against an API endpoint:
1. **GAIA** — best fit. Designed for programmatic evaluation, pass/fail scoring, widely cited. Leaderboard at huggingface.co/GAIA-benchmark.
2. **ToolBench** — good complement to AgentBench's task-completion focus. API-compatible evaluation available.
3. **DBBench** — SQL generation benchmark. Requires running AgentBench controller with Docker workers.

### If you want full-environment benchmarks (needs Docker/simulation):
- **WebArena** — most realistic web interaction benchmark
- **OSWorld** — Linux/macOS desktop automation
- **WebVoyager** — visual + textual web interaction

### Comparison with AgentBench:
- **AgentBench FC** (already in your toolkit) — function-calling style, 8 environments including SQL, OS interaction, knowledge graphs
- **GAIA** — more general-purpose, real-world tasks, higher ceiling (humans ~92%, top models ~50-60%)
- **LiveAgentBench** — continuously updated, no stale test sets
- **DBBench** — SQL generation only, single-turn, fast evaluation (300 samples in ~25-75 min depending on endpoint)

## Evaluation Patterns

### GAIA-style evaluation

See `scripts/gaia_bench.py` for a complete runnable template. Key patterns below.

#### Reasoning-field aware parsing
Some endpoints (notably `aip-best` via 141.33.165.84:8000) store the model output in a `reasoning` field instead of `content`. **Always check both fields:**
```python
msg = data["choices"][0].get("message", {})
content = msg.get("content", "")
reasoning = msg.get("reasoning", "")
```

#### Answer extraction from reasoning traces
Models output step-by-step reasoning before the final answer. Extract with this priority order:
1. Explicit markers: `Answer: ...`, `The answer is ...`, `**Answer:** ...`
2. Bracketed text in last 500 chars: `**...**`
3. Conclusion phrases: `Therefore ...`, `Thus ...`, `In conclusion ...`
4. Last substantial paragraph as fallback

Use `max_tokens >= 8192` — the reasoning field consumes most of the budget, and truncation produces empty content.

#### Evaluation criteria (multi-tier matching)
GAIA expected answers are single strings; model output is free-form. Match in this order:
1. **Exact match** (case-insensitive)
2. **Substring match** (model answer contains expected or vice versa)
3. **Numeric match** — extract all numbers via regex, compare pairwise with float equality
4. **Year match** — extract 4-digit years, compare first match

Answers starting with `ERROR:`, `[reasoning ...]` (no clear answer marker found), or `Unable to` are failures.

#### Critical pitfalls
- **Async hangs**: The `asyncio` version of the GAIA runner can hang on the first sample despite individual requests working. Use a synchronous loop instead.
- **No tool use baseline**: When evaluating non-agentic endpoints (no web search, file access, code execution), expect low scores on samples requiring external data (spreadsheets, GitHub APIs, real-time info). This is a known baseline limitation, not a model bug.
- **Progress checkpointing**: Each sample takes 20–60s. Save partial results after every 5 samples so a crashed run can resume rather than restarting.
- **Sampling**: Validation split has ~165 samples. For a statistically meaningful run, use 50+ samples randomly selected (seed 42 for reproducibility).
- **Level distribution**: Sample 1 (19/100), Level 2 (63/100), Level 3 (18/100) in 2023_all validation. If sampling by level, weight toward Level 2 (majority).
- **Level types are strings, NOT integers**: GAIA dataset `Level` field is a string (`"1"`, `"2"`, `"3"`). Python comparisons like `if s["Level"] == 1` silently return `False`, selecting 0 samples. This then cascades to NaN in numpy/matplotlib plots. **Always use string comparisons** for level filtering: `if s["Level"] == "1"`.
- **Runtime guard — fail fast on 0 samples**: Before starting the benchmark loop, validate that sample selection produced items. If `len(selected) == 0`, print a clear error about level type mismatch and abort. This prevents wasting hours on a silent 0-sample run.

#### Typical baseline scores (aip-best, reasoning parse, 8192 tokens)
- 10-sample run: 4/10 (40%) — Level 1: 2/2 (100%), Level 2: 2/8 (25%)
- Simple knowledge/reasoning questions: good performance
- Questions requiring real-time data or file access: fail (no tool use)

### Pass/Fail criteria
Most agentic benchmarks use **exact match** or **semantic similarity** on the final output. Some support step-level scoring (e.g., did the agent successfully open the file before reading it?).

## Running Agentic Benchmarks

### Minimal setup for API-evaluable benchmarks:
```bash
pip install gaia-benchmark    # or whatever framework the benchmark provides
# or use lm-evaluation-harness with custom tasks
```

### Requirements:
- API endpoint (OpenAI-compatible)
- Network access (for web-based tasks)
- Disk space for temporary files (GAIA downloads real files)

## DBBench (SQL Generation)

Single-turn SQL generation benchmark using AgentBench's DBBench-std task. Requires a running AgentBench controller at `http://localhost:5020` with 10 DBBench worker Docker containers.

### Setup
```bash
# Start workers
for i in $(seq 1 10); do
    docker start agentbench-fc-dbbench-std-$i
done
# Verify: curl -s http://localhost:5020/api/list_workers | python3 -m json.tool
```

### Runner configuration
- **API**: OpenAI-compatible endpoint (e.g., `http://141.33.165.84:8000/v1/chat/completions`)
- **Timeout**: 600s per sample for slow endpoints (llama.cpp servers)
- **max_tokens**: 8192 (aip-best uses reasoning field — 4096 may truncate)
- **temperature**: 0.1
- **SQL detection**: Check code blocks (` ```sql `) and inline keywords (`SELECT `, `FROM `, `WHERE `, `JOIN `)

### Endpoint comparison results
See `references/dbbench-endpoint-comparison.md` and `references/dbbench-2026-07-25-findings.md` for full details.

| Endpoint | SQL Rate | Avg Time | Max Time | Errors |
|---|---|---|---|---|
| litellm.kube.aip.de | 93.3% (280/300) | 5.3s | — | 0 |
| 141.33.165.84:8000 (v1: 300s/4096tok) | 29.3% (88/300) | 14.5s | 179.4s | 3 |
| 141.33.165.84:8000 (v2: 600s/8192tok) | 27.7% (83/300) | 14.7s | 345.5s | 2 |
| aip-best (localhost Ollama) | 92.7% (278/300) | 4.9s | 32.1s | 0 |

**Key lesson: Increasing timeout/tokens does NOT fix low SQL rate.** v2 used 600s timeout + 8192 max_tokens (up from 300s + 4096). SQL rate went *down* from 29.3% to 27.7%. Root cause: not truncation or timeout — model/quantization/server config differences between endpoints.

**SQL rate varies by sample quartile** — Q2/Q3 samples (76-225) are significantly harder (~12-15% SQL rate vs ~48% in Q1). Same pattern across runs, suggesting DBBench dataset ordering effect.

### Plotting
8-panel dashboard + multi-model comparison via:
```bash
/home/hermes/shboost-hvplot-env/bin/python3 scripts/generate_dbbench_plot.py results/<model>.json
/home/hermes/shboost-hvplot-env/bin/python3 scripts/generate_dbbench_plot.py --compare json1,json2,... --labels "name1","name2" output.png
```

## Related Benchmarks
- **AgentBench** / **AgentBench FC** — your existing setup, multi-turn environments
- **DBBench** — SQL generation, single-turn via AgentBench controller (see above section)
- **SWE-bench** — coding benchmark (see `evaluating-llms-harness`)
- **lm-evaluation-harness** — academic benchmarks (MMLU, GSM8K, etc.)