---
name: reana-client-docker
description: Use the Dockerized REANA client to ping a REANA server, list workflows, and format output with jq.
author: hermes
version: 1.0
---

# Overview
This skill provides a reusable workflow for interacting with a REANA server using the `reanahub/reana-client` Docker image. It covers:

1. **Ping** the server to verify connectivity.
2. **List** workflows with JSON output.
3. **Format** the list for human‑readable display using `jq` and `column`.

The approach relies on setting the `REANA_SERVER_URL` and `REANA_ACCESS_TOKEN` environment variables at runtime, which avoids issues with the client not picking up the config file inside the container.

# Prerequisites
- Docker must be installed and the current user must be able to run `docker` commands.
- REANA access token for the target server (dev or prod) must be available.
- Optional: the `jq` utility installed on the host for post‑processing (available in most Linux distributions).

# Steps
1. **Define variables** (replace with your values):
   ```bash
   REANA_URL="https://reana-dev.kube.aip.de"
   REANA_TOKEN="<your‑access‑token>"
   ```

2. **Important for workflow execution with mounted local files**: when using the Dockerized REANA client to run or upload a local workflow directory, always set the container working directory to the mounted path, for example `-w /workspace -v $(pwd):/workspace`. Otherwise `reana-client run` may find `reana.yaml` but upload referenced input files from the wrong directory.

   Correct pattern:
   ```bash
   sg docker -c "docker run --rm -i \
     -w /workspace \
     -e REANA_SERVER_URL=${REANA_URL} \
     -e REANA_ACCESS_TOKEN=${REANA_TOKEN} \
     -v $(pwd):/workspace \
     reanahub/reana-client:0.95.0-alpha.3 \
     run -w my-workflow"
   ```

3. **Ping the REANA server** to verify the connection:
   ```bash
   sg docker -c "docker run --rm \
     -e REANA_SERVER_URL=${REANA_URL} \
     -e REANA_ACCESS_TOKEN=${REANA_TOKEN} \
     reanahub/reana-client:0.95.0-alpha.3 ping"
   ```
   Expected output includes `Status: Connected`.

3. **List workflows (verbose JSON)**:
   ```bash
   sg docker -c "docker run --rm \
     -e REANA_SERVER_URL=${REANA_URL} \
     -e REANA_ACCESS_TOKEN=${REANA_TOKEN} \
     reanahub/reana-client:0.95.0-alpha.3 \
     list -v --json"
   ```
   This returns a JSON array with workflow metadata.

4. **Show the most recent N workflows nicely** (e.g., last 5):
   ```bash
   sg docker -c "docker run --rm \
     -e REANA_SERVER_URL=${REANA_URL} \
     -e REANA_ACCESS_TOKEN=${REANA_TOKEN} \
     reanahub/reana-client:0.95.0-alpha.3 \
     list -v --json" | \
     jq -r '.[:N][] | [.name, .run_number, .created, .status, (.duration|tostring), .id] | @tsv' | column -t
   ```
   Replace `N` with the number of entries you want (e.g., `5`).

# Pitfalls & Tips
- **Config file not used**: The client inside the container does not automatically read `~/.reana/config.yaml`. Supplying `REANA_SERVER_URL` and `REANA_ACCESS_TOKEN` as environment variables is more reliable.
- **Token safety**: Avoid exposing the token in shell history. Consider exporting the variables in a secure session or using a secrets manager.
- **`sg docker` wrapper**: In this environment we use `sg docker -c "..."` to run Docker commands under the appropriate group/privileges.
- **JSON parsing**: If `jq` is not available, you can install it (`apt-get install -y jq`) or manually process the JSON.

# Verification
After running the ping command, you should see:
```
REANA server: https://reana-dev.kube.aip.de
REANA server version: X.Y.Z
REANA client version: X.Y.Z
Authenticated as: <user>
Status: Connected
```
The formatted list command will produce a table similar to:
```
workflow-name                 12  2026-03-23T14:56:34   failed   6   <uuid>
shboost_...                  1   2026-03-21T23:31:39   finished 36344 <uuid>
... (up to N rows)
```

# References
- REANA client documentation: https://reana-client.readthedocs.io/
- Docker image: reanahub/reana-client (tags: 0.95.0-alpha.3)
