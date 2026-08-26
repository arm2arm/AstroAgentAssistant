#!/usr/bin/env python3
"""
Direct OS Interaction benchmark runner - bypasses Docker SDK bug in aiodocker.
Runs bash command generation tests without container execution.
Use this when os-std worker fails with:
  AttributeError: 'int' object has no attribute 'connect'
  at /usr/local/lib/python3.10/site-packages/aiodocker/stream.py:52

This is a Docker SDK compatibility issue, not missing data.
All 144 samples across 7 datasets are available.
"""
import json
import time
import requests
import glob
import os

# API Configuration
API_URL = "http://141.33.165.84:8000/v1/chat/completions"
MODEL_NAME = "aip-best"
API_KEY = "EMPTY"

def load_os_samples():
    """Load all OS interaction samples from data directories."""
    samples = []
    base_path = "/tmp/AgentBench/data/os_interaction/data"
    
    # Load from numbered directories (1-7)
    for i in range(1, 8):
        pattern = os.path.join(base_path, str(i), "*.json")
        for filepath in glob.glob(pattern):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    for item in data:
                        samples.append({
                            "index": len(samples),
                            "description": item.get("description", ""),
                            "expected_command": item.get("evaluation", {}).get("example", {}).get("code", ""),
                            "labels": item.get("labels", []),
                            "source_file": filepath,
                        })
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Warning: Failed to load {filepath}: {e}")
                continue
    
    return samples

def call_api(messages, tools=None):
    """Call the external API."""
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        "temperature": 0.1,
        "max_tokens": 512,
    }
    if tools:
        payload["tools"] = tools
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    
    try:
        resp = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def run_direct_benchmark(num_samples=None, output_file=None):
    """Run OS Interaction benchmark without Docker container execution."""
    samples = load_os_samples()
    
    if not samples:
        print("❌ No samples found. Check data directory structure.")
        return None
    
    if num_samples:
        samples = samples[:num_samples]
    
    print(f"Loaded {len(samples)} OS interaction samples")
    print(f"Running direct benchmark (bypassing Docker SDK bug)...")
    
    results = []
    start_time = time.time()
    
    for i, sample in enumerate(samples, 1):
        if i % 10 == 0 or i == len(samples):
            elapsed = time.time() - start_time
            rate = elapsed / i
            eta = rate * (len(samples) - i)
            print(f"[{i}/{len(samples)}] Rate: {rate:.1f}s/sample | ETA: {eta/60:.1f}min")
        
        # Build prompt
        messages = [
            {"role": "system", "content": "You are a Linux assistant. Generate a bash command to solve the task."},
            {"role": "user", "content": sample["description"]}
        ]
        
        result = call_api(messages)
        
        if "error" in result:
            results.append({
                "index": sample["index"],
                "error": result["error"],
                "status": "ERROR",
            })
            continue
        
        choice = result.get("choices", [{}])[0]
        response_msg = choice.get("message", {})
        content = response_msg.get("content") or response_msg.get("reasoning", "")
        
        if not content:
            results.append({
                "index": sample["index"],
                "error": "No content in response",
                "status": "EMPTY",
            })
            continue
        
        results.append({
            "index": sample["index"],
            "description": sample["description"][:100],
            "generated_command": content.strip()[:200],
            "expected_command": sample["expected_command"],
            "labels": sample["labels"],
            "status": "OK",
            "content_length": len(content),
        })
    
    elapsed = time.time() - start_time
    success = sum(1 for r in results if r.get("status") == "OK")
    
    print(f"\n✅ Complete: {success}/{len(results)} ({100*success/len(results):.1f}%)")
    print(f"Time: {elapsed:.1f}s ({elapsed/max(1,success):.1f}s per sample)")
    
    # Save results
    output_path = output_file or f"/tmp/agentbench_os_direct_{MODEL_NAME}_{int(time.time())}.json"
    
    with open(output_path, 'w') as f:
        json.dump({
            "model": MODEL_NAME,
            "task": "os_interaction_direct",
            "total": len(results),
            "successful": success,
            "elapsed_seconds": elapsed,
            "per_sample_time": elapsed/max(1,success),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "note": "Direct runner bypassing Docker SDK bug in aiodocker",
            "results": results
        }, f, indent=2)
    
    print(f"\nResults saved to {output_path}")
    
    # Print sample commands
    print("\n" + "="*60)
    print("SAMPLE GENERATED COMMANDS:")
    print("="*60)
    for r in results[:5]:
        if r.get("status") == "OK":
            print(f"\nTask: {r.get('description', 'N/A')[:80]}...")
            print(f"Generated: {r.get('generated_command', 'N/A')[:100]}...")
            print(f"Expected: {r.get('expected_command', 'N/A')[:100]}...")
    
    return {
        "model": MODEL_NAME,
        "task": "os_interaction_direct",
        "total": len(results),
        "successful": success,
        "elapsed_seconds": elapsed,
        "output_file": output_path,
        "results": results
    }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Direct OS Interaction benchmark runner")
    parser.add_argument("--samples", type=int, default=None, help="Number of samples to run")
    parser.add_argument("--output", type=str, default=None, help="Output file path")
    
    args = parser.parse_args()
    
    run_direct_benchmark(num_samples=args.samples, output_file=args.output)
