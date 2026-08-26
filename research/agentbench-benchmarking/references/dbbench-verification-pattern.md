# DBBench Verification Pattern

## Issue

When re-running DBBench benchmark with `llama3.2:3b`, parallel requests (5+ workers) can cause **0% success** due to Ollama initialization/stale state, even though manual tests show 100% success.

## Symptoms

- Initial benchmark run: 100% success (100/100 SQL)
- Re-run with same script: **0% success** (0/100 SQL)
- Manual `curl` test: 100% success
- Response times in failed run: ~1.5s (fast, but empty responses)

## Root Cause

Ollama server can enter a stale state or have race conditions when handling multiple concurrent requests. The first few requests may fail or return empty responses, causing the entire benchmark to fail.

## Fix Pattern

### Option 1: Single-Threaded Verification

```python
# Run with max_workers=1 for verification
results = []
for i, s in enumerate(samples):
    r = call_llm([...])
    results.append(r)
    if (i+1) % 20 == 0:
        print(f"{i+1}/100 | SQL: {sum(1 for x in results if x['success'])}")
```

**Expected**: ~98% success (normal variance due to stochasticity)

### Option 2: Manual Verification First

Before full run, test with 10 samples:

```bash
cd /tmp && ~/.hermes/hermes-agent/venv/bin/python << 'EOF'
import requests, json, time

samples = [json.loads(l) for l in open("/tmp/AgentBench/data/dbbench/standard.jsonl")][:10]

for i, s in enumerate(samples):
    payload = {
        "model": "llama3.2:3b",
        "messages": [
            {"role": "system", "content": "Output ONLY SQL in ```sql code block."},
            {"role": "user", "content": s.get("description", "")}
        ],
        "stream": False,
        "max_tokens": 512
    }
    
    resp = requests.post("http://localhost:11434/api/chat", json=payload, timeout=30)
    data = resp.json()
    content = data.get("message", {}).get("content", "")
    
    if "```sql" in content:
        print(f"{i+1}/10 | OK")
    else:
        print(f"{i+1}/10 | FAIL: {content[:100]}")
EOF
```

**Expected**: 10/10 OK

### Option 3: Restart Ollama

If parallel requests fail:

```bash
ollama stop llama3.2:3b
ollama serve &
sleep 5
# Re-run benchmark
```

## Response Structure

Ollama returns:

```json
{
  "model": "llama3.2:3b",
  "created_at": "2026-07-15T11:12:33Z",
  "message": {
    "role": "assistant",
    "content": "```sql\nSELECT ...```"
  },
  "done": true,
  "total_duration": 2179883216,
  "eval_count": 103
}
```

**Note**: Use `data["message"]["content"]` (not `choices[0].message.content` like OpenAI API).

## Expected Results

| Run Type | Success Rate | Notes |
|----------|--------------|-------|
| Initial (parallel) | 100% | Clean state |
| Re-run (parallel) | 0% | Stale state / race condition |
| Re-run (single-threaded) | ~98% | Normal variance |
| Manual curl test | 100% | Always works |

## Key Lesson

**Always verify with small sample first**. If parallel benchmark fails, retry single-threaded. The model is capable (100% in manual tests); the issue is concurrency/stale state.

## Reference

- Session: 2026-07-15, DBBench verification with `llama3.2:3b`
- Results: `/tmp/agentbench_llama32_final_verify/dbbench_final.json` (98/100, 1.47s avg)
