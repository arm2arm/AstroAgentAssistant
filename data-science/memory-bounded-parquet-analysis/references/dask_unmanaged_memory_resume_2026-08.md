# Dask unmanaged-memory worker kill & checkpoint resume (SH26 402M Gaia join, 2026-08-19)

## Symptom chain (validated)

On a 402M-row, 133-column Gaia join with Dask 2025.10.0 p2p shuffle (24 workers × 24 GB, 754 GB node, conda env `sh25`, py3.12, run via papermill inside tmux):

1. **Leading indicator** — log floods with:
   `WARNING - distributed.worker.memory - Unmanaged memory use is high ... Unmanaged memory: 16.61 GiB - Worker memory limit: 22.35 GiB`
   numpy/pandas arenas are not returned to the OS; managed + unmanaged exceeds the limit even though `managed` alone looks fine. The warning wall precedes the kill by minutes.
2. **Kill** — one worker dies; ~50 events within 45 s:
   `CommClosedError: Ephemeral Worker->Worker for gather`, `StreamClosedError: Stream is closed`, `ConnectionResetError: Connection reset by peer`, `CancelledError`, `TimeoutError`, `Address removed`.
3. **Stall, not progress** — final output part count frozen (10 of ~400 expected, 3.2 GB) for 2 h while 15–19 workers sit at 30–60% CPU, load ~50. Dask retries the failed p2p gathers forever; the dead worker's in-flight data never resolves. **Waiting does not fix it.** Diagnosis: sample the part count twice 60 s apart (flat = stalled), check `ps -u <user> -o pcpu= | awk '$1>50' | wc -l` (high = spinning on retries, not idle).

## Fix that worked

1. **Checkpoint each big p2p stage to disk** as you go (the notebook already wrote `__tmp_base`, `__tmp_dups`, `__tmp_enriched` parquet checkpoints next to the output dir — `sh26_final_joined_v190826.__tmp_<stage>`). Checkpoints are what made the resume cheap; without them a kill means full recompute.
2. **Resume notebook**: start fresh `Client`, `dd.read_parquet(last checkpoint)`, load only the small external tables still needed (BJ21 ~GBs, W25 ~GBs vs. the 1.6 TB Gaia+SH21 stage already done), re-run the remaining `set_index(shuffle="p2p")` joins, `repartition(partition_size="512MB")`, write final. Saved ~5 h of a ~7 h run.
   - Build the resume notebook from the original by replacing the heavy cells: config cell + original client/helper/paths cell + one new "load checkpoint, stage-2 joins, repartition" cell + original final-write cell + original verification cell. Strip the lazy reads of inputs the checkpoint already merged.
3. **Retune the cluster**: fewer workers, *larger* per-worker limit — 24 × 24 GB → **16 × 40 GB** (16 × 40 = 640 GB < 754 GB node). Unmanaged headroom is the constraint, not raw total RAM: the 40 GB limit absorbed 16 GB unmanaged + ~18 GB managed without a single warning.

## Rule of thumb

For shuffle-heavy Dask joins: budget `memory_limit >= 2 x (managed peak + observed unmanaged)` per worker, and verify the unmanaged-warning count stays at zero in the first 10 minutes of the shuffle.

## Kill-and-relaunch sequence (validated commands, via jump host)

```bash
ssh arm2arm@<jump> "ssh <compute-node>.nnew 'tmux kill-session -t join; kill <papermill-pid>; sleep 5; pkill -f papermill; pgrep -af dask'"
# confirm load dropped (was ~52, expect <2) and no dask procs remain
# remove the partial output dir BEFORE relaunch (stale parts corrupt the final table)
tmux new-session -d -s joinres
tmux send-keys -t joinres "rm -rf <partial-out> && python -m papermill resume.ipynb out.ipynb 2>&1 | tee /tmp/joinres.log" Enter
```

Caveats: `pgrep -f` patterns that appear in the command line itself self-match — kill by PID or session name instead. Checkpoint dirs can be wiped by `rm -rf` of the parent if you use `*` globs — name the partial output dir explicitly.

## Dask dashboard access (same run)

`Client(dashboard_address=":8787")` binds the UI to the node. From a remote agent host: `ssh -N -f -L 18787:<node-ip>:8787 <jump>` then `curl http://127.0.0.1:18787/status/` (expect 200). On dask 2025.10 the `/api/v1/info` and `/api/info` endpoints 404/hang even though the UI serves — treat the dashboard as browser-only; monitor via CLI (part count, `ps`, log grep) instead of scraping the API. Keep the tunnel loopback-only on shared hosts; do not bind 0.0.0.0.
