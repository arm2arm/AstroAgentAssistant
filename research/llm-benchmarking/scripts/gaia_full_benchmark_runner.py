#!/usr/bin/env python3
"""GAIA benchmark runner — full validation set (165 samples) with progress saving and auto-plots.

Use: run directly via venv or `python3 scripts/gaia_full_benchmark_runner.py`.
Saves progress every 10 samples so interrupted runs can resume.
Generates 3 plots on completion: accuracy by level, per-sample detail, response times.

Key quirks of openai-compatible endpoints with structured reasoning (e.g. aip-best):
  - Output is in `message.reasoning`, NOT `message.content`
  - Always use max_tokens >= 8192 (smaller truncates reasoning before answer)
  - Prompt explicitly: "At the end, state: 'Answer: [your answer]'"
  - Parser priority: Answer: marker → Therefore/Thus → last brackets → last paragraph
"""
import json, os, re, time, requests, numpy as np
from datasets import load_dataset

BASE_URL = os.environ.get("GAIA_BASE_URL", "http://141.33.165.84:8000/v1")
API_KEY = os.environ.get("GAIA_API_KEY", "placeholder")
MODEL_NAME = os.environ.get("GAIA_MODEL", "aip-best")
HF_TOKEN = os.environ.get("HF_TOKEN", "")
MAX_TOKENS = int(os.environ.get("GAIA_MAX_TOKENS", "8192"))
PROGRESS_FILE = os.environ.get("GAIA_PROGRESS_FILE", "/tmp/gaia_progress.json")

# ─── API call ───────────────────────────────────────────────────────────────
def call_llm(messages, max_tokens=MAX_TOKENS):
    payload = {"model": MODEL_NAME, "messages": messages, "max_tokens": max_tokens, "stream": False}
    try:
        resp = requests.post(f"{BASE_URL}/chat/completions", json=payload,
                            headers={"Authorization": f"Bearer {API_KEY}"}, timeout=180)
        return resp.json(), resp.status_code
    except Exception as e:
        return {"error": str(e)}, 0

# ─── Answer extraction ──────────────────────────────────────────────────────
def extract_answer(data):
    if "error" in data: return False, f"ERROR: {data['error']}"
    if not data.get("choices"): return False, "(no choices)"
    msg = data["choices"][0].get("message", {})
    content = msg.get("content", "")
    reasoning = msg.get("reasoning", "")
    if content and not content.strip().startswith("1.") and len(content.strip()) > 2:
        return True, content.strip(), "content"
    if reasoning:
        rt = reasoning.strip()
        for pat in [r'Answer:\s*(.+?)(?:\n|$)', r'answer:\s*(.+?)(?:\n|$)',
                    r'The answer is\s*(.+?)(?:\n|$)', r'So the answer is\s*(.+?)(?:\n|$)',
                    r'Final answer:\s*(.+?)(?:\n|$)', r'\*\*Answer:\*\*\s*(.+?)(?:\n|$)']:
            m = re.search(pat, rt, re.IGNORECASE)
            if m:
                a = re.sub(r'[.,;:!?]+$', '', m.group(1).strip())
                if a and len(a) < 200: return True, a, "reasoning (explicit)"
        bkt = re.findall(r'\*\*(.+?)\*\*', rt[-500:])
        if bkt:
            for b in reversed(bkt):
                b = b.strip().rstrip('.')
                if b and len(b) < 100 and not b.startswith('1.') and not b.startswith('Step'):
                    return True, b, "reasoning (bracket)"
        for pat in [r'(?:Therefore|Thus|Hence|In conclusion)[,.]?\s*(.+?)(?:\n|$)']:
            m = re.search(pat, rt, re.IGNORECASE)
            if m:
                a = re.sub(r'[.,;:!?]+$', '', m.group(1).strip())
                if a and len(a) < 200: return True, a, "reasoning (conclusion)"
        return True, f"[reasoning {len(rt)} chars, no clear answer]", "reasoning (no answer)"
    return False, "(empty)", "none"

# ─── Answer evaluation ──────────────────────────────────────────────────────
def evaluate(expected, model):
    if not model or model.startswith("ERROR") or "[reasoning" in model:
        return False, model
    if model.lower().strip() == expected.lower().strip(): return True, model
    if model.lower() in expected.lower() or expected.lower() in model.lower(): return True, model
    try:
        mn = re.findall(r'[\d.]+', model)
        en = re.findall(r'[\d.]+', expected)
        if mn and en:
            for a in mn:
                for b in en:
                    if float(a) == float(b): return True, model
    except ValueError: pass
    return False, model

# ─── Progress handling ──────────────────────────────────────────────────────
def save_progress(results, correct, total, idx, elapsed):
    tmp = PROGRESS_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump({"results": results, "correct": correct, "total": total,
                    "idx": idx, "elapsed": elapsed}, f, default=str)
    os.replace(tmp, PROGRESS_FILE)

# ─── Main ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 70)
    print("GAIA Benchmark Runner")
    print("=" * 70)
    print(f"Model: {MODEL_NAME}")
    print(f"Endpoint: {BASE_URL}")

    dataset = load_dataset("gaia-benchmark/GAIA", "2023_all",
                          split="validation", token=HF_TOKEN)
    available = len(dataset)
    print(f"Samples: {available}")

    level_counts = {lvl: sum(1 for s in dataset if s["Level"] == lvl)
                    for lvl in [1, 2, 3]}
    print(f"Levels: L1={level_counts[1]}, L2={level_counts[2]}, L3={level_counts[3]}")

    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            pdata = json.load(f)
        results = pdata["results"]
        correct = pdata["correct"]
        resume_idx = pdata["idx"] + 1
        start = pdata.get("elapsed", time.time())
        print(f"Resuming from sample {resume_idx}, prev correct: {correct}")
    else:
        results = []
        correct = 0
        resume_idx = 0
        start = time.time()

    print(f"Running samples {resume_idx} to {available}...\n")

    for i in range(resume_idx, available):
        sample = dataset[i]
        expected = sample["Final answer"]
        level = sample["Level"]
        elapsed_total = time.time() - start
        print(f"[{i+1}/{available}] L{level} ({correct}/{i-resume_idx+1}, {elapsed_total/60:.1f}m)...", end="", flush=True)
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Think step by step. At the end, state: 'Answer: [your answer]'"},
            {"role": "user", "content": sample["Question"]}
        ]
        t0 = time.time()
        data, status = call_llm(messages)
        elapsed = time.time() - t0
        ok, answer, source = extract_answer(data)
        is_correct, final_answer = evaluate(expected, answer)
        if is_correct: correct += 1
        results.append({
            "sample_id": i, "level": level, "expected": expected,
            "model_answer": final_answer, "correct": is_correct,
            "source": source, "time_seconds": elapsed,
        })
        if (i + 1) % 10 == 0 or i == available - 1:
            save_progress(results, correct, available, i, time.time() - start)
            print(f" saved ({correct}/{i+1-resume_idx})")
        else:
            status = "✓" if is_correct else "✗"
            print(f" {status} ({elapsed:.0f}s)")
        time.sleep(0.5)

    total_time = time.time() - start
    accuracy = correct / available if available > 0 else 0
    print(f"\n{'='*70}")
    print(f"FINAL: {correct}/{available} ({accuracy:.2%})")
    print(f"Time: {total_time:.0f}s ({total_time/60:.1f}m total)")
    for lvl in [1, 2, 3]:
        l_results = [r for r in results if r["level"] == lvl]
        if l_results:
            l_correct = sum(1 for r in l_results if r["correct"])
            print(f"  Level {lvl}: {l_correct}/{len(l_results)} ({l_correct/len(l_results):.0%})")

    with open("/tmp/gaia_full_results.json", "w") as f:
        json.dump({"model": MODEL_NAME, "endpoint": BASE_URL,
                    "benchmark": "GAIA full validation set (165 samples)",
                    "samples_tested": available, "correct": correct, "accuracy": accuracy,
                    "total_time_seconds": total_time, "results": results}, f, indent=2, default=str)
    print(f"Results: /tmp/gaia_full_results.json")

    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    levels = [r["level"] for r in results]
    correct_list = [1 if r["correct"] else 0 for r in results]
    times = [r["time_seconds"] for r in results]
    total_correct = sum(correct_list)
    overall_acc = total_correct / len(correct_list)
    mean_time = np.mean(times)
    median_time = np.median(times)
    level_stats = {}
    for lvl in [1, 2, 3]:
        c = [c for l, c in zip(levels, correct_list) if l == lvl]
        level_stats[lvl] = {"correct": sum(c), "total": len(c), "acc": sum(c)/len(c) if c else 0}

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    lp = [l for l in [1,2,3] if level_stats[l]["total"] > 0]
    bars = axes[0].bar([f'Level {l}' for l in lp], [level_stats[l]["correct"] for l in lp],
                       color=['#3498db','#e74c3c','#2ecc71'][:len(lp)], edgecolor='white', linewidth=2)
    axes[0].set_ylabel('Correct', fontsize=12, fontweight='bold')
    axes[0].set_title('Correct by Level', fontsize=13, fontweight='bold')
    mx = max(level_stats[l]["total"] for l in lp) + 2
    axes[0].set_ylim(0, mx)
    for bar, l in zip(bars, lp):
        h = bar.get_height()
        axes[0].text(bar.get_x()+bar.get_width()/2., h+0.1, f'{int(h)}/{level_stats[l]["total"]}\n({level_stats[l]["acc"]:.0%})',
                    ha='center', va='bottom', fontsize=11, fontweight='bold')
    axes[1].pie([total_correct, len(correct_list)-total_correct], labels=['Correct', 'Incorrect'],
               colors=['#27ae60','#bdc3c7'], autopct='%1.0f%%', startangle=90,
               pctdistance=0.75, wedgeprops=dict(width=0.4))
    axes[1].set_title(f'Overall: {overall_acc:.0%}', fontsize=13, fontweight='bold', pad=20)
    plt.tight_layout()
    fig.savefig("/tmp/gaia_full_accuracy.png", dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(); print("✓ gaia_full_accuracy.png")

    fig, ax = plt.subplots(figsize=(12, max(8, len(results)*0.15)))
    colors_ps = ['#27ae60' if c else '#e74c3c' for c in correct_list]
    ax.barh(range(len(results)), [1]*len(results), color=colors_ps, edgecolor='white', linewidth=1.5, height=0.8)
    ax.set_yticks(range(len(results)))
    ax.set_yticklabels([f"S{i+1}" for i in range(len(results))], fontsize=8)
    ax.set_xlim(0, 1.1)
    ax.spines[['top','right','left']].set_visible(False)
    ax.set_xticks([])
    lc = {1:'#3498db', 2:'#e74c3c', 3:'#2ecc71'}
    for i, r in enumerate(results):
        ax.text(-0.05, i, f"L{r['level']}", color=lc.get(r['level'],'gray'), fontsize=8, fontweight='bold', ha='right')
    ax.set_title('Per-Sample Results', fontsize=13, fontweight='bold')
    plt.tight_layout()
    fig.savefig("/tmp/gaia_full_per_sample.png", dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(); print("✓ gaia_full_per_sample.png")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].hist(times, bins=min(20, max(5, len(times)//3)), color='#3498db', edgecolor='white', linewidth=1.5, alpha=0.8)
    axes[0].axvline(mean_time, color='#e74c3c', linestyle='--', label=f'Mean: {mean_time:.1f}s')
    axes[0].axvline(median_time, color='#27ae60', linestyle='--', label=f'Median: {median_time:.1f}s')
    axes[0].legend(); axes[0].set_title('Response Time', fontsize=13, fontweight='bold')
    ct = [t for t,c in zip(times,correct_list) if c]
    it = [t for t,c in zip(times,correct_list) if not c]
    if ct or it:
        axes[1].boxplot([it, ct], labels=['Incorrect', 'Correct'], patch_artist=True,
            boxprops=[dict(facecolor='#e74c3c',alpha=0.3), dict(facecolor='#27ae60',alpha=0.3)],
            medianprops=dict(color='#2c3e50',linewidth=2))
    axes[1].set_title('Time: Correct vs Incorrect', fontsize=13, fontweight='bold')
    plt.tight_layout()
    fig.savefig("/tmp/gaia_full_times.png", dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(); print("✓ gaia_full_times.png")
    print("✅ GAIA Full Benchmark complete!")
