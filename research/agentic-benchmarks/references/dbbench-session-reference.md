# DBBench SQL Generation Benchmark — Session Findings (2026-07-25)

## Endpoint comparison results (300 samples each, dbbench-std)

| Endpoint | SQL Rate | Avg Time | Median | Max Time | Errors | Total Time |
|---|---|---|---|---|---|---|
| litellm.kube.aip.de | 93.3% (280/300) | 5.3s | — | — | 0 | 26.7 min |
| 141.33.165.84:8000 (v1: 300s timeout, 4096 tokens) | 29.3% (88/300) | 14.5s | 9.8s | 179.4s | 3 | 72.5 min |
| 141.33.165.84:8000 (v2: 600s timeout, 8192 tokens) | 27.7% (83/300) | 14.7s | 8.7s | 345.5s | 2 | 73.7 min |
| aip-best (localhost Ollama) | 92.7% (278/300) | 4.9s | 2.8s | 32.1s | 0 | 24.5 min |

## Key findings

### Increasing timeout/tokens does NOT improve SQL rate
v2 used 600s timeout + 8192 max_tokens (up from 300s + 4096). SQL rate went *down* from 29.3% to 27.7%. Root cause: not truncation or timeout — model/quantization/server config differences between endpoints.

### SQL rate varies by sample quartile (v2)
| Quartile | Samples | SQL Rate |
|---|---|---|
| Q1 (1-75) | 74 completed | 48.6% |
| Q2 (76-150) | 75 completed | 14.7% |
| Q3 (151-225) | 74 completed | 12.2% |
| Q4 (226-300) | 75 completed | 36.0% |

Same pattern in v1. DBBench dataset has harder SQL queries in the middle.

### Configuration details
- Model: aip-best (Qwen3.6-35B, Q5_K quantization)
- Context window: 1,048,576 tokens
- API: http://141.33.165.84:8000/v1/chat/completions (OpenAI-compatible)
- Uses `reasoning` field instead of `content` for output
- DBBench controller: http://localhost:5020
- 10 Docker workers: agentbench-fc-dbbench-std-{1..10}

### Pitfall: "API FAIL (no content)"
The llama.cpp endpoint occasionally returns responses with empty content. Always check both `content` and `reasoning` fields.

### Pitfall: comma-separated arguments in shell
When passing comma-separated JSON paths and labels to comparison scripts, use proper quoting to avoid shell splitting.

### Plotting
Requires `/home/hermes/shboost-hvplot-env/bin/python3` for numpy/matplotlib.
```bash
/home/hermes/shboost-hvplot-env/bin/python3 scripts/generate_dbbench_plot.py results/aip-best-141-33-165-84-v2.json
/home/hermes/shboost-hvplot-env/bin/python3 scripts/generate_dbbench_comparison.py "results/aip-best-141-33-165-84-v2.json,results/litellm-kube-aip-de.json,results/aip-best.json" --labels "aip-best (new),aip-best (litellm),aip-best (ollama)" results/comparison_aip_best_endpoints.png
```