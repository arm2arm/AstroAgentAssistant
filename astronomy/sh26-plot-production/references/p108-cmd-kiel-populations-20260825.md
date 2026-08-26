# P108 — multi-population CMD/Kiel dashboard (2026-08-25)

`src/sh26/plots/p108_cmd_kiel_populations.py` — 3×2 grid, **rows =
populations (FULL / RUWE≤1.4 / ruwe2=1 binary), columns = diagrams
(CMD | Kiel)**. Same layout class for any "same diagram, several
populations" request.

## Key design points

- **Shared color scale across all population panels**: compute the max
  cell count once from the FULL panel's hexbin, then
  `norm = LogNorm(vmin=1, vmax=max(cmax, 2))` for every panel. A
  filtered panel then reads as "same locations, lower colors = fewer
  survivors" — directly comparable. (vmin=1 floor = the "thin"
  light-grey sparse cells, same trick as P107 underlay.)
- cmax probe: throwaway `fig/ax` + `ax.hexbin(...).get_array().max()`,
  `plt.close(fig)` — cheap even at 327M rows.
- Kiel axes: 0.5/99.5 percentiles of the FULL kiel-finite sample, fixed
  once and shared across the 3 rows (CMD uses project-fixed
  (-1.5,4)×(-4,16) inverted).
- SPEC columns must include `dist50` even though make() never plots it —
  `sh26.lazy_catalog._derive` needs it for `mg0`. Forgetting it →
  `KeyError: 'dist50'` in smoke test.
- `ruwe2` is a REAL v250826 column (134 cols) — read directly, never
  recompute.

## Pitfalls hit this session

- **`ax.hexbin` accepts `bins="log"` OR `norm=` — never both.** Passing
  both warns `Only one of 'bins' and 'norm' arguments can be supplied,
  ignoring bins='log'` and silently drops the floor (log scale from 1
  becomes log of raw counts with mpl's own floor → different look).
  For a custom floor use `norm=LogNorm(vmin=1, vmax=...)` and OMIT
  `bins`.
- **pyarrow 3.1.2 API**: `dataset.files` is a **property** (not a
  method — `d.files()` → `TypeError: 'list' object is not callable`);
  `dataset.get_fragments()` returns a **generator** (not sliceable —
  wrap in `list(...)`); fragments are not sortable and can't be passed
  back to `ds.dataset(fragment)`. Cheapest per-file read:
  `pyarrow.parquet.read_table(path, columns=[...])` over
  `sorted(d.files)[:N]`.
- **Fraction semantics — raw vs converged**: v250826 build verification
  quoted ruwe2 = 10.5–10.8% (RAW 402M sample). On the CONVERGED
  population (MISSING==False, what every plot shows) it is **8.1%**
  (26,488,335 / 327,477,457). The binarity flag concentrates in
  non-converged stars. Any quoted flag fraction must state raw vs
  converged; sidecar `n_ruwe2` uses converged.
- Smoke fixture for this class needs: teff50, logg50, dist50, AV50,
  g/BP/RP mags, ruwe, ruwe2 (with NaN semantics — `np.full(N, np.nan)`
  then set 1.0 on the flagged fraction).

## Full run (v250826, <compute-node>)

- Runner: `run_p108_direct.py` in `/lustre/<user>/tmp/sh26_p108_src/`
  (clone of the run_p_direct pattern; SRC/OUTDIR/PID = 108), launched
  in tmux `p108`. Total **6.2 min** (read 47.9s warm; make 217.7s).
- Sidecar: n_full 327,477,457 · n_ruwe_cut 312,364,232 (95.4%) ·
  n_ruwe2 26,488,335 (8.1%); per-diagram n in `n_cmd`/`n_kiel` (CMD
  slightly smaller — needs finite mg0/bprp0).
- QA: 6/6 panels colored-pixel check OK; vision_analyze passed on
  1400px JPEG after `auxiliary.vision.timeout` raised 60→180
  (`hermes config set auxiliary.vision.timeout 180`) — full-figure
  analyses were timing out at 60s on the 14–18 tok/s aip-best backend.
- Bundle: `scripts/combine_figures.py` → `sh26_all_figures.pdf`
  108 pages; commit `6f173fe`.
