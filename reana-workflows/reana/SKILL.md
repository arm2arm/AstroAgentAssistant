---
name: reana
title: REANA Workflow Platform — Client Setup, Workflow Patterns, and Best Practices
description: >-
  Complete guide to the REANA reproducible analytics platform: Dockerized client setup,
  multi-backend profiles, workflow authoring patterns, S3 dataset workflows, and best
  practices. Covers dev/prod backends, serial workflows, REANA_WORKSPACE usage, and
  self-learning from finished workflows.
author: Hermes Agent
date: 2026-04-30
tags: [reana, workflow, reproducibility, data-science]
---

# REANA Workflow Platform

This umbrella skill covers the full REANA workflow lifecycle: client setup, workflow authoring, execution, and analysis patterns.

---

## 1. Client Setup

### Dockerized REANA Client (Primary Method)
```bash
docker run --rm \
  -e REANA_SERVER_URL=https://reana-dev.kube.aip.de \
  -e REANA_ACCESS_TOKEN=<TOKEN> \
  reanahub/reana-client:<VERSION> ping
```

**Critical**: The client inside the container does NOT read `~/.reana/config.yaml`. Always supply `REANA_SERVER_URL` and `REANA_ACCESS_TOKEN` as environment variables.

### Multi-Backend Config (Dev + Prod)
Create `~/.reana/config.yaml`:
```yaml
dev:
  server_url: https://reanadev.kube.aip.de
  access_token: <DEV_TOKEN>
prod:
  server_url: https://reana-p4n.aip.de
  access_token: <PROD_TOKEN>
```

Run with profile:
```bash
docker run --rm \
  -v "$HOME/.reana/config.yaml:/root/.reana/config.yaml:ro" \
  -e REANA_PROFILE=dev \
  reanahub/reana-client:<VERSION> ping
```

### Workflow Execution with Local Files
When running a local workflow directory via Dockerized client, **set the container working directory**:
```bash
docker run -i --rm \
  -e REANA_SERVER_URL=$REANA_SERVER_URL \
  -e REANA_ACCESS_TOKEN=$REANA_ACCESS_TOKEN \
  -v $(pwd):/workspace \
  -w /workspace \
  reanahub/reana-client:0.95.0-alpha.3 \
  run -w my-workflow -f /workspace/reana.yaml
```

For native `reana-client`, run from the project/workflow directory and use the local file path:
```bash
cd /path/to/workflow-project
reana-client run -w my-workflow -f reana.yaml
```
Do not pass Docker-only paths such as `/workspace/reana.yaml` to a native client. See `references/reana-operator-live-smoke.md` for the live-tested native-vs-Docker path handling and generated-YAML pitfalls. See `references/reana-client-failover.md` for the user-friendly native-client/Docker fallback policy using `reanahub/reana-client`.

### Token Safety
- Export token only in current shell: `export REANA_ACCESS_TOKEN=...`
- Do NOT write it into any file or skill
- File permissions 600 for config files

---

## 2. Workflow Authoring Patterns

### Minimal `reana.yaml` Template
```yaml
environment:
  repo: https://gitlab-p4n.aip.de/punch_public/reana/environments
  name: python-3.12-slim

workflow:
  type: serial
  specification:
    - name: step-name
      type: run
      image: python:3.12-slim
      command: python my_script.py
      compute_backend: kubernetes
      resources:
        memory: 32gb          # MANDATORY — org policy
        runtime: 02:00:00
      outputs:
        files:
          - output.png
```

### MANDATORY Rules
- **Never** modify the `environment:` block to point to a custom repo — use the central repository
- Memory is **forced to 32 GB** as per policy
- Use `kubernetes_memory_limit: "32Gi"` and `kubernetes_job_timeout` for newer serial syntax

### Using $REANA_WORKSPACE for Custom Scripts
```yaml
inputs:
  files:
    - my_script.py
workflow:
  type: serial
  specification:
    - name: step-name
      type: run
      environment: gitlab-p4n.aip.de:5005/p4nreana/reana-env:py311-astro
      commands:
        - bash -c "cd $REANA_WORKSPACE && pip install --quiet <deps> && python my_script.py"
      compute_backend: kubernetes
      resources:
        memory: 32gb
        runtime: 02:00:00
      outputs:
        files:
          - output.png
```

**Key**: Always `cd $REANA_WORKSPACE` explicitly — the working directory may not be the workspace root.

### Using uploaded scripts in generated workflows
Prefer a simple command that runs from REANA's execution directory. A live AIP dev-backend smoke test showed that injecting `cd "$REANA_WORKSPACE"` into generated commands can fail during workflow parameter expansion on some client/server combinations.

Robust pattern:
```yaml
commands:
  - bash -lc 'if [ -f requirements.txt ]; then pip install --quiet -r requirements.txt; fi && python3 analysis.py'
```

Avoid unless already verified for the target backend:
```yaml
commands:
  - bash -lc 'cd "$REANA_WORKSPACE" && python3 analysis.py'
```

### Avoiding Inline Script YAML Errors
- **Inline `bash -c "cat <<'PY' ... PY"` blocks break YAML parsing** — always use separate script files
- If using separate scripts, list them under `inputs.files`
- Use a list of commands instead of one long `bash -c`:
  ```yaml
  commands:
    - pip install --quiet <deps>
    - python script.py
  ```

---

## 3. S3 Dataset Workflows

### ShBoost 2024 Dataset Access Pattern
```python
import dask.dataframe as dd

S3_ENDPOINT = "https://s3.data.aip.de:9000"
S3_GLOB = "s3://shboost2024/shboost_08july2024_pub.parq/*.parquet"
STORAGE_OPTS = {
    "use_ssl": True,
    "anon": True,
    "client_kwargs": {"endpoint_url": S3_ENDPOINT},
}

df = dd.read_parquet(S3_GLOB, storage_options=STORAGE_OPTS)
```

### Caching Pattern
```python
CACHE_PATH = "shboost_cache.parquet"

def load_or_fetch(force_refresh=False):
    if os.path.isfile(CACHE_PATH) and not force_refresh:
        return pd.read_parquet(CACHE_PATH)
    df = dd.read_parquet(S3_GLOB, storage_options=STORAGE_OPTS)
    df = df[["bprp0", "mg0"]]  # select only needed columns
    df.to_parquet(CACHE_PATH, write_index=False)
    return pd.read_parquet(CACHE_PATH)
```

### REANA Workflow for S3 Plot
```yaml
inputs:
  files:
    - plot_cmd.py

workflow:
  type: serial
  specification:
    steps:
      - name: build-plot
        environment: gitlab-p4n.aip.de:5005/p4nreana/reana-env:py311-astro-ml.2891a60c
        kubernetes_memory_limit: "32Gi"
        kubernetes_job_timeout: 7200
        commands:
          - python3 plot_cmd.py --force-refresh
        outputs:
          files:
            - cmd.png
            - shboost_cache.parquet
```

### Common S3 Pitfalls
- Wrong S3 path: use `shboost_08july2024_pub.parq/*.parquet`
- Missing endpoint URL: include `client_kwargs.endpoint_url`
- Missing columns: verify column names with metadata
- Large dataset first run: ~200 GB metadata read, subsequent runs fast via cache

### Unauthenticated S3 Upload (curl fallback)
When the boto3-based `s3_media_upload.py` returns `InvalidAccessKeyId` for S3 buckets that use anonymous/public access (no auth required), use curl directly:
```bash
KEY="hermes/$(python3 -c 'import uuid; print(uuid.uuid4().hex[:16])")mp4"
curl -X PUT \
  -H "x-amz-acl: public-read" \
  -T /path/to/file.mp4 \
  "https://s3.data.aip.de:9000/scr4agent/$KEY"
echo "URL: https://s3.data.aip.de:9000/scr4agent/$KEY"
```
Key points:
- **Do NOT use `--url` flag** with curl PUT for S3 — it causes `SignatureDoesNotMatch` (curl sends `--url` in `--next` mode, mangling the PUT body).
- UUID-based keys under `hermes/` prefix; no auth headers needed.
- Target bucket: `scr4agent` at `https://s3.data.aip.de:9000`.

---

## 4. Post-Run Operations

### Standard Commands
```bash
reana-client ping                      # verify server connectivity
reana-client status -w <name>          # workflow status
reana-client logs -w <name>            # streaming logs
reana-client ls -w <name>              # list workspace files
reana-client download -w <name> -o .   # download outputs
```

### Dockerized Versions
```bash
docker run --rm \
  -e REANA_SERVER_URL=$REANA_SERVER_URL \
  -e REANA_ACCESS_TOKEN=$REANA_ACCESS_TOKEN \
  reanahub/reana-client:<VERSION> <command>
```

### Listing Finished Workflows
```bash
docker run --rm \
  -e REANA_SERVER_URL=$REANA_SERVER_URL \
  -e REANA_ACCESS_TOKEN=$REANA_ACCESS_TOKEN \
  reanahub/reana-client:<VERSION> list -v --json | \
  jq -r '.[:10][] | [.name, .run_number, .created, .status, .id] | @tsv' | column -t
```

### Self-Learning from Finished Workflows
1. List finished workflows: `reana-client list -v --json | jq '[.[] | select(.status=="finished")]'`
2. Download each `reana.yaml`: `reana-client download -w <id> -f reana.yaml -o <name>_reana.yaml`
3. Analyze patterns: `grep -h "environment:" *.yaml | sort | uniq -c | sort -nr`

---

## 5. Pitfalls & Best Practices

### `reana-client create` Bug
Older client versions raise "list indices must be integers or slices, not str". Workaround: ignore error, proceed to `reana-client start`.

### `REANA_WORKON` Environment Variable
If set to another workflow, `reana-client create` may refuse. Unset it: `unset REANA_WORKON`.

### Large Data Uploads
If workflow needs large input files, copy them into the folder before running — REANA uploads the entire folder as the workspace.

### Token Expiry
Access token may expire; regenerate via the REANA UI if you see authentication errors.

### Re-run Failed Workflows
Simply run the same `reana-client run ...` command again — REANA creates a new run number.

### Output Verification
After `run`, use `reana-client logs -w <name>` to confirm the script executed and outputs are produced.

---

## 6. REANA Operator Pattern

When the user asks natural-language operational questions like “job status”, “recent failed jobs”, “available backends”, or “run this code on REANA”, use the operator pattern in `references/reana-operator-design.md`.

Key rules:
- Assume `REANA_SERVER_URL` and `REANA_ACCESS_TOKEN` are already exported for execution; do not ask for or write tokens by default.
- Start by checking those variables, but never print `REANA_ACCESS_TOKEN`.
- Support job status, logs, recent jobs filtered by normalized status, backend/profile reporting, project scaffolding, `reana.yaml` validation, run submission, output listing/download, and failed-job diagnosis.
- Prefer separate script files plus `cd "$REANA_WORKSPACE"`; avoid inline heredoc scripts in YAML.
- Before running, validate that declared input files exist and that the upload workspace does not include `.git/`, `.reana/`, `.env`, private keys, or unintended huge files.

## 6. Operator-Style REANA Skill Pattern

For user-facing REANA automation, prefer a single operator/front-door skill over a long list of narrow one-off skills. The operator should map natural-language requests to status checks, backend inspection, recent-job filtering, logs, downloads, project scaffolding, YAML validation, and workflow submission.

Key rules:
- Assume `REANA_SERVER_URL` and `REANA_ACCESS_TOKEN` are already exported for execution.
- Never write or print `REANA_ACCESS_TOKEN`; display only whether a token is configured.
- Prefer native `reana-client` if installed; otherwise use Docker with `REANA_CLIENT_IMAGE` (`reanahub/reana-client` by default). Support `REANA_CLIENT_MODE=auto|native|docker` for explicit mode control.
- Scaffold separate script files plus `reana.yaml`; avoid inline heredoc code blocks.
- Explicitly `cd "$REANA_WORKSPACE"` when running uploaded scripts.
- Generate `.reanaignore` for `.git/`, `.env`, `.reana/`, caches, virtualenvs, and outputs.

See `references/reana-operator-pattern.md` for the concrete CLI shape, supported intents, and validation checklist used for the `reana-operator` implementation.

See `references/reana-task-first-operator.md` for the task-first REANA execution pattern: generate environment-aware `reana.yaml` from imports/requirements and AIP `reana-env` library availability, then submit via native→Docker client failover.

See `references/reana-task-preserve-existing-script.md` for the pitfall where task mode overwrites an existing `analysis.py` with placeholder scaffold code; preserve existing scripts unless `--code` or `--command` is explicitly supplied, and verify downloaded outputs rather than trusting `finished` alone.

## 7. Quick Reference Card

| Task | Command |
|------|---------|
| Ping server | `reana-client ping` |
| List workflows | `reana-client list -v --json` |
| Create workflow | `reana-client create -w <name> -f reana.yaml` |
| Start workflow | `reana-client start -w <name>` |
| Check status | `reana-client status -w <name>` |
| View logs | `reana-client logs -w <name>` |
| List files | `reana-client ls -w <name>` |
| Download output | `reana-client download -w <name> -o .` |
| Upload file | `reana-client upload -w <name> file.py` |