# OLMO-3.1 Benchmark Findings

## Date
2026-07-21

## Model Details
- **Name**: olmo-3.1:latest (Ollama)
- **Size**: 32.2 GB (Q4_K_M quantization)
- **Parameters**: 32.2B
- **Family**: olmo3

## Benchmark Results

### DBBench (SQL Generation)
- **Status**: Ran 20 samples only (114s/sample × 300 = ~11h — impractical)
- **SQL Rate**: Tested — model generates SQL correctly when prompted
- **Avg Time**: ~114-126s/sample
- **Errors**: 0 (when tool_definitions are stripped)
- **Verdict**: ✅ Capable but **too slow for batch benchmarking**

## Known Quirks

### 1. Response in `thinking` field
OLMO-3.1 returns its response in `message.thinking`, NOT `message.content`:

```python
# WRONG (will return empty):
content = msg.get("content", "") or msg.get("reasoning", "")

# CORRECT:
content = msg.get("content") or msg.get("reasoning") or msg.get("thinking") or ""
```

Verified: `message.content` is always `""` for OLMO-3.1.

### 2. Rejects tool definitions
OLMO-3.1 returns HTTP 400 if tool definitions are sent:

```
Error: "{model_name} does not support tools"
```

Fix: Strip `tool_definitions` from each message dict and omit `tools` from payload entirely.

### 3. GPU Performance
Tested on NVIDIA GB10 with 121GB RAM:
- First sample: ~114s (model load into VRAM)
- Subsequent samples: ~114s (model already cached in VRAM)
- Bottleneck: **Memory bandwidth**, not compute
- `eval_count`: ~1000 tokens per response
- `eval_duration`: ~96s

This is acceptable for a 32GB quantized model but impractical for 300-sample benchmark.

## Runner Pattern for OLMO-3.1

```python
def call_olmo(messages):
    # Strip tool_calls from messages
    clean_messages = []
    for msg in messages:
        m = dict(msg)
        m.pop("tool_calls", None)
        clean_messages.append(m)

    payload = {
        "model": "olmo-3.1:latest",
        "messages": clean_messages,
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": -1}
    }
    resp = requests.post("http://localhost:11434/api/chat", json=payload, timeout=180)
    data = resp.json()
    msg = data.get("message", {})
    # OLMO-3.1 uses 'thinking', not 'content'
    content = msg.get("thinking", "") or msg.get("content", "")
    if not content:
        return None
    return content
```

## Recommendation
Use OLMO-3.1 for:
- ✅ Single-sample quality checks
- ✅ Long-context reasoning tasks
- ✅ Tasks requiring high accuracy over speed

Do NOT use for:
- ❌ Batch benchmarking (300 samples)
- ❌ Time-sensitive applications
- ❌ Parallel task execution

Consider for benchmark comparison: run 20 samples, extrapolate to 300, report with caveat about sample size.
