---
name: agentbench-dbbench-benchmark
description: Run AgentBench DBBench benchmark against LLMs and generate standardized comparison dashboard. Use when testing any model on DBBench (SQL generation task).
version: 1.0.0
created: 2026-07-21
---

# AgentBench DBBench Benchmark

Run standardized DBBench benchmark on AgentBench FC and generate comparison dashboard with identical plot style for all models.

## Prerequisites

1. **AgentBench repo** at `/tmp/AgentBench` (git clone if missing)
2. **Docker images** already built (agentbench-fc-dbbench-std)
3. **10 dbbench workers** running (containers `agentbench-fc-dbbench-std-1` through `agentbench-fc-dbbench-std-10`)
4. **LLM endpoint** reachable (API URL + model name)

## Setup

### 1. Start DBBench Workers

```bash
# Start 10 dbbench workers (320 total capacity)
for i in $(seq 1 10); do
    docker start agentbench-fc-dbbench-std-$i
done

# Verify workers registered
curl -s http://localhost:5020/api/list_workers | python3 -m json.tool
# Should show 'dbbench-std' with 10 workers
```

### 2. Verify API Endpoint

```bash
# Test API is reachable
curl -s -o /dev/null -w "%{http_code}" \
  -X POST "http://YOUR_HOST:8000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{"model":"test","messages":[{"role":"user","content":"hi"}]}'
# Expected: 401 or 404 (model not found) — NOT connection refused
```

## Running Benchmark

### Runner Script Template

Create runner script at `/tmp/run_dbbench_N.py`:

```python
#!/usr/bin/env python3
"""DBBench benchmark runner - single-turn SQL generation mode."""

import requests
import json
import time
import re

API_URL = "http://YOUR_HOST:8000/v1/chat/completions"  # Replace
MODEL = "your-model-name"                              # Replace
CONTROLLER = "http://localhost:5020"
N = 300                                                 # DBBench has 300 samples total

def call_llm(messages, tools=None):
    payload = {"model": MODEL, "messages": messages, "stream": False,
               "temperature": 0.1, "max_tokens": 4096}
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    resp = requests.post(API_URL, json=payload,
                         headers={"Authorization": "Bearer EMPTY",
                                      "Content-Type": "application/json"},
                         timeout=180)
    if resp.status_code != 200:
        return None
    msg = resp.json().get("choices", [{}])[0].get("message", {})
    return msg.get("content") or msg.get("reasoning", "")

def is_sql(s):
    """Check if response contains SQL in code blocks or inline."""
    if "```" in s:
        for m in re.findall(r'```(?:sql)?\s*\n(.*?)```', s, re.DOTALL):
            if any(k in m.upper() for k in ['SELECT', 'FROM', 'WHERE', 'JOIN',
                                            'INSERT', 'UPDATE', 'DELETE', 'CREATE']):
                return True
    return any(k in s.upper() for k in ['SELECT ', 'FROM ', 'WHERE ', 'JOIN '])

def run_benchmark():
    results = []
    t0 = time.time()
    sql_n = 0
    err_n = 0

    print(f"DBBench: {N} samples | Model: {MODEL} | Start: {time.strftime('%H:%M')}")
    print("=" * 70)

    for idx in range(N):
        t1 = time.time()

        # Start sample from controller
        r = requests.post(f"{CONTROLLER}/api/start_sample",
                          json={"name": "dbbench-std", "index": idx}, timeout=30)
        if r.status_code != 200:
            results.append({"index": idx, "status": "ERROR",
                            "error": r.text[:200], "rounds": 0,
                            "time_sec": time.time()-t1})
            err_n += 1
            continue

        data = r.json()
        msgs = data.get("messages", [])
        tools = data.get("tools", None)

        # Call LLM
        resp_text = call_llm(msgs, tools)
        if resp_text is None:
            results.append({"index": idx, "status": "ERROR", "rounds": 1,
                            "time_sec": time.time()-t1})
            err_n += 1
            continue

        has_sql = is_sql(resp_text)
        if has_sql:
            sql_n += 1

        # Submit to controller
        r2 = requests.post(f"{CONTROLLER}/api/interact",
                           json={"session_id": idx,
                                 "agent_response": {"content": resp_text,
                                                    "status": "CONTINUE"}},
                           timeout=180)

        t_total = time.time() - t1
        tag = "SQL" if has_sql else "NONE"
        print(f"[{idx+1}] {tag:4s} {t_total:.1f}s")

        results.append({"index": idx, "status": "COMPLETED",
                        "has_sql": has_sql, "rounds": 1,
                        "time_sec": round(t_total, 2)})

    total = time.time() - t0

    print("=" * 70)
    print(f"Done: {total:.1f}s | {N} samples | {err_n} errors")
    print(f"SQL: {sql_n}/{N} ({sql_n/N*100:.0f}%) | Avg: {total/N:.1f}s/sample")

    # Save JSON
    out = {"model": MODEL, "task": "dbbench-std", "n_samples": N,
           "elapsed_seconds": round(total, 2), "sql_count": sql_n,
           "sql_rate": round(sql_n/N*100, 1), "error_count": err_n,
           "avg_time_sec": round(total/N, 2), "results": results}
    out_path = f"/tmp/agentbench_dbbench_{N}.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Saved: {out_path}")

    return out

if __name__ == "__main__":
    run_benchmark()
```

### Run Command

```bash
python3 /tmp/run_dbbench_N.py 2>&1 | tee /tmp/dbbench_output.log
```

Expected duration: ~15-25 min for 300 samples (depends on model speed).

## Visualization (Exact Same Style)

After benchmark completes, generate the standardized dashboard:

```python
import re, json, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# Parse log
lines = open('/tmp/dbbench_output.log').readlines()
times, has_sql = [], []
for line in lines:
    m = re.match(r'\[(\d+)\]\s+(SQL|NONE)\s+([\d.]+)s', line.strip())
    if m:
        times.append(float(m.group(3)))
        has_sql.append(m.group(2) == 'SQL')

n = len(times)
sql_n = sum(has_sql)

# Read JSON for metadata
with open('/tmp/agentbench_dbbench_300.json') as f:
    data = json.load(f)

total_time = data['elapsed_seconds']
avg_time = total_time / n

# Create 8-panel figure (EXACT layout)
fig = plt.figure(figsize=(18, 12))
gs = gridspec.GridSpec(3, 4, figure=fig, hspace=0.35, wspace=0.3,
                       left=0.06, right=0.96, top=0.92, bottom=0.06)

# Panel 1: Time histogram (top, 2 cols)
ax1 = fig.add_subplot(gs[0, :2])
ax1.hist(times, bins=20, color='#4A90D9', edgecolor='white', linewidth=1.2, alpha=0.85)
ax1.axvline(np.mean(times), color='red', linestyle='--', linewidth=2,
            label=f'Mean: {np.mean(times):.1f}s')
ax1.axvline(np.median(times), color='green', linestyle='--', linewidth=2,
            label=f'Median: {np.median(times):.1f}s')
ax1.set_xlabel('Response Time (seconds)', fontsize=13, fontweight='bold')
ax1.set_ylabel('Count', fontsize=13, fontweight='bold')
ax1.set_title(f'DBBench Response Time Distribution (n={n})', fontsize=14, fontweight='bold')
ax1.legend(loc='upper right', fontsize=11)
ax1.grid(axis='y', alpha=0.3)

# Panel 2: SQL bar (top, col 3)
ax2 = fig.add_subplot(gs[0, 2])
bars = ax2.bar(['SQL Generated', 'No SQL'], [sql_n, n-sql_n],
               color=['#4A90D9', '#E8E8E8'], edgecolor='white', linewidth=1.5, width=0.5)
for bar, count in zip(bars, [sql_n, n-sql_n]):
    ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1,
             str(count), ha='center', fontsize=16, fontweight='bold')
ax2.set_ylabel('Count', fontsize=13, fontweight='bold')
ax2.set_title(f'SQL Rate: {sql_n}/{n} ({sql_n/n*100:.0f}%)', fontsize=14, fontweight='bold')
ax2.grid(axis='y', alpha=0.3)
ax2.set_ylim(0, max(sql_n, n-sql_n)*1.15)

# Panel 3: Per-sample time (middle, full width)
ax3 = fig.add_subplot(gs[1, :])
colors_sample = ['#4CAF50' if s else '#E0E0E0' for s in has_sql]
ax3.bar(range(n), times, color=colors_sample, edgecolor='white', linewidth=0.3, width=0.8)
ax3.set_xlabel('Sample Index', fontsize=13, fontweight='bold')
ax3.set_ylabel('Time (seconds)', fontsize=13, fontweight='bold')
ax3.set_title(f'Per-Sample Time: Green=SQL ({sql_n}), Gray=No-SQL ({n-sql_n})',
              fontsize=14, fontweight='bold')
ax3.set_xticks(range(0, n, 25))
ax3.grid(axis='y', alpha=0.3)
ax3.axhline(10, color='orange', linestyle=':', alpha=0.5, linewidth=1, label='10s')
ax3.legend(fontsize=10)

# Panel 4: Cumulative SQL rate (top, col 4)
ax4 = fig.add_subplot(gs[0, 3])
cum_rate = np.cumsum(has_sql) / np.arange(1, n+1) * 100
ax4.plot(range(1, n+1), cum_rate, linewidth=2.5, color='#4A90D9')
ax4.axhline(sql_n/n*100, color='green', linestyle='--', linewidth=2,
            alpha=0.7, label=f'Final: {sql_n/n*100:.0f}%')
ax4.set_ylabel('SQL Rate (%)', fontsize=11)
ax4.set_title(f'Cumulative SQL Rate', fontsize=13, fontweight='bold')
ax4.legend(fontsize=10)
ax4.grid(alpha=0.3)
ax4.set_ylim(85, 105)

# Panel 5: SQL rate by 25-sample batches (bottom, col 1)
ax5 = fig.add_subplot(gs[2, 0])
batch_rates = [sum(has_sql[i:i+25])/25*100 for i in range(0, n, 25)]
batches = [f'{i+1}-{i+25}' for i in range(0, n, 25)]
ax5.bar(batches, batch_rates, color='#4A90D9', edgecolor='white', linewidth=1.2, width=0.6)
ax5.axhline(sql_n/n*100, color='red', linestyle='--', linewidth=1.5,
            alpha=0.7, label=f'{sql_n/n*100:.0f}% avg')
ax5.set_ylabel('SQL Rate (%)', fontsize=11, fontweight='bold')
ax5.set_title('SQL Rate by 25-Sample Batches', fontsize=12, fontweight='bold')
ax5.legend(fontsize=9)
ax5.grid(axis='y', alpha=0.3)
ax5.set_ylim(0, 110)

# Panel 6: Time stats (bottom, col 2)
ax6 = fig.add_subplot(gs[2, 1])
ax6.axis('off')
ax6.text(0.08, 0.95, 'Time Statistics', fontsize=13, fontweight='bold')
ax6.text(0.08, 0.80, f'Min:    {min(times):.1f}s', fontsize=11)
ax6.text(0.08, 0.68, f'Q25:    {np.percentile(times,25):.1f}s', fontsize=11)
ax6.text(0.08, 0.56, f'Median: {np.median(times):.1f}s', fontsize=11,
         fontweight='bold', color='#1565C0')
ax6.text(0.08, 0.44, f'Q75:    {np.percentile(times,75):.1f}s', fontsize=11)
ax6.text(0.08, 0.32, f'Max:    {max(times):.1f}s', fontsize=11)
ax6.text(0.08, 0.20, f'Mean:   {np.mean(times):.1f}s', fontsize=11)
ax6.text(0.08, 0.08, f'Std:    {np.std(times):.1f}s', fontsize=11)

# Panel 7: Speed categories (bottom, col 3)
ax7 = fig.add_subplot(gs[2, 2])
fast = sum(1 for t in times if t < 2)
med = sum(1 for t in times if 2 <= t < 5)
slow = sum(1 for t in times if 5 <= t < 10)
vslow = sum(1 for t in times if t >= 10)
cats = ['Fast\n(<2s)', 'Medium\n(2-5s)', 'Slow\n(5-10s)', 'Very\nSlow\n(>10s)']
counts = [fast, med, slow, vslow]
ax7.bar(cats, counts, color=['#4CAF50', '#FFA726', '#FF7043', '#EF5350'],
        edgecolor='white', linewidth=1.5, width=0.5)
for bar, count in zip(ax7.patches, counts):
    ax7.text(bar.get_x()+bar.get_width()/2, bar.get_height()+3,
             str(count), ha='center', fontsize=13, fontweight='bold')
ax7.set_ylabel('Count', fontsize=11, fontweight='bold')
ax7.set_title('Speed Categories', fontsize=12, fontweight='bold')
ax7.grid(axis='y', alpha=0.3)

# Panel 8: Summary box (bottom, col 4)
ax8 = fig.add_subplot(gs[2, 3])
ax8.axis('off')
summary_lines = [
    f'Model: {MODEL}',
    f'Task: dbbench-std',
    f'Samples: {n}',
    f'',
    f'SQL: {sql_n}/{n} ({sql_n/n*100:.0f}%)',
    f'Errors: {err_n}',
    f'Avg: {avg_time:.1f}s/sample',
    f'Total: {total_time:.0f}s ({total_time/60:.0f}min)',
]
y = 0.92
for line in summary_lines:
    color = '#1A1A2E'
    if line.startswith('SQL'):
        color = '#2E7D32' if sql_n/n >= 0.9 else '#C62828'
    ax8.text(0.05, y, line, fontsize=10.5, va='top', fontweight='bold' if line.startswith('SQL') else 'normal', color=color)
    y -= 0.065

# Title
plt.suptitle(f'AgentBench DBBench — {n}-Sample Benchmark\n{MODEL} | {sql_n}/{n} SQL ({sql_n/n*100:.0f}%) | {err_n} errors | {avg_time:.1f}s avg | {total_time/60:.0f}min total',
             fontsize=16, fontweight='bold', y=0.98, color='#1A1A2E')

plt.savefig('/tmp/agentbench_dbbench_300_results.png', dpi=150,
            bbox_inches='tight', facecolor='white')
print("Saved: /tmp/agentbench_dbbench_300_results.png")
```

## API Integration Notes

### Common API Endpoints

| Endpoint | Model | Notes |
|----------|-------|-------|
| `http://141.33.165.84:8000/v1` | aip-best | Qwen3.6-35B-A3B, reliable |
| `http://localhost:11434/api/chat` | Ollama models | Local Ollama |
| Custom endpoints | Various | Replace API_URL in runner |

### API Response Handling

Some vLLM endpoints return `content: null` with reasoning in `message.reasoning` field. Always handle both:

```python
msg = resp.json().get("choices", [{}])[0].get("message", {})
content = msg.get("content") or msg.get("reasoning", "")
if not content:
    return None
```

### Tool Args Format

Tool call arguments may be JSON strings, not dicts:

```python
func_args = tc.get("function", {}).get("arguments", {})
if isinstance(func_args, str):
    func_args = json.loads(func_args)
```

## Multi-Model Comparison

When comparing multiple models:

1. Run each model separately with identical 300-sample benchmark
2. Save each to `/tmp/agentbench_dbbench_<model>.json`
3. Generate individual plots with same style
4. Create summary table:

| Model | Size | SQL Rate | Avg Time | Errors |
|-------|------|----------|----------|--------|
| llama3.2:3b | 1.9GB | 100% | 3.8s | 0 |
| aip-best | - | 93% | 4.9s | 0 |
| qwen3.6:latest (local) | 23GB | ~3% | 28s | many |

## Infrastructure Issues & Fixes

### Workers Not Registered
```bash
# Check containers
docker ps --format '{{.Names}}' | grep agentbench-fc-dbbench
# Start all 10
for i in $(seq 1 10); do docker start agentbench-fc-dbbench-std-$i; done
# Verify
curl -s http://localhost:5020/api/list_workers | python3 -m json.tool
```

### Controller Returns "task does not exist"
```bash
# Worker not running - start it
docker compose -f /tmp/AgentBench/extra/docker-compose.yml up -d dbbench-std
```

### Worker Capacity Exhaustion
If running many samples, 10 workers (320 capacity) may get overwhelmed.
Solution: Ensure all 10 containers are running.

### Docker SDK Bug (OS Interaction only, not DBBench)
Not relevant for DBBench — this affects os_interaction task only.

### Ollama Initialization (Parallel Runs)
If running parallel benchmarks, Ollama can stall. Run single-threaded or with max_workers=1.

## File Outputs

| File | Description |
|------|-------------|
| `/tmp/agentbench_dbbench_300.json` | Full results data (one JSON per model) |
| `/tmp/agentbench_dbbench_300_results.png` | 8-panel dashboard plot |
| `/tmp/dbbench_output.log` | Raw terminal log with per-sample output |

## Key Reminders

- DBBench has **300 samples total** (not 50, not 100)
- **0 infrastructure errors** expected when workers are running
- **93-100% SQL rate** is normal for capable models
- **2-5s/sample** is normal for fast models; slower models may be 10-30s
- **Single-turn mode** only — no multi-round interaction (simpler, faster)
- **SQL detection** checks both code blocks and inline SQL
- Use **consistent plot style** for all models to enable direct comparison
- Docker containers stay running between benchmark runs — no need to restart
