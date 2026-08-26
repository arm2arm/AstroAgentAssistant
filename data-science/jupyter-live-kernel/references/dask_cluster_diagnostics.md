Dask cluster diagnostics — quick reference

Purpose

- Provide a small, copy-pasteable checklist and a robust script for querying a Dask
  scheduler from a remote login node or compute node. Capture common pitfalls
  observed in recent sessions (SSH quoting, interactive-only ~/.bashrc lines,
  tornado version mismatch warnings).

Run (safe wrapper)

1. Copy this file to the remote host (or read it there) and run the included
   script `scripts/query_dask_scheduler.py` instead of embedding a long one-liner
   in an ssh -c call. Example:

   ssh user@cluster 'python3 /path/to/query_dask_scheduler.py --scheduler tcp://141.33.4.144:8786'

2. If you must use a here-document over SSH, prefer creating a small temporary
   script remotely and executing it (avoid quoting hell):

   ssh user@host 'cat > /tmp/dask_info.py <<'"'PY'"'
   from dask.distributed import Client
   import json
   c = Client("tcp://141.33.4.144:8786")
   info = c.scheduler_info()
   print(json.dumps(info, indent=2))
   PY
   python3 /tmp/dask_info.py; rm /tmp/dask_info.py'

Common checks to run

- scheduler address: Client.scheduler.address or scheduler_info()["address"]
- active workers: len(scheduler_info()["workers"]) and each worker's memory_limit and nthreads
- total cluster memory: sum(worker['memory_limit'])
- dask/distributed/tornado versions: client.get_versions() — look for mismatches
- client.ncores() or client.nthreads() for core totals
- memory_summary: client.run(lambda: psutil.virtual_memory()._asdict()) on workers (requires psutil)

Tornado mismatch

- A repeated warning is: Client tornado 6.5.1 vs scheduler 6.5.5.
- Effect: may cause subtle networking oddities. Fix by aligning tornado across client, scheduler, and workers. Recommended approaches:
  - If you control the client (your login env): `pip install tornado==6.5.5` into the client env.
  - If you control the scheduler/workers: conda/pip install the matching version or restart with a consistent environment.
  - For immediate mitigation: avoid p2p shuffles and prefer disk/tables/tasks shuffles.

Dask shuffle strategy notes (from session)

- p2p: fast when network and versions are stable; brittle on heterogeneous or mismatched environments.
- disk/tasks: more robust on shared filesystems / heterogenous workers. Prefer `dataframe.shuffle.method: 'disk'` when you see p2p transfer failures.

Partitioning and memory

- If total data bytes and per-file sizes are available, pick partition_size ~ 256–1024 MiB per partition as a starting heuristic; aim for 100–1000 partitions per worker depending on worker memory and job shape.
- After joins or repeated reuse, call .persist() on large intermediates to avoid repeated graph recomputation.

When to open an admin ticket

- If scheduler and worker tornado versions cannot be aligned locally (cluster-managed images), ask the cluster ops to rebuild or restart with pinned tornado.
- If workers report unstable network connections or frequent worker restarts, provide the operator with your query output (json) and the exact VersionMismatchWarning text.

References

- scripts/query_dask_scheduler.py — small script to run remotely and report summary JSON
- For deeper reading: Dask docs (shuffle strategies) and Distributed troubleshooting guides.
