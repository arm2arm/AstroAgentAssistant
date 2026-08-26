# "Is the job finished?" — output verification pitfalls (2026-08-20)

Session context: user asked whether the <compute-node> SH26 join run had finished and
where its outputs were. The run was alive (kernel + ~15 python workers, ~8.5h
elapsed), but **no new output had been written** — everything on disk under
`final/combined/` dated from a May 25 run. Companion to
`join-monitoring-pitfalls-20260819.md` (process/dashboard lessons).

## 1. Output existence ≠ job completion — always check mtime

- `final/combined/sh26_phase2` (10 parts, 2.2 GB) and its `__tmp_base/dups/
  enriched` dirs existed but all stamped **2026-05-25 15:0x** — a prior run's
  artifacts. The current run (started 2026-08-18 ~23:00 UTC) had written
  nothing in ~30 h.
- Procedure: `stat -c "%y %n"` on the output part files AND the temp dirs;
  compare against the run start (kernel PID `etime`). Then sweep:
  `find /lustre/<user> /tmp -xdev -newermt "<run start>" -size +1M` — zero
  hits means no new data landed, no matter how busy the workers look.
- A low node load (0.89 on a 96-core node) with workers at ~10% CPU is
  consistent with an early/mid stage (read+shuffle) OR a stall — process
  liveness alone cannot tell them apart without scheduler state.

## 2. The saved .ipynb is a stale snapshot, not live state

- `sh2026_join.ipynb` on disk was last saved 2026-08-18 23:57, before the
  current run finished its first cells. Its outputs showed a
  `P2POutOfDiskError` ("P2P ran out of available disk space while temporarily
  storing transferred data") in cell 5 yet printed full final stats in cell 6
  (rows 402,121,784; missing 74.6M = 18.56%; 14,865 duplicated source_ids) —
  internally inconsistent because the saved state mixes executions.
- Use the notebook ONLY for: which paths it writes (`to_parquet` targets:
  `final/combined/sh26_phase2` + three `__tmp_*`, relative to
  `SH2025/reana/`) and the join logic. NEVER quote its printed numbers as the
  current run's result.
- Notebook inspection that worked (quoting-safe — write a script, scp it,
  run remotely; do NOT inline python in nested ssh): `json.load` the .ipynb,
  iterate code cells, print `execution_count` + output types + last stream
  tail + any traceback. A cell with `execution_count=None` + saved output =
  ran in an earlier kernel session, not the live one.

## 3. Port-scanning loopback for the dashboard is a dead end

- The kernel's in-process Dask cluster listens on random loopback ports
  (visible via `ss -tlnp | grep <kernel_pid>`). A curl scan over all python
  listener ports for `/api/info` hung past 90–120 s with no hit. Do not
  build monitoring on blind port scanning.
- `Client("tcp://141.33.4.144:8786")` in the ORIGINAL notebook's cell 0 is
  dead (connection-refused from both Newton and <compute-node>) — that scheduler is
  gone; the live cluster is local to the kernel on <compute-node>. If a user runs the
  ORIGINAL notebook (not the papermill wrapper), its dashboard is
  unreachable/unknown and verification must fall back to mtime + process
  liveness (and asking the user to look at the notebook UI).

## 4. Remote python via nested ssh — quoting

- Inline `ssh A "ssh B 'python3 -c \"...\"'"` with regex/re strings in it
  broke on quote mangling (multiple attempts). Pattern that worked every time:
  `write_file` locally → `scp` to jump → `scp` to node → `python3 script.py`.
- Filter the constant noise on Newton (`module: command not found` from
  .bashrc, ECDSA known-hosts warnings on <compute-node> hop) with
  `grep -vE "module: command not found|ECDSA|Offending|Matching"`.
