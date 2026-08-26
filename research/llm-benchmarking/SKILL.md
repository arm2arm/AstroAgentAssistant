---
name: llm-benchmarking
description: Systematic LLM benchmarking on AgentBench, DBBench, and other standardized evaluations
triggers:
  - benchmark model
  - agentbench
  - dbbench
  - compare models
  - evaluate llm
  - performance test
---

# LLM Benchmarking Workflows

## Overview
Systematic evaluation of LLMs on standardized benchmarks (AgentBench, DBBench, etc.) using local Ollama or API endpoints.

## Trigger Conditions
- User asks to benchmark a model on a task
- User wants to compare model performance
- User needs reproducible evaluation metrics
- User asks "how does model X perform on Y benchmark"

## AgentBench (THUDM) - Quick Reference

### Two Approaches

**1. Official Framework (Docker-based)**
```bash
cd /tmp/AgentBench
docker compose -f extra/docker-compose.yml up
python -m src.assigner --config configs/assignments/default.yaml
```
- ✅ Containerized environments (real OS/DB execution)
- ✅ Production reproducibility
- ⚠️ Heavy setup (~16GB RAM for WebShop)
- ⚠️ Complex configuration

**2. Direct API (Recommended for local testing)**
```bash
# Single-task benchmark
cd /tmp && ~/.hermes/hermes-agent/venv/bin/python agentbench_ollama_llama32.py

# Or inline script (see templates/)
```
- ✅ Fast setup, no Docker
- ✅ Works with any Ollama model
- ✅ Easy debugging
- ⚠️ No containerized environment execution

### Performance Baselines (as of 2026-07-15)

| Model | DBBench | KG | OS | LTP | Overall | Speed |
|-------|---------|----|----|----|---------|-------|
| **llama3.2:3b** | 96-100% | 100% | 100% | 100% | **98%** | 1.5-10s |
| **qwen3.6:latest** | 3% | - | - | - | **~3%** | 28s |
| **deepseek-r1:70b** | - | - | - | - | **N/A** | 27s |
| **aip-best (API)** | 20% | 0% | 3.8% | - | **12%** | 2.5s |

**Key Finding:** `llama3.2:3b` is optimal for local AgentBench workloads - 100x faster than 70B models with near-perfect accuracy on SQL/reasoning tasks.

> **⚠️ Endpoint variability:** The same model (aip-best) can show 93% SQL rate on `litellm.kube.aip.de` but only 29% on `141.33.165.84:8000`. Always verify with a 10-sample smoke test. See `references/benchmark-baselines.md` for full comparison and robust runner template with checkpointing.

### Benchmark Script Patterns

**SQL Extraction (DBBench):**
```python
def extract_sql(content):
    if not content: return None
    if "```sql" in content:
        return content.split("```sql")[1].split("```")[0].strip()
    elif "```" in content:
        return content.split("```")[1].split("```")[0].strip()
    return None
```

**Command Extraction (OS):**
```python
def extract_cmd(content):
    if not content: return None
    if "```bash" in content:
        return content.split("```bash")[1].split("```")[0].strip()
    elif "```" in content:
        return content.split("```")[1].split("```")[0].strip()
    return None
```

**Ollama API Call:**
```python
payload = {
    "model": "llama3.2:3b",
    "messages": [
        {"role": "system", "content": "Output ONLY SQL in ```sql code block."},
        {"role": "user", "content": user_prompt}
    ],
    "stream": False,
    "max_tokens": 512
}
resp = requests.post("http://localhost:11434/api/chat", json=payload, timeout=120)
```

## Pitfalls

### 1. Concurrency vs. Accuracy Tradeoff
- **5 workers:** 96% success (Ollama timeouts/empty responses)
- **Single-threaded:** 100% success
- **Recommendation:** Use 3-5 workers for speed, 1 for verification runs

### 2. Data Format Mismatches
- Lateral Thinking Excel: columns are `['story', 'answer', 'Story keys', 'Answer keys']`
- **NOT** `['question', 'clue']` as some docs suggest
- Always inspect data first: `pd.read_excel().columns.tolist()`

### 3. Model Output Format
- Small models (3B) need strict system prompts: "Output ONLY ```sql code block"
- Larger models (36B+) may ignore format instructions
- Always validate extraction logic before full benchmark run

### 4. Ollama Memory Constraints
- `llama3.2:3b`: 1.9GB (runs on 46GB available RAM)
- `qwen3.6:latest`: 22.3GB (causes VRAM errors with 5 workers)
- `deepseek-r1:70b`: 50.5GB (exceeds available 46GB)

### 5. API Endpoint Stability
- `aip-best` API (http://141.33.165.84:8000/v1): Use current endpoint above
- Always verify endpoint with a quick test before full benchmark
- Implement retry logic for overloaded servers

### 6. Endpoint Performance Variability (Discovered 2026-07-25)

The same model (aip-best/Qwen3.6-35B) can show dramatically different SQL rates across endpoints:

| Endpoint | SQL Rate | Avg Time | Verdict |
|----------|----------|----------|---------|
| litellm.kube.aip.de | 93.3% | 5.3s | ✅ Good |
| 141.33.165.84:8000 (Q5_K) | 29.3% | 14.5s | ❌ Degraded |

Root cause is likely different quantization (Q5_K vs Q4_K), temperature settings, or system prompt handling. **Always run a 10-sample smoke test before committing to a full 300-sample benchmark.** See `references/benchmark-baselines.md` for the full runner template with checkpointing.

### 7. Inspect AI 0.3.x API Differences (vs. older docs)
- `from inspect_ai.model import get_model` (NOT `from inspect_ai import get_model`)
- `generate()` is **async** — always `await model.generate(...)`, not sync
- Response uses `result.choices[0].message.content`, NOT `result.generations[0].text`
- OpenAI SDK must be >= 2.45.0 for Inspect Evals' OpenAI-compatible endpoints: `uv pip install --upgrade openai`
- Venv at `~/.hermes/hermes-agent/venv/` has python but **no pip** — use `uv pip install` instead

### 8. OpenAI-Compatible Endpoints with Structured Reasoning (e.g., aip-best)
- `message.content` is `null` — output is in `message.reasoning` (chain-of-thought, 10k+ chars)
- Answer is embedded in the reasoning trace, not standalone
- Always use `max_tokens >= 8192` — smaller budgets truncate reasoning before answer
- Prompt with explicit format: "At the end, state: 'Answer: [your answer]'"
- Parse patterns in priority: `Answer:` marker → `Therefore/Thus` → last brackets → last paragraph
- See `references/gaia-benchmark.md` for full parser and prompt templates
- Use `scripts/gaia_full_benchmark_runner.py` for a ready-to-run GAIA benchmark with built-in reasoning parser, progress saving, and auto-plots

### 8. GAIA Dataset Level Format (Critical Pitfall)
- Dataset levels are **strings** (`"1"`, `"2"`, `"3"`), NOT integers (`1`, `2`, `3`)
- Filtering with `dataset[i]["Level"] == 1` returns 0 samples — silent failure, no crash
- Always use string comparison: `dataset[i]["Level"] == "1"`
- Quick check: `sorted(set(s["Level"] for s in dataset))` returns `['1', '2', '3']`
- This caused a stratified 50-sample run to select 0 samples across multiple attempts — only discovered when the log showed "Levels: L1=0, L2=0, L3=0"

### 9. GAIA Timing Reality Check
- Reasoning-heavy models (aip-best) produce 20KB+ reasoning traces → 120s+/sample
- Full 165-sample validation set = ~5-6 hours — not practical for iterative work
- Use stratified subset (e.g., 50 samples: 15 L1, 30 L2, 5 L3) for ~1.5-2.5 hours
- Always verify a single sample timing before launching full run
- Baseline: text-only mode gives ~35s/sample on simpler queries, but complex GAIA questions push to 60-120s

### 10. Inspect CLI Flag Gotchas
- `--model-base-url` (NOT `--base-url`)
- No `--api-key` flag — set `OPENAI_API_KEY` env var or use `--env OPENAI_API_KEY=xxx`
- `inspect_evals/gaia` requires Docker sandboxes for tool execution (bash/python/web_browser)
- `uv run --extra gaia` only works inside a uv project; from `/tmp` use venv directly:
  `~/.hermes/hermes-agent/venv/bin/python -m inspect_evals.gaia ...`

### 11. GAIA via Inspect Evals Is Tool-Dependent
- `inspect eval inspect_evals/gaia_level1 --model openai/aip-best` runs with a built-in `react` agent
- The agent needs tool definitions (bash, python, web_browser) AND Docker sandboxes to work
- Without sandboxes the model generates tool-calling requests but nothing executes — all samples fail
- Text-only evaluation (no tools) is a valid fallback for measuring pure knowledge/reasoning ability
- Use `scripts/gaia_benchmark_runner.py` for text-only mode with reasoning parser

## Available Tasks (AgentBench)

| Task | Data File | Samples | Description |
|------|-----------|---------|-------------|
| **dbbench** | `dbbench/standard.jsonl` | 100 | SQL query generation |
| **knowledgegraph** | `knowledgegraph/std.json` | 50 | Multi-hop reasoning |
| **os_interaction** | `os_interaction/data/dev.json` | 26 | Linux command generation |
| **lateralthinkingpuzzle** | `lateralthinkingpuzzle/standard.xlsx` | 30 | Puzzle solving |
| **alfworld** | `alfworld/standard.json` | 20 | Household task planning |
| **avalon** | `avalon/` | 20 | Social deduction game |

## Quick Start Commands

```bash
# Run full benchmark suite (all 4 tasks)
cd /tmp && ~/.hermes/hermes-agent/venv/bin/python agentbench_ollama_llama32.py

# Run single task (DBBench)
cd /tmp && ~/.hermes/hermes-agent/venv/bin/python final_verify_dbbench.py

# Check Ollama status
curl -s http://localhost:11434/api/tags | python3 -m json.tool

# Test single prompt
curl -s -X POST "http://localhost:11434/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.2:3b", "messages": [{"role": "user", "content": "test"}], "stream": false}'
```

## Results Storage
- Default: `/tmp/agentbench_ollama_llama32/`
- Files: `dbbench.json`, `knowledgegraph.json`, `os_interaction.json`, `lateralthinking.json`

## Related Skills
- `astro-llm-research`: Domain-specific LLM workflows for astronomy
- `hermes-agent`: Ollama configuration and model management
- `ml-simulation-patterns`: Reproducible ML evaluation patterns
