# vLLM: Serving Gated HuggingFace Models

## Problem

Some models on HuggingFace require authentication before they can be served (e.g., `Soofi-Project/Soofi-S-Base`, Llama-2, Llama-3).

## Error Transcript

```
OSError: You are trying to access a gated repo.
Make sure to have access to it at https://huggingface.co/Soofi-Project/Soofi-S-Base.
401 Client Error. Cannot access gated repo for url ...
Access to model ... is restricted. You must have access to it and be authenticated to access it. Please log in.
```

## Solution

### 1. Log in to HuggingFace

```bash
huggingface-cli login
# Enter your HF token (get from https://huggingface.co/settings/tokens)
```

Or set environment variable:

```bash
export HF_TOKEN="hf_xxxxxxxx"
huggingface-cli login --token $HF_TOKEN
```

### 2. Verify Access

```bash
huggingface-cli whoami
# Should show your username if logged in
```

### 3. Serve the Model

```bash
vllm serve "Soofi-Project/Soofi-S-Base" --port 8000 --host 0.0.0.0
```

## Alternative: Use Public Models

If you don't have access to a gated model, use a public alternative:

```bash
# Llama-3.2 (public)
vllm serve "meta-llama/Llama-3.2-3B-Instruct" --port 8000

# Qwen3 (public)
vllm serve "Qwen/Qwen3-30B-A3B" --port 8000

# Mistral (public)
vllm serve "mistralai/Mistral-7B-Instruct-v0.3" --port 8000
```

## Docker Considerations

When running vLLM in Docker, you need to pass the token:

```bash
docker run --gpus all -p 8000:8000 \
  -e HF_TOKEN=$HF_TOKEN \
  vllm/vllm-openai:latest \
  --model "Soofi-Project/Soofi-S-Base" \
  --port 8000
```

Or use a `.netrc` file:

```bash
# ~/.netrc
machine huggingface.co
  login user
  password $HF_TOKEN
```

## Session Reference

- **Date**: 2026-07-15
- **Issue**: vLLM serve failed on gated model
- **Model**: `Soofi-Project/Soofi-S-Base`
- **Status**: Requires `huggingface-cli login` before serving
