# SH26 2-node join — corruption fix + verified ops (supersedes join-2node-execution-20260820.md)

Session 2026-08-20 evening. The earlier reference's claim "2-node join
completed, 402M verified" is WRONG as written: the 402M output was the
**single-node** morning run; the 2-node re-run **silently corrupted** the
output (402M → 4.8M rows) and overwrote it. Read this file, not the old one.

## Root cause (the one that matters)

**Shared `--local-directory` across nodes + `disk` shuffle = silent row
loss.** dask-worker.sh gave every node `--local-directory
/lustre/<user>/tmp/dask-sh26`. Disk-shuffle writes per-worker shuffle parts
under the local dir; 48 workers on 2 nodes in ONE Lustre tree → node B's
shuffle files clobber node A's. Every merge/groupby then loses rows with NO
exception — every stage logs "done". Observed collapse: base 134M (expect
402M), enr1 43M, enr2 14M, final 4.8M. Single node, same dir = correct
402M — that asymmetry is the diagnostic signature.

Fix (in repo `scripts/dask-worker.sh`, commit 283e573):
```bash
NODE_ID="${NODE_ID:-$(hostname -s)}"
LOCAL_DIR="${LOCAL_DIR:-/lustre/<user>/tmp/dask-sh26/$NODE_ID}"
export TMPDIR="${TMPDIR:-/lustre/<user>/tmp/disk-shuffle/$NODE_ID}"
mkdir -p "$LOCAL_DIR" "$TMPDIR"
# ... --local-directory "$LOCAL_DIR"
```
Rule: any multi-node Dask setup on shared storage gets per-node subdirs for
`--local-directory` AND TMPDIR (TMPDIR also covers client-side partd).
Never point two nodes at the same local dir.

## Silent data-loss tripwires (now in the notebook, keep them)

Row-count asserts are the only reliable detector — stages print "done"
regardless. Pattern in sh2026_join_v2.ipynb:
- `_write(name, ddf, path, expect_rows=N)` — after `to_parquet`, re-read
  parquet **metadata** row counts (cheap: `pq.ParquetFile(f).metadata.num_rows`,
  no data read) and `assert on_disk == expect_rows` with a message naming the
  shared-local-dir cause.
- Left joins preserve the left side: assert base == A_rows+B_rows (compute
  A/B counts once at Stage 1), enr1 == base, enr2 == enr1, final == enr2.
- VERIFY cell: `assert final_rows == A_rows + B_rows` (previously only
  column asserts — that's why 4.8M passed "VERIFY OK").
Apply this pattern to ANY multi-stage shuffle pipeline, not just SH26.

## Cluster ops that bit us (and the working patterns)

- **Stale-worker contamination:** a `Client(scheduler_file=...)` connects to
  whatever is registered, including workers from DEAD runs (tmux died,
  processes orphaned — killing the `dask worker` parent does NOT kill the 24
  nanny children). Papermill attached to 72 workers = 3 overlapping 24-sets,
  one of which ran the OLD shared-dir script. **Before any run:**
  1. query LIVE state (scheduler.json `n_workers` is a startup snapshot —
     UNRELIABLE):
     ```python
     from dask.distributed import Client
     from collections import Counter
     c = Client(scheduler_file=...)
     info = c.scheduler_info()
     print(len(info["workers"]), Counter(w["host"] for w in info["workers"].values()))
     for w in info["workers"].values(): print(w["host"], w["local_directory"])
     ```
     Check `local_directory` per host — any worker on the shared (non
     node-subdir) path must go.
  2. retire stragglers (dask 2026.7 API — `close_worker` does NOT exist,
     `retire_workers(hosts=...)` has wrong signature):
     ```python
     stale = [wid for wid, w in info["workers"].items() if w["host"] != "192.168.111.203"]
     c.retire_workers(workers=stale, close_workers=True, remove=True)
     ```
  3. wipe the stale shared scratch dir after retirement.
- **hmemt nodes are Slurm-gated:** `ssh arm2arm@hmemtNNNN.nnew` →
  "Access denied: user ... has no active jobs on this node." Can't pkill
  there; use the retire_workers API from <compute-node> instead. (<compute-node> is direct
  SSH, hmemt pool is not.)
- **papermill flag:** `-k python3` selects the kernel. `-X` does NOT exist
  (it's an nbconvert flag) — papermill errors "No such option '-X'".
- **pyproject build-backend typo broke `pip install -e .`:** repo had
  `build-backend = "setuptools.backends._legacy:_Backend"` (nonexistent) →
  `BackendUnavailable`. Correct: `setuptools.build_meta`. (Fixed commit
  61a45b2; all plot deps were already in the sh25 env, so editable install
  is offline-instant.)
- **`python -m sh26` needs the package importable:** src-layout repo is not
  on sys.path — `pip install -e .` (once) or `PYTHONPATH=src` per command.
- **Plot-side cluster:** the sh26 CLI builds its OWN LocalCluster from
  `config/dask.yaml` (<compute-node> copy: 24×4 threads × 30GB, spill on Lustre,
  dashboard :8787) — it does NOT attach to the join's external cluster.
  The join scheduler also wants :8787 → kill the join cluster before a
  dashboard-enabled plot run.
- **<compute-node> root is a 378G tmpfs** (carried over): `df -h /` before any
  temp-heavy job; partd disk-shuffle temp must be redirected
  (`temporary_directory` config in the notebook cluster cell →
  /lustre/<user>/tmp/disk-shuffle) — observed 348G /tmp fillup from this.

## Verified re-run state (2026-08-20 21:00 UTC)

Corrupted output quarantined (`..._CORRUPT_4.8M`). Clean papermill run
launched single-node (24 workers, all <compute-node>, per-node local dir — verified
via scheduler_info), Stage 0 rebuilding caches; first money check:
`row check: expect=402,038,986 on_disk=402,038,986` at Stage 1.
Monitor: `tail -2 /lustre/<user>/hermes/SH26/join_run.log`,
`tmux capture-pane -t wk1 -p | tail`,
`grep -E "row check|STAGE" /lustre/<user>/hermes/SH26/join_run.log`.
