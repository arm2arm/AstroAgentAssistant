# Helmholtz Blablador Available Models

## Model List

Retrieved from `https://api.helmholtz-blablador.fz-juelich.de/v1/models`:

| ID Alias | Model Name | Size | Description |
|----------|------------|------|-------------|
| `alias-apertus` | Apertus-8B-Instruct-2509 | 8B | Swiss model from Sep 2025 |
| `alias-eve` | EVE-Instruct | - | Earth Observation & Earth Science |
| `alias-fast` | MiniMax-M2.7 | 2.7B | Best model as of Apr 2026 |
| `alias-huge` | MiniMax-M2.7 | 2.7B | Same as alias-fast |
| `alias-large` | Qwen3.5-122B-A10B-FP8 | 122B | General purpose large model |
| `alias-code` | Qwen3-Coder-Next-FP8 | - | Code generation |
| `alias-embeddings` | Qwen3-Embedding-8B | 8B | Embeddings only |
| `alias-qwen36-35b` | Qwen3.6-35B-A3B-FP8 | 35B | Same model as aip-best |
| `alias-glm-huge` | GLM-5.2-AWQ-INT4 | - | GLM model |
| `alias-deepseek-v4-flash` | DeepSeek-V4-Flash | - | DeepSeek model |
| `alias-qwen-huge` | Qwen3.5-397B-A17B | 397B | Very large model |
| `hy-mt2-30b-fp8` | Hy-MT2-30B-A3B | 30B | Multilingual |
| `eve-instruct-4gpu` | EVE-Instruct | - | 4 GPU variant |

## Benchmark Results Summary

| Model | Alias | SQL Success | Rate Limit | Verdict |
|-------|-------|-------------|------------|---------|
| Apertus-8B | `alias-apertus` | ✅ Works | ❌ Yes (10 req) | Rate limited |
| Qwen3.5-122B | `alias-large` | ❌ Wrong format | ❌ Yes (10 req) | Incompatible |
| Qwen3.6-35B | `alias-qwen36-35b` | ❌ `content: None` | ❌ Yes (10 req) | Incompatible |
| GLM-5.2 | `alias-glm-huge` | ✅ Works | ❌ Yes (15 req) | Rate limited |
| MiniMax-M2.7 | `alias-huge` | ⚠️ Limited | ❌ Yes (10 req) | Rate limited |

## Notes

- All models hit **429 rate limit** after ~10-15 concurrent requests
- Models with `reasoning` field output (Qwen3.5, Qwen3.6) are incompatible with DBBench SQL extraction
- Only `alias-apertus` and `alias-glm-huge` generate proper SQL code blocks
- For production use, prefer `aip-best` endpoint (no rate limits, same model as `alias-qwen36-35b`)

## API Key

```
glpat-<YOUR_TOKEN>
```

**Note**: This key is for Helmholtz Blablador endpoint only. Do not share.
