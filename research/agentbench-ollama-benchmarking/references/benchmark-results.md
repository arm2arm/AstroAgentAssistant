# AgentBench Benchmark Results - Session 2026-07-15

## Model Comparison Summary

### `llama3.2:3b` (Recommended)
- **Size**: 1.9GB
- **Hardware**: CPU/GPU (no saturation)
- **DBBench**: 96-100% success (3 runs: 100%, 98%, 100%)
- **Knowledge Graph**: 100% (50/50)
- **OS Interaction**: 100% (26/26)
- **Lateral Thinking**: 100% (30/30)
- **Speed**: 1-10s/sample (avg 7.2s)
- **Concurrency**: 5 workers OK
- **Total time**: ~10 minutes for full suite

### `qwen3.6:latest` (Not Recommended)
- **Size**: 34GB
- **Hardware**: 100% GPU saturation
- **DBBench**: ~50% (timeout-prone)
- **Speed**: ~23s/sample
- **Concurrency**: 1 worker only
- **Total time**: 2+ hours for 300 samples
- **Issues**: Frequent timeouts, GPU saturation, impractical for batch

### `aip-best` API (Degraded)
- **Endpoint**: `http://141.33.165.84:8000/v1`
- **Status**: Down (HTTP 404) / Overloaded
- **Success rate**: 11.9% (when accessible)
- **Speed**: 2.2s/sample
- **Issues**: Unreliable, severely degraded performance

## Key Findings

1. **`llama3.2:3b` is optimal** for AgentBench on this hardware
   - Near-perfect accuracy (98-100%)
   - Fast inference (1-10s)
   - No resource constraints
   - Free (local)

2. **Larger models are impractical** for batch benchmarking
   - `qwen3.6:latest` takes 10-30x longer
   - GPU saturation prevents concurrency
   - Timeout-prone due to long inference times

3. **External APIs may be unreliable**
   - `aip-best` endpoint down/degraded
   - Rate limiting on Helmholtz endpoints
   - Local models provide consistent results

## Reproduction Commands

```bash
# Full benchmark suite
cd /tmp && ~/.hermes/hermes-agent/venv/bin/python agentbench_ollama_llama32.py

# DBBench only (300 samples)
cd /tmp && ~/.hermes/hermes-agent/venv/bin/python dbbench_qwen36.py

# Check Ollama status
ollama ps
curl -s http://localhost:11434/api/tags | python3 -m json.tool
```

## Results Locations

- `llama3.2:3b`: `/tmp/agentbench_ollama_llama32/`
- `qwen3.6:latest`: `/tmp/agentbench_ollama_qwen36/`
- `qwen3.6:latest` (DBBench): `/tmp/dbbench_qwen36/`

## Pitfalls Documented

1. **Excel column names**: Use `story`/`answer`, not `question`/`clue`
2. **Code block extraction**: Handle both ` ```sql ` and ` ``` ` formats
3. **Concurrency limits**: Large models need 1 worker only
4. **Timeout settings**: 120s for small models, 300s+ for large models
5. **System prompts**: Required for consistent code block output
