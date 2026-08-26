---
name: web-search-backend-management
title: Web Search — Backend Management, DuckDuckGo, and CLI Tools
description: >-
  Manage web search in Hermes Agent: backend switching (firecrawl, tavily, exa,
  parallel, duckduckgo), API key management, and the standalone DuckDuckGo skill
  for CLI-based searching. Covers diagnosis, switching, and free alternatives.
author: Hermes Agent
date: 2026-04-30
tags: [web-search, duckduckgo, firecrawl, tavily, exa, backend, search]
---

# Web Search — Backend Management + DuckDuckGo CLI

This umbrella covers Hermes Agent's web search infrastructure and the standalone
DuckDuckGo CLI skill.

---

## Part 1: Web Search Backend Management

### When to use
- `web_search` returns "Payment Required", "Insufficient credits", or similar billing errors
- Any configured search backend becomes unavailable
- User asks about alternative search backends or free options

### How Hermes Agent web search works
Search backends are configured via `~/.hermes/config.yaml`:
```yaml
web:
  backend: firecrawl   # change this to switch
```

API keys live in `~/.hermes/.env` (keys may be commented out but already present).

### Available backends

| Backend | Package | Env var | Free tier |
|---|---|---|---|
| **duckduckgo** | ddgs (CLI) | None needed | ✅ Yes, unlimited |
| **tavily** | tavily-python | `TAVILY_API_KEY` | Yes (1,000/mo) |
| **exa** | exa_py | `EXA_API_KEY` | No (paid) |
| **parallel** | parallel | `PARALLEL_API_KEY` | No (paid) |
| **firecrawl** | firecrawl-py | `FIRECRAWL_API_KEY` | No (paid) |

### Diagnosis steps
1. Check which backend is configured: grep `web:` in `~/.hermes/config.yaml`
2. Check if the API key exists in `~/.hermes/.env` (may be commented out)
3. Test connectivity by running `web_search` — if it fails, switch backend
4. Switch backend: edit `config.yaml` line `backend: <old>` → `backend: <new>`
5. For DuckDuckGo: also ensure `ddgs` is installed in the correct Python runtime

### Quick fix pattern
```bash
# For paid backends: switch config + ensure key
patch ~/.hermes/config.yaml "backend: firecrawl" "backend: tavily"

# For DuckDuckGo (free, no key needed):
patch ~/.hermes/config.yaml "backend: firecrawl" "backend: duckduckgo"
pip install ddgs   # if not already installed
```

### Key files
- Config: `~/.hermes/config.yaml` — `web.backend` key
- Keys: `~/.hermes/.env` — API keys for each backend
- Implementation: `~/.hermes/hermes-agent/tools/web_tools.py`

### Pitfalls
- Keys may be present but commented out in `.env` — uncomment them
- After changing config, restart the Hermes Agent session
- `web_extract` uses the same backend as `web_search`
- Firecrawl credits are consumed by both `web_search` and `web_extract`
- **DuckDuckGo runtime**: `ddgs` must be installed in the Python runtime that
  executes `web_search` (usually the hermes-agent venv), not just system Python

---

## Part 2: DuckDuckGo CLI — Standalone Skill

For when you need DuckDuckGo searching directly from the terminal (not via
Hermes Agent's `web_search` tool):

### Prerequisites
```bash
pip install ddgs    # CLI + Python API
```

### Key commands
```bash
# Text search
ddgs text -q "query" -m 10 -o json

# News search
ddgs news -q "query" -m 10 -o json

# Image search
ddgs images -q "query" -o json
```

### When to use this skill (vs `web_search` tool)
- You need standalone terminal searching outside Hermes Agent
- You want to pipe results into other commands
- You need fine-grained control over output format
- The `web_search` tool backend is down and you need a fallback

### When NOT to use this skill
- You're already in a Hermes Agent conversation — use the `web_search` tool
- You need web page content extraction — use `web_extract` instead

# Web Search Backend Management

## When to use

- `web_search` returns "Payment Required", "Insufficient credits", or similar billing errors
- Any configured search backend (firecrawl, parallel, exa, tavily, duckduckgo) becomes unavailable
- User asks about alternative search backends or free options

## How Hermes Agent web search works

Search backends are configured via `~/.hermes/config.yaml`:

```yaml
web:
  backend: firecrawl   # change this to switch
```

And API keys live in `~/.hermes/.env` (keys may be commented out but already present).

## Available backends (built-in `web_search` tool)

| Backend | Package | Env var | Free tier | Config key |
|---|---|---|---|---|
| **duckduckgo** | ddgs (CLI) | None needed | ✅ Yes, unlimited | `backend: duckduckgo` |
| **tavily** | tavily-python | `TAVILY_API_KEY` | Yes (1,000/mo) | `backend: tavily` |
| **exa** | exa_py | `EXA_API_KEY` | No (paid) | `backend: exa` |
| **parallel** | parallel | `PARALLEL_API_KEY` | No (paid) | `backend: parallel` |
| **firecrawl** | firecrawl-py | `FIRECRAWL_API_KEY` | No (paid) | `backend: firecrawl` |

## DuckDuckGo (native backend, no API key)

DuckDuckGo is a built-in backend — no API key or subscription needed. It calls the `ddgs` CLI via subprocess internally.

**Prerequisites**: `ddgs` must be installed in the Python runtime that runs `web_search`:
```bash
# In the hermes-agent venv (where web_tools.py runs)
~/.hermes/hermes-agent/venv/bin/python -m ensurepip --upgrade 2>/dev/null
~/.hermes/hermes-agent/venv/bin/python -m pip install ddgs

# Or in system Python if using local terminal backend
pip install ddgs --break-system-packages
```

**Install ddgs CLI too** (for standalone use or the skill):
```bash
pip install ddgs
```

When `backend: duckduckgo` is set, `_duckduckgo_search()` in `web_tools.py` invokes:
```bash
ddgs text -q "<query>" -m "<limit>" -o json
```

It maps `ddgs` fields (`title`, `href`, `body`) to the standard web search format (`title`, `url`, `description`, `position`).

## Free options summary

| Option | How it works | Setup required |
|---|---|---|
| **DuckDuckGo** (native) | `ddgs` CLI via subprocess | `pip install ddgs` |
| **Tavily** (native) | Native `web_search` tool | API key from tavily.com |
| **DuckDuckGo skill** | `ddgs` CLI or Python API | `pip install ddgs`, `skill_view(duckduckgo-search)` |
| MCP docs search | `mcp_docs_search_docs()` | Indexed libraries only |

## Diagnosis steps

1. **Check which backend is configured**: grep `web:` section in `~/.hermes/config.yaml`
2. **Check if the API key exists** in `~/.hermes/.env` (may be commented out)
3. **Test connectivity** by running `web_search` — if it still fails, switch backend
4. **Switch backend**: edit `config.yaml` line `backend: <old>` → `backend: <new>`
5. **For DuckDuckGo**: also ensure `ddgs` is installed in the correct Python runtime

## Switching backends

Edit `~/.hermes/config.yaml`:
```bash
patch ~/.hermes/config.yaml "backend: firecrawl" "backend: duckduckgo"
```

For paid backends, also ensure the corresponding API key is set in `~/.hermes/.env` (uncomment if needed).

## Key files

- Config: `~/.hermes/config.yaml` — `web.backend` key
- Keys: `~/.hermes/.env` — API keys for each backend
- Implementation: `~/.hermes/hermes-agent/tools/web_tools.py` — `_get_backend()`, backend dispatch functions (`_duckduckgo_search`, `_tavily_request`, `_exa_search`, `_parallel_search`)
- ddgs package: installed via `pip install ddgs`

## Quick fix pattern

```bash
# For paid backends: just switch config + ensure key
patch ~/.hermes/config.yaml "backend: firecrawl" "backend: tavily"
# Set TAVILY_API_KEY in .env

# For DuckDuckGo (free, no key needed):
patch ~/.hermes/config.yaml "backend: firecrawl" "backend: duckduckgo"
pip install ddgs   # if not already installed
```

## Pitfalls

- Keys may be present but commented out in `.env` — uncomment them
- After changing config, restart the Hermes Agent session for the change to take effect
- `web_extract` uses the same backend as `web_search`
- Firecrawl credits are consumed by both `web_search` and `web_extract`
- **DuckDuckGo runtime**: `ddgs` must be installed in the Python runtime that executes `web_search` (usually the hermes-agent venv), not just the system Python — terminal and `execute_code` are separate runtimes
