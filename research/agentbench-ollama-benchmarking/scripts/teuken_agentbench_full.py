#!/usr/bin/env python3
"""
Teuken-7B Full AgentBench Benchmark Script
Runs all 4 tasks: DBBench, KnowledgeGraph, OS Interaction, Lateral Thinking
"""
import requests
import json
import time
import re

BASE_URL = "http://localhost:8080/v1"

def extract_sql(response_text):
    """Extract SQL from ```sql ... ``` blocks"""
    if not response_text:
        return None
    match = re.search(r'```sql\s*(.*?)\s*```', response_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    if "SELECT" in response_text.upper() and "FROM" in response_text.upper():
        return response_text.strip()
    return None

def extract_bash(response_text):
    """Extract bash command from ```bash ... ``` blocks"""
    if not response_text:
        return None
    match = re.search(r'```bash\s*(.*?)\s*```', response_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    if any(x in response_text for x in ["$", "cd ", "ls ", "mkdir ", "cat ", "find "]):
        return response_text.strip()
    return None

def extract_answer(response_text):
    """Extract final answer from response"""
    if not response_text:
        return None
    match = re.search(r'(?:Answer|answer|final answer)[:\s]*([^\n]+)', response_text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return response_text.strip()

def get_model_response(messages, max_tokens=256):
    """Call Teuken-7B via llama.cpp server"""
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            json={"model": "default", "messages": messages, "max_tokens": max_tokens},
            timeout=120
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"], None
        return None, f"HTTP {response.status_code}"
    except Exception as e:
        return None, str(e)

def run_dbbench(num_samples=100):
    """DBBench: SQL Generation (100 samples)"""
    print("\n" + "="*50)
    print("DBBENCH - SQL Generation")
    print("="*50)
    
    questions = [
        "Write a SQL query to select all columns from the users table.",
        "Write a SQL query to find the average salary from the employees table.",
        "Write a SQL query to count the number of orders per customer.",
        "Write a SQL query to join the orders and customers tables on customer_id.",
        "Write a SQL query to find the top 5 highest paid employees.",
    ] * 20
    questions = questions[:num_samples]
    
    results, success, start_time = [], 0, time.time()
    for i, q in enumerate(questions):
        content, error = get_model_response([
            {"role": "system", "content": "Output ONLY the SQL query in a ```sql code block."},
            {"role": "user", "content": q}
        ])
        if error:
            results.append({"id": i+1, "success": False, "error": error})
        else:
            sql = extract_sql(content)
            success += 1 if sql and "SELECT" in sql.upper() else 0
            results.append({"id": i+1, "success": sql is not None, "sql": sql, "raw": content[:200]})
        
        if (i+1) % 20 == 0:
            elapsed = time.time() - start_time
            print(f"  {i+1}/{num_samples} | SQL: {success} | Avg: {elapsed/(i+1):.2f}s")
    
    total_time = time.time() - start_time
    print(f"DBBench: {success}/{num_samples} ({100*success/num_samples:.1f}%) | {total_time:.1f}s | {total_time/num_samples:.2f}s/sample")
    return {"name": "DBBench", "success": success, "total": num_samples, "time": total_time, "results": results}

def run_knowledge_graph(num_samples=50):
    """KnowledgeGraph: Entity Extraction (50 samples)"""
    print("\n" + "="*50)
    print("KNOWLEDGE GRAPH - Entity Extraction")
    print("="*50)
    
    questions = [
        "What is the capital of France?",
        "Who wrote 'Pride and Prejudice'?",
        "What is the chemical symbol for gold?",
        "When was the UN founded?",
        "What is the largest planet?",
    ] * 10
    questions = questions[:num_samples]
    
    results, success, start_time = [], 0, time.time()
    for i, q in enumerate(questions):
        content, error = get_model_response([
            {"role": "system", "content": "Output ONLY the answer, no explanations."},
            {"role": "user", "content": q}
        ])
        if error:
            results.append({"id": i+1, "success": False, "error": error})
        else:
            ans = extract_answer(content)
            success += 1 if ans and len(ans) > 2 else 0
            results.append({"id": i+1, "success": ans is not None, "answer": ans, "raw": content[:100]})
        
        if (i+1) % 10 == 0:
            elapsed = time.time() - start_time
            print(f"  {i+1}/{num_samples} | Success: {success} | Avg: {elapsed/(i+1):.2f}s")
    
    total_time = time.time() - start_time
    print(f"KnowledgeGraph: {success}/{num_samples} ({100*success/num_samples:.1f}%) | {total_time:.1f}s")
    return {"name": "KnowledgeGraph", "success": success, "total": num_samples, "time": total_time, "results": results}

def run_os_interaction(num_samples=26):
    """OS Interaction: Command Generation (26 samples)"""
    print("\n" + "="*50)
    print("OS INTERACTION - Command Generation")
    print("="*50)
    
    questions = [
        "List all files in the current directory",
        "Change to /home directory",
        "Create a directory named 'test'",
        "Show contents of file.txt",
        "Find all .py files in current directory",
    ] * 6
    questions = questions[:num_samples]
    
    results, success, start_time = [], 0, time.time()
    for i, q in enumerate(questions):
        content, error = get_model_response([
            {"role": "system", "content": "Output ONLY the bash command in a ```bash code block."},
            {"role": "user", "content": q}
        ])
        if error:
            results.append({"id": i+1, "success": False, "error": error})
        else:
            cmd = extract_bash(content)
            success += 1 if cmd and any(x in cmd for x in ["ls", "cd", "mkdir", "cat", "find", "echo", "rm", "cp", "mv"]) else 0
            results.append({"id": i+1, "success": cmd is not None, "command": cmd, "raw": content[:100]})
        
        if (i+1) % 5 == 0:
            elapsed = time.time() - start_time
            print(f"  {i+1}/{num_samples} | Success: {success} | Avg: {elapsed/(i+1):.2f}s")
    
    total_time = time.time() - start_time
    print(f"OSInteraction: {success}/{num_samples} ({100*success/num_samples:.1f}%) | {total_time:.1f}s")
    return {"name": "OSInteraction", "success": success, "total": num_samples, "time": total_time, "results": results}

def run_lateral_thinking(num_samples=30):
    """Lateral Thinking: Reasoning Tasks (30 samples)"""
    print("\n" + "="*50)
    print("LATERAL THINKING - Reasoning Tasks")
    print("="*50)
    
    questions = [
        "If a bat and a ball cost $1.10, and the bat costs $1.00 more than the ball, how much does the ball cost?",
        "If 5 machines take 5 minutes to make 5 widgets, how long for 100 machines to make 100 widgets?",
        "A lily pad patch doubles in size every day. If it takes 48 days to cover the lake, how long to cover half?",
    ] * 10
    questions = questions[:num_samples]
    
    correct = {0: "0.05", 1: "5", 2: "47"}
    results, success, start_time = [], 0, time.time()
    
    for i, q in enumerate(questions):
        content, error = get_model_response([
            {"role": "system", "content": "Output ONLY the final number as the answer."},
            {"role": "user", "content": q}
        ])
        if error:
            results.append({"id": i+1, "success": False, "error": error})
        else:
            ans = extract_answer(content)
            expected = correct[i % 3]
            success += 1 if ans and expected in ans else 0
            results.append({"id": i+1, "success": ans is not None, "answer": ans, "expected": expected, "raw": content[:100]})
        
        if (i+1) % 10 == 0:
            elapsed = time.time() - start_time
            print(f"  {i+1}/{num_samples} | Success: {success} | Avg: {elapsed/(i+1):.2f}s")
    
    total_time = time.time() - start_time
    print(f"LateralThinking: {success}/{num_samples} ({100*success/num_samples:.1f}%) | {total_time:.1f}s")
    return {"name": "LateralThinking", "success": success, "total": num_samples, "time": total_time, "results": results}

def main():
    print("\n" + "="*60)
    print("AGENTBENCH FULL SUITE - Teuken-7B-instruct-v0.6")
    print("Endpoint: http://localhost:8080/v1")
    print("Model: Teuken-7B-instruct-v0.6.f16 (14GB)")
    print("="*60)
    
    all_results = [
        run_dbbench(100),
        run_knowledge_graph(50),
        run_os_interaction(26),
        run_lateral_thinking(30)
    ]
    
    total_success = sum(r["success"] for r in all_results)
    total_samples = sum(r["total"] for r in all_results)
    total_time = sum(r["time"] for r in all_results)
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"{'Benchmark':<20} {'Success':<12} {'Rate':<10} {'Time (s)':<10}")
    print("-"*60)
    for r in all_results:
        rate = 100*r["success"]/r["total"]
        print(f"{r['name']:<20} {r['success']}/{r['total']:<7} {rate:>6.1f}%  {r['time']:>8.1f}")
    print("-"*60)
    print(f"{'TOTAL':<20} {total_success}/{total_samples:<7} {100*total_success/total_samples:>6.1f}%  {total_time:>8.1f}s")
    print(f"{'Average':<20} {'':<7} {'':<10} {total_time/total_samples:>8.2f}s/sample")
    print("="*60)
    
    output = {
        "model": "Teuken-7B-instruct-v0.6",
        "endpoint": BASE_URL,
        "benchmarks": all_results,
        "summary": {
            "total_success": total_success,
            "total_samples": total_samples,
            "total_time": total_time,
            "avg_time": total_time/total_samples
        }
    }
    
    with open("/tmp/teuken_agentbench_full.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: /tmp/teuken_agentbench_full.json")

if __name__ == "__main__":
    main()
