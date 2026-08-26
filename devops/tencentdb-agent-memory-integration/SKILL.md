---
name: tencentdb-agent-memory-integration
title: TencentDB Agent Memory deployment and Hermes proxy routing
description: "TencentDB deploy, asset creation, and Hermes proxy wiring."
author: Arman Khalatyan & Hermi
date: 2026-08-06
tags: [docker, llm-middleware, proxy-routing, memory-infrastructure, tencentdb]
---

# TencentDB Agent Memory — Deployment & Hermes Integration

## Architecture

Three Docker containers on a user-created network (`tdai-memory-stack`):

| Container | Port | Service | Auth gate |
|-----------|------|---------|-----------|
| `tdai-memory-core` | 8420 | SQLite memory store, L0→L3 pipeline | `x-tdai-user-key` header only |
| `tdai-memory-hub` | 8125 | Admin panel (SPA), user/asset management | Bearer token via panel login |
| `tdai-proxy` | 8096 | LLM request proxy with memory injection | Bearer + x-team-id + x-agent-id + x-task-id + x-conversation-id |
| Knowledge API | 8424 | Wiki/codegraph tools endpoint | Internal only |

Proxy intercepts LLM calls, retrieves matching memory (L2/L3 persona + skills), injects into system prompt, then forwards to upstream.

## Pre-deployment checklist

1. Ensure ports 8096, 8125, 8420, 8424 are free on host
2. Have a working LLM endpoint for both `MEMORY_LLM_*` (distillation) AND `PROXY_UPSTREAM_*` (user inference). Test upstream directly first — dead API key causes 401 that looks like proxy failure.
3. Bind to localhost if internal-only: `-p 127.0.0.1:PORT:PORT`

## Deployment steps

```bash
git clone https://github.com/TencentCloud/TencentDB-Agent-Memory.git /path/to/deploy
cd deploy/deploy/global-images
cp .env.example .env
# Edit .env — fill MEMORY_LLM_* and PROXY_UPSTREAM_* sections
./verify.sh            # dry-run + LLM probe (use --skip-llm to skip)
./start-all.sh         # pulls images, creates docker network, boots 3 containers
```

On first boot: `init-admin` creates admin user, generates random `sk-mem-****` key in `.admin-key`. Key is reused across restarts if volume survives.

## API discovery — docker exec workaround

Their REST API is undocumented. No OpenAPI spec, no Swagger. `auth/verify` requires POST with JSON body `{"user_key":"..."}` and Content-Type: application/json. Python urllib fails (empty body, wrong method); curl inside container matches the startup script environment:

```bash
ADMIN_KEY=$(cat deploy/global-images/.admin-key)

docker exec tdai-memory-core sh -c "
  curl -s -k -X POST http://localhost:8420/v3/meta/auth/verify \
    -H 'x-tdai-service-id: default' \
    -H 'Content-Type: application/json' \
    -d '{\"user_key\":\"'"$ADMIN_KEY"'\"}'"
```

Returns `user_id` — needed for team/agent/task creation.

### Team → Agent → Task provisioning order

**Order is strict:** Team first, then Agent, then Task. All require admin `user_id`.

⚠️ **Task create uses different field names:** needs `title` AND `creator_user_id` (not `name`/`owner_user_id` like Team/Agent). Mixing these up → 400 validation error.

```bash
# Team — returns data.team_id
POST /v3/meta/team/create {"name":"TeamName","owner_user_id":"USER_ID"}

# Agent — returns data.agent_id  
POST /v3/meta/agent/create {"team_id":"TEAM_ID","name":"AgentName","owner_user_id":"USER_ID"}

# Task — returns data.task_id (note: title + creator_user_id, NOT name/owner_user_id)
POST /v3/meta/task/create {"team_id":"TID","agent_id":"AGID","creator_user_id":"UID","title":"TaskTitle"}
```

All curl calls inside docker exec with x-tdai-user-key, x-tdai-service-id, Content-Type headers.

## Hermes proxy routing config

Add to `~/.hermes/config.yaml` under `providers:`:

```yaml
tencentdb-proxy:
  api: http://127.0.0.1:8096/hermes/default
  api_key: "sk-mem-..."
  default_model: YOUR_MODEL
  name: tencentdb-proxy
  models: [YOUR_MODEL]
  extra_headers:
    x-team-id: team-xxxxxx
    x-agent-id: agt-xxxxxx
    x-task-id: task-xxxxxx
    x-conversation-id: my-session-id
```

⚠️ Config change requires gateway restart which kills the current session — back up config first and plan to finish in a new session.

### Current limitations (v2.0.0)

1. **x-task-id required** — without it, proxy falls back to interactive form that Hermes cannot respond to → session bypass
2. **x-conversation-id is static** — same ID = same memory session; switching tasks requires editing config
3. **Proxy adds latency** — auth + retrieval + injection cycle

## Health checks

```bash
curl http://localhost:8420/health | python3 -m json.tool    # pipeline stats
curl http://localhost:8125/health                            # panel
curl http://localhost:8096/health                             # proxy + upstream status
docker ps                                                    # container state
```

## Rollback

```bash
cd /path/to/deploy/deploy/global-images
./stop-all.sh            # stops containers, preserves volumes + admin key
./stop-all.sh --purge    # nukes volumes, admin key, generated proxy config
```

Restore `~/.hermes/config.yaml` from backup (e.g., `.config.bak.pre-tencentdb`).
