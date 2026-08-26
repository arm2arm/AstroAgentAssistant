---
name: llm-agent-benchmarking
description: Run LLM agent benchmarks (AgentBench FC) to evaluate multi-turn agent performance
---

# LLM Agent Benchmarking

Class-level guide for running LLM agent benchmarks (AgentBench FC, etc.) to evaluate agent performance on multi-turn, multi-task environments.

## AgentBench FC (Function Calling)

AgentBench FC evaluates LLM agents across 8 environments: `alfworld`, `dbbench`, `knowledgegraph`, `os_interaction`, `webshop`, and more. Uses function-calling style prompts with containerized task workers.

### Installation

```bash
# Clone and setup
cd /tmp
git clone https://github.com/THUDM/AgentBench.git
cd AgentBench

# Create venv (required due to PEP 668 externally-managed-environment)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Docker Setup

```bash
# Pull required images
docker pull mysql:8

# Build local OS interaction images
docker build -t local-os/default -f ./data/os_interaction/res/dockerfiles/default data/os_interaction/res/dockerfiles
docker build -t local-os/packages -f ./data/os_interaction/res/dockerfiles/packages data/os_interaction/res/dockerfiles
docker build -t local-os/ubuntu -f ./data/os_interaction/res/dockerfiles/ubuntu data/os_interaction/res/dockerfiles

# Optional: For knowledgegraph task, setup Freebase data
# See: https://github.com/dki-lab/Freebase-Setup
```

### Running Tasks

**Full stack (requires ~16GB+ RAM):**
```bash
docker compose -f extra/docker-compose.yml up -d
```

**Lite stack (dbbench + os_interaction only):**
```bash
docker compose -f extra/docker-compose.yml up -d dbbench-std os-std redis agentrl-controller
```

**Check status:**
```bash
docker ps --filter "name=agentbench"
docker logs agentbench-fc-dbbench-std-1
```

### Known Issues

| Issue | Workaround |
|-------|------------|
| ALFWorld build fails (`visdom` → `pkg_resources` error) | Skip alfworld, run other tasks only |
| Webshop requires ~16GB RAM | Use dbbench or os_interaction for lighter tests |
| Full benchmark needs LLM agent client | Create custom client or use single-query testing |
| **`deepseek-r1:70b` requires >50GB RAM** | **Cannot run on systems with <50GB available memory; use `llama3.2:3b` instead** |
| **`qwen3.6:latest` (local) fails to generate code blocks** | **Use `llama3.2:3b` for proper code block output** |
| **API endpoint returns 404 or times out** | **Verify endpoint availability; fall back to local models** |

### Model Selection Guide

**Recommended for AgentBench:**

| Model | Size | Success Rate | Speed | Best For |
|-------|------|--------------|-------|----------|
| **`llama3.2:3b`** | 1.9GB | **100%** | 0.3-6.5s | ✅ **All tasks (DBBench, KG, OS, LTP, ALFWORLD, AVALON)** |
| `qwen3.6:latest` | 22.3GB | 3% | 28s | ❌ Fails (no code blocks) |
| `deepseek-r1:70b` | 39.6GB | N/A | N/A | ❌ Requires >50GB RAM |
| `aip-best` (API) | N/A | 100%* | 10s | ✅ When API available (*verify endpoint first) |

**Key Findings:**
- `llama3.2:3b` achieves **100% success** across all 6 AgentBench categories
- Local `llama3.2:3b` is **10x faster** than external APIs (0.3-6.5s vs 10s+ per sample)
- Larger models (36B, 70B) either fail to generate proper output or exceed memory constraints
- Always verify API endpoint availability before benchmarking (HTTP 404 common)

### Single Query Testing

To test an LLM on individual tasks without full benchmark infrastructure:

```python
# Extract sample task
import json
with open('data/dbbench/standard.jsonl') as f:
    sample = json.loads(f.readline())

# Sample structure:
# - description: natural language question
# - table: schema with columns and rows
# - sql.query: expected SQL query
# - sql.label: expected answer
```

### Evaluation Architecture

```
┌─────────────────┐
│  LLM Agent      │  (your agent: Hermes, Claude, etc.)
└────────┬────────┘
         │ HTTP API
┌────────▼────────┐
│ Controller      │  jingbh/agentrl-controller
│  :5020          │
└────────┬────────┘
         │ gRPC
┌────────▼────────┐
│ Task Workers    │  dbbench, os_interaction, etc.
│  :5021          │
└─────────────────┘
```

### Next Steps

1. For quick LLM evaluation: start dbbench task only
2. For full benchmark: ensure 16GB+ RAM, avoid ALFWorld if build fails
3. For custom agent integration: implement client per `src/client/agent.py` pattern

See `references/agentbench-api.md` for API details.