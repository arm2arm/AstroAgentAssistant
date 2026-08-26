#!/usr/bin/env python3
"""Measure tokens/sec of OpenAI-compatible streaming endpoints.

Usage:
    python3 tps_probe.py [BASE_URL [MODEL] ...]

Defaults: http://localhost:8088/v1 Qwen/Qwen3.8-27B
Each probe runs one 300-word-essay prompt (temp=0, max_tokens=8192) and
reports TTFT for the first reasoning token and the first content token,
then decode rates for both phases.

WHY THIS EXISTS (2026-08-19, Qwen3.8-27B on vLLM 0.27.1):
  * Thinking-enabled models stream chain-of-thought in a SEPARATE
    `delta.reasoning` field, not `delta.content`. A probe counting only
    `content` reports 0 tok/s while the model is actively generating.
  * Some servers cap thinking (~tens of reasoning tokens, ~1s TTFT),
    others do not (6k+ reasoning tokens, minutes of TTFT). The same
    prompt therefore behaves very differently across deployments of
    the same model — measure, don't assume.
  * The model id to send is whatever `/v1/models` lists (e.g. a renamed
    alias like `aip-best`), NOT the HuggingFace path — sending the path
    404s with "The model ... does not exist".

Stdlib only (urllib); no API key required for unauthenticated local
vLLM instances (pass a header via the KEY env var if needed).
"""
import json
import os
import sys
import time
import urllib.request


def probe(base_url: str, model: str) -> dict:
    key = os.environ.get("OPENAI_API_KEY", "EMPTY")
    url = base_url.rstrip("/") + "/chat/completions"
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user",
                      "content": "Write a 300-word paragraph about the "
                                 "history of sine waves."}],
        "max_tokens": 8192,
        "stream": True,
        "temperature": 0,
    }).encode()
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {key}"})
    t0 = time.time()
    first_reason = first_content = None
    n_r = n_c = 0
    finish = None
    with urllib.request.urlopen(req, timeout=900) as r:
        for line in r:
            line = line.decode().strip()
            if not line.startswith("data:"):
                continue
            d = line[5:].strip()
            if d == "[DONE]":
                break
            try:
                ch = json.loads(d)["choices"][0]
                delta = ch.get("delta", {})
                if ch.get("finish_reason"):
                    finish = ch["finish_reason"]
                if delta.get("content"):
                    if first_content is None:
                        first_content = time.time() - t0
                    n_c += len(delta["content"])
                if delta.get("reasoning"):
                    if first_reason is None:
                        first_reason = time.time() - t0
                    n_r += len(delta["reasoning"])
            except Exception:
                pass
    total = time.time() - t0
    t_first = min(t for t in (first_content, first_reason) if t is not None)
    # Combined decode rate over the whole generation window.
    combined = (n_r + n_c) / max(total - t_first, 0.01) / 4.0
    # Content-phase rate: content chars over the window from first content
    # token to end (approximate; reasoning may still interleave).
    content_rate = (n_c / max(total - (first_content or total), 0.01) / 4.0
                    if n_c else 0.0)
    return {
        "url": base_url, "model": model, "finish": finish,
        "reasoning_chars": n_r, "content_chars": n_c,
        "ttft_any_s": round(t_first, 2) if t_first else None,
        "ttft_content_s": round(first_content, 2) if first_content else None,
        "total_s": round(total, 2),
        "combined_tps": round(combined, 1),
        "content_phase_tps": round(content_rate, 1),
    }


def main() -> None:
    args = sys.argv[1:]
    probes = []
    i = 0
    while i + 1 < len(args) or i + 1 == len(args):
        url = args[i]
        model = args[i + 1] if i + 1 < len(args) else "default"
        probes.append((url, model))
        i += 2 if i + 1 < len(args) else 1
    for url, model in probes:
        try:
            print(json.dumps(probe(url, model), indent=2))
        except Exception as e:  # noqa: BLE001
            print(json.dumps({"url": url, "model": model, "error": str(e)}))


if __name__ == "__main__":
    main()
