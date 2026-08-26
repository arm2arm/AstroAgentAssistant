# 2-node Dask `disk` shuffle + shared `--local-directory` → SILENT data loss (2026-08-20)

Class-level bug + validated fix for multi-node Dask joins that use **`disk`
shuffle** (or any worker-side disk scratch) on a **shared filesystem**
(Lustre/GPFS/...), where the join is staged (merge → write cache → next merge).

## The failure signature (learn to recognize it)

- Every stage prints `done` / `cached X: parts=…, cols=…`.
- **No** exception, **no** worker-killed warning, **no** P2P transfer error.
- Row counts come out **progressively too small** down the pipeline while
  column counts stay correct.
- Real example: a **402,121,784-row** full join came out as **4,802,531 rows**.
  Stage chain: A 215M + B 186M → base 134M → enr1 43M → enr2 14M → final 4.8M.
- A **single-node** run of the *identical* code (same dir) produced the correct
  402M rows → the bug only manifests with 2+ nodes.

Diagnosis clue: if single-node works and 2-node silently truncates with the same
graph and the same `--local-directory` path, suspect **shared worker scratch dir**.

## Root cause

`dask worker --local-directory <path>` is where each worker writes its disk
shuffle / spill files. Dask assumes that directory is **local to the node**
(it's called `local_directory`). On a shared FS, if you give every node the
**same** path, node A's workers and node B's workers write into the **same
files** (same per-partition/partd naming). Their shuffle outputs collide and
clobber each other. Result: rows are lost in every merge and every
`groupby(...).size()`, silently — the ops still "succeed" structurally.

## Validated fix (repo `scripts/dask-worker.sh`, commit in SH26)

Key every node's scratch dirs to its hostname so trees never overlap:

```bash
NODE_ID="${NODE_ID:-$(hostname -s)}"
LOCAL_DIR="${LOCAL_DIR:-/lustre/<user>/tmp/dask-sh26/$NODE_ID}"
export TMPDIR="${TMPDIR:-/lustre/<user>/tmp/disk-shuffle/$NODE_ID}"
mkdir -p "$LOCAL_DIR" "$TMPDIR"

dask worker \
  --scheduler-file "$SCHED_FILE" \
  --local-directory "$LOCAL_DIR" \
  --nworkers 24 --nthreads 4 --memory-limit 30GB \
  ${IFACE:+--interface "$IFACE"}
```

Notes:
- Keep `TMPDIR` off the shared tree too — the client-side partd disk shuffle
  (dask/dataframe/shuffle.py `tempdir`) also writes `tmp*.partd` under `$TMPDIR`,
  which on some nodes defaults to a RAM-backed tmpfs `/tmp` (fills the 378G root).
  Set `dask.config.set({"dataframe.shuffle.method":"disk", "temporary_directory":
  "<lustre path>/$(hostname -s)"})` in the notebook for that side.
- `NODE_ID`/`LOCAL_DIR`/`TMPDIR` are env-overridable so a host with a
  non-unique `hostname -s` (e.g. k8s pods) can be disambiguated explicitly.
- Rule of thumb: **never let two nodes share a `--local-directory` tree** on a
  shared FS. If you can't guarantee unique hostnames, pass distinct `NODE_ID`.

## Safety net that would have caught it (row-count tripwires)

Column-count asserts are the usual VERIFY and they PASS even when rows are
silently dropped. Add **row-count** asserts after each disk-shuffle stage —
they only read parquet *metadata* (cheap, no compute):

```python
import pyarrow.parquet as pq, glob, os
def on_disk_rows(path):
    return sum(pq.ParquetFile(f).metadata.num_rows
               for f in glob.glob(os.path.join(path, "part.*")))
# a left join preserves its LEFT side's row count:
assert on_disk_rows(base) == n_A + n_B          # base = A×C, B×D concat
assert on_disk_rows(enr1) == on_disk_rows(base) # ×gaia
assert on_disk_rows(enr2) == on_disk_rows(enr1) # ×sh21
assert on_disk_rows(final)== on_disk_rows(enr2) # ×bj21×w25×dups
```

Wrap the cache writer so the check is automatic:

```python
def _write(name, ddf, path, expect_rows=None):
    ddf = ddf.repartition(partition_size=PART)
    ddf.to_parquet(path, engine="pyarrow", compression="snappy",
                   overwrite=True, write_index=False, write_metadata_file=True)
    if expect_rows is not None:
        n = on_disk_rows(path)
        assert n == expect_rows, f"{name}: ROW LOSS expect {expect_rows} got {n}"
    return ddf.npartitions
```

Because `overwrite=True` destroys the prior cache *before* the write completes,
a silent-loss run leaves a truncated cache that later stages read — so the
tripwire must fire at write time, not only in final VERIFY.

## When to use
Any multi-node Dask job doing shuffle-then-write stages on a shared FS. Cheap
to add the per-node dir + row asserts to any such pipeline; the bug is invisible
otherwise.
