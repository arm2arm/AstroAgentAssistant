# P90 — Raw per-star embeddings: OOM reality + Newton offload plan

Session 2026-08-17. User requested P90 = t-SNE + UMAP + CMD, inner box
X∈[−4,4], Y∈[−3,3] kpc, on the **raw** selected stars (explicit: "do not
bin anything… only normalize/rescale using quantile scaling"). 14-D
feature set: `l, b, dist50, teff50, logg50, met50, AV50, XGal, YGal,
ZGal, mg0, bprp0, pmra, pmdec` (pmra/pmdec joined via
`data/sh26_joined_50m_pm.parq`).

## Verified facts
- Sample = box ∩ finite-in-all-14 = **1,941,062** stars (95.5% of the
  2,032,412-star box). PM coverage in the *inner* box is far higher than
  the full-disk 41% (P82) — most inner-box stars matched in pm_50m.
- pm_50m.parquet: 49,993,036 rows; cols `pos, source_id, pmra, pmdec,
  pmra_error, pmdec_error, astrometric_params_solved`. Pre-joined
  catalog: `data/sh26_joined_50m_pm.parq` (and 200k:
  `data/sh26_cache_200k_pm.parq`).
- P75 precedent embedding feature set (11-D, cell-based): XGal, YGal,
  ZGal, teff50, logg50, mass50, age50, met50, mg0, bprp0, AV50 — via
  quantile-grid r=3/dim → ~177k cells, ~34k occupied; QuantileTransformer
  → TSNE(30)/UMAP on cell CENTERS, colored by met50. P73/P74 same grid.
- sklearn 1.9.0 / umap 0.5.12 / numpy (local venv).
- QuantileTransformer (uniform, n_quantiles=10000, seed=42) on the
  1.94M×14 matrix peaks ~2–3 GB and completes (~fine in background).
  Its output is 217 MB, cached to `/tmp/p90_scaled_<key>.npy`.

## The OOM wall (verified, two kills)
Hermes worker scopes are hard-capped at 4 GiB cgroup (`memory.max =
4294967296`). Host RAM (115 GB free) is irrelevant. Foreground is capped
at 600 s. sklearn `TSNE(perplexity=30, n_jobs=8).fit_transform` on 1.94M
points:
- Phase 1 (pairwise/conditional-probability pass) completes → prints
  "Mean sigma: 0.095".
- Phase 2 allocates the full neighborhood graph / P-matrix → **peaks just
  over 4 GiB → kernel OOM-kills the process (exit -9).**
So raw ~2M-point t-SNE cannot run in ANY session scope. UMAP on the same
matrix would be a similar order of memory (fit is cheaper but still
hundreds of MB to GB; the t-SNE is the hard blocker).

## Offload pattern (PLANNED — NOT end-to-end verified)
The transfer/submit step was gated by the user before completion, so the
end-to-end run is NOT confirmed. Treat as a candidate plan, re-verify each
step. Design that makes the *local* render a pure cache-hit:

1. Plot module caches everything to `/tmp` keyed by `md5(n_rows|perplexity
   |max_iter|umap_nn|umap_min_dist|seed)`:
   - `p90_scaled_<key>.npy` (the 14-D quantile-scaled matrix)
   - `p90_tsne_<key>.npy`, `p90_umap_<key>.npy` (2-D embeddings)
2. Local run does Dask load + selection + QuantileTransformer → writes
   scaled matrix, then tries to load embeddings from cache.
3. Cluster (Newton): copy scaled matrix + a tiny embed script to
   `/lustre/<user>/hermes/p90_embed/`; `sbatch` a node (~32 GB, ~1–2 h);
   script runs TSNE then UMAP (skip-if-cached), writes tsne.npy/umap.npy.
4. Fetch the two .npy back to local `/tmp/p90_{tsne,umap}_<key>.npy`;
   re-run the plot locally — it hits the embedding caches and only does
   load + hexbin + save (fits 4 GB, well under 600 s).

Verified sub-steps: Newton `sh25` conda env has **sklearn 1.7.1 +
umap 0.5.12** (installed umap-learn into it this session); scaled matrix
is 217 MB and present locally. NOT verified: scp transfer + sbatch +
fetch (gated before running). Embedding script written locally at
`/home/hermes/projects/SH26/scripts/p90_embed_job.py` (arg1=in dir with
scaled.npy, arg2=out dir; runs TSNE(PP=30,MI=1000,n_jobs=-1) then
UMAP(NN=15,MD=0.1,n_jobs=-1), skip-if-exists).

## In-session-safe fallback (VERIFIED pattern from P73–P75)
Cell-binning (quantile-grid r=3/D, embed ~34k–hundreds-of-k cell centers)
is the path that fits in a session. The user explicitly rejected binning
for P90, so use Newton for the true raw version; if Newton is off the
table, the only in-session options change the science (subsample for the
embedding only, or perplexity ~10 to squeeze under 4 GiB) and must be
confirmed with the user as a deviation.

## Code pitfall
sklearn 1.9.0 `QuantileTransformer.__init__` has **no `n_jobs` kwarg**
(TypeError). Remove it — the scaling step is fast regardless.
