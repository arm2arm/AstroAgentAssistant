# AgentBench DBBench Performance Baselines

## Model Comparison Summary

### llama3.2:3b (Local Ollama)
- **DBBench (SQL):** 96-100% (avg 98%)
- **Speed:** 1.5-10s per sample (depends on concurrency)
- **Memory:** 1.9GB
- **Verdict:** ✅ **OPTIMAL** for local workloads

### aip-best (Various Endpoints — Performance Varies Dramatically)

| Endpoint | SQL Rate | Avg Time | Total Time | Verdict |
|----------|----------|----------|------------|---------|
| litellm.kube.aip.de | 93.3% | 5.3s | 26.7 min | ✅ Good |
| 141.33.165.84:8000 (Q5_K) | 29.3% | 14.5s | 72.5 min | ❌ Degraded |

**Key finding:** The aip-best model served at `141.33.165.84:8000` (llama.cpp Q5_K) performs dramatically worse than the same model via `litellm.kube.aip.de`. The 141.33.165.84 endpoint produces 70% non-SQL output even on the identical 300-sample DBBench task. Likely causes: different quantization level, temperature setting, or system prompt handling.

### qwen3.6:latest (Local Ollama)
- **DBBench (SQL):** 3%
- **Issue:** Model outputs raw text without ```sql code blocks
- **Speed:** 28s per sample
- **Memory:** 22.3GB
- **Verdict:** ❌ **FAIL** - format incompatible

### deepseek-r1:70b (Local Ollama)
- **DBBench:** Not tested (memory error)
- **Issue:** Requires 50.5GB RAM, only 46GB available
- **Speed:** ~27s/sample (if it runs via swap)
- **Memory:** 50.5GB
- **Verdict:** ❌ **Impractical** - exceeds hardware

## DBBench Runner Script (Production-Ready)

Always use the robust runner with timeout handling, checkpointing, and error recovery:

```python
#!/usr/bin/env python3
"""DBBench runner with checkpointing — never lose work to a crash."""

import requests, json, time, re, os

API_URL = "http://YOUR_HOST:8000/v1/chat/completions"
MODEL = "your-model"
CONTROLLER = "http://localhost:5020"
N = 300
OUTPUT_DIR = "/home/hermes/projects/dbbench-benchmarks/results"
TIMEOUT = 300  # 5 min — some DBBench samples are very complex

def call_llm(messages, tools=None):
    payload = {"model": MODEL, "messages": messages,
               "stream": False, "temperature": 0.1, "max_tokens": 4096}
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    resp = requests.post(API_URL, json=payload,
                         headers={"Content-Type": "application/json"}, timeout=TIMEOUT)
    if resp.status_code != 200:
        return None
    msg = resp.json().get("choices", [{}])[0].get("message", {})
    content = msg.get("content") or msg.get("reasoning", "")
    return content if content else None

def is_sql(s):
    if "```" in s:
        for m in re.findall(r'```(?:sql)?\s*\n(.*?)```', s, re.DOTALL):
            if any(k in m.upper() for k in ['SELECT','FROM','WHERE','JOIN',
                                            'INSERT','UPDATE','DELETE','CREATE']):
                return True
    return any(k in s.upper() for k in ['SELECT ', 'FROM ', 'WHERE ', 'JOIN '])

def save_checkpoint(results, sql_n, err_n, total):
    """Save after every sample — prevents losing work to crashes."""
    times = [r["time_sec"] for r in results if r["status"] == "COMPLETED"]
    out = {"model": MODEL, "task": "dbbench-std", "n_samples": N,
           "elapsed_seconds": round(total, 2), "sql_count": sql_n,
           "sql_rate": round(sql_n/N*100, 1), "error_count": err_n,
           "avg_time_sec": round(total/N, 2),
           "min_time": round(min(times), 2) if times else None,
           "max_time": round(max(times), 2) if times else None,
           "median_time": round(sorted(times)[len(times)//2], 2) if times else None,
           "results": results}
    with open(os.path.join(OUTPUT_DIR, f"{MODEL}.json"), "w") as f:
        json.dump(out, f, indent=2)

def run_benchmark():
    results, t0, sql_n, err_n = [], time.time(), 0, 0
    for idx in range(N):
        t1 = time.time()
        try:
            r = requests.post(f"{CONTROLLER}/api/start_sample",
                              json={"name": "dbbench-std", "index": idx}, timeout=30)
            if r.status_code != 200:
                results.append({"index": idx, "status": "ERROR", "error": r.text[:200],
                                "rounds": 0, "time_sec": round(time.time()-t1, 2)})
                err_n += 1; save_checkpoint(results, sql_n, err_n, time.time()-t0); continue
            data = r.json()
            try:
                resp_text = call_llm(data.get("messages", []), data.get("tools", None))
            except requests.exceptions.ReadTimeout:
                results.append({"index": idx, "status": "ERROR", "error": "ReadTimeout",
                                "rounds": 1, "time_sec": round(time.time()-t1, 2)})
                err_n += 1; save_checkpoint(results, sql_n, err_n, time.time()-t0); continue
            if resp_text is None:
                results.append({"index": idx, "status": "ERROR", "rounds": 1,
                                "time_sec": round(time.time()-t1, 2)})
                err_n += 1; save_checkpoint(results, sql_n, err_n, time.time()-t0); continue
            has_sql = is_sql(resp_text)
            if has_sql: sql_n += 1
            try:
                requests.post(f"{CONTROLLER}/api/interact",
                              json={"session_id": idx,
                                    "agent_response": {"content": resp_text, "status": "CONTINUE"}},
                              timeout=TIMEOUT)
            except: pass
            results.append({"index": idx, "status": "COMPLETED", "has_sql": has_sql,
                            "rounds": 1, "time_sec": round(time.time()-t1, 2)})
            save_checkpoint(results, sql_n, err_n, time.time()-t0)
        except Exception as e:
            results.append({"index": idx, "status": "ERROR", "error": str(e)[:200],
                            "rounds": 0, "time_sec": round(time.time()-t1, 2)})
            err_n += 1; save_checkpoint(results, sql_n, err_n, time.time()-t0)
    print(f"Done: {time.time()-t0:.0f}s | SQL: {sql_n}/{N} ({sql_n/N*100:.0f}%) | Err: {err_n}")

if __name__ == "__main__":
    run_benchmark()
```

## SQL Extraction

```python
def extract_sql(content):
    if not content: return None
    if "```sql" in content:
        return content.split("```sql")[1].split("```")[0].strip()
    elif "```" in content:
        return content.split("```")[1].split("```")[0].strip()
    return None
```

## Known Pitfalls

### 1. Timeout Handling (Critical)
- DBBench has samples that can take 100-180s on quantized models or slower endpoints
- Default 180s timeout may be too short — use TIMEOUT=300
- Without try/except for `ReadTimeout`, a single timeout crashes the entire 300-sample run
- Sample 18 in the 141.33.165.84 run took 179s

### 2. Checkpointing (Critical)
- Save results after EVERY sample to a checkpoint JSON file
- If the process crashes or times out, results aren't lost
- Without checkpointing, a crash at sample 250 means redoing all 300

### 3. Endpoint Performance Variability (Discovered 2026-07-25)
- The same model (aip-best/Qwen3.6-35B) shows dramatically different SQL rates:
  - litellm.kube.aip.de: **93%** SQL rate, 5.3s avg
  - 141.33.165.84:8000: **29%** SQL rate, 14.5s avg (70% non-SQL output)
- Root cause: likely different quantization (Q5_K vs Q4_K), temperature, or system prompt
- **Always** verify endpoint performance with a quick 10-sample test before full 300-sample run

### 4. Python Environment
- System `python3` lacks numpy/matplotlib — use `/home/hermes/shboost-hvplot-env/bin/python3`
- The Hermes venv at `~/.hermes/hermes-agent/venv/` also lacks numpy/matplotlib
- Use the hvplot env for all plotting scripts

## Reproduction Commands

```bash
# Check DBBench controller + workers
curl -s http://localhost:5020/api/list_workers | python3 -m json.tool
docker ps --format '{{.Names}}' | grep agentbench-fc-dbbench

# Test API endpoint
curl -s -X POST "http://141.33.165.84:8000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{"model":"aip-best","messages":[{"role":"user","content":"Say hi"}]}'

# Run benchmark
python3 scripts/run_dbbench_aip_best.py 2>&1 | tee /tmp/dbbench_run.log

# Generate dashboard plot
/home/hermes/shboost-hvplot-env/bin/python3 \
  scripts/generate_dbbench_plot.py results/aip-best-141-33-165-84.json

# Generate comparison plot
/home/hermes/shboost-hvplot-env/bin/python3 \
  scripts/generate_dbbench_plot.py \
  --compare results/aip-best-141-33-165-84.json,results/litellm-kube-aip-de.json,results/aip-best.json \
  --labels "aip-best (141.33.165.84)","aip-best (litellm)","aip-best (Ollama)"
```

## Results Storage
- Base dir: `/home/hermes/projects/dbbench-benchmarks/results/`
- `<model>.json` — raw results, `<model>.png` — 8-panel dashboard
- `comparison_*.png` — multi-model comparison plots
- `<model>_checkpoint.json` — auto-saved checkpoint (per-sample)
