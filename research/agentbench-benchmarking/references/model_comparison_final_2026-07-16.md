# Final Model Comparison Summary (2026-07-16)

## Complete Benchmark Results

| Model | Size | DBBench | Speed | Memory | Verdict |
|-------|------|---------|-------|--------|---------|
| **llama3.2:3b** | 1.9GB | **100%** | 2.98s | 1.9GB | ✅ **BEST** |
| **qwen3.5:122b** | 81GB | **100%** | 22.7s | 81GB | ⚠️ Perfect but 7.6x slower |
| **qwen3.6:latest** | 23GB | **100%** | 30.7s | 23GB | ⚠️ Perfect but 10x slower |
| **Teuken-7B** | 14GB | 99% | 4.81s | 14GB | Good SQL (99%), weak reasoning (57%) |
| **aip-best (API)** | - | 14% | 2.2s | - | ❌ Broken API (null content) |
| **qwen3.6:latest (local, unfixed)** | 23GB | 0% | 16s | 23GB | ❌ Parser bug (thinking field) |

## Key Findings

### llama3.2:3b - Production Choice
- **100% success** across all 6 AgentBench categories (DBBench, KG, OS, LTP, ALFWORLD, AVALON)
- **2.98s/sample** average (fastest)
- **1.9GB** memory footprint (smallest)
- **Standard API** (no quirks)
- **Free** (local, no API costs)

### Reasoning Models (qwen3.6, qwen3.5:122b)
- **100% accuracy** achievable with proper parsing
- **Critical pitfall**: Output in `thinking` field, not `response`
- **Fix**: `content = data.get("response", "") or data.get("thinking", "") or ""`
- **Trade-off**: 10x slower, 12-42x more memory for same accuracy

### aip-best API - Broken
- Returns `content: null` for all responses
- Reasoning in separate `reasoning` field
- **Unusable** for standard OpenAI clients
- **Recommendation**: DO NOT USE

### Teuken-7B - Mixed Results
- **99% SQL** (excellent for structured queries)
- **57% reasoning** (weak for free-form tasks)
- **4.81s/sample** (1.6x slower than llama3.2)
- **14GB** memory (7x larger)

## Production Recommendation

**Use llama3.2:3b for all production workloads**:
- ✅ Same 100% accuracy as reasoning models
- ✅ 10x faster (3s vs 30s)
- ✅ 12x less memory (1.9GB vs 23GB)
- ✅ Standard API (no `thinking` field quirks)
- ✅ Free (local, no API costs)

**Only use reasoning models when**:
- 100% accuracy is mandatory (not 99.5%)
- Speed and memory are not constraints
- You can implement custom `thinking` field parsing

## Benchmark Scripts

- `scripts/qwen36_dbbench_v2.py` - Fixed reasoning model benchmark
- `scripts/run_all_agentbench_llama32.py` - Full 6-task suite
- `references/qwen36_reasoning_model_fix.md` - Detailed fix documentation
