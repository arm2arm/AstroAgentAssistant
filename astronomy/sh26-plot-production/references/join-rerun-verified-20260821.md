# SH26 full-catalog join re-run — VERIFIED (2026-08-21)

Companion to `join-2node-corruption-fix-20260820.md`. The single-node
papermill re-run (launched 2026-08-20 22:03 UTC, tmux `join`/`wk1` on
<compute-node>) **completed overnight** and the output is correct — even though
papermill's last cell raised on a stale assert (see below).

## Verified output (checked 2026-08-21, no re-run needed)

`/lustre/<user>/ipython/SH2025/reana/final/combined/sh26_final_joined_v190826/`

- **402,121,784 rows × 132 cols**, 197 GB, **3032 parts**
- == the verified known-good single-node run exactly
- MISSING: 74,644,327 (18.56%); SHBOOST/MISSING crosstab:
  (F,F)=137,859,267 (T,F)=189,618,190 (F,T)=48,947,687 (T,T)=25,696,640
- duplicated source_ids: 14,865; no float64 leaks; column set exact (132)
- A=215,234,730, B=186,804,256, A+B=402,038,986 → final = A+B+82,798
  (benign duplicate-key fan-out, stable across correct runs)

All 8 Stage-0 caches rebuilt fresh 2026-08-20 22:04–22:12; stage caches
base/dups/enr1/enr2 rewritten 22:42–04:21. Corrupted 4.8M output still
quarantined as `..._CORRUPT_4.8M`.

## Why papermill "failed" at the end — stale exact assert

VERIFY cell (cell In[10]) raised:
`ROW COUNT MISMATCH: final=402,121,784 vs A+B=402,038,986 ... data loss, do not use`.
That assert was the OLD exact-equality check. The 2026-08-20 "one-sided
asserts" commit (8330ccc) claimed to fix `_write` **and** VERIFY; only the
`_write` half actually landed (the VERIFY-cell `str.replace` failed its
exact-text match in a partially-applied multi-cell patch). The run data
was never wrong — the tripwire was miscalibrated.

Fix: commit **931000a** — VERIFY now does `assert final >= A+B` (loss =
hard fail) + prints `MATCHES known-good run` when `final == 402,121,784`.
Deployed to <compute-node>, md5-verified.

**Lesson (generic):** multi-cell notebook patches with per-cell
`assert old in src` fail loudly at the FIRST mismatch, but the file is
already half-rewritten by then, and a later commit captures the partial
state. Post-patch verification must grep the COMMITTED blob for every
intended marker (`git show <sha> -- <file> | grep <marker>`), not just the
pre-deploy working tree.

## Deploying to a dirty remote working tree (<compute-node>)

<compute-node>'s repo has uncommitted local edits (config/dask.yaml, worker
script) → `git pull` refuses. `scp` and nested-ssh heredocs both failed
(two-hop stdin/`-c` quoting; large base64 arg through double ssh died
with exit -1). What WORKED:

```bash
# on <compute-node> (reachable via Newton 141.33.4.144):
cd /lustre/<user>/hermes/SH26
git fetch origin                      # objects arrive even when tree is dirty
git cat-file -e 931000a && echo HAS_COMMIT
git show 931000a:notebooks/sh2026_join_v2.ipynb > /tmp/nb931.ipynb
md5sum /tmp/nb931.ipynb               # compare with local md5
cp /tmp/nb931.ipynb /lustre/<user>/hermes/SH26/notebooks/sh2026_join_v2.ipynb
```

`git show <sha>:<path>` sidesteps the dirty tree entirely — deploy an
exact committed blob, then md5-verify against local. (<compute-node> tree sync
still pending — user needs to decide; offered but not yet approved.)

## Next steps (planned, not started)

Plots campaign on the verified 402M output, 3 waves:
1. **Smoke:** `python -m sh26 plots -p 1,2 --data <final> --outdir /lustre/<user>/hermes/sh26_full/figures --no-cuts`
2. **Cheap:** `-p 1-71,76-81,83-89,92-94 --combine` (~74 plots)
3. **Expensive ML:** P72/74/79/90/91 subsampled to 5M, labeled
Env: `/lustre/<user>/SOFTWARE/conda/sh25/bin/python` (sh26 editable-installed).
Cluster: `config/dask.yaml` (24×4 threads × 30 GB, dashboard :8787) — the
sh26 CLI builds its OWN LocalCluster, so kill the join's scheduler/`wk1`
worker set (tmux `wk1` still up, 24 idle workers) before Wave 1 to free
:8787 + RAM.
Housekeeping available: delete stale `sh26_final_joined_v190826.__tmp_*`
dirs from old runs; sync <compute-node> working tree to committed state.
