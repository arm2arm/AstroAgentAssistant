# aip-best API Issues (Qwen3.6-35B-A3B)

## Problem Summary
The `aip-best` endpoint (Qwen3.6-35B-A3B) returns **non-standard OpenAI responses** that break all standard parsers.

## Root Cause

### Direct Endpoint (`http://141.33.165.84:8000/v1`)
```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": null,              // ← EMPTY! No answer
      "reasoning_content": "Here's a thinking process: 1. Analyze..."  // ← Only reasoning
    }
  }]
}
```

**Impact**: 14% success rate (parser extracts `null` → failure)

### LiteLLM Proxy (`http://141.33.165.84:4000/v1`)
Same broken format passed through. Requires **custom parser** to extract `reasoning_content`.

**Workaround**: 75.2% success with custom parser (still 24% worse than Llama-3.2-3B)

## Benchmark Results

| Endpoint | Success Rate | Avg Time | Notes |
|----------|--------------|----------|-------|
| Direct (`:8000`) | 14% | 1.61s | Standard parser fails |
| LiteLLM (`:4000`) | 75.2% | 1.36s | Custom parser needed |
| Llama-3.2-3B | 99.5% | 2.98s | Standard API |

## Failure Analysis

### Lateral Thinking (20% success)
Model gets stuck in **reasoning loops** and never outputs the final answer:
- **Question**: "If a bat and ball cost $1.10, how much does the ball cost?"
- **Expected**: `0.05`
- **Actual**: `null` (reasoning only, no answer)
- **Even worse**: Sometimes outputs wrong answer like `$0.10`

### DBBench (14% failure)
When it does output, often:
- Outputs **reasoning text** instead of SQL
- Outputs **incomplete code blocks**
- Outputs **explanations** instead of pure SQL

## Architecture Issue
`Qwen3.6-35B-A3B` appears to be a **reasoning-focused model** (like o1) that:
- Separates `reasoning_content` from `content`
- **Intentionally leaves `content` empty** by design
- Requires **custom client logic** to extract reasoning as the "answer"

## Custom Parser Example

```python
def get_model_response(messages):
    response = requests.post(
        "http://141.33.165.84:4000/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"model": "aip-best", "messages": messages}
    )
    data = response.json()
    
    # Standard parser fails (content is null)
    # content = data["choices"][0]["message"]["content"]  # ← None!
    
    # Custom parser: extract from reasoning_content
    reasoning = data["choices"][0]["message"].get("reasoning_content", "")
    return reasoning  # Use reasoning as the "answer"
```

## Conclusion
**Not production-ready** for tasks requiring final answers. Designed for **chain-of-thought reasoning only**, not task completion.

**Recommendation**: Use **Llama-3.2-3B** (99.5% success, standard API, no quirks).

## References
- Session 2026-07-16: Full benchmark suite with aip-best (LiteLLM)
- Direct endpoint: 14% success (broken)
- LiteLLM proxy: 75.2% success (custom parser)
- Llama-3.2-3B: 99.5% success (optimal)
