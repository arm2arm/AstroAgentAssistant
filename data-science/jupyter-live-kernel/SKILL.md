---
name: jupyter-live-kernel
description: "Iterative Python via live Jupyter kernel (hamelnb)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [jupyter, notebook, repl, data-science, exploration, iterative]
    category: data-science
---

# Jupyter Live Kernel (hamelnb)

Gives you a **stateful Python REPL** via a live Jupyter kernel. Variables persist
across executions. Use this instead of `execute_code` when you need to build up
state incrementally, explore APIs, inspect DataFrames, or iterate on complex code.

## When to Use This vs Other Tools

| Tool | Use When |
|------|----------|
| **This skill** | Iterative exploration, state across steps, data science, ML, "let me try this and check" |
| `execute_code` | One-shot scripts needing hermes tool access (web_search, file ops). Stateless. |
| `terminal` | Shell commands, builds, installs, git, process management |

**Rule of thumb:** If you'd want a Jupyter notebook for the task, use this skill.

## Prerequisites

1. **uv** must be installed (check: `which uv`)
2. **JupyterLab** must be installed: `uv tool install jupyterlab`
3. A Jupyter server must be running (see Setup below)

## Setup

The hamelnb script location:
```
SCRIPT="$HOME/.agent-skills/hamelnb/skills/jupyter-live-kernel/scripts/jupyter_live_kernel.py"
```

If not cloned yet:
```
git clone https://github.com/hamelsmu/hamelnb.git ~/.agent-skills/hamelnb
```

### Starting JupyterLab

Check if a server is already running:
```
uv run "$SCRIPT" servers
```

If no servers found, start one:
```
jupyter-lab --no-browser --port=8888 --notebook-dir=$HOME/notebooks \
  --IdentityProvider.token='' --ServerApp.password='' > /tmp/jupyter.log 2>&1 &
sleep 3
```

Note: Token/password disabled for local agent access. The server runs headless.

### Creating a Notebook for REPL Use

If you just need a REPL (no existing notebook), create a minimal notebook file:
```
mkdir -p ~/notebooks
```
Write a minimal .ipynb JSON file with one empty code cell, then start a kernel
session via the Jupyter REST API:
```
curl -s -X POST http://127.0.0.1:8888/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"path":"scratch.ipynb","type":"notebook","name":"scratch.ipynb","kernel":{"name":"python3"}}'
```

## Core Workflow

All commands return structured JSON. Always use `--compact` to save tokens.

Note: For non-interactive / batch / HPC runs (nbconvert/papermill via SSH or SLURM) see references/run_noninteractive_hpc.md and scripts/run_notebook_noninteractive.sh for tested examples, common pitfalls (conda activation, PATH differences, `module` in ~/.bashrc), and a recommended sbatch wrapper.

### 1. Discover servers and notebooks

### 1. Discover servers and notebooks

```
uv run "$SCRIPT" servers --compact
uv run "$SCRIPT" notebooks --compact
```

### 2. Execute code (primary operation)

```
uv run "$SCRIPT" execute --path <notebook.ipynb> --code '<python code>' --compact
```

State persists across execute calls. Variables, imports, objects all survive.

Multi-line code works with $'...' quoting:
```
uv run "$SCRIPT" execute --path scratch.ipynb --code $'import os\nfiles = os.listdir(".")\nprint(f"Found {len(files)} files")' --compact
```

### 3. Inspect live variables

```
uv run "$SCRIPT" variables --path <notebook.ipynb> list --compact
uv run "$SCRIPT" variables --path <notebook.ipynb> preview --name <varname> --compact
```

### 4. Edit notebook cells

```
# View current cells
uv run "$SCRIPT" contents --path <notebook.ipynb> --compact

# Insert a new cell
uv run "$SCRIPT" edit --path <notebook.ipynb> insert \
  --at-index <N> --cell-type code --source '<code>' --compact

# Replace cell source (use cell-id from contents output)
uv run "$SCRIPT" edit --path <notebook.ipynb> replace-source \
  --cell-id <id> --source '<new code>' --compact

# Delete a cell
uv run "$SCRIPT" edit --path <notebook.ipynb> delete --cell-id <id> --compact
```

### 5. Verification (restart + run all)

Only use when the user asks for a clean verification or you need to confirm
the notebook runs top-to-bottom:

```
uv run "$SCRIPT" restart-run-all --path <notebook.ipynb> --save-outputs --compact
```

## Practical Tips from Experience

### Dask cluster diagnostics (session additions)

- ### Recent session additions: Dask P2P shuffle failure checklist

A short, copy-pasteable checklist for runs that fail with "P2P ... failed during transfer phase" or with large graph warnings. Also see references/sh2026_dask_p2p.md for session details and commands.

Use the bundled references/dask_cluster_diagnostics.md for a copy-pasteable checklist and a remote-safe script for querying schedulers. It includes SSH here-doc patterns that avoid quoting bugs and explains how to interpret version mismatches (tornado) and why to prefer 'disk' shuffle when p2p fails.

## Practical Tips from Experience

1. **First execution after server start may timeout** — the kernel needs a moment
   to initialize. If you get a timeout, just retry.

2. **The kernel Python is JupyterLab's Python** — packages must be installed in
   that environment. If you need additional packages, install them into the
   JupyterLab tool environment first.

3. **--compact flag saves significant tokens** — always use it. JSON output can
   be very verbose without it.

4. **For pure REPL use**, create a scratch.ipynb and don't bother with cell editing.
   Just use `execute` repeatedly.

5. **Argument order matters** — subcommand flags like `--path` go BEFORE the
   sub-subcommand. E.g.: `variables --path nb.ipynb list` not `variables list --path nb.ipynb`.

6. **If a session doesn't exist yet**, you need to start one via the REST API
   (see Setup section). The tool can't execute without a live kernel session.

7. **Errors are returned as JSON** with traceback — read the `ename` and `evalue`
   fields to understand what went wrong.

8. **Occasional websocket timeouts** — some operations may timeout on first try,
   especially after a kernel restart. Retry once before escalating.

## Timeout Defaults

The script has a 30-second default timeout per execution. For long-running
operations, pass `--timeout 120`. For long-running operations, pass `--timeout 120`. Use generous timeouts (60+) for initial
setup or heavy computation.

## Non-interactive notebook execution (nbconvert / papermill)

When you need to run notebooks non-interactively (SSH, cron, SLURM), prefer
explicit, robust wrappers that avoid shell-quoting pitfalls and do not rely on
interactive shell startup behaviour. Common tools:

- nbconvert: simple run top→bottom, use for straightforward execution.
- papermill: recommended when you want parameterisation, better exit codes,
  and clearer programmatic control.

Key recommendations and pitfalls

- Use absolute paths to the interpreter and tool binaries instead of relying on
  `source ~/.bashrc` in remote one-liners. Example: `/lustre/.../conda/env/bin/jupyter`.
- Avoid deeply nested quoting in here-documents or chained SSH -c commands; they
  are a common source of empty-variable bugs (we saw papermill receive an empty
  input path when a one-liner's quoting expanded incorrectly).
- If your .bashrc uses `module` or other interactive-only commands, non-
  interactive shells may print errors such as `module: command not found`.
  These are noisy but usually harmless; explicitly source the conda env or call
  the env's binaries directly in job scripts to be robust.
- Always capture stdout/stderr to a log file and use `--debug` or verbose modes
  when diagnosing failures.
- If the notebook connects to external services (Dask scheduler, databases),
  ensure those services are reachable from the compute node where the job runs
  or provide a fallback (LocalCluster) in the notebook or via a pre-run cell.

Minimal robust patterns (choose one)

1) Direct binary invocation (recommended):

/lustre/<user>/SOFTWARE/conda/sh25/bin/jupyter nbconvert --to notebook --execute \
  '/path/to/in.ipynb' --output '/path/to/out.ipynb' \
  --ExecutePreprocessor.timeout=36000 --ExecutePreprocessor.kernel_name=python3

or

/lustre/<user>/SOFTWARE/conda/sh25/bin/papermill '/path/to/in.ipynb' '/path/to/out.ipynb' -k python3

2) Small wrapper script (safe for SSH and scheduler submission) — keep it in
   your repo and call it from sbatch/cron.

3) SLURM example: create an `sbatch` script that activates the environment
   explicitly (`source /opt/miniconda3/etc/profile.d/conda.sh && conda activate /path/to/env`) or calls the environment's binaries directly.

Debugging checklist (if run fails)

- Inspect the log: it should contain nbconvert/papermill output and any kernel
  tracebacks.
- Check the output notebook exists and is non-empty.
- Run a single-cell execution to isolate where it hangs (kernel startup vs a
  cell doing network I/O). Use `nbclient` or papermill to execute just the
  first cell.
- Confirm environment: `python -c "import papermill,nbformat;print(papermill.__version__)"`.
- If the notebook connects to Dask, verify scheduler/workers are reachable from
  the node, or modify the notebook to fall back to LocalCluster when remote
  scheduler is unavailable.

Papermill + Dask notebook pitfalls (durable lessons)

- If you plan to pass `-p NAME VALUE` to papermill, ensure the notebook contains
  a code cell tagged `parameters`. Without that tag, papermill will warn that it
  got unknown parameters and your overrides will not take effect.
- Avoid unconditional `client.restart()` inside batch notebooks that connect to a
  shared remote scheduler. In production/SLURM runs the scheduler may already
  hold task state, and restart can fail before any real notebook work begins.
  Prefer no restart, or guard it with `try/except` and continue.
- When debugging Dask `P2P ... failed during transfer phase` on a remote
  cluster, do not assume your explicit `shuffle="disk"` calls fully eliminate
  P2P. A later `repartition(partition_size=...)` or other expression-level
  optimization may still trigger transfer-heavy paths.
- If a wide joined dataframe already has a workable partitioning, prefer
  `final_ddf = final_ddf.persist()` and write it directly instead of forcing a
  final `repartition(partition_size=...)`. On fragile clusters this is often
  more robust than trying to normalize partition size right before `to_parquet`.
- For session-specific commands and the SH2026 Dask reproduction, see
  `references/papermill-dask-batch-pitfalls.md`.

Support files

See references/run-notebook-templates and scripts/run_notebook_*.sh in this
skill for small wrapper examples and session notes (useful troubleshooting
snippets generated from recent runs).  

Appendix: session-specific debugging notes

- When running one-liners over SSH prefer not to embed variable setting and
  command execution inside a single -c string. Use a small wrapper script or
  a here-document that is transferred and run to avoid quoting expansion bugs.
- If papermill reports `Notebook does not appear to be JSON: ''`, first check
  that your input path is non-empty and readable (`[ -s "$IN" ]`) and that
  no quoting/expansion turned it into an empty string. Then re-run papermill
  with the explicit absolute path.

Support files

- references/run-notebook-templates.md  (session templates & checks)

