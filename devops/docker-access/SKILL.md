---
name: docker-access
description: Verify Docker availability and run containers on this host.
---

# Docker Access

## Environment
- **Docker:** v29.2.1
- **Daemon:** Running (local)
- **User:** Can pull and run arbitrary containers

## Quick Checks

```bash
docker version              # verify daemon
docker run --rm hello-world # quick smoke test
```

## Digital Twin Docker Compose

```bash
docker compose -f docker-compose.yml -f docker-compose-hifis.yml up -d
```

Access: Web UI at `localhost:5000`

## Known Issues
- MongoDB must have accelerator lattice data pre-loaded
- Crash signature: `TypeError: Accelerator.__init__() missing 1 required keyword-only argument: 'energy'`
