# 402M Campaign Ops + Full-Scale Plot Pitfalls (2026-08-21)

Session-specific detail for the full-catalog (402M, v190826) pyarrow-direct
campaign and the served-table work. Umbrella context: SKILL.md sections
"Served-table mode" and "Critical pitfalls"; runbook:
`references/served-table-gate2.md`.

## Newton ↔ <compute-node> file sync (gotcha that cost time)

- **Newton's `/lustre` ≠ <compute-node>'s `/lustre`** (different mount views):
  `cp` from Newton into `/lustre/<user>/hermes/SH26/` does NOT land in what
  <compute-node> reads. Correct sync = local → Newton `/tmp` → **direct scp
  Newton→<compute-node>** (final hop), then **md5-verify ON <compute-node>**.
- scp can fail transiently inside a batch loop (rc 0 but file missing) —
  re-run single-file and check rc.

## Background jobs over double-hop ssh

- `ssh newton 'ssh <compute-node> nohup cmd &'` **hangs the outer ssh on channel
  teardown** even though the job DID start (the shell stays a session
  leader of the bg process). Do not diagnose the hang as a failure — check
  `pgrep` + the log first.
- Clean pattern: write a launcher script locally
  (`/tmp/launchNN.sh`: `cd repo && nohup timeout -k 60 <budget> python
  /tmp/run_p_direct.py <id> > /tmp/cheap_pNN.log 2>&1 & echo PID=$!`),
  scp local→Newton→<compute-node>, `chmod +x`, execute — returns immediately with
  the job PID.

## Plot failures in the 77-plot campaign

- **P73** (`umap_all_binned`): `ModuleNotFoundError: hdbscan` in the sh25
  conda env. Fix: `/lustre/<user>/SOFTWARE/conda/sh25/bin/python -m pip
  install -q hdbscan`. P74–P89 don't need it. `import hdbscan` has no
  `__version__` attribute — verify import only, not version.
- **P81** (`disk_multi_candle`): stalled >30 min inside `fig.savefig`
  (killed by the 60-min campaign timeout). Cause: panel (a) scattered
  ~300M converged points with `rasterized=True` at 300 dpi —
  `PathCollection` aggregation dominates. Fix (commit 170b39f): subsample
  the *display* scatter to 2M points — seeded `np.random.default_rng(42)`
  choice + sorted indices (reproducible); analysis stays on full data;
  param `cmd_maxpts` (default 2_000_000). Visually identical at s=0.3.
  **Rule: any full-402M plot that scatters raw points must subsample the
  display layer** (hexbin/bincount are fine at full scale — only
  per-point artists blow up).

## Served-table probe facts (dask/distributed 2026.7.1, verified local +
node)

- `client.get_dataset(name)` — **NO `columns=` kwarg** in this build.
  Returns a **LAZY `dask.dataframe` (dask_expr) collection**; project with
  `ddf[cols]` — pushdown happens at `.compute()`, only selected columns
  cross the wire.
- `client.publish_dataset({name: ddf})` (MAPPING form);
  `client.unpublish_dataset(name)`; `client.list_datasets()`.
- `dd.read_parquet → persist()` produces a read-tasks graph (no "large
  graph" warning; that only appears when publishing a locally-embedded
  pandas frame).
- In a probe, `LocalCluster` binds its SCHEDULER to a random port —
  `dashboard_address` is NOT the scheduler port. Connect subprocess clients
  to `cluster.scheduler_address` (symptom: `OSError: Timed out trying to
  connect to tcp://127.0.0.1:<dashboard port>`).
- Probe scripts that spawn a cluster need `if __name__ == "__main__":`
  (spawn start method re-imports main → RuntimeError without it).

## Gate 1 evidence (local 200k, real cluster + real CLI)

Served P01 vs parquet path: sidecar `n_points` 160,975 == 160,975; PNG
723,000 B **byte-identical**. publish → plot → unpublish → cluster close
all clean. Gate 2 (<compute-node>) PASS criterion: P01 `n_points == 322,771,318`.
