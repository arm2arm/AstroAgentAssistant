# Long raw-data embeddings on the host (t-SNE / UMAP)

Class pattern for embedding jobs that exceed the terminal tool limits
(P90: 1.94M points × 14-D t-SNE + UMAP).

## Terminal tool hard limits (measured 2026-08-17)
- Background sessions: `memory.max = 4294967296` (4 GiB) cgroup cap →
  OOM kill (-9) the moment a job peaks above it.
- Foreground: memory unlimited (user slice `max`), but a single call
  cannot exceed ~600 s.
- Host: 121 GB RAM, 20 cores; `hermes` has NO sudo.

⇒ any job that is both >10 min AND >4 GB must run outside the terminal
tool.

## Working pattern: systemd user oneshot (no sudo)
Runs under `user-1003.slice` (unlimited memory, all cores):
1. Self-contained job script with its own shebang
   (`#!/home/hermes/.hermes/hermes-agent/venv/bin/python`; that venv has
   sklearn 1.9.0 / umap 0.5.12 / numpy 2.4.6 / matplotlib 3.11.1): read
   cached inputs from /tmp, write outputs to /tmp, print progress lines.
2. Unit `~/.config/systemd/user/<name>.service`:
   ```ini
   [Unit]
   Description=...
   After=network.target
   [Service]
   Type=simple
   WorkingDirectory=/home/hermes/projects/SH26
   StandardOutput=append:/tmp/<name>.log
   StandardError=append:/tmp/<name>.log
   ExecStart=<venv-python> <script>
   ```
3. `systemctl --user daemon-reload && systemctl --user start <name>`
4. Poll `systemctl --user is-active <name>`; logs: `cat /tmp/<name>.log`;
   RAM/CPU: `systemctl --user status <name>`.
5. Stop: `systemctl --user stop <name>` (tool consent prompt may fire —
   ask the user to confirm in chat).

## Pitfalls (all hit live, 2026-08-17)
- **ExecStart does NOT parse bash `2>&1`.**
  `ExecStart=/bin/sh -c 'python script.py > log 2>&1'` makes the wrapper
  shell misparse the redirection and **exit 0 without ever running the
  command** (systemd reports `Result=success`, the log stays
  empty/stale). Use systemd-native `StandardOutput=append:` /
  `StandardError=append:` (or `StandardOutput=file:...`) instead.
  Debug symptom: service inactive immediately, `ExecMainStatus=0`,
  log file unchanged.
- **Hermes venv sklearn (1.9.0, CPython 3.11.15 aarch64) ships a VERBOSE
  t-SNE Cython build**: prints `[QuadTree] Inserting depth …` / `selected
  child` and `[t-SNE] …` lines to stderr for EVERY point insertion
  (millions/min at 1.94M). With `StandardError=journal` this floods
  rsyslog: ~1 GB/h to `/var/log/syslog` — the disk fills mid-run.
  Unsilenceable from Python (TSNE has no verbose kwarg; build-level
  printf). Always redirect to a FILE. If already flooding (user sudo):
  `/etc/rsyslog.d/10-no-quadtree.conf` with `:msg, contains, "[QuadTree]"
  stop` + `:msg, contains, "[t-SNE]" stop`, then `systemctl restart
  rsyslog` and `truncate -s 0 /var/log/syslog`. The inner-loop log I/O
  also measurably slows each iteration.
- **QuantileTransformer (this sklearn) has NO `n_jobs` kwarg** — pass
  `random_state` only; `n_jobs=-1` crashes the whole run.
- sklearn t-SNE writes embeddings ONLY on clean finish — a mid-run kill
  loses everything. Cache the quantile-scaled input matrix to /tmp first
  so the rerun starts from there.
- **A foreground run of the job script that hits the 600 s command
  timeout leaves an ORPHAN process** that keeps running. `pgrep -af`
  output includes the tool call's own bash wrapper — identify the real
  job by its python script path and kill the orphan BY PID before
  starting the oneshot (avoid `pkill -f` — it can match the tool call's
  own command line and hang the call).
- `fill_between`/`plot` have no `step` kwarg in matplotlib — use
  `ax.fill_between(x, h, step="pre")` / `ax.step(x, h, where="pre")`.
- Open-ended histogram bins swap easily — after binning, verify the bins
  partition (sum of per-bin counts == total).

## Timing numbers (host, 20 cores)
- t-SNE 200k×14-D, 250 iters, 8 jobs: 207 s (neighborhood phase parallel).
- t-SNE 19.4k×14-D, 1000 iters, 8 jobs: **74 s** (1% subset, foreground).
- UMAP 19.4k: 16 s.
- t-SNE 1.94M×14-D, pp=30: neighborhood build ~1 h (parallel 8), then
  gradient iterations ~40–45 min EACH (single-threaded in this build)
  → 1000 iters is infeasible on host (days). For full runs use
  `max_iter` 300–500 (KL plateaus fast) or a SLURM node.
- UMAP 1.94M: expect ~10–20 min.

## Interactive test protocol (user preference)
- User rejected the 200k-cache smoke test for P90 — test on a **seeded
  1% subset of the real 50M selection** instead (subsample param, seed 42,
  separate cache key). Same pipeline, one foreground call. Then "do it
  for 10% sample" — subset-first (1% → 10% → full) before any full run.
- User also said "stop watching job": do NOT set up continuous watchers
  (background pollers, cron monitors) for long jobs — report status on
  request only, and remove any watchers when asked.
- Param overrides without code edits: `python3 -m sh26 plots -p N
  --param pN.<key>=<value>` (`cli.parse_params` coerces int/float).

## P90 specifics
- Input: `data/sh26_joined_50m_pm.parq` (catalog+PM join; pm_50m.parquet =
  49,993,036 rows: source_id, pmra, pmdec, pmra_error, pmdec_error,
  astrometric_params_solved).
- Box X[-4,4] Y[-3,3]: 2,032,412 converged; 1,941,062 finite in all 14
  columns (95.5%; dropouts = no PM match or NaN photometry → no imputation).
- Module: `src/sh26/plots/p90_tsne_umap_cmd_center.py`; `subsample` param
  (1.0 full / 0.01 / 0.1 test). Cache: `/tmp/p90_{scaled,tsne,umap}_<key>.npy`,
  key = `md5("p90|n=..|pp=..|mi=..|nn=..|md=..|seed=42[|sub=..]")[:12]`.
  A cache-hit render fits one 600 s foreground call (~5–8 min: Dask load +
  hexbin + save).
- 10% run (194,106 stars): oneshot `p90-embed-10pct.service` with the
  file-redirection unit above; key `3f8c8b965afb`.
