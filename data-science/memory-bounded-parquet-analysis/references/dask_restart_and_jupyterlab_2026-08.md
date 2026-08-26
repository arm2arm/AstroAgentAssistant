# Dask client.restart() timeout on cold Lustre + JupyterLab run-dir hygiene (SH26 v2, 2026-08-20)

Follow-up to `dask_staged_join_pipeline_2026-08.md`. Lessons from the first interactive run of the v2 staged-join notebook on <compute-node> (dask 2025.10.0, 24 workers × 30 GB, conda `sh25`).

## `client.restart()` 120 s reconnect timeout

Default `client.restart()` waits only 120 s for all workers to re-register. With 24 workers doing cold dask/pandas imports **from Lustre**, that is not enough:

```
TimeoutError: Waited for 24 worker(s) to reconnect after restarting but,
after 120s, 24 have not returned. Consider a longer timeout, or wait_for_workers=False.
```

Fix (per stage-end cell):

```python
client.restart(timeout=600, wait_for_workers=False)
client.wait_for_workers(N_WORKERS, timeout=1800)   # cold starts from Lustre are slow
```

Key facts:

- **The TimeoutError does not mean the stage failed.** The cache write completes *before* the restart call. On a restart-timeout, verify stage completion by counting rows of each cache dir instead of re-running the stage:

  ```python
  import pyarrow.dataset as ds
  for n in names:
      print(n, ds.dataset(f"{CACHE}/{n}.f32.parq").count_rows())
  ```

  In the 2026-08-20 run all 8 Stage-0 caches were complete (A=215,234,730, B=186,804,256, C=189,543,472, D=137,859,267, gaia=1,811,709,771, sh21=362,392,321, bj21=1,467,744,818, w25=1,464,150,460) despite the restart raising.
- If workers never come back (ground truth: `ps -eo etimes,rss,args | grep -c spawn_main` and `free -g`), re-run the **cluster cell** to build a fresh client. Nothing is lost — all caches are on disk.
- Dashboard API in dask 2025.10: `/api/info`, `/api/system`, `/api/workers`, `/api/v1/*` all **404** even when the scheduler is healthy; only `/health` (200 `ok`) works. For external monitoring use `/health` + process counts + cache dir stats, not the old API endpoints. In-kernel, `client.scheduler_info()["workers"]` remains reliable — wait loops should poll that, e.g. 30 s × up to 60 iterations after a restart.

## JupyterLab run-dir hygiene (Lustre)

- Papermill output notebooks (`*_out.ipynb`, multi-MB with embedded outputs) in the JupyterLab root dir make file-browser listing and notebook open slow on Lustre. Move to `notebook_outputs/` (gitignored) and point papermill there: `python -m papermill in.ipynb ../notebook_outputs/out.ipynb`.
- Git hygiene on the run clone (<compute-node>, `/lustre/<user>/hermes/SH26`):
  - `.gitignore` has **no effect on tracked files** — a common wrong fix. For a tracked file you want to keep local edits on, use `git update-index --skip-worktree <file>`.
  - Untracked scratch notebooks: move them into the ignored output folder rather than committing or gitignoring each one.
  - When the agent has already deployed a notebook file via scp, a later `git pull` fails with "untracked working tree files would be overwritten" — check `git diff --no-index <file> <(git show origin/main:<file>)` first; identical → `rm` + pull.
- Interactive (non-papermill) runs: cells must be run in order (each stage reads the previous stage's cache); after any failure, do NOT restart the kernel — fix and re-run just the failed cell, earlier caches are untouched. `client.restart()` at stage end is expected and benign; wait for it to return before the next cell.
- JupyterLab without auth on a shared subnet: `--ServerApp.token='' --ServerApp.password=''` requires `--ServerApp.allow_remote_access=True` (else it refuses to start) — but prefer token or `--ip=127.0.0.1` + SSH tunnel on shared nodes.
