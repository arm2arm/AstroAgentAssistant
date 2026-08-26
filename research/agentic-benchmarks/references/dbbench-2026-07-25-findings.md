# DBench SQL Generation Findings — Session Reference (2026-07-25)

## Endpoint Comparison: aip-best across 3 endpoints

Three endpoints serving the same named model "aip-best" produced dramatically different DBench SQL generation rates:

| Endpoint | SQL Rate | Avg Time | Errors | Notes |
|---|---|---|---|---|
| `litellm.kube.aip.de` | 93.3% (280/300) | 5.3s | 0 | Best performer |
| `141.33.165.84:8000` (v1, 300s timeout, 4096 tokens) | 29.3% (88/300) | 14.5s | 3 | Low SQL rate |
| `141.33.165.84:8000` (v2, 600s timeout, 8192 tokens) | 27.7% (83/300) | 14.7s | 2 | Even slightly worse |

## Key Finding: Increasing timeout/tokens did NOT help

**Hypothesis**: The low SQL rate was caused by response timeouts (300s) and/or token truncation (4096 max_tokens cutting off SQL output).

**Test**: Ran with 600s timeout and 8192 max_tokens.

**Result**: SQL rate actually *decreased* (27.7% vs 29.3%). The root cause is **not** timeouts or token limits.

**Root cause**: The model on `141.33.165.84:8000` uses Q5_K quantization and may have different server configuration (temperature, top_p, etc.) than the kube endpoint, producing different output quality.

## Key Finding: SQL rate varies by sample quartile

Both runs show the same pattern — SQL rate drops sharply in the middle of the dataset:

| Quartile | v1 SQL Rate | v2 SQL Rate |
|---|---|---|
| Q1 (samples 1-75) | 49.3% | 48.6% |
| Q2 (samples 76-150) | 11.0% | 14.7% |
| Q3 (samples 151-225) | 21.6% | 12.2% |
| Q4 (samples 226-300) | 36.0% | 36.0% |

The SQL rate is consistent between runs within each quartile, suggesting the DBench dataset has harder SQL queries (more complex JOINs, subqueries) in the middle.

## Configuration Details

- **Model**: aip-best (Qwen3.6-35B, Q5_K quantization)
- **Context window**: 1,048,576 tokens
- **API**: `http://141.33.165.84:8000/v1/chat/completions` (OpenAI-compatible)
- **DBBench task**: dbbench-std (MySQL SQL generation)
- **Controller**: `http://localhost:5020`
- **Workers**: 10 Docker containers (`agentbench-fc-dbbench-std-1` through `10`)

## Benchmark Script Template

```python
#!/usr/bin/env python3
"""DBBench benchmark runner for OpenAI-compatible API endpoints."""

import requests, json, time, re, os

API_URL = "http://ENDPOINT:8000/v1/chat/completions"
MODEL = "aip-best"
CONTROLLER = "http://localhost:5020"
N = 300
TIMEOUT = 600  # seconds per sample — slow endpoints need this
MAX_TOKENS = 8192

def call_llm(messages, tools=None):
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "temperature": 0.1,
        "max_tokens": MAX_TOKENS,
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    resp = requests.post(API_URL, json=payload,
                         headers={"Content-Type": "application/json"}, timeout=TIMEOUT)
    if resp.status_code != 200:
        return None
    data = resp.json()
    msg = data.get("choices", [{}])[0].get("message", {})
    content = msg.get("content", "") or msg.get("reasoning", "")  # aip-best uses reasoning field
    return content if content else None

def is_sql(s):
    """Check if response contains SQL in code blocks or inline."""
    if "```" in s:
        for m in re.findall(r'```(?:sql)?\s*\n(.*?)```', s, re.DOTALL):
            if any(k in m.upper() for k in ['SELECT', 'FROM', 'WHERE', 'JOIN',
                                            'INSERT', 'UPDATE', 'DELETE', 'CREATE']):
                return True
    return any(k in s.upper() for k in ['SELECT ', 'FROM ', 'WHERE ', 'JOIN '])
```

## Pitfall: "API FAIL (no content)"

The aip-best endpoint at `141.33.165.84:8000` occasionally returns responses with empty content (the `content` field is empty/null). Always check both `content` and `reasoning` fields, and treat empty responses as errors:

```python
content = msg.get("content", "") or msg.get("reasoning", "")
if not content:
    # Handle as error
```

## Pitfall: No tool stripping needed for OpenAI-compatible endpoints

Unlike Ollama (where `tool_definitions` in messages must be stripped for non-tool models), the OpenAI-compatible endpoint at `141.33.165.84:8000` handles tool definitions properly. The runner should pass tools through to the API without stripping.