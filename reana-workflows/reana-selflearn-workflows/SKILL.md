---
name: reana-selflearn-workflows
description: Self‑learn REANA by listing finished workflows on the development backend, downloading their `reana.yaml` files, and providing guidelines for writing correct REANA workflows.
author: Hermi (sorgenfresser)
version: 1.0
---

## Purpose
This skill automates a quick “self‑learning” cycle for REANA on the development backend:
1. **Discover** all workflows that have finished successfully.
2. **Download** the `reana.yaml` specification of each finished workflow.
3. **Summarise** common patterns and pitfalls.
4. **Provide** a ready‑to‑use template (`reana-workflow-with-env`) for writing new, correct REANA workflows that obey the organisation’s policies (environment repository, 32 GB memory, no custom environments).

It is useful when you want to study existing successful analyses and bootstrap new ones without manually browsing the REANA UI.

## Prerequisites
- Docker installed (to run the REANA client image `reanahub/reana-client`).
- REANA **development** backend URL (e.g., `https://reana-dev.kube.aip.de`).
- A valid REANA **access token** with `read` permission on the development cluster.
- `jq` installed on the host (used to filter JSON output). If not present, install via `apt-get install -y jq` (Debian/Ubuntu) or the equivalent for your distro.

## Variables (set before running the skill)
```bash
REANA_URL="<development-backend-url>"   # e.g., https://reana-dev.kube.aip.de
REANA_TOKEN="<your-access-token>"
OUTPUT_DIR="reana_finished_yaml"        # directory where the yaml files will be saved
``` 
Make sure `OUTPUT_DIR` exists or will be created.

## Steps
### 1. Ping the server (optional sanity check)
```bash
sg docker -c "docker run --rm \
  -e REANA_SERVER_URL=${REANA_URL} \
  -e REANA_ACCESS_TOKEN=${REANA_TOKEN} \
  reanahub/reana-client:0.95.0-alpha.3 ping"
```
You should see `Status: Connected`.

### 2. List **finished** workflows (JSON output)
```bash
FINISHED_JSON=$(sg docker -c "docker run --rm \
  -e REANA_SERVER_URL=${REANA_URL} \
  -e REANA_ACCESS_TOKEN=${REANA_TOKEN} \
  reanahub/reana-client:0.95.0-alpha.3 list -v --json" |
  jq -c '[.[] | select(.status=="finished")]')

echo "Found $(echo $FINISHED_JSON | jq 'length') finished workflows"
```
The variable `FINISHED_JSON` now holds an array of workflow objects.

### 3. Create output directory
```bash
mkdir -p "$OUTPUT_DIR"
```

### 4. Loop over each workflow and download its `reana.yaml`
```bash
index=0
printf "%s" "$FINISHED_JSON" | jq -c '.[]' | while read -r wf; do
  wf_id=$(echo "$wf" | jq -r '.id')
  wf_name=$(echo "$wf" | jq -r '.name')
  echo "Downloading reana.yaml for workflow $wf_name (ID: $wf_id)"

  # Use reana-client download with --output-dir to keep each yaml separate
  sg docker -c "docker run --rm \
    -e REANA_SERVER_URL=${REANA_URL} \
    -e REANA_ACCESS_TOKEN=${REANA_TOKEN} \
    -v $(pwd)/${OUTPUT_DIR}:/out \
    reanahub/reana-client:0.95.0-alpha.3 download -w ${wf_id} -f reana.yaml -o /out/${wf_name}_reana.yaml"

done
```
After the loop, `$OUTPUT_DIR` contains files like `<workflow_name>_reana.yaml` for every successfully finished workflow.

### 5. Quick analysis of the collected YAMLs (optional)
You can now run a simple grep/count to see which environments are used most often:
```bash
grep -h "environment:" $OUTPUT_DIR/*_reana.yaml | sort | uniq -c | sort -nr | head -20
```
Or list steps that commonly appear:
```bash
grep -h "- name:" $OUTPUT_DIR/*_reana.yaml | cut -d':' -f2 | sort | uniq -c | sort -nr | head -20
```
These one‑liners give you a high‑level view of the patterns that work.

### 6. Generate a new correct workflow template
If you need to write a new workflow, reuse the **reana‑workflow‑with‑env** skill that already enforces the organisational policy. Example:
```bash
reana-workflow-with-env \
  step_name=myanalysis \
  docker_image=python:3.12-slim \
  command='pip install -r requirements.txt && python run.py' \
  runtime=04:00:00 \
  output=results.png > new_reana.yaml
```
The produced `new_reana.yaml`:
- References an approved environment from `https://gitlab-p4n.aip.de/punch_public/reana/environments`.
- Sets `memory: 32gb` by default.
- Includes the user‑provided Docker image, command, runtime, and declared output.

## Pitfalls & Tips
- **Environment block**: Never replace the `environment:` section with a custom image. Always point to the central repository.
- **Token safety**: Export `REANA_ACCESS_TOKEN` in a secure session, or store it in a temporary file with strict permissions (`chmod 600`). Avoid typing it on the command line where it may end up in shell history.
- **Large result sets**: If the development backend holds more than a few thousand workflows, consider paging the `list` command (`--page-size 1000`) and filtering incrementally.
- **Naming collisions**: The download step adds the workflow name to the filename. If two workflows share the same name, the second will overwrite the first. Use the workflow ID in the filename if you need strict uniqueness:
  ```bash
  ... -o /out/${wf_id}_reana.yaml
  ```
- **Missing `reana.yaml`**: Some older workflows may not have a `reana.yaml` stored as an output. In that case the download will fail; you can ignore those or inspect the workspace manually.
- **Memory limit**: The skill always sets `memory: 32gb`. If you need more, you must get explicit permission and edit the YAML manually.

## Verification
1. Run the ping command – you see `Status: Connected`.
2. After step 2, `echo $FINISHED_JSON | jq 'length'` returns a non‑zero integer.
3. After step 4, list the output directory:
   ```bash
   ls -1 $OUTPUT_DIR | wc -l
   ```
   The count should equal the number of finished workflows.
4. Open one of the downloaded YAML files to confirm it looks like a normal REANA spec (has `environment:`, `workflow:` sections, etc.).

## References
- REANA client documentation: https://reana-client.readthedocs.io/
- Official REANA environment repository (must be used): https://gitlab-p4n.aip.de/punch_public/reana/environments
- `jq` manual: https://stedolan.github.io/jq/manual/
- Docker image used: `reanahub/reana-client:0.95.0-alpha.3`

---

**Generated by**: Hermi (sorgenfresser) – OpenAI gpt‑5.4 model
