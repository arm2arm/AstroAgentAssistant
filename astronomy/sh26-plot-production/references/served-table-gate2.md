# Gate 2 — Production Published Table on <compute-node> (2026-08-21)

Status: **Gate 1 PASSED** (local 200k: served P01 byte-identical to parquet
path, n_points 160,975, PNG 723,000 B). Gate 2 pending user scheduler start.
Code is commit `78d9cfc` + md5-synced to `/lustre/<user>/hermes/SH26` on
<compute-node> (repo dirty there → `git pull` blocked; sync via direct scp
Newton→<compute-node>, verify md5 on the node).

## API facts (dask/distributed 2026.7.1, verified on the node)

- `client.get_dataset(name)` — **NO `columns=` kwarg** in this version.
  Returns a **LAZY `dask.dataframe`** (not eager). Project with
  `ddf[cols].compute()` → column pushdown happens on the workers; only the
  selected columns cross the wire.
- Publish: `client.publish_dataset({name: ddf})` (mapping form, idempotent —
  unpublish a stale name first). Unpublish: `client.unpublish_dataset(name)`.
  List: `client.list_datasets()`.
- `dd.read_parquet` → `persist()` graph is read-tasks (no "large graph"
  warning; that only appears when embedding local pandas frames).

## Runbook (user runs cells on <compute-node>; agent drives the client side)

1. **Scheduler**: `dask scheduler --host 0.0.0.0 --port 8787
   --dashboard-address :8788` (nohup → /tmp/sched.log)
2. **Workers**: `dask worker tcp://localhost:8787 --nthreads 4 --memory 30GB
   --nworkers 4 --name sh26w` — **4 workers suffice** (table ~95 GB); 24
   workers ≈ 720 GB, only if 700+ GB free.
3. **Publish**: `cd /lustre/<user>/hermes/SH26 && PYTHONPATH=src
   <sh25 python> scripts/sh26_publish.py publish --scheduler
   tcp://localhost:8787` (default = v190826 final, `--columns auto`,
   converged-only, float32, ~95 GB, server_info.json).
4. **Status**: same script, subcommand `status`.

Client side (agent): no route to 192.168.111.x → `ssh -L
8787:localhost:8787 arm2arm@141.33.4.144`, then `python -m sh26 plots -p 1
--data publish:sh26 --served tcp://127.0.0.1:8787 --no-cuts`.

## Gate 2 pass criteria

- P01 via served path: **`n_points == 322,771,318`** (pyarrow-direct
  reference) and matches sidecar/loader fields sane.
- Timing breakdown: pull (compute) vs render (make()) split per plot.
- Teardown: `sh26_publish.py unpublish` frees worker RAM; verify
  `list_datasets()` empty.

## Context notes

- <compute-node>: 96 c / 754 GB RAM; shared node — check `free -g` before worker
  sizing. Campaign baseline (pyarrow-direct 77-plot run) lives in
  `/lustre/<user>/hermes/sh26_full/figures/`; P73 needs `hdbscan` installed
  in the sh25 env (`pip install -q hdbscan`).
- `LazyCatalog` served mode: `close()` disconnects the Client only — it never
  stops the remote scheduler/workers (not owned by the plot process).
