# Dead-cluster hangs, cache-write trap, P2P cross-node caveats (SH26 2-node, 2026-08-20)

Companion to `dask_distributed_cluster_ops_2026-08.md`. Lessons from the 2-node SH26 full-catalog join session that followed the initial 2-node setup.

## 1. "A stage hangs" — first rule out a dead cluster (validated)

Observed: after all 48 workers died (P2P transfer failure), a Stage-1 `to_parquet` "hang" was actually a **silent no-op cluster**: with 0 registered workers, dask.distributed submits tasks that never run — no error, no timeout, just an infinite wait. A live scheduler process + attached kernel is NOT proof the cluster works.

Diagnosis order for "a stage hangs mid-pipeline":
1. `pgrep -af dask worker` on every node — are there ANY worker procs?
2. `cat <scheduler.json>` — read the `n_workers` field. 0 = dead cluster; stop and rebuild workers (the scheduler file + scheduler process can stay; workers just re-register).
3. `tmux ls` / `tmux capture-pane -t wkX -p | tail` — worker sessions may have crashed out of tmux while the scheduler keeps living.
4. Only if workers are confirmed alive: inspect `client.scheduler_info()` — check each worker's `paused` flag (memory-pause queueing: workers cross `memory.pause` → their tasks queue → the join stalls) vs frozen processing counts with many "waiting" tasks (shuffle stall).

## 2. `to_parquet(overwrite=True)` delete-then-write trap (observed)

`overwrite=True` removes the existing output dir BEFORE the write proves itself. A worker death mid-write left `base.parq` as an EMPTY directory and destroyed the previous good ~82 GB cache — forcing a full Stage-1 recompute.

Hardened `_write` pattern:
```python
def _write(name, ddf, path):
    tmp = path + ".tmp"
    # ensure tmp is clean (it's ours, short-lived)
    if os.path.exists(tmp):
        shutil.rmtree(tmp)
    ddf = _f32(ddf).repartition(partition_size=PART)
    ddf.to_parquet(tmp, engine="pyarrow", compression="snappy",
                   overwrite=True, write_index=False)   # compute finishes here
    if os.path.exists(path):
        shutil.rmtree(path)
    os.rename(tmp, path)          # atomic-ish swap on same FS (Lustre)
    ...
```
A dead run then leaves the prior cache intact and the stage resumes instead of recomputing. Note: `to_parquet` on a dask df is lazy until the graph executes; the swap must happen after successful compute (as written), which is what `to_parquet` itself does when called.

## 3. P2P shuffle cross-node caveat

The setup doc's claim "P2P moves data cross-node automatically" holds ONLY if each worker's *contact address* (driven by `--interface`) is reachable from the other nodes' workers — P2P shuffle uses direct TCP on ephemeral ports between workers. If any advertised address is unroutable, the transfer phase either **deadlocks (hang)** or throws `RuntimeError: P2P <id> failed during transfer phase`. Both symptoms were seen in this session.

- Reachability probe: small socket server/client pair, high port, BOTH directions:
  - server node: `python3 -c "import socket; s=socket.socket(); s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1); s.bind(('0.0.0.0',29511)); s.listen(); s.settimeout(20); s.accept(); print('ACCEPT_OK')"` (backgrounded)
  - client node: connect to `host:29511` → expect `CONNECT_OK`
  - Repeat reversed.
- Fallback when high ports are restricted or the wrong interface was chosen: `dask.config.set({"dataframe.shuffle.method": "disk"})` — routes shuffle through the spill dir on shared FS, needs no direct worker↔worker traffic. Slower than P2P; NOT yet validated on this cluster (do not present as best practice until it is).
- Stage-1 of the SH26 pipeline contains 3 full shuffles (A×C, B×D, then a 402M-row groupby for dups) — a P2P stall there looks like a generic hang.
- Cheap algorithmic improvement (proposed, not yet applied): compute `dups` from A and B *before* the merges (disjoint source_ids) and concat — shuffles ~215M+186M rows of 1 column instead of 402M rows of 80.

## 4. AIP hmem-pool environment facts

- Node names are `hmemtXXXX.nnew` (e.g. `hmemt1057.nnew`) — **not** `hmem002.nnew`. Guessing short names fails DNS. Check `/etc/hosts` on the scheduler node for the real pool names.
- Each node has dual subnets: eth `192.168.111.x` and IB `192.168.119.x` (IB hostnames `hmemtXXXX-ib0.nnew`). The worker `--interface` must be the one whose subnet actually routes between the two nodes (`ip -brief` on each; pick IB only if IB links both nodes).
- Nested-SSH quoting (agent → Newton → node) breaks on parens/quotes in inline `bash -c` strings; drop the probe script to Lustre (`/tmp/porttest.py`) and exec it on the remote node instead.
