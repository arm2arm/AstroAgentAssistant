# GAIA Benchmark — Running Against Non-Tool-Calling Endpoints

## Key Finding: Reasoning Field Instead of Content

The `aip-best` model (via `141.33.165.84:8000/v1`) does NOT return model output in the standard `content` field. Instead:
- `message.content` is `null` when the model generates reasoning
- `message.reasoning` contains the full chain-of-thought (10k+ chars)
- Answer is embedded in the reasoning trace, not standalone

**This is a provider-specific quirk** — any OpenAI-compatible endpoint that uses structured reasoning stores output this way.

## Prompt Template

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant. Think step by step. At the end, state: 'Answer: [your answer]'"},
    {"role": "user", "content": question},
]
```

The explicit "Answer:" marker dramatically improves parse success rate.

## Max Tokens

- **512 tokens**: Model reasoning gets truncated before answering. Score: 0%.
- **2048 tokens**: Still truncated in many cases. Score: 0%.
- **8192 tokens**: Gives model room to reason + state answer. Score: ~40% on 10 samples.
- **Recommendation**: Always use 8192+ for reasoning-heavy benchmarks.

## Answer Extraction Patterns (priority order)

```python
# 1. Explicit Answer: marker
r'Answer:\s*(.+?)(?:\n|$)'
r'answer:\s*(.+?)(?:\n|$)'

# 2. Conclusion phrases
r'(?:Therefore|Thus|Hence|So|In conclusion)[,.]?\s*(.+?)(?:\n|$)'

# 3. Last bracketed content (last 500 chars of reasoning)
r'\*\*(.+?)\*\*'  # markdown bold
r'\`(.+?)\`'      # backticks

# 4. Last substantial paragraph (not starting with "1." or "Step")
```

## Evaluation Matching

GAIA answers are typically short strings (numbers, single words, dates). Use:
1. **Exact match** (case-insensitive)
2. **Substring match** (answer within response or vice versa)
3. **Numeric tolerance** (within 1% for numbers)
4. **Year match** (4-digit years)

## Sample Results (aip-best, text-only mode)

| Run | Samples | Tokens | Accuracy | Notes |
|-----|---------|--------|----------|-------|
| Pilot | 10 | 512 | 0% | Content truncated to null |
| Pilot | 10 | 2048 | 0% | 9/10 responses empty |
| Pilot | 10 | 8192 | 40% | Reasoning parser working |
| Full | 50 | 8192 | TBD | See `scripts/gaia_full_benchmark_runner.py` |

Correct on: pure reasoning, trivia, math, code syntax.
Failed on: questions requiring web search, file access, or real-time data (expected — no tool use).

## Running Long Benchmarks: Progress Saving

The GAIA validation set has 165 samples; each takes 30-60s (total 2-3 hours). Use `scripts/gaia_full_benchmark_runner.py` which:
- Saves progress every 10 samples to `/tmp/gaia_progress.json` (resumable)
- Auto-generates 3 plots on completion (`gaia_full_accuracy.png`, `gaia_full_per_sample.png`, `gaia_full_times.png`)
- Configuration via env vars: `GAIA_BASE_URL`, `GAIA_MODEL`, `GAIA_MAX_TOKENS`, `HF_TOKEN`

## Important Limitation

GAIA was designed to test **agentic** capability — the model must use tools (web browser, bash, python) to solve tasks. Running it in text-only mode measures **pure knowledge/reasoning** ability, not agentic ability. A 40% score is reasonable for a model without tool calling on text-only GAIA.

For true GAIA evaluation, you need:
- Docker sandbox environments (for bash/python isolation)
- Inspect Evals with `react` agent and tool definitions
- Or a custom tool executor wrapper