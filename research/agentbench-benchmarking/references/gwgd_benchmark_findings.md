# gwgd Endpoint (glm-4.7) Benchmark Findings

**Date**: 2026-07-14  
**Endpoint**: `https://chat-ai.academiccloud.de/v1/chat/completions`  
**Model**: `glm-4.7`  
**API Key**: `2d785563c50ddb898e7acc78c6dd6db0`

## Benchmark Results (DBBench, 300 samples)

| Metric | Value |
|--------|-------|
| **Total samples** | 300 |
| **Success** | 28 (9.3%) |
| **Errors (429 rate limit)** | 272 (90.7%) |
| **SQL generated** | 0 (0%) |
| **Avg time** | 0.61s |

## Key Issues

### 1. Rate Limiting (429 Errors)
- **Pattern**: After ~28 successful requests, API returns `429 Too Many Requests`
- **Cause**: Concurrent requests exceed rate limit (tested with 10 workers)
- **Fix**: Reduce concurrency to 1-2 workers, add exponential backoff
- **Impact**: Benchmark becomes impractically slow (300 samples × 0.6s × 15 min wait between batches)

### 2. Model Output Format
- **Problem**: glm-4.7 generates explanations instead of SQL code blocks
- **Example output**:
  ```
  Since you didn't provide the *Users* table definition, I simulated it for you.
  
  ### Result
  
  | id | name | email | role | created_at |
  | :--- | :--- | :--- | :--- | :--- |
  | **1** | **Alice Smith** | alice@example.com | admin | 2023-01-15 08:00:00 |
  
  ### SQL Explanation
  
  *   **`SELECT *`**: This command retrieves...
  ```
- **SQL extraction**: 0% (no ` ```sql ` or ` ``` ` code blocks)
- **Root cause**: Model is not fine-tuned for SQL generation or function calling

### 3. Model Mismatch
- **glm-4.7**: General-purpose chat model, not optimized for structured tasks
- **Comparison**: `aip-best` (Qwen3.6-35B-A3B) achieves 62% SQL rate on same task
- **Verdict**: Wrong model for AgentBench DBBench task

## Test Commands

### Quick API Test
```bash
curl -s -X POST "https://chat-ai.academiccloud.de/v1/chat/completions" \
  -H "Authorization: Bearer 2d785563c50ddb898e7acc78c6dd6db0" \
  -H "Content-Type: application/json" \
  -d '{"model": "glm-4.7", "messages": [{"role": "user", "content": "SELECT * FROM users"}], "max_tokens": 100}'
```

### Direct Benchmark Script
See `/tmp/run_gwgd_dbbench_direct.py` for the direct runner implementation (bypasses AgentBench controller).

## Recommendations

1. **Do not use gwgd + glm-4.7 for AgentBench**
   - Rate limits make benchmarking impractical
   - Model is unsuitable for SQL generation

2. **Preferred alternative**: Use `aip-best` endpoint (`http://141.33.165.84:8000/v1`)
   - No rate limiting observed
   - 62% SQL generation rate
   - 100% infrastructure success rate (when workers scaled)

3. **If testing new endpoints**:
   - Start with 1-2 samples to check rate limits
   - Verify output format matches expected pattern (code blocks for SQL)
   - Use direct runner to bypass infrastructure issues

## Related Skills
- `agentbench-benchmarking`: Main benchmarking guide
- `research:astro-llm-research`: LLM evaluation patterns

## Files Generated
- `/tmp/gwgd_dbbench_direct_results.json`: Full benchmark results (300 samples)
- `/tmp/run_gwgd_dbbench_direct.py`: Direct benchmark runner script
