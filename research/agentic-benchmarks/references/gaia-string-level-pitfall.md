# GAIA Benchmark Pitfalls — Session Reference (2026-07-20)

## Critical Bug: String vs Integer Level Comparison

**Symptom**: Benchmark runs selected 0 samples, crashed during plotting with `ValueError: cannot convert float NaN to integer`.

**Root Cause**: GAIA dataset `Level` field is a **string** (`"1"`, `"2"`, `"3"`), not an integer. Python comparisons `if s["Level"] == 1` silently return `False` for all samples, selecting 0 items.

**Debugging path**:
1. Output showed `Selected: 0 samples` — immediately suspicious
2. Quick check: `ds[i]["Level"]` → `'2'` (string), `type` → `<class 'str'>`
3. Code had: `level1 = [i for i in range(available) if dataset[i]["Level"] == 1]`
4. Fix: Change to string comparison: `== "1"`, `== "2"`, `== "3"`

**Files affected**: All GAIA benchmark scripts and `agentic-benchmarks` skill.

**Fix applied**:
- `agentic-benchmarks/scripts/gaia_bench.py`: Updated `generate_plots()` to use string keys for level filtering
- `agentic-benchmarks/SKILL.md`: Added pitfall documentation

**Runtime guard to add**:
```python
if len(selected) == 0:
    print("ERROR: 0 samples selected! Check if Level field is string vs int.")
    print(f"  Sample level repr: {repr(dataset[0]['Level'])}")
    sys.exit(1)
```

**Never ignore this**: A silent 0-sample selection wastes time (each sample takes 2+ min) and crashes at the plotting stage with confusing NaN errors.

## Benchmark Runtime Estimates

| Split | Samples | Est. Time (2 min/sample) | Practical? |
|-------|---------|--------------------------|------------|
| Validation | 165 | ~5.5 hours | No |
| 50-sample stratified | 50 | ~1.7 hours | Yes |
| 10-sample quick | 10 | ~33 min | Yes (debug) |

Recommend: 50-sample stratified run (15 L1, 30 L2, 5 L3) for meaningful results.
