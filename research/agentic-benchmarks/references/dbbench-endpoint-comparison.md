# DBBench: aip-best endpoint comparison findings

## Endpoints compared (300 samples each, dbbench-std)

| Endpoint | SQL Rate | Avg Time | Max Time | Errors |
|---|---|---|---|---|
| litellm.kube.aip.de | 93.3% (280) | 5.3s | — | 0 |
| 141.33.165.84:8000 (v1: 300s/4096tok) | 29.3% (88) | 14.5s | 179.4s | 3 |
| 141.33.165.84:8000 (v2: 600s/8192tok) | 27.7% (83) | 14.7s | 345.5s | 2 |
| aip-best (localhost Ollama) | 92.7% (278) | 4.9s | 32.1s | 0 |

## Key lesson: bigger timeout/tokens does NOT fix low SQL rate

v2 used 600s timeout + 8192 max_tokens (up from 300s + 4096). SQL rate went *down* from 29.3% to 27.7%.

Root cause: not truncation or timeout — model/quantization/server config differences between endpoints.