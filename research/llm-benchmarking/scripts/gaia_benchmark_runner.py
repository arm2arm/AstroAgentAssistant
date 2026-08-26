#!/usr/bin/env python3
"""GAIA benchmark runner for OpenAI-compatible endpoints with reasoning field support.

Usage:
    HF_TOKEN=your_hf_token python3 gaia_benchmark_runner.py \
        --model aip-best \
        --base-url http://141.33.165.84:8000/v1 \
        --api-key placeholder \
        --samples 10 \
        --max-tokens 8192

Environment variables:
    HF_TOKEN     HuggingFace access token for GAIA dataset
    API_KEY      API key (optional for endpoints that don't require it)
"""
import argparse
import asyncio
import json
import os
import re
import sys
import time
from datasets import load_dataset
import requests

DEFAULT_ARGS = {
    "model": "aip-best",
    "base_url": "http://141.33.165.84:8000/v1",
    "api_key": "placeholder",
    "max_tokens": 8192,
    "samples": 10,
    "timeout": 300,
}

def parse_args():
    parser = argparse.ArgumentParser(description="GAIA benchmark runner")
    parser.add_argument("--model", default=DEFAULT_ARGS["model"])
    parser.add_argument("--base-url", default=DEFAULT_ARGS["base_url"])
    parser.add_argument("--api-key", default=DEFAULT_ARGS["api_key"])
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_ARGS["max_tokens"])
    parser.add_argument("--samples", type=int, default=DEFAULT_ARGS["samples"])
    parser.add_argument("--timeout", type=int, default=DEFAULT_ARGS["timeout"])
    parser.add_argument("--output", default="/tmp/gaia_bench_results.json")
    return parser.parse_args()

def call_llm(messages, base_url, api_key, model, max_tokens, timeout):
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "stream": False,
    }
    try:
        resp = requests.post(
            f"{base_url}/chat/completions",
            json=payload,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout,
        )
        data = resp.json()
        return data, resp.status_code
    except Exception as e:
        return {"error": str(e)}, 0

def extract_answer_from_response(data):
    """Extract answer from model response, handling reasoning field."""
    if "error" in data:
        return False, f"ERROR: {data['error']}", "error"
    if not data.get("choices"):
        return False, "(no choices)", "none"
    
    choice = data["choices"][0]
    msg = choice.get("message", {})
    content = msg.get("content")
    reasoning = msg.get("reasoning", "")
    
    # Try content first
    if content:
        text = content.strip()
        if text and not text.startswith("1.") and len(text) > 2:
            return True, text, "content"
    
    # Try reasoning with improved parsing
    if reasoning:
        reasoning_text = reasoning.strip()
        
        # 1. Explicit Answer: marker
        for pattern in [
            r'Answer:\s*(.+?)(?:\n|$)',
            r'answer:\s*(.+?)(?:\n|$)',
            r'The answer is\s*(.+?)(?:\n|$)',
            r'So the answer is\s*(.+?)(?:\n|$)',
            r'Final answer:\s*(.+?)(?:\n|$)',
            r'\*\*Answer:\*\*\s*(.+?)(?:\n|$)',
        ]:
            match = re.search(pattern, reasoning_text, re.IGNORECASE)
            if match:
                answer = match.group(1).strip()
                answer = re.sub(r'[.,;:!?]+$', '', answer)
                if answer and len(answer) < 200:
                    return True, answer, "reasoning (explicit)"
        
        # 2. Conclusion phrases
        for pattern in [
            r'(?:Therefore|Thus|Hence|So|In conclusion)[,.]?\s*(.+?)(?:\n|$)',
            r'(?:Therefore|Thus|Hence|So|In conclusion)[,.]?\s*\*\*(.+?)\*\*',
        ]:
            match = re.search(pattern, reasoning_text, re.IGNORECASE)
            if match:
                answer = match.group(1).strip().rstrip('.')
                if answer and len(answer) < 200:
                    return True, answer, "reasoning (conclusion)"
        
        # 3. Last bracketed content in last 500 chars
        last_part = reasoning_text[-500:]
        for pattern in [r'\*\*(.+?)\*\*', r'\`(.+?)\`']:
            matches = re.findall(pattern, last_part)
            if matches:
                for m in reversed(matches):
                    m = m.strip().rstrip('.')
                    if m and len(m) < 100 and not m.startswith('1.'):
                        return True, m, "reasoning (bracket)"
        
        # 4. Last substantial paragraph
        paragraphs = re.split(r'\n{2,}', reasoning_text)
        for p in reversed(paragraphs[-3:]):
            p = p.strip()
            if p and len(p) > 20 and len(p) < 200 and not p.startswith('1.') and not p.startswith('Step'):
                clean = re.sub(r'\*\*|`', '', p).strip().rstrip('.')
                if clean and 'Answer' not in clean:
                    return True, clean, "reasoning (last para)"
        
        # 5. Fallback
        last = reasoning_text[-300:].strip()
        if last and len(last) < 200 and not last.startswith('1.') and not last.startswith('Step'):
            return True, last, "reasoning (fallback)"
        
        return True, f"[Long reasoning ({len(reasoning_text)} chars), no answer found]", "reasoning (no answer)"
    
    return False, "(no content or reasoning)", "none"

def evaluate_sample(expected_answer, model_answer):
    """Evaluate if model response matches expected answer."""
    if not model_answer or model_answer.startswith("ERROR") or "[Long reasoning" in model_answer:
        return False, model_answer
    
    # Direct match (case-insensitive)
    if model_answer.lower().strip() == expected_answer.lower().strip():
        return True, model_answer
    
    # Substring match
    if model_answer.lower() in expected_answer.lower() or expected_answer.lower() in model_answer.lower():
        return True, model_answer
    
    # Numeric comparison
    try:
        model_nums = re.findall(r'[\d.]+', model_answer)
        expected_nums = re.findall(r'[\d.]+', expected_answer)
        if model_nums and expected_nums:
            for mn in model_nums:
                for en in expected_nums:
                    if float(mn) == float(en):
                        return True, model_answer
    except:
        pass
    
    return False, model_answer

async def main():
    args = parse_args()
    HF_TOKEN = os.environ.get("HF_TOKEN", "")
    
    print("=" * 70)
    print("GAIA Benchmark Runner")
    print("=" * 70)
    print(f"Model: {args.model}")
    print(f"Endpoint: {args.base_url}")
    print(f"Max tokens: {args.max_tokens}")
    print(f"Samples: {min(args.samples, 165)} (validation split)")
    print()
    
    # Load dataset
    print("Loading GAIA dataset...")
    dataset = load_dataset(
        "gaia-benchmark/GAIA",
        "2023_all",
        split="validation",
        token=HF_TOKEN,
    )
    print(f"Loaded {len(dataset)} samples\n")
    
    # Run samples
    results = []
    correct = 0
    total = min(args.samples, len(dataset))
    
    print(f"Running {total} samples...")
    print("=" * 70)
    
    for i in range(total):
        sample = dataset[i]
        question = sample["Question"]
        expected_answer = sample["Final answer"]
        level = sample["Level"]
        
        print(f"\nSample {i+1}/{total} (Level {level}):")
        print(f"Question: {question[:80]}...")
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Think step by step. At the end, state: 'Answer: [your answer]'"},
            {"role": "user", "content": question},
        ]
        
        start_time = time.time()
        data, status = call_llm(messages, args.base_url, args.api_key, args.model, args.max_tokens, args.timeout)
        elapsed = time.time() - start_time
        
        is_correct, model_answer, source = extract_answer_from_response(data)
        correct_flag, final_answer = evaluate_sample(expected_answer, model_answer)
        
        if correct_flag:
            correct += 1
            status_str = "✓ CORRECT"
        else:
            status_str = "✗ INCORRECT"
        
        preview = model_answer[:80]
        print(f"Expected: {expected_answer}")
        print(f"Got: {preview}{'...' if len(model_answer) > 80 else ''}")
        print(f"Source: {source}")
        print(f"Status: {status_str} ({elapsed:.1f}s)")
        
        results.append({
            "sample_id": i, "level": level, "expected": expected_answer,
            "model_answer": model_answer, "correct": correct_flag,
            "source": source, "time_seconds": elapsed,
        })
        
        if i < total - 1:
            time.sleep(0.5)
    
    accuracy = correct / total if total > 0 else 0
    
    print("\n" + "=" * 70)
    print("RESULTS:")
    print("=" * 70)
    print(f"Model: {args.model}")
    print(f"Benchmark: GAIA Level 1")
    print(f"Samples tested: {total}")
    print(f"Correct: {correct}")
    print(f"Accuracy: {accuracy:.2%}")
    
    sources = {}
    for r in results:
        s = r["source"]
        sources[s] = sources.get(s, 0) + 1
    print(f"\nSource breakdown: {json.dumps(sources)}")
    
    with open(args.output, "w") as f:
        json.dump({
            "model": args.model, "endpoint": args.base_url,
            "benchmark": "GAIA Level 1 (reasoning parse)",
            "max_tokens": args.max_tokens,
            "samples_tested": total, "correct": correct, "accuracy": accuracy,
            "results": results,
        }, f, indent=2, default=str)
    print(f"\nSaved to: {args.output}")
    print("\n✓ Benchmark complete!")

if __name__ == "__main__":
    asyncio.run(main())
