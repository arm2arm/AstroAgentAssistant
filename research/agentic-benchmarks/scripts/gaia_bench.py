#!/usr/bin/env python3
"""
GAIA Benchmark Runner — class-level script for agentic-benchmarks skill.

Run against any OpenAI-compatible endpoint. Handles:
  - Reasoning-field aware parsing (model outputs in 'reasoning' not 'content')
  - Multi-tier answer matching (exact, substring, numeric, year)
  - Progress checkpointing (crash recovery every 5 samples)
  - Plot generation (overall accuracy, per-sample, timing, source)

Usage:
  python3 gaia_bench.py --model <name> --endpoint <url> [--samples 50]

Environment variables:
  HF_TOKEN — HuggingFace token for GAIA dataset access
  API_KEY  — API key (default: placeholder)
"""
import json, os, re, sys, time, random, argparse
import numpy as np
import requests
from datasets import load_dataset

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_PLOTS = True
except ImportError:
    HAS_PLOTS = False

DEFAULT_MODEL = "aip-best"
DEFAULT_ENDPOINT = "http://141.33.165.84:8000/v1"
DEFAULT_TOKENS = 8192
DEFAULT_SAMPLES = 50
PROGRESS_FILE = "/tmp/gaia_progress.json"


def call_llm(messages, endpoint, model, max_tokens, api_key, timeout=120):
    """Call an OpenAI-compatible chat endpoint."""
    payload = {"model": model, "messages": messages, "max_tokens": max_tokens, "stream": False}
    try:
        resp = requests.post(f"{endpoint}/chat/completions", json=payload,
                            headers={"Authorization": f"Bearer {api_key}"}, timeout=timeout)
        return resp.json(), resp.status_code
    except Exception as e:
        return {"error": str(e)}, 0


def extract_answer(data):
    """
    Extract answer from model response.
    Handles both 'content' and 'reasoning' fields.
    Returns (ok, answer_string, source_type).
    """
    if "error" in data:
        return False, f"ERROR: {data['error']}", "error"
    if not data.get("choices"):
        return False, "(no choices)", "empty"

    msg = data["choices"][0].get("message", {})
    content = msg.get("content", "")
    reasoning = msg.get("reasoning", "")

    # Try content first (clean answer without reasoning overhead)
    if content:
        text = content.strip()
        if text and not text.startswith("1.") and len(text) > 2:
            return True, text, "content"

    # Try reasoning with priority-ordered patterns
    if reasoning:
        rt = reasoning.strip()

        # 1. Explicit answer markers
        for pat in [r'Answer:\s*(.+?)(?:\n|$)', r'answer:\s*(.+?)(?:\n|$)',
                    r'The answer is\s*(.+?)(?:\n|$)', r'So the answer is\s*(.+?)(?:\n|$)',
                    r'Final answer:\s*(.+?)(?:\n|$)', r'\*\*Answer:\*\*\s*(.+?)(?:\n|$)']:
            m = re.search(pat, rt, re.IGNORECASE)
            if m:
                a = re.sub(r'[.,;:!?]+$', '', m.group(1).strip())
                if a and len(a) < 200:
                    return True, a, "reasoning (explicit)"

        # 2. Bracketed text in last 500 chars
        bkt = re.findall(r'\*\*(.+?)\*\*', rt[-500:])
        if bkt:
            for b in reversed(bkt):
                b = b.strip().rstrip('.')
                if b and len(b) < 100 and not b.startswith('1.') and not b.startswith('Step'):
                    return True, b, "reasoning (bracket)"

        # 3. Conclusion phrases
        for pat in [r'(?:Therefore|Thus|Hence|So|In conclusion)[,.]?\s*(.+?)(?:\n|$)']:
            m = re.search(pat, rt, re.IGNORECASE)
            if m:
                a = re.sub(r'[.,;:!?]+$', '', m.group(1).strip())
                if a and len(a) < 200:
                    return True, a, "reasoning (conclusion)"

        # 4. Last paragraph fallback
        paragraphs = re.split(r'\n{2,}', rt)
        for p in reversed(paragraphs[-3:]):
            p = p.strip()
            if p and 20 < len(p) < 200 and not p.startswith('1.') and not p.startswith('Step'):
                clean = re.sub(r'\*\*|`', '', p).strip().rstrip('.')
                if 'Answer' not in clean:
                    return True, clean, "reasoning (paragraph)"

        # 5. Long reasoning, no answer found
        return True, f"[reasoning {len(rt)} chars, no clear answer]", "reasoning (no answer)"

    return False, "(empty)", "none"


def evaluate(expected, model_answer):
    """
    Multi-tier answer matching for GAIA evaluation.
    Returns (is_correct, clean_answer_string).
    """
    # Reject obviously failed extractions
    if not model_answer or model_answer.startswith("ERROR") or "[reasoning" in model_answer:
        return False, model_answer

    # Tier 1: Exact match (case-insensitive)
    if model_answer.lower().strip() == expected.lower().strip():
        return True, model_answer

    # Tier 2: Substring match
    if model_answer.lower() in expected.lower() or expected.lower() in model_answer.lower():
        return True, model_answer

    # Tier 3: Numeric comparison
    try:
        mn = re.findall(r'[\d.]+', model_answer)
        en = re.findall(r'[\d.]+', expected)
        if mn and en:
            for a in mn:
                for b in en:
                    if float(a) == float(b):
                        return True, model_answer
    except (ValueError, OverflowError):
        pass

    # Tier 4: Year comparison (4-digit years)
    my = re.findall(r'\d{4}', model_answer)
    ey = re.findall(r'\d{4}', expected)
    if my and ey and my[0] == ey[0]:
        return True, model_answer

    return False, model_answer


def save_progress(results, correct, total, idx, elapsed):
    """Save checkpoint for crash recovery."""
    with open(PROGRESS_FILE, "w") as f:
        json.dump({"results": results, "correct": correct, "total": total,
                    "idx": idx, "elapsed": elapsed}, f, default=str)


def generate_plots(results, output_dir="/tmp"):
    """Generate benchmark visualization plots."""
    if not HAS_PLOTS:
        print("matplotlib not available, skipping plots")
        return

    os.makedirs(output_dir, exist_ok=True)

    levels = [r["level"] for r in results]
    correct_list = [1 if r["correct"] else 0 for r in results]
    times = [r["time_seconds"] for r in results]

    total_correct = sum(correct_list)
    total_samples = len(correct_list)
    overall_acc = total_correct / total_samples if total_samples > 0 else 0
    mean_time = np.mean(times)
    median_time = np.median(times)

    # Level statistics — CRITICAL: GAIA dataset levels are STRINGS ("1","2","3"), not integers.
    # Comparing str → int returns False, producing 0 matches and NaN in plots.
    # Always use string keys when filtering results by level.
    level_stats = {}
    for lvl in ["1", "2", "3"]:
        c = [c for l, c in zip(levels, correct_list) if str(l) == str(lvl)]
        level_stats[lvl] = {"correct": sum(c), "total": len(c),
                            "acc": sum(c)/len(c) if c else 0}

    # Plot 1: Overall accuracy (bar + donut)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    levels_present = [l for l in [1,2,3] if level_stats[l]["total"] > 0]
    labels = [f'Level {l}' for l in levels_present]
    data = [level_stats[l]["correct"] for l in levels_present]
    counts = [level_stats[l]["total"] for l in levels_present]
    accs = [level_stats[l]["acc"] for l in levels_present]
    colors_bar = ['#3498db', '#e74c3c', '#2ecc71'][:len(levels_present)]

    bars = axes[0].bar(labels, data, color=colors_bar, edgecolor='white', linewidth=2)
    axes[0].set_ylabel('Correct Answers', fontweight='bold')
    axes[0].set_title('Correct Answers by Level', fontweight='bold')
    axes[0].set_ylim(0, max(counts)+2 if counts else 2)
    for bar, cnt, acc in zip(bars, counts, accs):
        axes[0].text(bar.get_x()+bar.get_width()/2., bar.get_height()+0.1,
                    f'{int(bar.get_height())}/{cnt}\n({acc:.0%})',
                    ha='center', va='bottom', fontweight='bold')

    _, _, _ = axes[1].pie([total_correct, total_samples-total_correct],
        labels=['Correct', 'Incorrect'], colors=['#27ae60', '#bdc3c7'],
        autopct='%1.0f%%', startangle=90, wedgeprops=dict(width=0.4, edgecolor='white'))
    axes[1].set_title(f'Overall Accuracy: {overall_acc:.0%}', fontweight='bold', pad=20)
    center = plt.Circle((0,0), 0.25, fc='white')
    axes[1].add_artist(center)
    axes[1].text(0, 0.05, f'{total_correct}/{total_samples}', ha='center', va='center',
                fontsize=16, fontweight='bold')
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, "gaia_overall_accuracy.png"),
               dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

    # Plot 2: Per-sample results
    fig, ax = plt.subplots(figsize=(12, max(8, len(results)*0.15)))
    colors_ps = ['#27ae60' if c else '#e74c3c' for c in correct_list]
    ax.barh(range(len(results)), [1]*len(results), color=colors_ps,
            edgecolor='white', linewidth=1.5, height=0.8)
    ax.set_yticks(range(len(results)))
    ax.set_yticklabels([f"S{i+1}" for i in range(len(results))], fontsize=8)
    ax.set_title('Per-Sample Results', fontweight='bold')
    ax.set_xlim(0, 1.1)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.set_xticks([])
    lc = {1: '#3498db', 2: '#e74c3c', 3: '#2ecc71'}
    for i, r in enumerate(results):
        ax.text(-0.05, i, f"L{r['level']}", color=lc.get(r['level'], 'gray'),
                fontsize=8, fontweight='bold', ha='right')
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, "gaia_per_sample.png"),
               dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

    # Plot 3: Response times
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].hist(times, bins=min(15, max(5, len(times)//3)), color='#3498db',
                edgecolor='white', linewidth=1.5, alpha=0.8)
    axes[0].axvline(mean_time, color='#e74c3c', linestyle='--', label=f'Mean: {mean_time:.1f}s')
    axes[0].axvline(median_time, color='#27ae60', linestyle='--', label=f'Median: {median_time:.1f}s')
    axes[0].legend()
    axes[0].set_title('Response Time Distribution', fontweight='bold')

    correct_t = [t for t, c in zip(times, correct_list) if c]
    incorrect_t = [t for t, c in zip(times, correct_list) if not c]
    if incorrect_t or correct_t:
        axes[1].boxplot([incorrect_t, correct_t],
                        labels=['Incorrect', 'Correct'], patch_artist=True,
                        boxprops=[dict(facecolor='#e74c3c', alpha=0.3),
                                  dict(facecolor='#27ae60', alpha=0.3)])
    axes[1].set_title('Response Time: Correct vs Incorrect', fontweight='bold')
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, "gaia_response_times.png"),
               dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"Plots saved to {output_dir}/")


def main():
    parser = argparse.ArgumentParser(description="GAIA Benchmark Runner")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model name")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT, help="API endpoint")
    parser.add_argument("--tokens", type=int, default=DEFAULT_TOKENS,
                        help="max_tokens (default: 8192)")
    parser.add_argument("--samples", type=int, default=DEFAULT_SAMPLES,
                        help="Number of samples (default: 50)")
    parser.add_argument("--no-plots", action="store_true", help="Skip plot generation")
    parser.add_argument("--api-key", default="placeholder", help="API key")
    parser.add_argument("--resume", action="store_true", help="Resume from last checkpoint")
    args = parser.parse_args()

    model = args.model
    endpoint = args.endpoint
    max_tokens = args.tokens
    n_samples = args.samples
    api_key = args.api_key

    print("=" * 60)
    print(f"GAIA Benchmark: {model}")
    print(f"Endpoint: {endpoint}")
    print(f"Max tokens: {max_tokens}")
    print(f"Samples: {n_samples}")
    print("=" * 60)

    # Load dataset
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        print("ERROR: HF_TOKEN environment variable not set")
        sys.exit(1)

    print("\nLoading GAIA dataset (validation split)...")
    dataset = load_dataset("gaia-benchmark/GAIA", "2023_all",
                          split="validation", token=hf_token)
    available = len(dataset)
    print(f"Available: {available} samples")

    # Select samples
    random.seed(42)
    indices = random.sample(range(available), min(n_samples, available))
    selected = [dataset[i] for i in indices]

    level_counts = {}
    for s in selected:
        level_counts[s["Level"]] = level_counts.get(s["Level"], 0) + 1
    print(f"Selected: {len(selected)} samples. Levels: {level_counts}")

    # Resume from checkpoint if available
    results = []
    correct = 0
    resume_idx = 0
    start_time = time.time()

    if args.resume and os.path.exists(PROGRESS_FILE):
        print(f"\nResuming from checkpoint...")
        with open(PROGRESS_FILE) as f:
            pdata = json.load(f)
        results = pdata["results"]
        correct = pdata["correct"]
        resume_idx = pdata["idx"] + 1
        start_time = pdata.get("elapsed", time.time() - start_time)
        print(f"Resuming from sample {resume_idx}, previous correct: {correct}")
    elif os.path.exists(PROGRESS_FILE):
        print(f"\nCheckpoint file exists but --resume not set. "
              f"To resume, use --resume flag.")

    print(f"\nRunning samples {resume_idx}/{len(selected)}...")

    for i in range(resume_idx, len(selected)):
        sample = selected[i]
        question = sample["Question"]
        expected = sample["Final answer"]
        level = sample["Level"]

        elapsed_total = time.time() - start_time
        print(f"\n[{i+1}/{len(selected)}] L{level} "
              f"(correct: {correct}/{i-resume_idx+1}, {elapsed_total:.0f}s)...",
              end="", flush=True)

        messages = [
            {"role": "system",
             "content": "You are a helpful assistant. Think step by step. "
                       "At the end, state: 'Answer: [your answer]'"},
            {"role": "user", "content": question}
        ]

        t0 = time.time()
        data, status = call_llm(messages, endpoint, model, max_tokens, api_key)
        elapsed = time.time() - t0

        ok, answer, source = extract_answer(data)
        is_correct, final_answer = evaluate(expected, answer)

        if is_correct:
            correct += 1

        results.append({
            "sample_id": i, "level": level, "expected": expected,
            "model_answer": final_answer, "correct": is_correct,
            "source": source, "time_seconds": elapsed,
        })

        # Checkpoint every 5 samples
        if (i + 1) % 5 == 0:
            save_progress(results, correct, len(selected), i,
                         time.time() - start_time)
            print(f" [checkpoint]")
        else:
            print(f" {'✓' if is_correct else '✗'} ({elapsed:.0f}s)")

        time.sleep(0.5)  # Rate limiting

    # Final results
    total_time = time.time() - start_time
    accuracy = correct / len(selected) if len(selected) > 0 else 0

    print("\n" + "=" * 60)
    print(f"FINAL: {correct}/{len(selected)} ({accuracy:.2%})")
    print(f"Time: {total_time:.0f}s ({total_time/len(selected):.1f}s/sample)")

    for lvl in [1, 2, 3]:
        lr = [r for r in results if r["level"] == lvl]
        if lr:
            lc = sum(1 for r in lr if r["correct"])
            print(f"  Level {lvl}: {lc}/{len(lr)} ({lc/len(lr):.0%})")

    # Save results
    output_file = "/tmp/gaia_bench_results.json"
    with open(output_file, "w") as f:
        json.dump({
            "model": model, "endpoint": endpoint,
            "benchmark": "GAIA (validation)",
            "samples_tested": len(selected), "correct": correct,
            "accuracy": accuracy, "total_time_seconds": total_time,
            "results": results,
        }, f, indent=2, default=str)
    print(f"\nResults: {output_file}")

    # Generate plots
    if not args.no_plots and HAS_PLOTS:
        print("\nGenerating plots...")
        generate_plots(results)
        print("Done.")

    print("\n✅ Benchmark complete.")


if __name__ == "__main__":
    main()
