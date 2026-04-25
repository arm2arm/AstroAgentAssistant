---
name: reana-dev-workflow-setup
description: Set up a REANA development workflow in its own directory, place a minimal reana.yaml, and run it using the Dockerized REANA client.
author: Hermi (sorgenfresser)
version: 1.0
---

## Purpose
This skill automates the standard workflow for creating and executing a REANA analysis on the **development** REANA instance (`https://reana-dev.kube.aip.de`).
It:
1. Creates a dedicated folder for the workflow.
2. Populates the folder with a minimal `reana.yaml` and any user‑provided source files.
3. Provides the exact commands to run the workflow (native client or Dockerized client).
4. Lists useful post‑run checks (ping, status, logs, file listing).

The skill does **not** embed the access token; the user must export `REANA_SERVER_URL` and `REANA_ACCESS_TOKEN` in their shell before invoking the commands.

## Prerequisites
- Docker installed and the current user can run `docker` commands.
- REANA **development** backend reachable at `https://reana-dev.kube.aip.de`.
- A valid REANA access token with at least `read`/`run` permission (export it as `REANA_ACCESS_TOKEN`).
- `jq` (optional, for any JSON post‑processing).

## Variables (set before using the skill)
```bash
WORKFLOW_NAME="my_analysis"           # name you want for the workflow and its folder
WORKFLOW_DIR="${WORKFLOW_NAME}"       # folder that will be created (can be absolute or relative)
# Optional: list of additional source files to copy into the folder (space‑separated)
SOURCE_FILES="script.py data.csv"      # leave empty if none
```

## Step‑by‑step instructions
### 1. Create the workflow directory
```bash
mkdir -p "${WORKFLOW_DIR}"
```
If the directory already exists, the command will leave its contents untouched.

### 2. Add a minimal `reana.yaml`
The skill ships a reference file `templates/minimal_reana.yaml`. Copy it into the new directory:
```bash
cp "$(dirname $(realpath $0))/templates/minimal_reana.yaml" "${WORKFLOW_DIR}/reana.yaml"
```
*(If you call the skill from a Bash script, replace `$(dirname $(realpath $0))` with the absolute path to the skill directory, e.g. `~/.hermes/skills/reana-workflows/reana-dev-workflow-setup/templates`.)*

Edit the copied file in‑place to set the workflow‑specific command or extra inputs. A quick one‑liner using `sed` (or manually edit) is:
```bash
sed -i "s|<WORKFLOW_NAME>|${WORKFLOW_NAME}|g" "${WORKFLOW_DIR}/reana.yaml"
```
The template already contains placeholders for `<WORKFLOW_NAME>` and a generic `command` entry that you should replace with the actual command you want to run (e.g. `python run_analysis.py`).

### 3. Copy any additional source files
```bash
if [ -n "${SOURCE_FILES}" ]; then
  cp ${SOURCE_FILES} "${WORKFLOW_DIR}/"
fi
```
Make sure the files are reachable from the directory (relative paths work fine).

### 4. Export REANA environment variables (once per shell session)
```bash
export REANA_SERVER_URL="https://reana-dev.kube.aip.de"
export REANA_ACCESS_TOKEN="<YOUR_TOKEN_HERE>"
```
*Never store the token in the skill; paste it only when you run the commands.*

### 5. Run the workflow
You have two equivalent options:
#### a) Native REANA client (if installed locally)
```bash
cd "${WORKFLOW_DIR}"
reana-client run -w "${WORKFLOW_NAME}" -f reana.yaml
```
#### b) Dockerized REANA client (no local installation required)
```bash
docker run -i --rm \
  -e REANA_SERVER_URL="$REANA_SERVER_URL" \
  -e REANA_ACCESS_TOKEN="$REANA_ACCESS_TOKEN" \
  -v "$(pwd)/${WORKFLOW_DIR}":/workspace \
  reanahub/reana-client:0.95.0-alpha.3 \
  run -w "${WORKFLOW_NAME}" -f /workspace/reana.yaml
```
Both commands will submit the workflow to the dev backend and start execution.

### 6. Useful post‑run checks (run **anytime** after step 5)
```bash
# Verify the server is reachable
reana-client ping

# Get the current status of the workflow
reana-client status -w "${WORKFLOW_NAME}"

# Stream the logs (real‑time output)
reana-client logs -w "${WORKFLOW_NAME}"

# List files that are present in the workflow workspace
reana-client ls -w "${WORKFLOW_NAME}"
```
If you used the Dockerized client, prepend the same `docker run … reanahub/reana-client …` wrapper to each of the above commands, mounting the current directory as `/workspace`.

## Minimal `reana.yaml` template (stored under `templates/minimal_reana.yaml`)
```yaml
# -------------------------------------------------
# Minimal REANA workflow for the development backend
# -------------------------------------------------
environment:
  repo: https://gitlab-p4n.aip.de/punch_public/reana/environments
  name: python-3.12-slim   # choose the most appropriate environment

workflow:
  type: serial
  specification:
    - name: <WORKFLOW_NAME>
      type: run
      image: python:3.12-slim
      command: |
        # Replace the line below with the actual command you need
        echo "Hello REANA!"
      compute_backend: kubernetes
      resources:
        memory: 32gb
        runtime: 01:00:00   # hh:mm:ss – adjust as needed
      outputs:
        files:
          - output.png   # example output, list everything you want to keep
```
**Important:**
- **Never** modify the `environment:` block to point to a custom repo – the organisation’s central repository must be used.
- Memory is forced to **32 GB** as per policy.
- Adjust `runtime` and `outputs` to match your analysis.

## Pitfalls & Tips
- **Token exposure**: Export the token only in the current shell (`export REANA_ACCESS_TOKEN=…`). Do not write it into any file or script.
- **Folder naming collisions**: Ensure `WORKFLOW_NAME` is unique; otherwise a later run will overwrite the previous folder.
- **Large data**: If your workflow needs large input files, copy them into the folder before step 5; REANA will upload the entire folder as the workspace.
- **Debugging**: Use `reana-client logs -w <name>` to see the exact error messages from the container if the job fails.
- **Re‑run**: To retry a failed workflow, simply run the same `reana-client run …` command again – REANA will create a new run number.

## Verification checklist (run after you have set up a workflow)
1. `ls ${WORKFLOW_DIR}` shows at least `reana.yaml` and any source files you added.
2. `reana-client ping` reports `Status: Connected`.
3. `reana-client run …` returns a run number and finishes without immediate errors.
4. `reana-client status -w <name>` eventually shows `finished`.
5. `reana-client ls -w <name>` lists the declared output files.

---
Generated by Hermi (sorgenfresser) – OpenAI gpt‑5.4 model
