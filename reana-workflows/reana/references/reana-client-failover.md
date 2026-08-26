# REANA client native/Docker failover pattern

Use this when REANA operations must work on machines with or without a native `reana-client` executable.

## Client selection policy

Default user-friendly behavior:

1. Prefer native `reana-client` when it exists on `PATH`.
2. If native `reana-client` is missing, check for `docker`.
3. If Docker exists, verify the daemon is reachable with `docker version`.
4. Run Docker Hub image `reanahub/reana-client`.
5. If neither native client nor Docker works, stop with a clear setup message.

Environment overrides:

```bash
REANA_CLIENT_MODE=auto    # default: native first, Docker fallback
REANA_CLIENT_MODE=native  # require native client
REANA_CLIENT_MODE=docker  # force Dockerized client
REANA_CLIENT_IMAGE=${REANA_CLIENT_IMAGE:-reanahub/reana-client:0.95.0-alpha.3}
```

Docker image reference: https://hub.docker.com/r/reanahub/reana-client

## Token handling

Assume credentials are already exported:

```bash
REANA_SERVER_URL=https://reana-dev.kube.aip.de
REANA_ACCESS_TOKEN=<set in environment>
```

Never print or write `REANA_ACCESS_TOKEN`; report only `Token configured: yes/no`.

## Native vs Docker command paths

Native workflow run:

```bash
cd /path/to/project
reana-client run -w my-workflow -f reana.yaml
```

Docker workflow run:

```bash
docker run --rm \
  -e REANA_SERVER_URL \
  -e REANA_ACCESS_TOKEN \
  -v /path/to/project:/workspace \
  -w /workspace \
  reanahub/reana-client:0.95.0-alpha.3 \
  run -w my-workflow -f /workspace/reana.yaml
```

Important: `/workspace/reana.yaml` is Docker-only. Passing it to native `reana-client` fails because `/workspace` does not exist on the host.

## Live-tested generated command pattern

A live REANA dev smoke test showed that generated serial commands should avoid expanding `$REANA_WORKSPACE` in `bash -lc` on some client/server combinations; it can fail during workflow parameter expansion.

Prefer:

```yaml
commands:
  - bash -lc 'if [ -f requirements.txt ]; then pip install --quiet -r requirements.txt; fi && python3 analysis.py'
```

Avoid in generated operator templates unless explicitly verified for that backend:

```yaml
commands:
  - bash -lc 'cd "$REANA_WORKSPACE" && python3 analysis.py'
```

## Useful verification sequence

With dev env exported, verify both paths when Docker is available:

```bash
reana-client ping
REANA_CLIENT_MODE=docker python reana_operator.py ping
REANA_CLIENT_MODE=docker python reana_operator.py recent --limit 2
```

For a full smoke test, scaffold a tiny Python job that writes `output.txt`, run it, poll until `finished`, then download and read the output file.
