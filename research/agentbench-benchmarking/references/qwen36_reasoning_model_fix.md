# qwen3.6:latest Reasoning Model Fix

## Problem

When benchmarking `qwen3.6:latest` (and similar reasoning models like `aip-best`), the benchmark returns **0% success** even though the model is capable.

## Root Cause

These models are **reasoning-focused** and separate thought from answer:

```json
{
  "model": "qwen3.6:latest",
  "response": "",                    // ← EMPTY!
  "thinking": "Here's a thinking process:\n1. Analyze input...\n```sql\nSELECT * FROM users;\n```"
}
```

The actual SQL output is in the **`thinking` field**, not `response`.

## Impact

- **Without fix**: 0/50 success (0%) — all responses empty
- **With fix**: 50/50 success (100%) — extracting from `thinking` field
- **Speed**: 30.74s/sample (10x slower than llama3.2-3B)

## Fix

Extract from both fields:

```python
data = response.json()
content = data.get("response", "") or data.get("thinking", "") or ""
sql = extract_sql(content)
```

## CLI Verification

The CLI works because it displays both fields:

```bash
ollama run qwen3.6:latest "SELECT * FROM users"
# Shows: "Here's a thinking process: ... ```sql SELECT * FROM users; ```"
```

## Model Comparison

| Model | Size | DBBench | Speed | Verdict |
|-------|------|---------|-------|---------|
| **llama3.2-3B** | 1.9GB | 100% | 3s | ✅ **Best** (standard API, 10x faster) |
| **qwen3.6:latest** | 23GB | 100% | 30.7s | ⚠️ Perfect but 10x slower |
| **qwen3.5:122b** | 81GB | 100% | 22.7s | ⚠️ Perfect but 7.6x slower |

## Recommendation

For production, prefer **llama3.2-3B**:
- Same 100% accuracy
- 10x faster (3s vs 30s)
- 12x less memory (1.9GB vs 23GB)
- Standard API (no `thinking` field quirks)

Use reasoning models only when 100% accuracy is mandatory and speed/memory are not constraints.

## Implementation Pattern

See `scripts/qwen36_dbbench_v2.py` for the fixed benchmark script that handles both `response` and `thinking` fields.
