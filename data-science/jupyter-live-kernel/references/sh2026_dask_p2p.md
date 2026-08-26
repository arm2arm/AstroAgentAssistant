Summary

This reference captures reproducible diagnostics and pragmatic fixes used during a recent Newton run that failed with a Dask "P2P ... failed during transfer phase" RuntimeError while running a large papermill job. It's intentionally concise and prescriptive so you can follow the same steps quickly.

When to consult

- You see RuntimeError('P2P ... failed during transfer phase') in notebook/papermill logs.
- Large shuffle operations or graph sizes (>20 MiB) appear in warnings from distributed.client.
- Remote log tails are polluted by interactive ~/.bashrc lines (e.g. `module: command not found`).

Observed signals from the run

- Dask raised graph-size warnings like "Sending large graph of size 43.39 MiB".
- Final to_parquet triggered a P2P transfer failure during shuffle.
- Notebook used many partitions (tens of thousands) and produced large task graphs.
- Remote non-interactive shells printed `/home/arm2arm/.bashrc: line 13: module: command not found` before logs.
- Tornado version mismatch warning: client/workers 6.5.1 vs scheduler 6.5.5.

Root-cause hypotheses

- Peer-to-peer (P2P) transfers failed due to worker-level networking instability or plugin transfer exceptions while moving many partitions.
- Excessively large graphs + many partitions increase serialized graph size and network pressure.
- Version mismatch in tornado or networking libraries can make worker comms fragile.

Immediate mitigations (safe, low-friction)

1) Prefer disk shuffle for large joins/writes

- In the notebook (early, before heavy ops):

  import dask
  dask.config.set({
      'dataframe.shuffle.method': 'disk'
  })

- Also use set_index(..., shuffle='disk') when you must set index.

Why: disk shuffle avoids large P2P in-memory transfers and is more robust for big datasets.

2) Reduce partition count, persist frequently, checkpoint intermediate tables

- Repartition heuristically (example): target ~256–1024 MiB per partition depending on cluster memory.
  Use dd.repartition(partition_size='512MB') for heavy tables.
- Persist small lookup tables (Gaia, SH21, BJ21) before repeated joins: df = df.persist() or client.scatter().
- Write intermediate checkpoints to parquet and read them back to keep graph sizes small.

3) Guard client.restart() and long-running restarts

- Replace blind client.restart() calls with a guarded version to avoid surprising scheduler restarts on remote runs:

  try:
      client.restart(wait_for_workers=False)
  except Exception as e:
      print('client.restart skipped or failed:', e)

4) Persist / broadcast small tables instead of embedding them in large graphs

- For small enrichment tables, use client.scatter() or compute them and convert to pandas to broadcast.
- Example: small_df = small_ddf.compute(); scattered = client.scatter(small_df, broadcast=True)

5) Final write: reduce partitions again, persist, wait for workers

- Before final_ddf.to_parquet(...):

  final_ddf = final_ddf.repartition(partition_size='512MB').persist()
  try:
      client.wait_for_workers()
  except Exception:
      pass

- Then call to_parquet. If shuffle-related transfers still occur, reduce partition count further (1–16 partitions) for the write step and let workers stream the data to storage.

6) If SSH log tailing is noisy due to ~/.bashrc errors

- Run tails under a clean non-login shell to avoid sourcing .bashrc:

  ssh host "bash --norc -c 'tail -n 200 /path/to/log'"

- Or call the job node's tail using an administrative wrapper or use sbatch with --output to capture logs.

7) sbatch / papermill wrapper pattern (robust)

- Use absolute interpreter/binary paths or explicitly source conda before running papermill. Example sbatch snippet:

  #!/bin/bash
  #SBATCH --time=06:00:00
  #SBATCH --cpus-per-task=16
  #SBATCH --mem=128G
  export OMP_NUM_THREADS=1
  export MKL_NUM_THREADS=1
  /lustre/<user>/SOFTWARE/conda/sh25/bin/python3 -m papermill \
    /lustre/<user>/ipython/SH2025/reana/sh2026_join_out.optimized.ipynb \
    /lustre/<user>/ipython/SH2025/reana/sh2026_join_out.optimized.executed.$SLURM_JOB_ID.ipynb \
    -k python3

- This avoids reliance on interactive startup and `module` in .bashrc.

8) Tornado / distributed version mismatch

- If you see VersionMismatchWarning for tornado, align versions across scheduler and workers. Example (conda):

  conda activate /path/to/env
  conda install -c conda-forge tornado=6.5.5 distributed=2025.10.0 dask=2025.10.0

- Then restart scheduler & workers. Note: needs admin or orchestrated rollout (service restart).

Deeper mitigations (if failures persist)

- Temporarily reduce concurrency: fewer workers / threads per worker; increase worker memory so transfers are chunked.
- Use distributed shuffle diagnostics (enable DEBUG logs for distributed.shuffle and inspect worker logs for transfer tracebacks).
- Use explicit shuffle plugins tuning (see distributed/shuffle docs) or switch to tasks-based shuffles only for controlled environments.

Repro steps used in session (commands used)

- Safe scp of patched notebook:
  scp -o BatchMode=yes -o StrictHostKeyChecking=accept-new ./file.ipynb user@host:/path/file.ipynb

- Create and submit sbatch script via ssh here-doc (avoids quoting pitfalls):
  ssh user@host 'cat > /home/user/run_papermill.sbatch <<"SBATCH"\n<sbatch script>\nSBATCH\n&& sbatch /home/user/run_papermill.sbatch'

- Tail logs avoiding .bashrc:
  ssh user@host "bash --norc -c 'tail -n 200 /home/user/logs/papermill-production-509479.err'"

Notes and caveats

- These are pragmatic mitigations that worked for the observed run. If problems persist, capture full worker logs (not just notebook stderr) and consider aligning tornado and distributed versions cluster-wide.
- Do not edit other users' ~/.bashrc without explicit approval. Use non-login shells or wrapper scripts instead.

References

- Dask shuffle design and disk shuffle docs: https://docs.dask.org/
- Distributed shuffle implementation notes: site-packages/distributed/shuffle

