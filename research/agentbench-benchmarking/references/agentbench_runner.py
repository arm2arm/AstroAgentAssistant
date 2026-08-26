#!/usr/bin/env python3
"""
AgentBench Direct Runner - Works with the actual API format.
Use this instead of the built-in assigner for custom LLM integration.
"""
import os
import sys
import time
import json
import re
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen3.6:latest"
CONTROLLER_URL = "http://localhost:5020/api"
TASK_NAME = "os-std"  # or "dbbench-std"

def call_ollama(messages, tools=None):
    """Call Ollama chat API with function calling support."""
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
    }
    if tools:
        payload["tools"] = tools
    
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"  Ollama error: {e}")
        return None

def run_single_sample(idx, task_name):
    """Run a single sample using the correct API flow."""
    print(f"  Starting sample {idx}...")
    
    # Get initial prompt from controller
    resp = requests.post(
        f"{CONTROLLER_URL}/start_sample",
        json={"name": task_name, "index": idx}
    )
    
    if resp.status_code != 200:
        return {"error": f"start_sample failed: {resp.text}"}
    
    data = resp.json()
    messages = data.get("messages", [])
    tools = data.get("tools", [])
    
    if not messages and not tools:
        return {"error": "No initial messages or tools"}
    
    # Use index as session_id (API quirk)
    session_id = idx
    print(f"  Session ID: {session_id}, Tools: {len(tools)}")
    
    max_rounds = 15
    final_answer = None
    
    for round_num in range(max_rounds):
        # Call Ollama
        result = call_ollama(messages, tools if round_num == 0 else None)
        
        if not result:
            return {"error": "Ollama call failed", "round": round_num}
        
        response_msg = result.get("message", {})
        content = response_msg.get("content", "")
        tool_calls = response_msg.get("tool_calls", [])
        
        print(f"  Round {round_num + 1}: {len(content)} chars, {len(tool_calls)} tool calls")
        
        # Check for finish/answer action in tool calls
        if tool_calls:
            for tc in tool_calls:
                func_name = tc.get("function", {}).get("name")
                if func_name in ["finish_action", "answer_action", "commit_final_answer"]:
                    args = tc.get("function", {}).get("arguments", {})
                    final_answer = args.get("answer") or args.get("answers") or args.get("thought")
                    print(f"  Final answer: {final_answer}")
                    return {
                        "status": "COMPLETED",
                        "final_answer": final_answer,
                        "rounds": round_num + 1,
                        "history_length": len(messages)
                    }
        
        # Send response to worker via interact endpoint
        interact_resp = requests.post(
            f"{CONTROLLER_URL}/interact",
            json={
                "session_id": session_id,
                "agent_response": {
                    "content": content,
                    "status": "CONTINUE"
                }
            }
        )
        
        if interact_resp.status_code != 200:
            return {"error": f"interact failed: {interact_resp.text}", "round": round_num}
        
        result_data = interact_resp.json()
        output = result_data.get("output", {})
        status = output.get("status", "RUNNING")
        
        print(f"  Worker status: {status}")
        
        if status == "COMPLETED":
            final_answer = output.get("final_answer")
            print(f"  Completed! Answer: {final_answer}")
            return {
                "status": "COMPLETED",
                "final_answer": final_answer,
                "rounds": round_num + 1,
                "history_length": len(messages)
            }
        elif status == "FAILED":
            return {
                "status": "FAILED",
                "error": output.get("error", "Unknown error"),
                "rounds": round_num + 1,
                "history_length": len(messages)
            }
        
        # Get updated history for next round
        messages = output.get("history", messages)
    
    return {
        "status": "MAX_ROUNDS_REACHED",
        "final_answer": final_answer,
        "rounds": max_rounds,
        "history_length": len(messages)
    }

def run_benchmark(task_name, num_samples=5):
    print(f"=== AgentBench Direct Runner ===")
    print(f"Model: {MODEL_NAME}")
    print(f"Task: {task_name}")
    print(f"Samples: {num_samples}")
    print()
    
    # Get available indices
    resp = requests.get(f"{CONTROLLER_URL}/get_indices?name={task_name}")
    indices = resp.json() if resp.status_code == 200 else []
    print(f"Available samples: {len(indices)}")
    
    samples_to_run = indices[:num_samples]
    results = []
    
    start_time = time.time()
    
    for i, idx in enumerate(samples_to_run, 1):
        print(f"[{i}/{len(samples_to_run)}] Sample {idx}")
        result = run_single_sample(idx, task_name)
        results.append({"index": idx, **result})
        
        # Save intermediate results
        with open(f"/tmp/agentbench_progress.json", 'w') as f:
            json.dump(results, f, indent=2)
        
        print()
    
    elapsed = time.time() - start_time
    
    # Summary
    print("=== Summary ===")
    print(f"Total time: {elapsed:.1f}s ({elapsed/len(results):.1f}s per sample)")
    
    statuses = {}
    for r in results:
        s = r.get("status", "UNKNOWN")
        statuses[s] = statuses.get(s, 0) + 1
    
    for s, c in statuses.items():
        print(f"  {s}: {c}")
    
    # Save final results
    output_file = f"/tmp/agentbench_results_{task_name}_{MODEL_NAME.replace(':', '_')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            "model": MODEL_NAME,
            "task": task_name,
            "elapsed_seconds": elapsed,
            "results": results
        }, f, indent=2)
    
    print(f"\nResults saved to {output_file}")
    return results

if __name__ == "__main__":
    task = sys.argv[1] if len(sys.argv) > 1 else "os-std"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    run_benchmark(task, n)
