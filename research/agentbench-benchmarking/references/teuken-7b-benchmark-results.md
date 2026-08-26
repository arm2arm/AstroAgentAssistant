# Teuken-7B Benchmark Results

**Date:** 2026-07-15  
**Model:** Teuken-7B-instruct-v0.6.f16 (14GB GGUF)  
**Serving:** llama.cpp server (http://localhost:8080/v1)  
**Total Samples:** 206

## Results Summary

| Benchmark | Samples | Success | Rate | Time | Avg/s |
|-----------|---------|---------|------|------|-------|
| **DBBench** (SQL) | 100 | 99 | **99.0%** | 507.4s | 5.07s |
| **KnowledgeGraph** | 50 | 49 | **98.0%** | 67.3s | 1.35s |
| **OS Interaction** | 26 | 15 | **57.7%** | 107.0s | 4.11s |
| **Lateral Thinking** | 30 | 17 | **56.7%** | 308.8s | 10.29s |
| **TOTAL** | **206** | **180** | **87.4%** | **990.4s** | **4.81s** |

## Key Findings

### Strengths
- **Structured tasks excel**: SQL (99%), Knowledge Graph (98%)
- **High accuracy on deterministic outputs**: Code generation, tool calling
- **Comparable to Llama-3.2-3B** on structured tasks (99% vs 99.5%)

### Weaknesses
- **Reasoning tasks**: 56.7% on Lateral Thinking (vs 100% for Llama-3.2-3B)
- **OS commands**: 57.7% success (vs 100% for Llama-3.2-3B)
- **Slow inference**: 4.81s/sample vs 2.98s for Llama-3.2-3B (1.6x slower)
- **Large memory footprint**: 14GB vs 1.9GB (7.4x larger)

## Comparison with Other Models

| Model | Size | DBBench | KG | OS | LTP | Overall | Speed | Verdict |
|-------|------|---------|----|----|----|---------|-------|---------|
| **Llama-3.2-3B** | 1.9GB | **99.5%** | **100%** | **100%** | **100%** | **99.5%** | 2.98s | ✅ **BEST** |
| **Teuken-7B** | 14GB | 99.0% | 98.0% | 57.7% | 56.7% | **87.4%** | 4.81s | ⚠️ Good SQL, weak reasoning |
| **aip-best (LiteLLM)** | 35B | 86.0% | 80.0% | 88.5% | 20.0% | **75.2%** | 1.36s | ⚠️ Fast but inconsistent |

## Technical Notes

### Serving Setup
```bash
# Build llama.cpp with CUDA support
cd /tmp/llama.cpp && mkdir build && cd build
cmake .. -DGGML_CUDA=ON && make -j$(nproc) llama-server llama-cli

# Download GGUF model
cd ~/models
hf download mradermacher/Teuken-7B-instruct-v0.6-GGUF --include "*f16.gguf" --local-dir .

# Serve model
/tmp/llama.cpp/build/bin/llama-server \
  -m ~/models/Teuken-7B-instruct-v0.6.f16.gguf \
  -c 2048 --port 8080 --host 0.0.0.0 -ngl 99
```

### Performance Characteristics
- **Token generation**: ~18 tokens/sec (vs ~100+ for Llama-3.2-3B)
- **Context window**: 2048 tokens (sufficient for most tasks)
- **GPU offload**: 99 layers (full GPU utilization)
- **Batch processing**: Single-slot only (no concurrency due to memory)

## Recommendations

### When to Use Teuken-7B
- ✅ **SQL generation** (99% accuracy, comparable to Llama-3.2-3B)
- ✅ **Knowledge retrieval** (98% accuracy)
- ✅ **When larger context needed** (7B vs 3B parameter model)

### When to Avoid
- ❌ **Reasoning tasks** (56.7% vs 100% for Llama-3.2-3B)
- ❌ **OS/command generation** (57.7% vs 100%)
- ❌ **Memory-constrained systems** (14GB vs 1.9GB)
- ❌ **High-throughput needs** (4.81s vs 2.98s per sample)

### Verdict
**Llama-3.2-3B remains the optimal choice** for AgentBench workloads:
- 12% higher overall accuracy (99.5% vs 87.4%)
- 1.6x faster inference
- 7.4x smaller memory footprint
- Better reasoning capabilities

Teuken-7B offers no clear advantage over Llama-3.2-3B for this use case.

## Benchmark Scripts
- `/tmp/teuken_agentbench_full.py` - Full 206-sample benchmark suite
- `/tmp/teuken_agentbench_partial.py` - Partial 100-sample test

## Related Files
- `/tmp/teuken_agentbench_full.json` - Complete results JSON
- `/tmp/teuken_full_bench.log` - Execution log
