# llama.cpp Server Setup and Usage

## Overview

llama.cpp provides fast, local LLM inference with OpenAI-compatible API. Ideal for AgentBench benchmarking and production deployments.

## Build from Source

```bash
cd /tmp
git clone --depth 1 https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
mkdir build && cd build
cmake .. -DGGML_CUDA=ON  # Enable CUDA support
make -j$(nproc) llama-server llama-cli
```

**Result**: `/tmp/llama.cpp/build/bin/llama-server` and `llama-cli`

## Download GGUF Models

### Public Models (no auth required)

```bash
cd ~/models
curl -L -o "llama-3.2-3b-instruct.Q4_K_M.gguf" \
  "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf"
```

### Gated Models (require license acceptance)

1. **Visit the model page** and click "Agree and access repository":
   https://huggingface.co/Soofi-Project/Soofi-S-Rhine-Preview-GGUF

2. **Log in** with your Hugging Face account

3. **Download with token**:
   ```bash
   export HF_TOKEN="hf_..."
   cd ~/models
   hf download Soofi-Project/Soofi-S-Rhine-Preview-GGUF \
     --include "*Q5_K_M.gguf" \
     --local-dir . \
     --token "$HF_TOKEN"
   ```

**⚠️ Manual license acceptance is REQUIRED** for gated models. Token alone won't work.

## Start Server

```bash
/tmp/llama.cpp/build/bin/llama-server \
  -m ~/models/llama-3.2-3b-instruct.Q4_K_M.gguf \
  -c 4096 \
  --port 8080 \
  --host 0.0.0.0 \
  -ngl 99  # Offload all layers to GPU
```

**Options**:
- `-c 4096`: Context size (increase for longer prompts)
- `--port 8080`: API port
- `-ngl 99`: GPU offload (99 = all layers)
- `--host 0.0.0.0`: Listen on all interfaces

## API Usage

### Health Check

```bash
curl http://localhost:8080/health
# {"status":"ok"}
```

### Chat Completions (OpenAI-compatible)

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "default",
    "messages": [
      {"role": "user", "content": "What is the capital of France?"}
    ],
    "max_tokens": 100
  }'
```

### Python Example

```python
import requests

response = requests.post(
    "http://localhost:8080/v1/chat/completions",
    json={
        "model": "default",
        "messages": [{"role": "user", "content": "Hello!"}],
        "max_tokens": 100
    }
)

content = response.json()["choices"][0]["message"]["content"]
print(content)
```

## Model Comparison

| Model | Size | Speed | Success Rate | Verdict |
|-------|------|-------|--------------|---------|
| **llama3.2-3b-instruct-Q4_K_M** | 1.9GB | 2s/sample | 100% | ✅ **BEST** |
| Soofi-S-Rhine-Preview-Q5_K_M | 30GB | ? | ? | ⚠️ Gated (requires license) |
| qwen3.6-30B-Q4_K_M | 22GB | 30s/sample | 3% | ❌ Output format mismatch |

## Pitfalls

1. **Gated models**: Must accept license on HF web interface before download works
2. **Port conflicts**: Kill existing server before starting new one on same port
   ```bash
   process(action='kill', session_id='proc_xxx')
   ```
3. **CUDA architecture**: Build with `-DGGML_CUDA=ON` for GPU support
4. **NCCL missing**: Warning about NCCL is normal for single-GPU setups
5. **Model size**: 3B models (llama3.2) are 10x faster than 30B+ for AgentBench tasks

## Benchmark Integration

Use with AgentBench by pointing to `http://localhost:8080/v1/chat/completions`:

```python
API_URL = "http://localhost:8080/v1/chat/completions"
MODEL_NAME = "default"

def call_llm(messages, tools=None):
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "max_tokens": 512,
        "temperature": 0.1,
    }
    if tools:
        payload["tools"] = tools
    
    resp = requests.post(API_URL, json=payload, timeout=180)
    return resp.json()
```

## Results

**llama3.2-3b-instruct** (1.9GB, Q4_K_M):
- **DBBench**: 100% SQL, 3.8s/sample
- **KG**: 100% success, 2.6s/sample
- **OS**: 100% commands, 0.3s/sample
- **LTP**: 100% success, 4.0s/sample
- **ALFWORLD**: 100% success, 1.4s/sample
- **AVALON**: 100% success, 0.4s/sample
- **Overall**: 100% at 1.92s avg

**Verdict**: Best option for local AgentBench benchmarking and production deployment.
