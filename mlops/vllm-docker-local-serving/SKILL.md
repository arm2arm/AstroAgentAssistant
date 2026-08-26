---
name: vllm-docker-local-serving
description: "Use when running vLLM in Docker on a local GPU host."
---

# vLLM in Docker — Local GPU Host Serving

Class: running `vllm/vllm-openai` containers on a physical GPU box (e.g. AIP ARM64 host, container named per model) and verifying the endpoint is actually usable — including agent use (tool calls). Covers container recreation, port binding, cache persistence, cold-start diagnosis.

## Known-good reference deployment (user's Qwen3.8-27B-FP8)

```bash
docker run -d --name qwen38 --gpus all --ipc host \
  -p <host-ip>:8002:8002 \
  -v vllm-cache:/root/.cache/vllm \
  -v hf-cache:/root/.cache/huggingface \
  --entrypoint vllm vllm/vllm-openai:v0.27.1-aarch64 \
  serve Qwen/Qwen3.8-27B-FP8 \
  --served-model-name qwen3.8-27b \
  --host 0.0.0.0 --port 8002 \
  --max-model-len 262144 \
  --gpu-memory-utilization 0.85 \
  --enable-prefix-caching \
  --reasoning-parser qwen3 --tool-call-parser qwen3_xml --enable-auto-tool-choice \
  --speculative-config '{"method":"dspark","model":"Doopeworld/Qwen3.8-27B-DSpark-vLLM","num_speculative_tokens":7,"draft_sample_method":"probabilistic"}'
```

Note `--entrypoint vllm` (image default entrypoint differs) and that DSpark speculative decode needs the separate draft model from HF. The bundled `serving-llms-vllm` skill is protected from curator patches — keep container-ops lessons here.

## Port binding — the loopback trap

- `-p 127.0.0.1:PORT:PORT` = loopback only. External clients get connection refused even though the container is healthy.
- A host's own LAN IP can resolve locally via `lo` (`ip route get <ip>` → `local ... dev lo`), so `curl http://<host-ip>:PORT` FROM the host tests the loopback bind, not external reachability. An "unreachable" IP may actually be the local host.
- Always confirm the real bind: `ss -tln | grep <port>`.
- When the endpoint has **no API auth**, rebind to the specific host IP (`-p <host-ip>:8002:8002`), not `0.0.0.0`, to limit exposure.

## Recreating a container without losing caches

`docker rm` destroys the container filesystem, including `/root/.cache`. Consequences:
- vLLM Triton/FlashInfer JIT compile cache lost → ~15 min re-JIT cold start (vs ~5 min warm).
- HF model cache lost → full re-download (~200 s for a 27B FP8 66-shard model).

Fix: mount named volumes for `/root/.cache/vllm` and `/root/.cache/huggingface` in the run command. If you must recreate without them, `docker cp qwen38:/root/.cache/. /tmp/cache-backup/` before `docker rm` and restore after.

## Startup phases (what normal looks like)

1. **Weight load** — `Loading safetensors checkpoint shards: NN%` progress (≈3 min for 27B FP8).
2. **JIT/warmup** — `Warming up ... Triton kernels`, `flashinfer.jit: Autotuning process starts`, then a **long silent stretch** (minutes; much longer on cold cache).
3. **API ready** — `/health` returns 200.

Diagnosing the silent stretch (compile vs. hang): `docker logs` idle + GPU 0% but the EngineCore process at ~100% CPU inside the container = compilation, not deadlock. Poll `/health` in a **background** loop (30 s interval, up to ~50 min budget) — foreground 600 s terminals time out mid-warmup and look like failures.

## Verification sequence (before declaring an endpoint usable)

1. `GET /health` → 200
2. `GET /v1/models` → confirm model id + max_model_len
3. `POST /v1/chat/completions` minimal prompt, `max_tokens` ≥ 50 (reasoning models burn tokens on reasoning content)
4. For agent use: same call with a `tools` array — confirm the response carries a well-formed `tool_calls` entry (parser-dependent; e.g. `qwen3_xml`)
5. Check external reachability from the intended client path, not just localhost
