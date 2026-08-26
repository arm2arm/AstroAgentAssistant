# Full-catalog (v220826) paper rerender campaign — 2026-08-23

Goal: replace all stale 50M-era figure renders with 100% full-catalog
(v220826) renders for the paper draft.

## Provenance audit method

Every `paper/figures/*.json` sidecar carries the render vintage:
- `dataset` field = data path used (`..._50m.parq` = STALE,
  `sh26_final_joined_v220826` = current).
- Quick audit: count sidecars whose JSON contains neither `v220826`
  nor is a known-full plot. Result on 2026-08-23: 78/97 sidecars stale
  → wave-based remote rerender launched.
- Only ~97 of 106 plots have sidecars in `paper/figures/` — some live
  only in `/tmp/p103_redo_full`, `/tmp/p104_full`, `/tmp/p105p106_full`;
  copy those PDFs into `paper/figures/` and reference exact filenames
  from `\includegraphics`.

## Wave driver pattern (proven, zero failures)

- `scripts/run_plot_full.py <id>`: pyarrow-direct per-plot process.
  Reads union of pushed columns via `pyarrow.dataset(...).to_table`,
  applies `MISSING==False`, `_derive`s, calls `make_fn(pdf, ctx)`.
  Typical timing on <compute-node> (96c exclusive): read 402M rows 12–30 s;
  most plots finish 60–160 s total; expensive ones (P72 ML dashboard)
  take minutes. Peak RAM ~10–20 GB per process.
- `scripts/launch_paper_full.sh <wave_file>`: bash launcher, MAXPAR=4
  concurrent processes, one log per plot in `<out>/logs/pNN.log`.
  Waves: `wave1_ids.txt` (53 plots), `wave2_ids.txt` (26).
- Deploy route: tar src+scripts → scp to Newton (141.33.4.144) →
  nested ssh to <compute-node>.nnew → untar under `/lustre/<user>/tmp/paper_full`
  (never touch `/lustre/<user>/hermes/SH26`). Nested-ssh nohup rule:
  write script to /tmp, then
  `ssh <compute-node> 'nohup bash /tmp/x.sh >log 2>&1 </dev/null &'`.
- Monitor loop (agent-side background): poll every 4 min counting
  `*.json` in the outdir vs expected total; stop when count reached.

## Operational pitfalls hit this session

- **Wave 1 finished but wave 2 did NOT auto-start** — launcher exits
  after its wave file; waves must be launched explicitly per file.
  After wave 1 completes, check `pgrep -f run_plot_full` = NONE, then
  launch wave 2 manually.
- **Nested ssh with trailing `&` can hang the outer call past timeout**
  even when the remote job starts fine — always verify via a separate
  short `pgrep -c -f run_plot_full.py` call instead of trusting the
  launch call's exit.
- **Verify completion per plot**, not by json count alone: a plot that
  crashed mid-render leaves a log without `done`; loop over logs and
  flag any missing the `P<NN> done` line.
- Sidecar `n_points` sanity anchor: converged = **327,477,457**
  (full catalog); inner box X[−5,5]×Y[−4,4] = 27,508,904
  (SHBOOST=T 17,465,111 / F 10,043,793).

## Paper-side integration

- Chapter files reference figures by EXACT filename; several inner-box
  plots have names like `sh26_p85_shboost_xy_center.pdf` (not
  `..._zoom.pdf`). Grep all `\includegraphics{...}` in `doc/chapters/`,
  test each against `paper/figures/<name>`, fix names or copy files.
- After swapping renders: clean aux, pdflatex → bibtex → ×2, then
  assert `cite_warn=0 ref_warn=0` in the final log; page montage via
  `pdftoppm -png -r 40` + montage for visual QA.
- aa.cls gotchas confirmed: `\citet/\citep` are FORBIDDEN in the
  abstract ("Citations are not allowed in the abstract") — use plain
  text mentions there; duplicate `\appendix` across chapter files
  raises `theapsection already defined` — keep exactly one.
