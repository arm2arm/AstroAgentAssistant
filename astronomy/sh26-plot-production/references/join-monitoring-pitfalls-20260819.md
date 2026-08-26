# Monitoring a long Dask/papermill run on a remote node — pitfalls (2026-08-19)

Follow-up to `join-execution-20260819.md` (setup + fixes). These monitoring
lessons came from the final hours of the 402M-row join run.

## Do NOT infer worker death from process names

With an in-process `Client(n_workers=…)` (notebook/papermill pattern),
worker processes' `comm` is plain **`python`**, not `dask_worker`.
`pgrep dask_worker` / `ps aux | grep dask_worker` returns EMPTY even for a
fully healthy 24-worker cluster — this produced a false "all workers
exited" alarm. Reliable check:

```bash
# find the kernel: child of the papermill pid (ipykernel_launcher)
ps --ppid <kernel_pid> -o pid,pcpu,pmem,etime,comm
# ~20 rows at 92–102% CPU = cluster grinding, not hung
```

`pgrep -f distributed` also misses them (cmdline is `python
-Xfrozen_modules=off -m ipykernel_launcher ...` on the workers here).

## Dashboard port: why the requested port "didn't stick"

`dashboard_address=":8787"` silently fell back to a random port (41129,
43243, …) because a **stale scheduler from an old run (state T — stopped,
never killed) still held the listening sockets on 8786 AND 8787**
(`ss -ltnp` shows them with the old PID). Port discovery that works:

```bash
# on the node: non-loopback listener of the kernel pid
ss -ltnp | grep 0.0.0.0 | grep <kernel_pid>
# health: curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:<port>/status  → 200
```

Tunnel from a workstation (no route to the private subnet):
`ssh -L <port>:<node_cluster_ip>:<port> -J <jump_user>@<jump_host> <node>`.
For a stable port: kill the stale T-state scheduler first (tenant process —
user approval), then `:8787` binds.

## Part-count plateaus are not stalls

During the final `to_parquet` cell the on-disk part count sat at 10/24,500
for 30+ min while every worker ran 92–102% CPU. Remaining partitions are
the widest (full join + float32 cast over 133 cols) and flush only on
partition completion. Liveness = worker %CPU + scratch-dir `du -sh`
movement, NOT new-file arrival rate. (Run was still in progress at session
end — the plateau→completion transition was not observed; treat as
consistent-with, not guaranteed.)

## Noise + dead-end monitoring paths

- **tmux pane floods**: the per-worker `Unmanaged memory use is high`
  warning loop (benign — numpy arenas not returned to OS) scrolls real
  output off-screen. Read with a filter:
  `tmux capture-pane -t join -p -S -200 | grep -avE "Unmanaged memory|not released" | tail`.
- **Scheduler HTTP API**: `/api/v1/tasks`, `/api/v1/summary` → **404** on
  dask 2025.10 (dashboard is the tornado UI, not the old API). Attaching an
  interactive `Client("tcp://…")` to a saturated scheduler can hang (90 s
  timeout observed). Do not build monitoring on either.
- `dmesg`/`journalctl` OOM checks may be permission-denied on cluster
  nodes; cross-check with `free -g` (plenty free ⇒ not OOM).

## One-shot progress probe (paste-ready)

```bash
tmux capture-pane -t join -p -S -200 | grep -avE "Unmanaged memory|not released" | tail -6
for d in __tmp_base __tmp_dups __tmp_enriched; do
  echo -n "$d: "; ls <out_root>/sh26_final_joined_v190826.$d 2>/dev/null | wc -l
done
echo -n "final: "; ls <out_root>/sh26_final_joined_v190826 2>/dev/null | wc -l
du -sh <scratch_dir> <out_root>/sh26_final_joined_v190826 2>/dev/null
ps --ppid $(pgrep -f ipykernel | head -1) -o pcpu= | sort -rn | head -3
free -g | sed -n 2p; uptime
```
