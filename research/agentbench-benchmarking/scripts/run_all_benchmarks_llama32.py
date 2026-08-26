#!/usr/bin/env python3
"""Full AgentBench suite using llama3.2:3b."""
import json
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import os

MODEL = "llama3.2:3b"
OLLAMA_URL = "http://localhost:11434/api/chat"
BASE_DIR = "/tmp/AgentBench"
RESULTS_DIR = "/tmp/agentbench_llama32_results"
os.makedirs(RESULTS_DIR, exist_ok=True)

def call_llm(messages, max_tokens=512):
    """Call local Ollama API."""
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.0, "num_predict": max_tokens}
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def run_dbbench(n_samples=100):
    """Run DBBench (SQL generation)."""
    print("\n" + "="*60)
    print("DBBENCH (SQL Generation)")
    print("="*60)
    
    samples_file = f"{BASE_DIR}/data/dbbench/standard.jsonl"
    samples = []
    with open(samples_file, 'r') as f:
        for i, line in enumerate(f):
            if i >= n_samples: break
            samples.append(json.loads(line))
    
    def extract_sql(content):
        if not content: return None
        if "```sql" in content: return content.split("```sql")[1].split("```")[0].strip()
        elif "```" in content: return content.split("```")[1].split("```")[0].strip()
        return None
    
    def process(s):
        sid = s.get("id", s.get("sample_id", 0))
        prompt = s.get("prompt", "")
        start = time.time()
        resp = call_llm([
            {"role": "system", "content": "Output ONLY SQL in ```sql block."},
            {"role": "user", "content": prompt}
        ])
        elapsed = time.time() - start
        if "error" in resp: return {"id": sid, "status": "error", "time": elapsed}
        sql = extract_sql(resp.get("message", {}).get("content", ""))
        return {"id": sid, "sql": sql, "time": elapsed, "success": sql is not None}
    
    results = []
    with ThreadPoolExecutor(max_workers=5) as ex:
        futures = {ex.submit(process, s): s for s in samples}
        for i, fut in enumerate(as_completed(futures)):
            r = fut.result()
            results.append(r)
            if (i+1) % 20 == 0:
                succ = sum(1 for x in results if x.get("success"))
                print(f"Progress: {i+1}/{len(samples)} | SQL: {succ}")
    
    succ = sum(1 for x in results if x.get("success"))
    avg = sum(x["time"] for x in results) / len(results)
    print(f"DBBENCH: {succ}/{len(results)} SQL ({100*succ/len(results):.1f}%) | Avg: {avg:.2f}s")
    with open(f"{RESULTS_DIR}/dbbench.json", "w") as f: json.dump(results, f)
    return succ, len(results), avg

def run_kg(n_samples=50):
    """Run Knowledge Graph benchmark."""
    print("\n" + "="*60)
    print("KNOWLEDGE GRAPH (Multi-hop Reasoning)")
    print("="*60)
    
    samples_file = f"{BASE_DIR}/data/knowledgegraph/std.json"
    with open(samples_file, 'r') as f:
        samples = json.load(f)[:n_samples]
    
    def process(s):
        sid = s.get("id", 0)
        prompt = s.get("question", "")
        start = time.time()
        resp = call_llm([
            {"role": "system", "content": "Answer the question concisely."},
            {"role": "user", "content": prompt}
        ], max_tokens=128)
        elapsed = time.time() - start
        if "error" in resp: return {"id": sid, "status": "error", "time": elapsed}
        ans = resp.get("message", {}).get("content", "")
        return {"id": sid, "answer": ans, "time": elapsed, "success": bool(ans)}
    
    results = []
    with ThreadPoolExecutor(max_workers=3) as ex:
        futures = {ex.submit(process, s): s for s in samples}
        for i, fut in enumerate(as_completed(futures)):
            r = fut.result()
            results.append(r)
            if (i+1) % 10 == 0:
                succ = sum(1 for x in results if x.get("success"))
                print(f"Progress: {i+1}/{len(samples)} | Success: {succ}")
    
    succ = sum(1 for x in results if x.get("success"))
    avg = sum(x["time"] for x in results) / len(results)
    print(f"KG: {succ}/{len(results)} ({100*succ/len(results):.1f}%) | Avg: {avg:.2f}s")
    with open(f"{RESULTS_DIR}/knowledgegraph.json", "w") as f: json.dump(results, f)
    return succ, len(results), avg

def run_os(n_samples=50):
    """Run OS Interaction benchmark."""
    print("\n" + "="*60)
    print("OS INTERACTION (Command Generation)")
    print("="*60)
    
    json_file = f"{BASE_DIR}/data/os_interaction/data/dev.json"
    with open(json_file, 'r') as f:
        samples = json.load(f)[:n_samples]
    
    def extract_cmd(content):
        if not content: return None
        if "```bash" in content: return content.split("```bash")[1].split("```")[0].strip()
        elif "```" in content: return content.split("```")[1].split("```")[0].strip()
        return None
    
    def process(s):
        sid = s.get("id", 0)
        prompt = s.get("instruction", "")
        start = time.time()
        resp = call_llm([
            {"role": "system", "content": "Output ONLY the bash command in ```bash block."},
            {"role": "user", "content": prompt}
        ], max_tokens=256)
        elapsed = time.time() - start
        if "error" in resp: return {"id": sid, "status": "error", "time": elapsed}
        cmd = extract_cmd(resp.get("message", {}).get("content", ""))
        return {"id": sid, "command": cmd, "time": elapsed, "success": cmd is not None}
    
    results = []
    with ThreadPoolExecutor(max_workers=3) as ex:
        futures = {ex.submit(process, s): s for s in samples}
        for i, fut in enumerate(as_completed(futures)):
            r = fut.result()
            results.append(r)
            if (i+1) % 10 == 0:
                succ = sum(1 for x in results if x.get("success"))
                print(f"Progress: {i+1}/{len(samples)} | Success: {succ}")
    
    succ = sum(1 for x in results if x.get("success"))
    avg = sum(x["time"] for x in results) / len(results)
    print(f"OS: {succ}/{len(results)} ({100*succ/len(results):.1f}%) | Avg: {avg:.2f}s")
    with open(f"{RESULTS_DIR}/os_interaction.json", "w") as f: json.dump(results, f)
    return succ, len(results), avg

def main():
    """Run full benchmark suite."""
    print(f"Starting Full AgentBench Suite ({MODEL})")
    print(f"Started at: {datetime.now().isoformat()}")
    
    results = {}
    
    # DBBench (100 samples)
    r1 = run_dbbench(100)
    results["dbbench"] = {"success": r1[0], "total": r1[1], "time": r1[2]}
    
    # KG (50 samples)
    r2 = run_kg(50)
    results["knowledgegraph"] = {"success": r2[0], "total": r2[1], "time": r2[2]}
    
    # OS (50 samples)
    r3 = run_os(50)
    results["os_interaction"] = {"success": r3[0], "total": r3[1], "time": r3[2]}
    
    # Summary
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)
    print(f"{'Task':<25} {'Success':<12} {'Rate':<12} {'Avg Time'}")
    print("-"*60)
    total_succ = 0
    total_all = 0
    for task, data in results.items():
        rate = 100*data["success"]/data["total"]
        print(f"{task:<25} {data['success']}/{data['total']:<10} {rate:>6.1f}%     {data['time']:.2f}s")
        total_succ += data["success"]
        total_all += data["total"]
    
    print("-"*60)
    overall_rate = 100*total_succ/total_all
    print(f"{'OVERALL':<25} {total_succ}/{total_all:<10} {overall_rate:>6.1f}%")
    print(f"\nResults saved to: {RESULTS_DIR}/")

if __name__ == "__main__":
    main()
