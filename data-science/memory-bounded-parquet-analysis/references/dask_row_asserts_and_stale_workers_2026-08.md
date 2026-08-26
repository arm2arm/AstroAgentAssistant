# Row-tripwire calibration + stale-worker-pool contamination (SH26, 2026-08-20)

Follow-up to `dask_2node_diskshuffle_shared_localdir_2026-08.md`. Two lessons
from the re-run of the SH26 402M-row staged join after the 2-node corruption.

## 1. Row-count tripwires must be ONE-SIDED (`<` fails, `>` warns)

The original reference's strict `assert on_disk == expect_rows` fired a
**false positive** on a correct run:

- expected (A+B) = 402,038,986; on disk = 402,121,784 → assert aborted a GOOD run.
- 402,121,784 is **exactly** the previously verified good-run count, so the
  pipeline behaved correctly — `base` legitimately carries a small
  duplicate-key fan-out (+82,798 rows) from the C/D enrichment merges.

Why one-sided checks are the correct semantics for disk-shuffle pipelines:

- Shuffle/scratch-dir collisions only **delete** rows — they can never
  CREATE them. So `on_disk < expect` is the only corruption signature.
- `on_disk > expect` means fan-out (duplicate join keys). Review it, print a
  note, don't abort.
- Final VERIFY: `assert nrow >= A+B`, and additionally flag
  "MATCHES known-good run (402,121,784)" when equal to the known-good
  constant — equality-with-known-good is the strongest pass signal.

```python
def _write(name, ddf, path, expect_rows=None):
    ddf = ddf.repartition(partition_size=PART)
    ddf.to_parquet(path, engine="pyarrow", compression="snappy",
                   overwrite=True, write_index=False, write_metadata_file=True)
    if expect_rows is not None:
        n = on_disk_rows(path)   # pyarrow metadata sum over part.*
        if n < expect_rows:
            raise AssertionError(f"{name}: ROW LOSS — expected >= {expect_rows:,}, on disk {n:,}")
        if n > expect_rows:
            print(f"note: {name} has {n - expect_rows:,} MORE rows than expected "
                  f"(benign fan-out from duplicate join keys)")
    return ddf.npartitions
```

Corollary: when designing row assertions, derive the expected value from the
*left-preservation* property of the specific join (left join preserves its
left side), and treat "known-good constant equality" as a pass-marker rather
than a hard requirement — fan-out deltas are run-stable but conceptually
independent of the corruption class you're guarding against.

## 2. Stale-worker contamination: a "fresh" launch can inherit a poisoned pool

Papermill/notebook launched with `Client(scheduler_file=...)` attached to a
scheduler that **still had workers from a previous (buggy) generation
registered**:

- Run #1 saw **72 workers / 2 TB** (should be 24): the killed parent's 24
  child workers survived as orphans, plus a stale launcher set from the
  corrupted 2-node run.
- Orphans registered against the OLD shared `--local-directory` = the
  row-loss bug live in the "clean" relaunch.

Killing the tmux/launcher session does NOT kill worker child processes;
killing the parent does NOT retire children already registered with the
scheduler.

Recovery sequence (validated):

1. Kill the papermill/session process.
2. Attach a client to the scheduler and **retire the stale workers explicitly**:
   `client.retire_workers(workers=[...], remove=True, close_workers=True)`.
   (`close_worker` does not exist in dask 2026.7.1 — `retire_workers` is the
   API.) Note: workers on Slurm-gated nodes that are no longer SSH-reachable
   ("no active jobs on this node") can still be retired through the scheduler
   API — no direct SSH needed.
3. Verify from the client: `len(client.scheduler_info()["workers"]) == 0`
   (or exactly the expected set), and `pgrep -af dask` on each reachable node
   to confirm no orphan processes.
4. Delete any stale shared scratch dirs from the old generation, then relaunch
   workers from the per-node script, then the notebook.

**Preflight before any long run on a shared scheduler:** print the live worker
set (count, hostnames, local dirs) from `client.scheduler_info()` and require
it to match the intended topology exactly before the first stage executes.
This is the cheapest tripwire in the system — it catches every stale/orphan
contamination class in one check.

## 3. Notebook JSON patching: validate the blob before deploying

While rewriting asserts in the .ipynb, a multi-line string replacement
collapsed a cell's `source` array into a single string and **silently dropped
two helper functions** (`_f32`, part of `_write`) from the committed notebook
(2 insertions / 37 deletions instead of the intended edit) — caught only
because the deploy script grepped the committed blob for the new markers
before copying to the compute node.

Rules for programmatic .ipynb edits:

- After editing, **re-extract and grep the committed/working blob** for every
  marker the change should have added AND for pre-existing definitions that
  must survive (`def _write`, `def _f32`, …). Both directions.
- Keep `source` as a list of lines (json.dump with `indent=1` is fine, but a
  cell whose source became one giant string is a red flag — check
  `isinstance(cell["source"], list)` and no element containing multiple
  newlines for code cells).
- Only after the blob validates, copy to the runtime node and re-grep THERE.

## 4. Deploy divergence: direct-copy deploys break `git pull` on the node

Repeating `scp`/`git show > file` deploys onto the node's repo working tree
accumulates "local changes" (`M notebooks/…`, `M scripts/…`) until
`git pull` refuses with "commit or stash them". The node clone and the
runtime copies then silently diverge from the git history. Fix pattern:
periodically reconcile the node clone — `git stash` (or commit the real param
changes separately from output noise), `git pull`, then re-`diff` deployed
runtime copies against `git show main:<file>` to confirm identity.
