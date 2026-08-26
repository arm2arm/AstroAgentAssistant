#!/usr/bin/env python3
"""Rate limit test for Helmholtz Blablador endpoint.
Runs 20 samples with concurrency=5 to detect 429 errors early."""
import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

API_URL = "https://api.helmholtz-blablador.fz-juelich.de/v1/chat/completions"
API_KEY = "glpat-<YOUR_TOKEN>"
MODEL = "alias-glm-huge"  # Change to test other models

def call_llm(sample_id):
    """Call Helmholtz API with a simple SQL query."""
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a SQL expert. Generate ONLY the SQL query in a ```sql code block. No explanations."},
            {"role": "user", "content": f"Sample {sample_id}: SELECT * FROM users WHERE id = {sample_id}"}
        ],
        "max_tokens": 256
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    start = time.time()
    try:
        resp = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        elapsed = time.time() - start
        
        if resp.status_code == 200:
            data = resp.json()
            msg = data.get("choices", [{}])[0].get("message", {})
            content = msg.get("content") or ""
            reasoning = msg.get("reasoning") or ""
            
            sql = None
            for text in [content, reasoning]:
                if "```sql" in text:
                    sql = text.split("```sql")[1].split("```")[0].strip()
                    break
            
            return {"id": sample_id, "status": "success", "sql": sql is not None, "time": elapsed}
        else:
            return {"id": sample_id, "status": "error", "code": resp.status_code, "time": elapsed}
            
    except Exception as e:
        return {"id": sample_id, "status": "error", "error": str(e), "time": time.time() - start}

if __name__ == "__main__":
    print(f"Rate limit test for {MODEL}")
    print(f"Endpoint: {API_URL}")
    print(f"Samples: 20, Concurrency: 5")
    print("-" * 60)
    
    results = []
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(call_llm, i): i for i in range(20)}
        
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            
            status = "✅" if result["status"] == "success" else "❌"
            sql_status = "SQL" if result.get("sql") else "No SQL"
            print(f"{status} Sample {result['id']}: {result['status']} ({result['time']:.2f}s) - {sql_status}")
    
    total_time = time.time() - start_time
    
    # Summary
    success_count = sum(1 for r in results if r["status"] == "success")
    error_count = sum(1 for r in results if r["status"] == "error")
    sql_count = sum(1 for r in results if r.get("sql"))
    rate_limit_count = sum(1 for r in results if r.get("code") == 429)
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total samples: 20")
    print(f"Success: {success_count} ({100*success_count/20:.1f}%)")
    print(f"Errors: {error_count} ({100*error_count/20:.1f}%)")
    print(f"  - Rate limited (429): {rate_limit_count}")
    print(f"SQL generated: {sql_count} ({100*sql_count/20:.1f}%)")
    print(f"Total time: {total_time:.2f}s")
    print(f"Avg time/sample: {total_time/20:.2f}s")
    print()
    
    if rate_limit_count > 5:
        print("⚠️  WARNING: High rate limit errors detected.")
        print("   This model is NOT suitable for full benchmarks.")
    elif rate_limit_count == 0:
        print("✅ No rate limits detected on 20 samples.")
        print("   Safe to proceed with full benchmark (300 samples).")
    else:
        print("⚠️  Some rate limit errors detected.")
        print("   Consider reducing concurrency or skipping full benchmark.")
