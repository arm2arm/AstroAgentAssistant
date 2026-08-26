# AgentBench FC Installation and Quick Start

**Purpose**: Install and run AgentBench FC (Function Calling) — a benchmark for evaluating LLM agents across multiple environments (dbbench, os_interaction, knowledgegraph, webshop, alfworld).

**Discovered**: July 14, 2026 — session testing Hermes Agent's performance on LLM agent benchmarks.

---

## Installation Pattern

AgentBench FC (THUDM/AgentBench) does **not** have a `setup.py` or `pyproject.toml` at the root. The correct install pattern is:

```bash
# Clone
git clone https://github.com/THUDM/AgentBench.git
cd AgentBench

# Create venv (required due to PEP 668 externally-managed environment)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies from requirements.txt (NOT pip install -e .)
pip install -r requirements.txt
```

**Why this pattern?**
- No `setup.py` or `pyproject.toml` at root → `pip install -e .` fails
- Dependencies are in `requirements.txt` at repo root
- PEP 668 enforced → venv required (or `--break-system-packages`)

---

## Running the Benchmark

### Full Benchmark (Requires Docker)

AgentBench FC uses Docker Compose for containerized task workers. Requires:

- Docker + Docker Compose
- ~16GB+ RAM (webshop alone needs 16GB)
- Multiple Docker images (mysql:8, local-os/*, freebase)

**Setup steps:**

```bash
# 1. Pull/build required Docker images
docker pull mysql:8
docker build -t local-os/default -f ./data/os_interaction/res/dockerfiles/default data/os_interaction/res/dockerfiles
docker build -t local-os/packages -f ./data/os_interaction/res/dockerfiles/packages data/os_interaction/res/dockerfiles
docker build -t local-os/ubuntu -f ./data/os_interaction/res/dockerfiles/ubuntu data/os_interaction/res/dockerfiles

# 2. (Optional) Set up Freebase for knowledgegraph task
# Download from https://github.com/dki-lab/Freebase-Setup
# Place at ./virtuoso_db/virtuoso.db

# 3. Start all services
docker compose -f extra/docker-compose.yml up
```

This starts:
- AgentRL Controller
- Task workers for: alfworld, dbbench, knowledgegraph, os_interaction, webshop
- Freebase server (for KG)
- Redis (for container allocation)

### Running Tasks

After Docker services are up, run the assigner with a config:

```bash
PYTHONPATH=/path/to/AgentBench python -m src.assigner --config configs/start_task_lite.yaml
```

**Config files:**
- `configs/start_task_lite.yaml` — low-resource preset (dbbench-std, os-std)
- `configs/start_task.yaml` — full preset
- Custom configs in `configs/assignments/`

**Agent configs:**
- `configs/agents/api_agents.yaml` — API-based agents (GPT, etc.)
- `configs/agents/fs_agent.yaml` — filesystem agent
- `configs/agents/openai-chat.yaml` — OpenAI chat models

---

## Quick Test (No Docker)

To test the Python stack without Docker:

```bash
cd /tmp/AgentBench
source .venv/bin/activate
PYTHONPATH=/tmp/AgentBench python -m src.assigner --help
```

This verifies dependencies are installed but won't run actual tasks (requires Docker containers).

---

## Pitfalls

1. **No editable install** — `pip install -e .` fails. Use `pip install -r requirements.txt` instead.
2. **Docker memory** — webshop needs ~16GB RAM. alfworld leaks memory/disk (requires worker restart).
3. **Freebase setup** — knowledgegraph task requires Freebase DB at `./virtuoso_db/virtuoso.db`.
4. **Python version** — venv uses Python 3.11 (not system Python 3.12).
5. **CUDA warnings** — torch/transformers may show deprecation warnings (safe to ignore).

---

## Available Environments

| Environment | Abbrev | Description |
|-------------|--------|-------------|
| alfworld | AF | Text-based puzzle games |
| dbbench | DB | SQL query tasks |
| knowledgegraph | KG | Freebase SPARQL queries |
| os_interaction | OS | Linux shell tasks |
| webshop | WS | E-commerce navigation |

---

## Alternative Benchmarks

If AgentBench is too heavy, consider:
- **BigBench** — simpler LLM capability benchmark
- **GLUE/SuperGLUE** — NLP tasks
- **Custom eval** — write a focused eval for your specific use case

---

## Session Notes

**July 14, 2026**: Tested AgentBench FC installation on Hermes Agent (Linux 6.17, Python 3.11.15). Successfully installed dependencies via venv + requirements.txt. Full benchmark requires Docker Compose + 16GB+ RAM. For quick "how am I doing" checks, a simpler custom eval may be more practical than the full AgentBench suite.

**Key takeaway**: AgentBench is overkill for quick agent performance checks. Use it for formal benchmarking across multiple environments, not for ad-hoc "test my agent" runs.
