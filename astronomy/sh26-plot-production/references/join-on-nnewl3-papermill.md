# Running the SH26 catalog join on <compute-node> (papermill) — 2026-08-19

Context: user wanted to re-run the catalog join themselves on the reserved
node. Two papermill wrappers were committed to the repo (`/home/hermes/
projects/SH26`, branch main, ~b593bb5) plus the original kept as reference:

- `notebooks/sh2026_join.ipynb` — the ORIGINAL, verbatim (reference).
  Connects to `Client("tcp://141.33.4.144:8786")` + `client.restart()`.
- `notebooks/sh2026_join_papermill.ipynb` — the RUNNABLE join: local Dask
  cluster, absolute paths, a pre-flight input-existence assert, and papermill
  params `root25`, `workdir`, `n_workers`, `threads_per_worker`,
  `memory_limit`, `local_dir`.
- `notebooks/all_plots_papermill.ipynb` — the plot-campaign wrapper (separate
  task, same session): Agg backend → env/data check → smoke P01+P40 (aborts
  on failure) → `python -m sh26 plots --all` under the hood → moves the
  combined PDF to `SH26/sh26_all_full.pdf`.

## Two corrections vs the original join notebook (the actual work)

1. **The remote scheduler is dead.** `ssh arm2arm@141.33.4.144 && ss -ltnp |
   grep 8786` is empty (verified 2026-08-19) — nothing listens, and the stale
   STOPPED scheduler PIDs from the 2026-08-18 plan are gone; node idle
   (load 0.00, ~742 GB free). Re-check before scheduling (shared node).
   Use a LOCAL cluster on <compute-node> instead:
   ```python
   from dask.distributed import Client
   client = Client(n_workers=24, threads_per_worker=4, memory_limit="24GB",
                   dashboard_address=":8787", local_directory="/tmp/dask-sh26")
   # 24×4 procs / 576 GB — fits the 96-core / ~754 GB node.
   ```
   Dashboard forward (<compute-node> → Newton): `ssh -L 8787:localhost:8787
   -J arm2arm@141.33.4.144 <compute-node>.nnew` → http://localhost:8787

2. **Two-root relative paths.** The original notebook's cwd was
   `SH2025/reana/`, so `final/...` resolved to `SH2025/reana/final/...` but
   `../IN_SH_2021_RERUN` and `../gaiadr3` resolved to `SH2025/...`. A single
   `workdir` root gets both wrong. Split into two params:
   - `root25  = /lustre/<user>/ipython/SH2025`
   - `workdir = /lustre/<user>/ipython/SH2025/reana`
   and prefix each path with the correct root:
   | input | root | path under root |
   |---|---|---|
   | A (SH26 WITH_SHBOOST) | root25 | IN_SH_2021_RERUN/WITH_SHBOOST/*parq |
   | B (SH26 WITHOUT_SHBOOST) | root25 | IN_SH_2021_RERUN/WITHOUT_SHBOOST/*parq |
   | C (shboost_splits) | workdir | final/results/shboost_splits/ |
   | D (splits) | workdir | final/results/splits/ |
   | Gaia float32 | root25 | gaiadr3/GaiaSource.float32.parq |
   | SH21 | root25 | gaiadr3/STAGE3_FINAL_SH_2021/sh_edr3_2021_v1.2.parq/ |
   | BJ21 | root25 | gaiadr3/BailerJones2021/gedr3dist_512_split.dump.parq/ |
   | W25 | root25 | gaiadr3/weiler25_distances_small.parq |
   | output `sh26_phase2` (+`__tmp_base/dups/enriched`) | workdir | final/combined/... |

## Run commands (on <compute-node>, in tmux — hours)

```bash
ssh arm2arm@141.33.4.144 && ssh <compute-node>.nnew
mkdir -p /lustre/<user>/hermes/SH26 && cd /lustre/<user>/hermes/SH26
git clone git@gitlab.aip.de:<user>/SH26.git . 2>/dev/null || git pull
cd notebooks
tmux new -s join
/lustre/<user>/SOFTWARE/conda/sh25/bin/python3 -m papermill \
  sh2026_join_papermill.ipynb sh2026_join_out.ipynb --no-prompt
```

Pre-flight inputs (all present 2026-08-19): A/B 12,288 parts each; C/D ~12,288;
Gaia float32 4,096; SH21 386; BJ21 514; W25 66. **Output overwrites
`reana/final/combined/sh26_phase2` + the three `__tmp_*` dirs** (June
artifacts). The join is deterministic, so a re-run reproduces them; the 210 GB
`sh26_final_joined/` is a DIFFERENT path and is not touched. (Open question
left to user: add an `out_suffix` param if a non-destructive parallel output
is wanted.)

## Pitfall (hit this session — general, not SH26-specific)

**Never edit a `.ipynb` with the `patch` tool / raw text find-replace.** A
cell's `source` is a JSON list of individually-escaped strings; a fuzzy text
patch that inserts a raw multi-line code block breaks the escaping
(`json: Expecting value: line N`) and the notebook stops loading. I hit this
on `sh2026_join.ipynb` and had to `scp` the original back from Newton to undo
the mangle. Edit notebooks PROGRAMMATICALLY instead:

```python
import json
nb = json.load(open(path))
# mutate: nb['cells'][i]['source'] = [line + '\n' for line in new_code.split('\n')]
json.dump(nb, open(path, 'w'), indent=1)
json.load(open(path))                       # re-validate JSON
for i, c in enumerate(nb['cells']):         # re-validate code
    if c['cell_type'] == 'code':
        compile(''.join(c['source']), f'<cell {i}>', 'exec')
```

For papermill, tag the params cell `{"tags": ["parameters"]}` and put
`matplotlib.use("Agg")` before any pyplot import for headless nodes.
