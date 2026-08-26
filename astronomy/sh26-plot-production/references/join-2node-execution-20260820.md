# 2-node Dask join on <compute-node> + hmemt — execution notes (2026-08-20)

Outcome: full 402M-row join completed as `sh26_final_joined_v190826`
(402,121,784 rows × **132 cols**, 1436 parts, 194 GB,
`/lustre/<user>/ipython/SH2025/reana/final/combined/sh26_final_joined_v190826`).
Notebook `sh2026_join_v2.ipynb`; caches in `cache_v2/`; final output verified
col-by-col against the notebook's column lists (zero missing/extra).

## Cluster layout

- Scheduler: <compute-node>, tmux `sched`, `dask-scheduler.sh` → writes
  `/lustre/<user>/tmp/dask/scheduler.json` (Lustre = shared discovery).
- Workers: <compute-node> (tmux `wk1`) + one hmemt node (tmux `wk2`), both via
  `dask-worker.sh <IFACE>` — 24 workers × 4 threads × 30 GB each = 48 total.
- Scripts live in the SH26 repo `scripts/dask-{scheduler,worker}.sh`
  (single source of truth) AND deployed to `/lustre/<user>/tmp/dask/`
  (what tmux actually runs). **After editing the repo copy, `cp` it to
  /lustre/<user>/tmp/dask/ or the workers run the stale file** — this
  drift caused a git conflict once.
- Notebook cluster cell: `Client(scheduler_file=..., timeout=120,
  set_as_default=True)`; assert `len(scheduler_info()["workers"]) == 48`
  loudly (silent 24-worker continues are the worst failure mode).
- hmem pool naming: nodes are `hmemtNNNN.nnew` (NOT `hmem002`); each has
  eth (192.168.111.x) and IB (192.168.119.x) — check `ip -brief` +
  /etc/hosts before choosing `--interface`.

## Pitfalls (all hit this session)

1. **P2P shuffle is unreliable cross-node.** Symptom:
   `RuntimeError: P2P <id> failed during transfer phase`, or stage "hangs"
   mid-join. P2P needs direct worker↔worker TCP on ephemeral ports via the
   advertised contact addresses; any wrong interface = deadlock with no
   error. FIX (worked): `dask.config.set({"dataframe.shuffle.method": "disk"})`.
   Slightly slower, network-proof, and since the spill/tmp dirs are on
   shared Lustre both nodes see the same shuffle path.

2. **"No disk space" on a node with infinite Lustre = tmpfs root.**
   <compute-node>'s `/` is a **378 GB tmpfs (RAM disk)**; `/tmp` lives on it.
   Disk-shuffle's client-side partd path wrote **348 GB of `/tmp/tmp*.partd`**
   and filled the root. Diagnose: `df -h` (tmpfs `/`), then
   `du -xh /tmp | sort -rh | head`. Two independent shuffle write paths:
   - partd (client graph, `tmp*.partd` dirs) → controlled by
     **`dask.config.set({"temporary_directory": "/lustre/..."})`** (falls
     back to `$TMPDIR`/`tempfile.mkdtemp()` otherwise)
   - distributed worker-side disk shuffle → `worker.local_directory`
     (already pinned via `--local-directory /lustre/<user>/tmp/dask-sh26`
     in dask-worker.sh — this one was fine, 400 KB)
   Cleanup when run is finished: `rm -rf /tmp/tmp*.partd`.
   Never trust "Lustre has space" — check `df -h /tmp` on compute nodes.

3. **dask 2026.7.1 CLI renames:** `dask worker --threads` is now
   **`--nthreads`** (old flag → "unexpected extra argument (N)" error),
   and **`--config` does not exist** on the worker CLI. Worker-side dask
   config goes through env vars, e.g.:
   ```bash
   export DASK_DISTRIBUTED__WORKER__MEMORY__TARGET=0.85
   export DASK_DISTRIBUTED__WORKER__MEMORY__SPILL=0.90
   export DASK_DISTRIBUTED__WORKER__MEMORY__PAUSE=0.95
   export DASK_DISTRIBUTED__WORKER__MEMORY__TERMINATE=0.99
   ```
   (pattern in dask-worker.sh; overridable from outside).

4. **`Client.restart()` on a local in-kernel cluster kills all workers and
   they never respawn** (dask 2025.10+; observed 2025.10 and 2026.7).
   `wait_for_workers` then burns its full timeout silently. Never use it;
   release memory with `del` + `gc` (720 GB budget makes restarts
   unnecessary) or drop the client and build a fresh `Client`.

5. **`to_parquet(overwrite=True)` deletes the destination dir FIRST.**
   A run that dies mid-write (e.g. cluster lost its workers) leaves an
   empty dir and the previous good cache is gone → forced recompute (lost
   the 82 GB `base.parq` once). Harden `_write`: write to
   `<name>.parq.new` and `os.replace`/rename over the old dir only on
   success. (Pattern proposed, not yet applied to the notebook.)

6. **Zero-worker hang:** if the notebook "hangs" at a `_write`/compute and
   `scheduler.json` shows `"n_workers": 0` — workers crashed (often after
   the P2P failure); the scheduler and kernel stay alive, so nothing errors,
   it just waits forever. Check `pgrep -af dask` on each node + the tmux
   panes for the exit reason. Interrupt, relaunch workers, rerun stage
   (caches make it cheap).

7. **Column-count asserts must be computed, not magic numbers.**
   `EXPECTED_NCOLS = len(AB)+len(CD)+len(GAIA)+len(SH21)+len(BJ21)+len(W25)+3-1`
   (−1 for CD `ID`→`source_id` overlap with AB) — plus an
   **unexpected-columns** test (planned set vs actual). The old "134" was an
   arithmetic slip in the plan; actual output is 132 cols (49 AB + 31 CD +
   13 Gaia + 24 SH21 + 7 BJ21 + 6 W25 + MISSING/SHBOOST/dups).

8. **Scheduler placement:** scheduler is the SPOF for in-flight work (task
   graph in RAM; it dies → all worker work lost). If a spare node exists,
   run scheduler there and workers on the big nodes. Cost: none (scheduler
   is ~1–2 GB, off the P2P/disk data path); needs only network reachability.

## Recovery / ops snippets

```bash
# workers gone? 
ssh <compute-node>.nnew 'pgrep -af dask; cat /lustre/<user>/tmp/dask/scheduler.json | head'
# rebuild pool (scheduler can stay up)
tmux new -d -s wk1 '/lustre/<user>/tmp/dask/dask-worker.sh <IFACE>'
ssh hmemtNNNN.nnew 'tmux new -d -s wk2 "/lustre/<user>/tmp/dask/dask-worker.sh <IFACE>"'
# shutdown: workers first, scheduler last
tmux kill-session -t wk1; ssh hmemtNNNN.nnew 'tmux kill-session -t wk2'; tmux kill-session -t sched
# git on <compute-node> clone (running notebook dirties the .ipynb):
git stash push notebooks/<nb> ; git pull --rebase ; git stash drop
# divergent branches: git pull --rebase; on conflict in dask-worker.sh keep
# local if it has --nthreads; git config pull.rebase true (one-time)
```
