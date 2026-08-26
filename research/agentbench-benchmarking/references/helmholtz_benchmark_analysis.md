# Helmholtz Blablador Endpoint Benchmark Analysis

## Endpoint Configuration

- **Base URL**: `https://api.helmholtz-blablador.fz-juelich.de/v1`
- **API Key**: `glpat-<YOUR_TOKEN>`
- **Available Models**: See `references/helmholtz_available_models.md`

## Benchmark Results (DBBench, 300 samples)

### Model Comparison

| Model | Alias | Success | SQL Rate | Errors | Avg Time | Verdict |
|-------|-------|---------|----------|--------|----------|---------|
| Qwen3.6-35B-A3B | `aip-best` | 100% | 99.7% | 0% | 10.11s | ✅ **Production Ready** |
| GLM-5.2-AWQ-INT4 | `alias-glm-huge` | 5% | 4.7% | 95% | 0.96s | ❌ Rate Limited |
| MiniMax-M2.7 | `alias-huge` | 3.3% | 3.3% | 96.7% | 0.25s | ❌ Rate Limited |
| Apertus-8B | `alias-apertus` | 3.3% | 3.3% | 96.7% | 0.06s | ❌ Rate Limited |
| Qwen3.5-122B | `alias-large` | 0% | 0% | N/A | ~4s | ❌ Wrong Output Format |
| Qwen3.6-35B | `alias-qwen36-35b` | 0% | 0% | N/A | ~3.5s | ❌ `content: None` |

### Key Findings

#### 1. Severe Rate Limiting

All Helmholtz models hit **429 Too Many Requests** after ~10-30 concurrent requests:
- `alias-glm-huge`: 95% errors (285/300) on 300-sample benchmark
- `alias-huge`: 96.7% errors (290/300)
- `alias-apertus`: 96.7% errors (290/300)

**Pattern**: First 10-15 requests succeed, then 429 errors dominate.

#### 1a. 502 Proxy Error (2026-07-18)

When running 300-sample DBBench benchmark against `alias-glm-huge`:
- **249/300 samples (83%) failed with 502 Proxy Error**
- Error: `502 Server Error: Proxy Error for url: https://api.helmholtz-blablador.fz-juelich.de/v1/chat/completions`
- The proxy server at Helmholtz fails under sustained load (not just 429 rate limiting)
- This is a **different failure mode** from 429 — the proxy itself is overloaded
- **Impact**: Even with reduced concurrency (3 workers), the proxy fails
- **Verdict**: Helmholtz Blablador endpoint is **unreliable for batch benchmarking** — use `aip-best` (141.33.165.84:8000) instead

#### 2. Output Format Incompatibility

Some models return incompatible response structures:

**`alias-large` (Qwen3.5-122B)**:
```json
{
  "choices": [{
    "message": {
      "content": null,
      "reasoning": "Thinking Process: ... ```sql ... ```"
    }
  }]
}
```
- SQL is embedded in `reasoning` field, not `content`
- Output includes verbose thinking process, not clean SQL
- **Verdict**: Wrong format for DBBench SQL extraction

**`alias-qwen36-35b` (Qwen3.6-35B)**:
```json
{
  "choices": [{
    "message": {
      "content": null,
      "reasoning": "Here's a thinking process: ..."
    }
  }]
}
```
- Same model as `aip-best` but Helmholtz returns `content: None`
- All output in `reasoning` field
- **Verdict**: Incompatible with standard parser

**`alias-glm-huge` (GLM-5.2)**:
- Returns both `content` and `reasoning` fields
- SQL extraction works from either field
- **Issue**: Rate limiting prevents full benchmark

#### 3. Speed vs Reliability Tradeoff

| Model | Speed | Reliability |
|-------|-------|-------------|
| `alias-huge` | 0.25s | 3.3% |
| `alias-glm-huge` | 0.96s | 5% |
| `alias-apertus` | 0.06s | 3.3% |
| `aip-best` | 10.11s | 100% |

**Insight**: Helmholtz models are 10-40x faster but unusable due to rate limits.

## Available Models

See `references/helmholtz_available_models.md` for full list.

Key aliases:
- `alias-apertus` → Apertus-8B-Instruct-2509
- `alias-eve` → EVE-Instruct (Earth Observation)
- `alias-fast` → MiniMax-M2.7
- `alias-huge` → MiniMax-M2.7
- `alias-large` → Qwen3.5-122B-A10B-FP8
- `alias-code` → Qwen3-Coder-Next-FP8
- `alias-qwen36-35b` → Qwen3.6-35B-A3B-FP8
- `alias-glm-huge` → GLM-5.2-AWQ-INT4
- `alias-qwen-huge` → Qwen3.5-397B-A17B

## Testing Checklist

Before using a new Helmholtz model for benchmarks:

1. **Single-sample test**: Verify SQL generation works
   ```bash
   curl -s -X POST "https://api.helmholtz-blablador.fz-juelich.de/v1/chat/completions" \
     -H "Authorization: Bearer YOUR_KEY" \
     -d '{"model": "alias-X", "messages": [{"role": "user", "content": "SELECT 1"}]}'
   ```

2. **Check output format**:
   - Is `content` field populated? (not `None`)
   - Is SQL in ```sql code block?
   - Is `reasoning` field present? (some models put output there)

3. **Rate limit test**: Run 10-20 samples concurrently
   - Watch for 429 errors
   - If rate limited, model is unsuitable for full benchmarks

4. **Full benchmark**: Only proceed if:
   - No rate limits on 20+ samples
   - 100% SQL extraction success
   - Output format is compatible

## Recommendation

**Use `aip-best` (Qwen3.6-35B-A3B) for AgentBench benchmarks.**

Helmholtz endpoints are:
- ❌ Severely rate-limited (~10 concurrent requests max)
- ❌ Incompatible output formats for most models
- ❌ Unsuitable for production workloads

**When to use Helmholtz**:
- Quick single-sample tests
- Models not available elsewhere (e.g., GLM-5.2, EVE-Instruct)
- Non-benchmark tasks with low concurrency

## Scripts

- `scripts/helmholtz_test_single.py`: Quick single-sample test
- `scripts/helmholtz_rate_limit_test.py`: Rate limit probe (10 samples)

## References

- [Helmholtz Blablador API Docs](https://api.helmholtz-blablador.fz-juelich.de/docs) (if available)
- Session log: 2026-07-14 multi-model DBBench benchmark
