# Teuken-7B Benchmark Results (Full AgentBench Suite)

**Date**: 2026-07-16  
**Model**: `mradermacher/Teuken-7B-instruct-v0.6.f16.gguf` (14GB)  
**Server**: llama.cpp (`/tmp/llama.cpp/build/bin/llama-server -m Teuken-7B-instruct-v0.6.f16.gguf -c 2048 --port 8080 -ngl 99`)  
**Inference Speed**: ~18 tokens/sec (GPU-accelerated)

## Results Summary

| Benchmark | Success | Rate | Time | Avg/s |
|-----------|---------|------|------|-------|
| **DBBench** (SQL) | 99/100 | **99.0%** | 507.4s | 5.07s |
| **KnowledgeGraph** | 49/50 | **98.0%** | 67.3s | 1.35s |
| **OS Interaction** | 15/26 | **57.7%** | 107.0s | 4.11s |
| **Lateral Thinking** | 17/30 | **56.7%** | 308.8s | 10.29s |
| **TOTAL** | **180/206** | **87.4%** | **990.4s** | **4.81s** |

## Comparison with Llama-3.2-3B

| Metric | Teuken-7B | Llama-3.2-3B | Delta |
|--------|-----------|--------------|-------|
| **Overall Success** | 87.4% | 99.5% | -12.1% |
| **Avg Time** | 4.81s | 2.98s | +61% slower |
| **Model Size** | 14GB | 1.9GB | 7.4x larger |
| **DBBench** | 99.0% | 99.5% | -0.5% |
| **KnowledgeGraph** | 98.0% | 100% | -2.0% |
| **OS Interaction** | 57.7% | 100% | **-42.3%** |
| **Lateral Thinking** | 56.7% | 100% | **-43.3%** |

## Key Findings

### Strengths
- **SQL Generation**: 99.0% (excellent, nearly matches Llama-3.2-3B)
- **Knowledge Retrieval**: 98.0% (very good)

### Weaknesses
- **OS Commands**: 57.7% (very poor vs 100%)
- **Reasoning Tasks**: 56.7% (very poor vs 100%)
- **Speed**: 1.6x slower than Llama-3.2-3B
- **Memory**: 7.4x larger than Llama-3.2-3B

### Conclusion
**Teuken-7B offers no advantage** over Llama-3.2-3B:
- ❌ 12% less accurate overall
- ❌ 1.6x slower
- ❌ 7.4x larger memory footprint
- ✅ Only advantage: slightly better at some edge-case SQL queries (negligible)

**Recommendation**: Stick with **Llama-3.2-3B** for all workloads.

## Benchmark Script
```bash
cd /tmp && ~/.hermes/hermes-agent/venv/bin/python teuken_agentbench_full.py
```

Results saved to: `/tmp/teuken_agentbench_full.json`

## Failure Analysis

### OS Interaction Failures (57.7%)
Model struggles with:
- Command syntax variations
- Pipe/redirection operators
- Complex shell constructs

Example failure:
- **Question**: "List all Python files in current directory"
- **Expected**: `find . -name "*.py"` or `ls *.py`
- **Actual**: `list python files` (invalid command)

### Lateral Thinking Failures (56.7%)
Model fails multi-step reasoning:
- **Question**: "If a bat and ball cost $1.10, and the bat costs $1.00 more than the ball, how much does the ball cost?"
- **Expected**: `0.05`
- **Actual**: `0.10` (classic bat/ball cognitive bias error)

## Inference Performance
- **Prompt Processing**: ~367 tokens/sec (very fast)
- **Generation**: ~18 tokens/sec (moderate)
- **Total Latency**: 5-10s/sample (depends on output length)

## Model Details
- **Base**: Teuken-7B-instruct-v0.6
- **Quantization**: F16 (full precision, no quantization)
- **Context**: 2048 tokens
- **CUDA**: Full GPU offload (`-ngl 99`)

## References
- Session 2026-07-16: Full benchmark execution
- Plot: `/tmp/model_comparison_bars.png`
- Data: `/tmp/teuken_agentbench_full.json`
