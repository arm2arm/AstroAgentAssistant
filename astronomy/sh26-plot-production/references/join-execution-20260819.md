# v190826 join run: fixes, monitoring, dashboard — 2026-08-19

Execution record for the sh2026_join_papermill.ipynb re-run on <compute-node>
(see join-v190826-pm-float32.md for PM/float32 changes, and
join-on-<compute-node>-papermill.md for setup). Commit chain: 30b8d3c → 0d820bb →
150514b.

## Three fixes between first launch and successful re-run

1. **Pre-flight glob** (`0d820bb`): C/D split files are named `0.parq`,
   `10000.parq`, … — glob `*.parq`, NOT `part.*.parquet`. The first live run
   failed at the pre-flight assert on exactly this (good — pre-flight did its
   job before any compute).
2. **p2p spill disk** (`150514b`, user-directed: "the spill disk must be in
   /lustre/<user>/tmp"): <compute-node> `/tmp` is a **378 GB tmpfs (RAM-backed)**.
   A+B merge + 5 × `set_index(shuffle="p2p")` over 402M rows staged **185 GB**
   of p2p shuffle shards there → `P2POutOfDiskError` (ENOSPC) mid-run while
   351 GB RAM sat free. NOT a RAM problem: Dask p2p always stages shuffle
   shards through the worker scratch dir (`local_directory`). Fix:
   `local_dir = "/lustre/<user>/tmp/dask-sh26"` (1.6 PB free) + `rm -rf`
   the stale tmpfs scratch before relaunch. Cost: slower than tmpfs;
   benefit: no ENOSPC and ~185 GB of RAM no longer consumed by tmpfs
   buffering. Observed peak scratch on Lustre: **1.6 TB**, reclaimed to
   ~71 GB as stages completed.
3. **`--no-prompt` does not exist** in papermill 2.7.0 (I suggested it in the
   run commands; user corrected: "there is no --no-prompt option on
   papermill"). The command is simply:
   `python -m papermill sh2026_join_papermill.ipynb sh2026_join_out.ipynb`
   (no input cells in this notebook anyway).

## Monitoring pattern (worked)

- tmux session `join`; `tmux capture-pane -t join -p | tail -N` for cell
  progress + warnings.
- Milestones: pre-flight → `__tmp_base` (~24,576 parts, 103 GB) →
  `__tmp_dups` (20 parts) → `__tmp_enriched` (~25k parts) → `final` parts →
  verification prints `float64 cols remaining: none (all float32)`.
- Health checks: load avg, `free -g`, `du -sh` on scratch + output dirs.
  Worker `Pausing/Resuming at ~80% memory` log churn = normal backpressure,
  NOT OOM — do not react.
- ~6 h to the enriched stage (13:20 → 19:26 UTC). The parquet
  metadata-collection phase over ~49k input files is slow/single-core and
  looks "stuck" — it isn't.
- User preference observed: "let us just wait" — status ON REQUEST only;
  no watchers, no cron polls.

## Dashboard access (per-run random port)

Local `Client(...)` auto-assigns a scheduler port EACH run (41129, 43243, …)
and binds 0.0.0.0 — a `dashboard_address=":8787"` setting did NOT stick.
Discover on <compute-node>: `ss -ltnp | grep 0.0.0.0 | grep <kernel_pid>` → take the
non-127.0.0.1 entry. From a workstation (no route to the newton21 subnet —
tunnel through <compute-node>'s cluster IP):

```bash
ssh -L <port>:192.168.111.203:<port> -J arm2arm@141.33.4.144 <compute-node>.nnew
# → http://localhost:<port>/status
```

Attaching an interactive `Client("tcp://…")` to a saturated scheduler can
hang (observed 90 s timeout) — use the UI or file-based checks instead.
