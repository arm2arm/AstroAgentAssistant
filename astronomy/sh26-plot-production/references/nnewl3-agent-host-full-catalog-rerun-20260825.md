# Full-catalog plot runs on <compute-node>, driven from the agent host (2026-08-25, verified)

Ran P01–P04 on the full 402M v220826 catalog (~3 min/plot, all rc=0) using a
disposable git worktree + tmux. This is the repeatable recipe when the user
asks for full-catalog figures but the agent must not disturb the user's
working repo on <compute-node>.

## Topology (agent host has no route to 192.168.111.x)

```
agent --ssh--> arm2arm@141.33.4.144 (Newton) --ssh--> <compute-node>.nnew
```
- Every command: `ssh arm2arm@141.33.4.144 "ssh <compute-node>.nnew '<cmd>'"`
- File transfer is **two hops with Newton as relay** (no ProxyJump/`scp -3`
  between agent and <compute-node>):
  `cat script | ssh newton "cat > /tmp/s && scp -q /tmp/s <compute-node>.nnew:/tmp/s"`
- **Always md5-verify the script at every hop** (this caught a stale-script
  rerun failure).

## Environment on <compute-node>

- **Python env: `/lustre/<user>/SOFTWARE/conda/sh25/bin/python3`**
  (dask 2026.7.1, matplotlib, pyarrow, yaml — the FULL plotting stack).
  The `sh26` conda env has NO matplotlib; `tf2obj` either. Probe with:
  `$p -c "import matplotlib, dask.dataframe, pyarrow, yaml"` per env.
- User repo `/lustre/<user>/hermes/SH26` sits on an OLDER commit with
  uncommitted notebook work — **do not git-reset or stash it**. <compute-node> CAN
  reach the private GitLab remote (`git ls-remote git@gitlab.aip.de:<user>/SH26.git` works), so:
  ```
  cd /lustre/<user>/hermes/SH26
  git fetch origin sh26.plots.v0.2.0
  git worktree add /tmp/sh26_run_v020 <tag-SHA>   # worktree add by NAME fails; use SHA
  ```
  Clean worktree → `git status --short` empty → provenance sidecars record
  `git_dirty: False`.

## Launcher pattern (bash, one process per plot, sequential)

- Write the launcher LOCALLY, `bash -n` it, transfer (two-hop + md5),
  run under **tmux** (`tmux new-session -d -s sh26rN "bash /tmp/script.sh"`)
  so SSH disconnects can't kill it (Linger=no on this box — see
  <compute-node>-long-job-launch-20260825.md).
- **Bash pitfall (hit twice):** plot ids like `01` in a heredoc-embedded
  Python become `PID = 01` → SyntaxError (octal). Compute
  `local PIDNUM=$((10#$PID))` in bash and interpolate `$PIDNUM`.
- **Log pitfall:** use a FRESH log dir / truncate with `: >` per attempt;
  appending (`>>`) to per-plot logs makes reruns show stale failure lines
  above the new attempt.
- Structure: `run_plot()` per id with skip-if-PNG-exists, per-plot log
  `logs/pNN.log`, and a `MASTER.log` line `PNN rc=$rc HH:MM:SS` + final
  `ALL DONE` marker — status is then one `cat MASTER.log` away.
- Plot body: pyarrow-direct recipe (column pushdown via
  `_resolve(spec.columns, spec.derived, quality_cuts=False)` →
  `ds.dataset(DATA, format="parquet").to_table(columns=...)` →
  `MISSING == False` → `_derive` → `make(pdf, ctx)`), with `PlotContext(...
  extra={"loader": "pyarrow-direct", "quality_cuts": False, "code_fingerprint":
  code_fingerprint()})`. Data: `sh26_final_joined_v220826` (production
  recipe; no quality cuts — full-catalog figures use convergence filter only).
- Expected: read ~10–20 s, converged 402,121,784 → 327,477,457, P01 ~3 min
  (N=322,771,318 after photometry-NaN drop), P02–P04 ~2–4 min each, ~15 GB
  peak.

## Retrieving artifacts

```
ssh newton "scp -q <compute-node>.nnew:<out>/sh26_p0[1-4]_*.png /tmp/"   # on Newton
scp -q arm2arm@141.33.4.144:/tmp/sh26_p0*.png /tmp/local_dir/   # to agent host
```
Then deliver via `MEDIA:/local/path` (Telegram). Sidecar JSONs travel the
same path — they now carry `code_fingerprint` (git SHA + dirty) and
`library_versions`, which is the provenance proof for the rerun.

## QA notes

- `vision_analyze` flagged P01/P02/P04 axis labels showing literal
  `\n(col: ...)` — **false alarm**: matplotlib interprets `\n` in labels;
  the pre-existing full-catalog figures show the identical rendering.
  Confirm against a known-good shipped figure before "fixing" anything.
- P04 is a rectangular (l, b) equirectangular map by design (matches
  shipped production P04), not an elliptical Mollweide — also not a bug.
