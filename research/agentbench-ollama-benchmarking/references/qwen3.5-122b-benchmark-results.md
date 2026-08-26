# qwen3.5:122b-a10b DBBench Benchmark Results

**Date**: 2026-07-16  
**Model**: `qwen3.5:122b-a10b` (122B parameters)  
**Size**: 81GB (97GB RAM used)  
**Endpoint**: Ollama (`http://localhost:11434`)

## Summary

| Metric | Value |
|--------|-------|
| **Samples** | 50 |
| **Success** | **50/50** |
| **Success Rate** | **100.0%** |
| **Total Time** | 1135.1s (18.9 min) |
| **Avg Time/Sample** | **22.70s** |

## Key Findings

### Perfect Accuracy
- **First model to achieve 100%** on DBBench (50/50 SQL queries)
- **Marginal improvement** over Llama-3.2-3B (99.5% → 100%, only 0.5% gap)

### Performance Trade-offs
- **Speed**: 22.70s/sample (7.6x slower than Llama-3.2-3B at 2.98s)
- **Memory**: 97GB RAM (42x larger than Llama-3.2-3B at 1.9GB)
- **Practicality**: 50 samples in 18.9 min vs 2.5 min for Llama-3.2-3B

### Why 3B beats 122B for Production
| Factor | Llama-3.2-3B | qwen3.5:122b | Delta |
|--------|--------------|--------------|-------|
| **DBBench** | 99.5% | 100% | +0.5% |
| **Speed** | 2.98s | 22.70s | 7.6x slower |
| **Memory** | 1.9GB | 81GB | 42x larger |
| **100 samples** | ~5 min | ~38 min | 7.6x longer |

### Conclusion
While `qwen3.5:122b-a10b` achieves perfect accuracy, the **7.6x speed penalty** and **42x memory cost** make it impractical for most production use cases. The **0.5% accuracy gain** (99.5% → 100%) does not justify the massive resource overhead.

**Recommendation**: Use **Llama-3.2-3B** for production (99.5% is "good enough" for most applications). Reserve `qwen3.5:122b` for maximum-accuracy experiments where speed doesn't matter.

## Benchmark Script
```bash
cd /tmp && ~/.hermes/hermes-agent/venv/bin/python qwen122_dbbench.py
```

Results saved to: `/tmp/qwen122_dbbench_results.json`

## Model Loading Notes
- **Initial load time**: ~1 hour (16% → 100%)
- **RAM usage**: 97GB peak (81GB model + overhead)
- **GPU utilization**: 84% GPU, 16% CPU during inference
- **Context length**: 262144 tokens (max)

## Comparison with Other Models

| Model | Size | DBBench | Speed | Verdict |
|-------|------|---------|-------|---------|
| **Llama-3.2-3B** | 1.9GB | 99.5% | 2.98s | ✅ **Best overall** |
| **qwen3.5:122b** | 81GB | 100% | 22.70s | ⚠️ Perfect but slow |
| **Teuken-7B** | 14GB | 99.0% | 4.81s | Good SQL, weak reasoning |
| **aip-best (LiteLLM)** | 35B | 86.0% | 1.36s | ❌ Broken API format |

## Session Notes
- **Benchmark run time**: ~19 min for 50 samples
- **No errors or timeouts** during execution
- **Consistent performance**: 22.7s/sample throughout (no degradation)
- **Output format**: Correctly generates ```sql code blocks
- **Parsing**: 100% success rate with standard SQL extraction logic
