#!/usr/bin/env python3
"""DBBench benchmark runner for OpenAI-compatible API endpoints.

Usage:
    python3 run_dbbench_aip_best.py

Configuration at the top of the file:
    API_URL, MODEL, CONTROLLER, N, TIMEOUT, MAX_TOKENS

Features:
- Timeout handling (catches requests.exceptions.ReadTimeout)
- Checkpointing (saves results after every sample via save_checkpoint)
- Progress reporting with ETA
- Error handling for controller/API failures
"""

import requests
import json
import time
import re
import os
import sys

# ─── Configuration ───
API_URL = "http://141.33.165.84:8000/v1/chat/completions"
MODEL = "aip-best"
CONTROLLER = "http://localhost:5020"
N = 300
OUTPUT_DIR = "/home/hermes/projects/dbbench-benchmarks/results"
OUT_PATH = os.path.join(OUTPUT_DIR, "aip-best-141-33-165-84.json")
TIMEOUT = 600  # seconds per sample — 600s needed for slow llama.cpp endpoints
MAX_TOKENS = 8192  # 8192 needed for reasoning models (aip-best uses reasoning field)


def call_llm(messages, tools=None):
    """Call LLM via OpenAI-compatible API. Always check both content and reasoning fields."""
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "temperature": 0.1,
        "max_tokens": MAX_TOKENS,
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    resp = requests.post(
        API_URL,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT,
    )
    if resp.status_code != 200:
        print(f"    API error {resp.status_code}: {resp.text[:200]}")
        return None

    data = resp.json()
    msg = data.get("choices", [{}])[0].get("message", {})
    # aip-best stores output in 'reasoning' field on some servers
    content = msg.get("content", "") or msg.get("reasoning", "")
    if not content:
        return None
    return content


def is_sql(s):
    """Check if response contains SQL in code blocks or inline."""
    if "```" in s:
        for m in re.findall(r'```(?:sql)?\s*\n(.*?)```', s, re.DOTALL):
            if any(k in m.upper() for k in ['SELECT', 'FROM', 'WHERE', 'JOIN',
                                            'INSERT', 'UPDATE', 'DELETE', 'CREATE']):
                return True
    return any(k in s.upper() for k in ['SELECT ', 'FROM ', 'WHERE ', 'JOIN '])


def save_checkpoint(results, sql_n, err_n, total, t0):
    """Save intermediate results after each sample for crash recovery."""
    times = [r["time_sec"] for r in results if r["status"] == "COMPLETED"]
    out = {
        "model": MODEL, "task": "dbbench-std", "n_samples": N,
        "elapsed_seconds": round(total, 2),
        "sql_count": sql_n,
        "sql_rate": round(sql_n / N * 100, 1) if N > 0 else 0,
        "error_count": err_n,
        "avg_time_sec": round(total / len(results), 2) if results else 0,
        "min_time": round(min(times), 2) if times else None,
        "max_time": round(max(times), 2) if times else None,
        "median_time": round(sorted(times)[len(times)//2], 2) if times else None,
        "results": results,
    }
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=2)
    tmp_path = OUT_PATH.replace(".json", "_checkpoint.json")
    with open(tmp_path, "w") as f:
        json.dump(out, f, indent=2)


def run_benchmark():
    results = []
    t0 = time.time()
    sql_n = 0
    err_n = 0

    print(f"DBBench: {N} samples | Model: {MODEL} | Start: {time.strftime('%H:%M')}")
    print(f"API: {API_URL}")
    print(f"Timeout: {TIMEOUT}s per sample | Max tokens: {MAX_TOKENS}")
    print("=" * 70)

    for idx in range(N):
        t1 = time.time()

        # Start sample from controller
        try:
            r = requests.post(f"{CONTROLLER}/api/start_sample",
                              json={"name": "dbbench-std", "index": idx}, timeout=30)
        except Exception as e:
            print(f"[{idx+1}] CONTROLLER ERROR: {e}")
            results.append({"index": idx, "status": "ERROR", "error": str(e)[:200],
                            "rounds": 0, "time_sec": round(time.time()-t1, 2)})
            err_n += 1
            save_checkpoint(results, sql_n, err_n, time.time()-t0, t0)
            continue

        if r.status_code != 200:
            print(f"[{idx+1}] ERROR: {r.text[:100]}")
            results.append({"index": idx, "status": "ERROR", "error": r.text[:200],
                            "rounds": 0, "time_sec": round(time.time()-t1, 2)})
            err_n += 1
            save_checkpoint(results, sql_n, err_n, time.time()-t0, t0)
            continue

        data = r.json()
        msgs = data.get("messages", [])
        tools = data.get("tools", None)

        # Call LLM
        try:
            resp_text = call_llm(msgs, tools)
        except requests.exceptions.ReadTimeout:
            print(f"[{idx+1}] TIMEOUT (>{TIMEOUT}s)")
            results.append({"index": idx, "status": "ERROR", "error": "ReadTimeout",
                            "rounds": 1, "time_sec": round(time.time()-t1, 2)})
            err_n += 1
            save_checkpoint(results, sql_n, err_n, time.time()-t0, t0)
            continue
        except Exception as e:
            print(f"[{idx+1}] API FAIL: {e}")
            results.append({"index": idx, "status": "ERROR", "error": str(e)[:200],
                            "rounds": 1, "time_sec": round(time.time()-t1, 2)})
            err_n += 1
            save_checkpoint(results, sql_n, err_n, time.time()-t0, t0)
            continue

        if resp_text is None:
            print(f"[{idx+1}] API FAIL (no content)")
            results.append({"index": idx, "status": "ERROR", "rounds": 1,
                            "time_sec": round(time.time()-t1, 2)})
            err_n += 1
            save_checkpoint(results, sql_n, err_n, time.time()-t0, t0)
            continue

        has_sql = is_sql(resp_text)
        if has_sql:
            sql_n += 1

        # Submit to controller
        try:
            r2 = requests.post(f"{CONTROLLER}/api/interact",
                               json={"session_id": idx,
                                     "agent_response": {"content": resp_text, "status": "CONTINUE"}},
                               timeout=TIMEOUT)
        except Exception as e:
            print(f"[{idx+1}] SUBMIT ERROR: {e}")
            r2 = None

        t_total = time.time() - t1
        tag = "SQL" if has_sql else "NONE"
        elapsed = time.time() - t0
        eta = elapsed / (idx + 1) * (N - idx - 1) if idx + 1 > 0 else 0
        print(f"[{idx+1}/{N}] {tag:4s} {t_total:.1f}s | SQL={sql_n} err={err_n} | ETA={eta/60:.0f}m")

        results.append({"index": idx, "status": "COMPLETED", "has_sql": has_sql,
                        "rounds": 1, "time_sec": round(t_total, 2)})
        save_checkpoint(results, sql_n, err_n, time.time()-t0, t0)

    total = time.time() - t0
    print("=" * 70)
    print(f"Done: {total:.1f}s total | {N} samples | {err_n} errors")
    print(f"SQL: {sql_n}/{N} ({sql_n/N*100:.0f}%) | Avg: {total/N:.1f}s/sample")

    times = [r["time_sec"] for r in results if r["status"] == "COMPLETED"]
    times_sorted = sorted(times) if times else []
    if times_sorted:
        n = len(times_sorted)
        print(f"Min: {min(times):.1f}s | Max: {max(times):.1f}s | Median: {times_sorted[n//2]:.1f}s")

    out = {
        "model": MODEL, "task": "dbbench-std", "n_samples": N,
        "elapsed_seconds": round(total, 2), "sql_count": sql_n,
        "sql_rate": round(sql_n/N*100, 1), "error_count": err_n,
        "avg_time_sec": round(total/N, 2),
        "min_time": round(min(times), 2) if times else None,
        "max_time": round(max(times), 2) if times else None,
        "median_time": round(times_sorted[len(times_sorted)//2], 2) if times_sorted else None,
        "results": results,
    }
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Saved: {OUT_PATH}")
    return out


if __name__ == "__main__":
    run_benchmark()