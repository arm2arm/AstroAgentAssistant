# Dask distributed cluster operations (SH26 2-node, dask 2026.7.1, 2026-08-20)

Operational lessons from scaling the SH26 full-catalog join pipeline from a single 96-core/754 GB node (<compute-node>) to <compute-node> + hmem002, and from the dask 2025.10→2026.7.1 CLI migration. All on shared Lustre (data, caches, spill).

## 1. client.restart() is BROKEN on local in-kernel clusters (dask ≥ 2025.10)

- `client.restart()` on `Client(processes=True)` kills all workers; they never respawn (verified: 0 worker procs, 0 worker scratch dirs, dashboard alive).
- A following `wait_for_workers(N, timeout=1800)` then counts down the full timeout against an empty cluster. Bumping `restart(timeout=600, wait_for_workers=False)` + `wait_for_workers(1800)` made the hang longer, not shorter.
- Original error: `TimeoutError: Waited for 24 worker(s) to reconnect after restarting but, after 120s, 24 have not returned.`
- **Fix (validated: full 402M-row run completed 2026-08-20):** remove `client.restart()` entirely. End each stage with `del <tables>` + `gc.collect()`. With a ~720 GB node budget there is no memory pressure requiring a restart. If a fresh process space is ever truly needed: `client.close()` then construct a new `Client(...)`.
- NOTE: `references/dask_staged_join_pipeline_2026-08.md` still recommends the restart pattern in its "Key pattern" line — that line is superseded by this file.

## 2. dask 2026.7.1 CLI changes (vs 2025.x)

- `dask worker`: flag is `--nthreads`, NOT `--threads`. The old name makes the value land as an "unexpected extra argument" parse error: `Error: Got unexpected extra argument: (4)`.
- `dask worker` has NO `--config` option. Worker-side config goes via env:
  ```bash
  export DASK_DISTRIBUTED__WORKER__MEMORY__TARGET=0.85
  export DASK_DISTRIBUTED__WORKER__MEMORY__SPILL=0.90
  export DASK_DISTRIBUTED__WORKER__MEMORY__PAUSE=0.95
  export DASK_DISTRIBUTED__WORKER__MEMORY__TERMINATE=0.99
  ```
  (dotted `distributed.worker.memory.target` → `DASK_DISTRIBUTED__WORKER__MEMORY__TARGET`.)
- Dashboard API drift: `/health` works but `/api/info` and `/api/system` return 404 in 2025.10/2026.7 — cannot poll worker count externally; use `len(client.scheduler_info()["workers"])` in-kernel.
- Always check `dask worker --help` in the TARGET env before scripting flags — envs on shared clusters drift independently.

## 3. Two-node cluster via scheduler-file on shared FS

Pattern (same as the project's historical `dask-scheduler.sh`/`dask-worker.sh` scripts, now repo-committed at `scripts/` in SH26 and deployed to `/lustre/<user>/tmp/dask/`):

```bash
# node 1 (<compute-node>): scheduler
dask scheduler --scheduler-file /lustre/<user>/tmp/dask/scheduler.json \
  --host 0.0.0.0 --port 8786 --dashboard-address :8787

# node 1 AND node 2 (hmem002): workers
dask worker --scheduler-file /lustre/<user>/tmp/dask/scheduler.json \
  --local-directory /lustre/<user>/tmp/dask-sh26 \
  --nworkers 24 --nthreads 4 --memory-limit 30GB \
  --interface ib0   # pick via `ip -brief` on each node; IB only if IB links both
```

Notebook cluster cell (external cluster):
```python
client = Client(scheduler_file="/lustre/<user>/tmp/dask/scheduler.json",
                timeout=120, set_as_default=True)
dask.config.set({"dataframe.shuffle.method": "p2p"})
client.wait_for_workers(48, timeout=600)
assert len(client.scheduler_info()["workers"]) == 48
```

Why almost nothing else changes: data, stage caches, and spill all live on shared Lustre — no path edits. P2P shuffle (already enabled) moves data cross-node automatically. `dask.config.set` memory thresholds are client-side only; external workers get theirs from the CLI/env above.

Operational notes:
- Run each daemon in tmux (`tmux new -d -s sched "…"`), capture progress with `tmux capture-pane -t wk1 -p | tail`.
- Kill order on teardown: workers first, then scheduler, then `client.close()` in the kernel.
- Stale schedulers on the port (e.g. STOPPED-state PIDs from weeks ago) block startup — `pgrep -af "dask scheduler"` and `kill -9` before starting.
- Canary: run one cheap stage (e.g. stage 2) before a long multi-stage run. If interconnect is only 10 GbE, cross-node shuffle can be SLOWER than a single-node memory path — measure, don't assume.
- `wait_for_workers` needs a timeout + assert: a failed worker on node 2 otherwise hangs the whole run.

## 4. Git + JupyterLab notebook workflows (pain points hit repeatedly)

- A RUN notebook accumulates output cells → `git pull` aborts with "local changes would be overwritten". Fix: `git stash push <nb> && git pull && git stash drop` (the local diff is just execution output). For a long-running notebook, prefer `git update-index --assume-unchanged <nb>` and sync only when the run is done.
- A user "commit everything" of a run notebook may contain BOTH real param changes (e.g. `PART = "256MB"`) and output noise — when merging against agent-side edits, diff `git show <commit> -- <nb>` first; take the user's param, re-apply the agent's logic, do not blindly pick a side.
- `git pull --rebase` on the node clone: if the rebase leaves a detached HEAD with a conflict, resolve with `git checkout --ours <file>` (keep local), `git add`, `git rebase --continue`, `git push`. Repo scripts and deployed runtime copies (`/lustre/<user>/tmp/dask/`) are SEPARATE — after a rebase/merge, `cp` repo → runtime and `diff` to confirm identity.

## 5. Column-contract testing for staged join pipelines

- Do NOT hardcode the expected final column count. Compute it from the source column lists at runtime: `sum(len(list)) + flags - overlap` (rename-overlap: C/D `ID` → `source_id` collides with A/B `source_id`, so −1).
- Assert BOTH directions: expected count == actual, AND exact set match (missing list AND unexpected list). The "134 vs 132" episode: plan arithmetic said 134, real lists sum to 132, the stale `assert == 134` would have failed a correct run; the fix was computing the count + set-diff test.
- Verify against the real on-disk schema (`pyarrow.parquet` read_schema on one part) — it's instant and independent of the notebook.

## 6. Small operational rules confirmed this session

- "Sending large graph of size 11 MiB" UserWarning at submit is cosmetic for one-shot cached pipelines (one-time upload, seconds). Suppress with `warnings.filterwarnings("ignore", message="Sending large graph")`; don't re-architect the graph.
- Never `rm -rf` the SPILL or CACHE dir while a run is in progress — in-use spill files on Lustre can error workers mid-run. Old spill files are inert (Dask never reuses them); clean post-run.
- If a stage prints suspicious partition counts (e.g. `parts=1` for a 13 GB table, or 190 where the cache had 47), the stage is REBUILDING not skipping — check the cache path + skip logic before letting it finish.
- `persist()` does not pay off in read-each-once staged pipelines: intermediates are read exactly once, so there is nothing to reuse; it only moves the OOM risk from disk to RAM. Legit niche: small lookup tables (e.g. 3 GB dups) persisting inside a stage that reads them repeatedly.
