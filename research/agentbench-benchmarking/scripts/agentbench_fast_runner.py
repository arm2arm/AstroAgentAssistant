#!/usr/bin/env python3
"""
AgentBench Fast Runner - Single-round SQL generation test.
Evaluates SQL generation quality without multi-round execution.
"""
import os
import sys
import time
import json
import re
import requests

# API Configuration
API_URL = "http://141.33.165.84:8000/v1/chat/completions"
MODEL_NAME = "aip-best"
API_KEY = "EMPTY"
CONTROLLER_URL = "http://localhost:5020/api"
TASK_NAME = "dbbench-std"

def call_api(messages, tools=None):
    """Call the external API."""
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        "temperature": 0.1,
        "max_tokens": 2048,
    }
    if tools:
        payload["tools"] = tools
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    
    try:
        resp = requests.post(API_URL, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"  API error: {e}")
        return None

def extract_sql(content):
    """Extract SQL from response."""
    match = re.search(r'```sql\s*(.*?)\s*```', content, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match = re.search(r'```(?:\s*)(SELECT|INSERT|UPDATE|DELETE|SHOW)\s+.*?```', content, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(0).strip()[3:-3].strip()
    return None

def run_single_sample(idx):
    """Run a single DBBench sample - single round only."""
    resp = requests.post(
        f"{CONTROLLER_URL}/start_sample",
        json={"name": TASK_NAME, "index": idx}
    )
    
    if resp.status_code != 200:
        return {"error": f"start_sample failed", "index": idx}
    
    data = resp.json()
    messages = data.get("messages", [])
    tools = data.get("tools", [])
    
    if not messages:
        return {"error": "No messages", "index": idx}
    
    result = call_api(messages, tools)
    
    if not result:
        return {"error": "API failed", "index": idx}
    
    choice = result.get("choices", [{}])[0]
    response_msg = choice.get("message", {})
    content = response_msg.get("content") or response_msg.get("reasoning", "")
    tool_calls = response_msg.get("tool_calls", [])
    
    sql_query = None
    for tc in tool_calls:
        func_name = tc.get("function", {}).get("name")
        if func_name == "execute_sql":
            func_args = tc.get("function", {}).get("arguments", {})
            if isinstance(func_args, str):
                try:
                    func_args = json.loads(func_args)
                except:
                    func_args = {}
            sql_query = func_args.get("query", "") if isinstance(func_args, dict) else ""
            break
    
    if not sql_query:
        sql_query = extract_sql(content)
    
    return {
        "index": idx,
        "status": "OK" if sql_query else "NO_SQL",
        "sql": sql_query,
        "content_length": len(content),
        "tool_calls": len(tool_calls),
    }

def run_benchmark(num_samples=100):
    print(f"=== Fast AgentBench DBBench Benchmark ===")
    print(f"Model: {MODEL_NAME}")
    print(f"API: {API_URL}")
    print(f"Task: {TASK_NAME}")
    print(f"Samples: {num_samples} (single-round SQL generation)")
    print()
    
    resp = requests.get(f"{CONTROLLER_URL}/get_indices?name={TASK_NAME}")
    indices = resp.json() if resp.status_code == 200 else []
    print(f"Available samples: {len(indices)}")
    
    samples_to_run = indices[:num_samples]
    results = []
    
    start_time = time.time()
    
    for i, idx in enumerate(samples_to_run, 1):
        if i % 10 == 0:
            elapsed = time.time() - start_time
            rate = elapsed / i
            eta = rate * (len(samples_to_run) - i)
            print(f"[{i}/{len(samples_to_run)}] Sample {idx} | Rate: {rate:.1f}s/sample | ETA: {eta/60:.1f}min")
        
        result = run_single_sample(idx)
        results.append(result)
        
        with open(f"/tmp/agentbench_fast_results_{MODEL_NAME}.json", 'w') as f:
            json.dump({
                "model": MODEL_NAME,
                "api": API_URL,
                "task": TASK_NAME,
                "total_samples": num_samples,
                "completed": len(results),
                "elapsed_seconds": time.time() - start_time,
                "results": results
            }, f, indent=2)
    
    elapsed = time.time() - start_time
    
    print(f"\n=== Summary ===")
    print(f"Total time: {elapsed:.1f}s ({elapsed/len(results):.1f}s per sample)")
    
    statuses = {}
    sql_count = 0
    for r in results:
        s = r.get("status", "UNKNOWN")
        statuses[s] = statuses.get(s, 0) + 1
        if r.get("sql"):
            sql_count += 1
    
    for s, c in statuses.items():
        print(f"  {s}: {c}")
    
    print(f"\nSQL generated: {sql_count}/{len(results)} ({100*sql_count/len(results):.1f}%)")
    
    with open(f"/tmp/agentbench_fast_results_{MODEL_NAME}.json", 'w') as f:
        json.dump({
            "model": MODEL_NAME,
            "api": API_URL,
            "task": TASK_NAME,
            "total_samples": num_samples,
            "completed": len(results),
            "elapsed_seconds": elapsed,
            "sql_generated": sql_count,
            "results": results
        }, f, indent=2)
    
    print(f"\nResults saved to /tmp/agentbench_fast_results_{MODEL_NAME}.json")
    
    print(f"\n=== Sample SQL Queries ===")
    for r in results[:5]:
        if r.get("sql"):
            print(f"Sample {r['index']}: {r['sql'][:100]}...")
    
    return results

if __name__ == "__main__":
    run_benchmark(100)
