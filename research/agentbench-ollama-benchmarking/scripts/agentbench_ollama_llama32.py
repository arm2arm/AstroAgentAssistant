#!/usr/bin/env python3
"""
AgentBench with Ollama - Full benchmark suite
Usage: python agentbench_ollama_llama32.py
"""
import json
import time
import requests
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
MODEL = "llama3.2:3b"
OLLAMA_URL = "http://localhost:11434/api/chat"
BASE_DIR = "/tmp/AgentBench"
RESULTS_DIR = "/tmp/agentbench_ollama_llama32"
os.makedirs(RESULTS_DIR, exist_ok=True)

# Extraction functions
def extract_sql(content):
    if not content: return None
    if "```sql" in content:
        return content.split("```sql")[1].split("```")[0].strip()
    elif "```" in content:
        return content.split("```")[1].split("```")[0].strip()
    return None

def extract_cmd(content):
    if not content: return None
    if "```bash" in content:
        return content.split("```bash")[1].split("```")[0].strip()
    elif "```" in content:
        return content.split("```")[1].split("```")[0].strip()
    return None

def call_llm(messages, max_tokens=512, timeout=120):
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "max_tokens": max_tokens
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def run_dbbench(n_samples=100, workers=5):
    print(f"\n{'='*60}")
    print(f"DBBENCH (SQL) - {n_samples} samples")
    print(f"{'='*60}")
    
    samples = [json.loads(l) for l in open(f"{BASE_DIR}/data/dbbench/standard.jsonl")][:n_samples]
    results = []
    
    def process(s):
        start = time.time()
        r = call_llm([
            {"role": "system", "content": "Output ONLY SQL in ```sql code block."},
            {"role": "user", "content": s.get("description", "")}
        ])
        elapsed = time.time() - start
        if "error" in r:
            return {"id": s.get("id", 0), "status": "error", "time": elapsed}
        content = r.get("message", {}).get("content", "")
        sql = extract_sql(content)
        return {"id": s.get("id", 0), "sql": sql, "time": elapsed, "success": sql is not None}
    
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(process, s): s for s in samples}
        for i, fut in enumerate(as_completed(futures)):
            r = fut.result()
            results.append(r)
            if (i+1) % 20 == 0:
                succ = sum(1 for x in results if x.get("success"))
                print(f"  {i+1}/{n_samples} | SQL: {succ}")
    
    succ = sum(1 for x in results if x.get("success"))
    avg = sum(x["time"] for x in results) / len(results)
    print(f"\nDBBENCH: {succ}/{n_samples} ({100*succ/n_samples:.1f}%) | Avg: {avg:.2f}s")
    json.dump(results, open(f"{RESULTS_DIR}/dbbench.json", "w"))
    return succ, n_samples, avg

def run_knowledgegraph(n_samples=50, workers=3):
    print(f"\n{'='*60}")
    print(f"KNOWLEDGE GRAPH - {n_samples} samples")
    print(f"{'='*60}")
    
    samples = json.load(open(f"{BASE_DIR}/data/knowledgegraph/std.json"))[:n_samples]
    results = []
    
    def process(s):
        start = time.time()
        r = call_llm([
            {"role": "system", "content": "Answer concisely."},
            {"role": "user", "content": s.get("question", "")}
        ], max_tokens=128)
        elapsed = time.time() - start
        if "error" in r:
            return {"id": s.get("id", 0), "status": "error", "time": elapsed}
        content = r.get("message", {}).get("content", "")
        return {"id": s.get("id", 0), "answer": content, "time": elapsed, "success": bool(content)}
    
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(process, s): s for s in samples}
        for i, fut in enumerate(as_completed(futures)):
            r = fut.result()
            results.append(r)
            if (i+1) % 10 == 0:
                succ = sum(1 for x in results if x.get("success"))
                print(f"  {i+1}/{n_samples} | Success: {succ}")
    
    succ = sum(1 for x in results if x.get("success"))
    avg = sum(x["time"] for x in results) / len(results)
    print(f"\nKG: {succ}/{n_samples} ({100*succ/n_samples:.1f}%) | Avg: {avg:.2f}s")
    json.dump(results, open(f"{RESULTS_DIR}/knowledgegraph.json", "w"))
    return succ, n_samples, avg

def run_os_interaction(n_samples=26, workers=3):
    print(f"\n{'='*60}")
    print(f"OS INTERACTION - {n_samples} samples")
    print(f"{'='*60}")
    
    samples = json.load(open(f"{BASE_DIR}/data/os_interaction/data/dev.json"))[:n_samples]
    results = []
    
    def process(s):
        start = time.time()
        r = call_llm([
            {"role": "system", "content": "Output ONLY bash command in ```bash block."},
            {"role": "user", "content": s.get("description", "")}
        ], max_tokens=256)
        elapsed = time.time() - start
        if "error" in r:
            return {"id": s.get("id", 0), "status": "error", "time": elapsed}
        content = r.get("message", {}).get("content", "")
        cmd = extract_cmd(content)
        return {"id": s.get("id", 0), "command": cmd, "time": elapsed, "success": cmd is not None}
    
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(process, s): s for s in samples}
        for i, fut in enumerate(as_completed(futures)):
            r = fut.result()
            results.append(r)
            if (i+1) % 10 == 0:
                succ = sum(1 for x in results if x.get("success"))
                print(f"  {i+1}/{n_samples} | Success: {succ}")
    
    succ = sum(1 for x in results if x.get("success"))
    avg = sum(x["time"] for x in results) / len(results)
    print(f"\nOS: {succ}/{n_samples} ({100*succ/n_samples:.1f}%) | Avg: {avg:.2f}s")
    json.dump(results, open(f"{RESULTS_DIR}/os_interaction.json", "w"))
    return succ, n_samples, avg

def run_lateral_thinking(n_samples=30, workers=2):
    print(f"\n{'='*60}")
    print(f"LATERAL THINKING - {n_samples} samples")
    print(f"{'='*60}")
    
    df = pd.read_excel(f"{BASE_DIR}/data/lateralthinkingpuzzle/standard.xlsx")
    samples = df.to_dict('records')[:n_samples]
    results = []
    
    def process(s):
        start = time.time()
        prompt = f"Story: {s['story']}\nAnswer: {s['answer']}"
        r = call_llm([
            {"role": "user", "content": prompt}
        ], max_tokens=256)
        elapsed = time.time() - start
        if "error" in r:
            return {"id": s.get("id", 0), "status": "error", "time": elapsed}
        content = r.get("message", {}).get("content", "")
        return {"id": s.get("id", 0), "answer": content, "time": elapsed, "success": bool(content)}
    
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(process, s): s for s in samples}
        for i, fut in enumerate(as_completed(futures)):
            r = fut.result()
            results.append(r)
            if (i+1) % 10 == 0:
                succ = sum(1 for x in results if x.get("success"))
                print(f"  {i+1}/{n_samples} | Success: {succ}")
    
    succ = sum(1 for x in results if x.get("success"))
    avg = sum(x["time"] for x in results) / len(results)
    print(f"\nLTP: {succ}/{n_samples} ({100*succ/n_samples:.1f}%) | Avg: {avg:.2f}s")
    json.dump(results, open(f"{RESULTS_DIR}/lateralthinking.json", "w"))
    return succ, n_samples, avg

def main():
    print("="*70)
    print("AgentBench with Ollama - llama3.2:3b")
    print("="*70)
    print(f"Model: {MODEL}")
    print(f"Ollama URL: {OLLAMA_URL}")
    print(f"Results: {RESULTS_DIR}")
    
    total_succ = 0
    total_all = 0
    total_time = 0
    
    succ, n, avg = run_dbbench(n_samples=100, workers=5)
    total_succ += succ; total_all += n; total_time += avg
    
    succ, n, avg = run_knowledgegraph(n_samples=50, workers=3)
    total_succ += succ; total_all += n; total_time += avg
    
    succ, n, avg = run_os_interaction(n_samples=26, workers=3)
    total_succ += succ; total_all += n; total_time += avg
    
    succ, n, avg = run_lateral_thinking(n_samples=30, workers=2)
    total_succ += succ; total_all += n; total_time += avg
    
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    print(f"{'Task':<25} {'Success':<12} {'Rate':<12} {'Avg Time'}")
    print("-"*70)
    print(f"{'Total':<25} {total_succ}/{total_all}     {100*total_succ/total_all:>6.1f}%     {total_time/4:.2f}s")
    print("-"*70)
    print(f"\nResults saved to: {RESULTS_DIR}/")

if __name__ == "__main__":
    main()
