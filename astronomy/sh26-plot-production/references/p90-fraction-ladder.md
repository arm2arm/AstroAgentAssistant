# P90 fraction ladder: precompute → cache → render recipe

Measured 2026-08-18. This supersedes the "1.94M t-SNE infeasible (days)"
timing block in `p90-long-embeddings.md`.

## Recipe (validated at 10/20/35/50%)

1. **Derive the exact cache key first** — the plot module's
   `_cache_key(n, params)` gives `n = int(N_FULL * frac)` and
   `key = md5(f"p90|n={n}|pp=30|mi=1000|nn=15|md=0.1|seed=42|sub={frac}")[:12]`.
   Print it BEFORE running anything; the precompute script and the
   `--param` render must agree or you recompute for nothing.
2. **Precompute embeddings in a user-oneshot** (`scripts/p90_embed_<F>pct.py`,
   cloned from the previous fraction via sed on FRAC/KEY/name). It loads the
   quantile-scaled full box `/tmp/p90_scaled_73e9427dba4a.npy`
   (1,941,062 × 14 — already cached), subsamples with
   `np.random.RandomState(42).choice(n_full, size=int(n_full*frac), replace=False)`
   — EXACTLY the plot module's scheme (do NOT use `default_rng`; the module
   uses legacy `RandomState`, mismatched draw order → cache miss at render) —
   then QuantileTransformer (no n_jobs!) → t-SNE(pp=30, mi=1000, n_jobs=8,
   verbose=0) → UMAP(nn=15, md=0.1, serial by seed), saving all three
   `/tmp/p90_{scaled,tsne,umap}_<key>.npy` so the render is a cache hit.
3. **Render foreground** (fits one 600 s call, ~16 s after the 40 s Dask
   load):
   `PYTHONPATH=src python -m sh26 plots -p 90 --data data/sh26_joined_50m_pm.parq --no-cuts --param p90.subsample=<frac> --threads 16 --memory 64GB`

## Pitfalls hit this session

- **FORGET `--no-cuts` → hard fail**: QC cuts 40.7M → 8.6M rows, box+finite
  drops to 176 stars, `RuntimeError: P90: too few selected rows`. The
  module's selection is built on the converged+PM+finite population; the
  full-catalog runs are `--no-cuts` (per user default). Cache key n then
  also mismatches.
- **Module not importable from bare venv** — must `PYTHONPATH=src` (repo is
  not pip-installed); `python -m sh26` from the repo dir without it
  → `No module named sh26`.
- **CLI positional is `-p 90`, not `90`** — bare `plots 90` →
  `unrecognized arguments` (argparse exit 2, empty of useful output if you
  only grepped).
- **sed-cloning the unit file leaves stale names** in ExecStart/Output if
  you sed `p90-embed-35pct` before `p90_embed_35pct` — run both seds and
  verify `grep ExecStart` before daemon-reload.
- **Figure filename collision**: every render overwrites the SAME
  `paper/figures/sh26_p90_tsne_umap_cmd_center.png/pdf/json`. The JSON
  sidecar records the actual `n_selected`/frac, but the PNG on disk is
  always the last render. If the user wants a ladder to compare side by
  side, copy each fraction out to a distinct name right after rendering.
- Foreground terminal `sleep 500` calls time out at 420 s — poll in ≤400 s
  sleeps; the oneshot keeps running regardless.

## Measured timings (host, 20 cores; box of 1,941,062 stars)

| frac | n | t-SNE (pp30, mi1000, 8j) | UMAP (nn15, md0.1, serial) |
|---|---|---|---|
| 10% | 194,106 | 258 s | 84 s |
| 20% | 388,212 | 654 s | 198 s |
| 35% | 679,371 | 1315 s | 383 s |
| 50% | 970,531 | 2035 s | 683 s |

Scaling mildly super-linear (t-SNE ≈ n^1.4). **Full 1.94M extrapolation:
t-SNE ~1.5 h + UMAP ~25 min ≈ 2 h** — a single host oneshot is feasible for
the final 100% deliverable; the older "days / use SLURM" guidance is
overridden by these measurements.

## Cache keys (this ladder)

10% `3f8c8b965afb` · 20% `81d2fcbd0597` · 35% `e1ca38174d3d` · 50%
`1dc1aea909d5` · full(1.0) `73e9427dba4a` (no `|sub=` in key).
