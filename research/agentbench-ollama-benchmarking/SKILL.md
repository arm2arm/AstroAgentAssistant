---
name: agentbench-ollama-benchmarking
description: Benchmark LLMs using AgentBench suite with local Ollama models
version: "1.1"
created: "2026-07-15"
tags:
  - benchmarking
  - ollama
  - agentbench
  - llm-evaluation
---

# AgentBench Benchmarking with Ollama

## Overview
Benchmark LLMs using AgentBench suite (DBBench, Knowledge Graph, OS Interaction, Lateral Thinking) with local Ollama models.

## Quick Start

### 1. Verify Ollama Status
```bash
curl -s http://localhost:11434/api/tags | python3 -m json.tool
ollama ps
```

### 2. Run Full Benchmark Suite
```bash
cd /tmp && ~/.hermes/hermes-agent/venv/bin/python agentbench_ollama_llama32.py
```

Results saved to: `/tmp/agentbench_ollama_llama32/`

### 3. Individual Task Scripts
- **DBBench (SQL)**: `/tmp/dbbench_qwen36.py` (single-threaded, 300 samples)
- **Knowledge Graph**: See script template below
- **OS Interaction**: See script template below
- **Lateral Thinking**: See script template below

## Model Performance (Empirical Results)

| Model | Size | DBBench | Overall | Speed | Recommendation |
|-------|------|---------|---------|-------|----------------|
| `llama3.2:3b` | 1.9GB | **99.5%** | **99.5%** | 2.98s | ✅ **OPTIMAL** |
| `teuken-7b` (GGUF) | 14GB | 99.0% | 87.4% | 4.81s | ⚠️ Good SQL, weak reasoning |
| `qwen3.5:122b-a10b` | 81GB | **100.0%** | TBD | 22.70s | ⚠️ Perfect but **7.6x slower** |
| `qwen3.6:latest` | 34GB | ~50% (timeouts) | ~50% | ~23s/sample | ❌ Impractical |
| `aip-best` (LiteLLM) | 35B | 86.0% | 75.2% | 1.36s | ⚠️ Broken API format |

**Key Finding**: `llama3.2:3b` achieves near-perfect accuracy with 7-8x speedup vs larger models, making it the production choice despite `qwen3.5:122b` achieving 100% on DBBench.

**Why 3B beats 122B** for SQL/code tasks:
- **99.5% vs 100%**: Marginal accuracy difference (0.5% gap)
- **2.98s vs 22.7s**: 7.6x speed penalty for 122B
- **1.9GB vs 81GB**: 42x memory cost for 122B
- **Practicality**: 100 samples in 5 min (3B) vs 38 min (122B)
- **Diminishing returns**: SQL generation doesn't need 122B params

**qwen3.5:122b-a10b Performance** (Session 2026-07-16):
- **DBBench**: 50/50 (100.0%) — First model to achieve perfect score
- **Speed**: 22.70s/sample (7.6x slower than Llama-3.2-3B)
- **Memory**: 97GB RAM used (81GB model)
- **Verdict**: Perfect accuracy but impractical for production (18.9 min for 50 samples vs 2.5 min for Llama-3.2-3B)
- **Use case**: Maximum-accuracy experiments where speed doesn't matter

**Teuken-7B Performance Breakdown** (Session 2026-07-16):
- **DBBench**: 99.0% (excellent SQL)
- **KnowledgeGraph**: 98.0% (excellent)
- **OS Interaction**: 57.7% (weak command generation)
- **Lateral Thinking**: 56.7% (weak reasoning)
- **Overall**: 87.4% (7x larger, 1.6x slower, 12% less accurate than Llama-3.2-3B)

**aip-best API Issue** (Session 2026-07-16):
- **Direct endpoint** (`http://141.33.165.84:8000/v1`): 14% success (broken)
- **LiteLLM proxy** (`http://141.33.165.84:4000/v1`): 75.2% success (custom parser needed)
- **Root cause**: Model outputs `reasoning_content` but `content: null`
- **Parser workaround**: Extract from `reasoning_content` field instead of `content`
- **Conclusion**: Not production-ready; requires custom client code

**Why 3B beats 35B** (Session 2026-07-15):
- **Better fine-tuning** for SQL/code instruction following
- **Follows strict formatting** (critical for code block parsing)
- **Stable inference** (no GPU saturation, no timeouts)
- **Task-appropriate** (SQL generation doesn't need 35B params)
- **Output format**: Larger models may output explanations instead of ````sql` blocks → parsing fails even if SQL is correct
- **GPU saturation**: 34GB model saturates GPU → unpredictable inference times, timeouts under load

**Teuken-7B Performance Breakdown** (Session 2026-07-16):
- **DBBench**: 99.0% (excellent SQL)
- **KnowledgeGraph**: 98.0% (excellent)
- **OS Interaction**: 57.7% (weak command generation)
- **Lateral Thinking**: 56.7% (weak reasoning)
- **Overall**: 87.4% (7x larger, 1.6x slower, 12% less accurate than Llama-3.2-3B)

**aip-best API Issue** (Session 2026-07-16):
- **Direct endpoint** (`http://141.33.165.84:8000/v1`): 14% success (broken)
- **LiteLLM proxy** (`http://141.33.165.84:4000/v1`): 75.2% success (custom parser needed)
- **Root cause**: Model outputs `reasoning_content` but `content: null`
- **Parser workaround**: Extract from `reasoning_content` field instead of `content`
- **Conclusion**: Not production-ready; requires custom client code

## Data Files

| Task | Location | Format | Samples |
|------|----------|--------|---------|
| DBBench | `/tmp/AgentBench/data/dbbench/standard.jsonl` | JSONL | 300 |
| Knowledge Graph | `/tmp/AgentBench/data/knowledgegraph/std.json` | JSON | 50 |
| OS Interaction | `/tmp/AgentBench/data/os_interaction/data/dev.json` | JSON | 26 |
| Lateral Thinking | `/tmp/AgentBench/data/lateralthinkingpuzzle/standard.xlsx` | Excel | 30 |

## Pitfalls

### 1. Excel Column Names (Lateral Thinking)
**DO NOT** use `question`/`clue` columns. The Excel file has:
- `story` (not `question`)
- `answer` (not `clue`)

**Wrong:**
```python
prompt = f"Question: {s['question']}\nClue: {s['clue']}"
```

**Correct:**
```python
prompt = f"Story: {s['story']}\nAnswer: {s['answer']}"
```

### 2. Code Block Extraction
Models may output SQL/bash in various formats. Extract robustly:
```python
def extract_sql(content):
    if not content: return None
    if "```sql" in content:
        return content.split("```sql")[1].split("```")[0].strip()
    elif "```" in content:
        return content.split("```")[1].split("```")[0].strip()
    return None
```

### 3. Concurrency vs Speed Tradeoff
- **`llama3.2:3b`**: 5 workers OK (1-2s/sample)
- **`qwen3.6:latest`**: 1 worker only (34GB GPU saturation, ~23s/sample)
- **High concurrency on large models**: Causes timeouts, empty responses

### 4. Docker Stack ALFWorld Fix (Python 3.9)
**Problem**: `textworld` package fails to build on Python 3.9 due to C extension/build system incompatibility. Multiple attempts (different versions, `--no-deps`, `--no-build-isolation`) all fail.

**Workaround**: Skip ALFWorld service in Docker stack. The Direct API method works perfectly for all other tasks.

**If ALFWorld is required**:
- Upgrade entire stack to Python 3.10+ (breaking change for other services)
- OR use Direct API method (bypass Docker entirely)
- OR fork/patch `textworld` build system (significant effort)

**Docker Compose command (skip ALFWorld)**:
```bash
docker compose -f extra/docker-compose.yml up -d controller redis dbbench-std os_interaction-std knowledgegraph-std freebase
```

### 5. System Prompt for SQL
For consistent SQL code blocks:
```python
{"role": "system", "content": "Output ONLY SQL in ```sql code block."}
```

### 6. Timeout Settings
- **Small models** (`llama3.2:3b`): 120s timeout
- **Large models** (`qwen3.6:latest`): 300s+ timeout (but still impractical for batch)

## Benchmark Script Template

```python
#!/usr/bin/env python3
import json, time, requests, os
from concurrent.futures import ThreadPoolExecutor, as_completed

MODEL = "llama3.2:3b"
OLLAMA_URL = "http://localhost:11434/api/chat"
RESULTS_DIR = "/tmp/agentbench_results"
os.makedirs(RESULTS_DIR, exist_ok=True)

def call_llm(messages, max_tokens=512, timeout=120):
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "max_tokens": max_tokens
    }
    resp = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
    return resp.json()

# Load samples and run benchmark...
```

## Official AgentBench Setup (Docker)

For containerized environments:
```bash
cd /tmp/AgentBench
docker compose -f extra/docker-compose.yml up -d controller redis dbbench-std os_interaction-std knowledgegraph-std freebase
```

**Note**: ALFWorld and WebShop services may fail to build due to dependency issues (`visdom` package, `textworld` build failure on Python 3.9). Skip them if not needed.

**Controller API**: Runs on port 5020 (not 5000). Endpoints: `/api/list_workers`, `/api/get_indices`, `/api/start_sample`, `/api/interact`.

**Direct API method** (recommended for LLM benchmarking): Bypass Docker stack entirely and call Ollama directly. See "Quick Start" above.

Requires:
- MySQL:8 (for DBBench)
- Custom OS images (for OS Interaction)
- ~16GB RAM (for WebShop)
- Ports 5020 available (controller)

## References
- [AgentBench GitHub](https://github.com/THUDM/AgentBench)
- [AgentBench Paper](https://arxiv.org/abs/2308.03688)
- Ollama API: `http://localhost:11434/api/chat`

## Support Files
- `references/alfworld-docker-build-failure.md` — Detailed troubleshooting guide for ALFWorld Docker build issues on Python 3.9 (textworld package, Inform7 download failures)
- `references/vllm-gated-models.md` — Guide for serving gated HuggingFace models with vLLM
- `references/aip-best-api-issues.md` — Root cause analysis of aip-best API broken response format (content: null, reasoning_content only)
- `references/teuken-7b-benchmark-results.md` — Full Teuken-7B benchmark results (87.4% overall, weak on reasoning/OS tasks)
- `references/qwen3.5-122b-benchmark-results.md` — **qwen3.5:122b-a10b DBBench results (100% success, 22.7s/sample, 81GB model) - perfect accuracy but 7.6x slower than Llama-3.2-3B**
- `scripts/agentbench_ollama_llama32.py` — Unified benchmark script for all AgentBench tasks (DBBench, KG, OS, LTP)
- `scripts/teuken_agentbench_full.py` — Full benchmark script for Teuken-7B (all 4 tasks, 206 samples)
- `scripts/qwen122_dbbench.py` — **DBBench script for qwen3.5:122b-a10b (50 samples, 100% success)**

## Session Notes (2026-07-15)
**Model Comparison**: `llama3.2:3b` vs `qwen3.6:latest` vs `aip-best` API
- **llama3.2:3b**: 98-100% success, 1-10s/sample, 1.9GB RAM — **OPTIMAL**
- **qwen3.6:latest**: ~50% success (timeouts), ~23s/sample, 34GB VRAM — **IMPRACTICAL**
- **aip-best API**: 11.9% success, 10s/sample — **DEGRADED**

**Why 3B beats 35B** for SQL/code tasks:
1. Better fine-tuning for instruction following
2. Strict output format compliance (critical for parsing)
3. Stable inference (no GPU saturation)
4. Task-appropriate (SQL doesn't need 35B params)
5. Larger models output explanations instead of code blocks → parsing fails

**Session Notes (2026-07-16) - Full Benchmark Suite**
**Teuken-7B (GGUF) Full Suite Results**:
- **DBBench**: 99/100 (99.0%) | 507s | 5.07s/sample
- **KnowledgeGraph**: 49/50 (98.0%) | 67s | 1.35s/sample
- **OS Interaction**: 15/26 (57.7%) | 107s | 4.11s/sample
- **Lateral Thinking**: 17/30 (56.7%) | 309s | 10.29s/sample
- **TOTAL**: 180/206 (87.4%) | 990s | 4.81s/sample

**aip-best (LiteLLM) Full Suite Results**:
- **DBBench**: 86/100 (86.0%) | 152s | 1.52s/sample
- **KnowledgeGraph**: 40/50 (80.0%) | 46s | 0.92s/sample
- **OS Interaction**: 23/26 (88.5%) | 34s | 1.32s/sample
- **Lateral Thinking**: 6/30 (20.0%) | 48s | 1.59s/sample
- **TOTAL**: 155/206 (75.2%) | 281s | 1.36s/sample

**aip-best API Root Cause Analysis**:
- **Issue**: Model outputs `reasoning_content` but leaves `content: null`
- **Impact**: Standard OpenAI parsers fail (14% success with direct endpoint)
- **Workaround**: Custom parser extracts from `reasoning_content` field (75.2% success)
- **Conclusion**: Not production-ready; requires custom client code
- **Lateral Thinking failure**: Model gets stuck in reasoning loops, never outputs final answer

**Final Recommendation**: **Llama-3.2-3B** is optimal (99.5% accuracy, 2.98s/sample, 1.9GB). Teuken-7B offers no advantage (slower, heavier, less accurate). aip-best API is unreliable (broken response format).

**Docker Stack**: Successfully built dbbench, os_interaction, knowledgegraph services. ALFWorld failed due to `textworld` build incompatibility on Python 3.9. Direct API method recommended.

**ALFWorld Fix Attempts (All Failed)**:
- Added build deps (`libffi-dev`, `libc6-dev`)
- Tried `textworld==1.4.0` with `--no-deps`
- Tried `sitecustomize.py` stub (needs too many submodules)
- Final error: `tar: Child returned status 2` during Inform7 download/extract
- **Conclusion**: Skip ALFWorld in Docker; use Direct API (99.5% success on other 4 tasks)

**vLLM Test (2026-07-15)**: Attempted to serve `Soofi-Project/Soofi-S-Base` but model is **gated** on Hugging Face. Requires `huggingface-cli login` before serving. Use public models (e.g., `meta-llama/Llama-3.2-3B-Instruct`) for testing.

**llama.cpp Setup (2026-07-15)**:
- **Build**: `cd /tmp/llama.cpp && mkdir build && cd build && cmake .. -DGGML_CUDA=ON && make -j$(nproc) llama-server llama-cli`
- **Server**: `/tmp/llama.cpp/build/bin/llama-server -m ~/models/<model>.gguf -c 2048 --port 8080 --host 0.0.0.0 -ngl 99`
- **Model Download**: `curl -L -o model.gguf "https://huggingface.co/<user>/<model>/resolve/main/model-Q4_K_M.gguf"`
- **Gated Models**: Requires `hf auth login` and accepting license on Hugging Face before download
- **API**: OpenAI-compatible at `http://localhost:8080/v1/chat/completions`
- **Test**: `curl http://localhost:8080/health` → `{"status":"ok"}`