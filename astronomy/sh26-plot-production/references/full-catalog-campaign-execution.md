# Full-402M Campaign Execution (pyarrow-direct batch + monitor)

Session 2026-08-21. How to run single plots AND 10–80-plot campaigns on the
full 402M catalog on <compute-node>, reliably, with auto-completion delivery.

## Verified data facts (sh26_final_joined_v190826)

- Path: `/lustre/<user>/ipython/SH2025/reana/final/combined/sh26_final_joined_v190826`
- **402,121,784 rows × 132 cols, 197 GB, 3032 parts, all float32**
- **INCLUDES pmra/pmdec/pmra_error/pmdec_error** (4 PM cols) — the old plan's
  "P82/P90–P93 blocked on 402M PM join" is STALE. P82 runs on the full set.
- converged (`MISSING==False`): **327,477,457**; MISSING 74,644,327 (18.56%)
- duplicated source_ids: 14,865; base legitimately = A+B+82,798 (fan-out)
- P01 n_points 322,771,318 (drops NaN dereddened phot); P08/09 315,122,335
  (finite SH21 match); P10 327,476,946

## Why the Dask CLI fails at 402M (do NOT "fix" the CLI by bumping memory)

`python -m sh26 plots` at 402M: `blocksize="32MB"` → ~6000 tiny partitions;
`repartitiontofewer` merges them into ~12.36 GiB output chunks, but
`--memory X` is divided across config `n_workers` (24×30GB layout → 4.96 GiB
/worker) → `MemoryError`, all workers die, plot FAILED in ~96 s. The served-
table architecture (doc/full_catalog_plan.md) is the proper long-term fix;
until it lands, use the direct loader below — it is proven for the cheap campaign.

## The direct loader (proven template, on <compute-node> at /tmp/run_p_direct.py)

```python
import sys, time, importlib
from pathlib import Path
sys.path.insert(0, "/lustre/<user>/hermes/SH26/src")
DATA  = "/lustre/<user>/ipython/SH2025/reana/final/combined/sh26_final_joined_v190826"
OUTDIR = "/lustre/<user>/hermes/sh26_full/figures"
PID = int(sys.argv[1]) if len(sys.argv) > 1 else 1
from sh26.registry import registry
spec, make_fn = registry.spec(PID), registry.make_fn(PID)
from sh26.lazy_catalog import _resolve, _derive
cols = _resolve(spec.columns, spec.derived, quality_cuts=False)
import pyarrow.dataset as ds
tbl = ds.dataset(DATA, format="parquet").to_table(columns=cols)   # ~12 s for 402M
pdf = tbl.to_pandas(); del tbl
pdf = pdf[pdf["MISSING"] == False]              # hard convergence filter
if spec.derived: pdf = _derive(pdf, spec.derived)
keep = [c for c in (*spec.columns, *spec.derived) if c in pdf.columns]
from sh26.context import PlotContext
ctx = PlotContext(outdir=Path(OUTDIR), dataset=DATA,
                  extra={"loader": "pyarrow-direct", "quality_cuts": False})
make_fn(pdf[keep].copy(), ctx)
```

Peaks ~15 GB RAM. Per-plot timing: ~90 s–2 min for simple hexbins,
P03/P05 (C-hexbin) ~5–6 min, P01 (derived + big) ~3.5 min.

## Campaign loop pattern (batch script)

```bash
for p in <ids>; do
  echo "########## P$p ##########  $(date +%H:%M:%S)"
  timeout -k 60 3600 /lustre/<user>/SOFTWARE/conda/sh25/bin/python \
      /tmp/run_p_direct.py $p > /tmp/cheap_p$p.log 2>&1
  rc=$?; echo "P$p rc=$rc  $(date +%H:%M:%S)"
  [ $rc -ne 0 ] && echo "P$p rc=$rc" >> /tmp/cheap_failures.txt
done
echo "CHEAP_CAMPAIGN_DONE"        # single stable marker for the monitor
```
Launch: `nohup bash /tmp/run_cheap.sh > /tmp/cheap_run.log 2>&1 &`
77-plot cheap campaign (P11–P89 minus P72/P79): **~2.5 h**, 0 failures observed.

## Quoting pitfalls (hit twice, cost real time)

- **NEVER build the loop script via `printf %s <b64> | base64 -d` or heredoc
  through nested ssh** (`local ssh 144 'ssh <compute-node> ...'`): the pipe/redirect
  lands on the WRONG hop (144, not <compute-node>) and the script silently ends up
  with an EMPTY loop (`for p in ; do`) + no exec bit → "Permission denied" or
  a no-op. The sed-substitution variant also expanded `$ids_line` to nothing.
- **Working transfer: write the file LOCALLY with the final content
  (Python f-string), then `scp local→141.33.4.144→<compute-node>.nnew`** (two hops),
  `chmod +x`, then VERIFY before launch: `bash -n`, and count the ids
  (`grep '^for p in' | wc -w` should equal n_ids + 4: `for in <ids> ; do` —
  actually 4 keyword words + n_ids). An empty loop passes `bash -n` — the
  word-count check is the real tripwire.
- Small python snippets on <compute-node>: `python -c` with a base64-piped one-liner
  via `printf %s <b64> | base64 -d | python` works ONLY when the whole
  pipeline is inside the INNER ssh quotes (redirect target = <compute-node>).
- `scp` from the agent host to 144 works; scp 144→<compute-node> must run as an ssh
  command ON 144. (Direct scp local→<compute-node> has no route.)

## Deploying code to <compute-node> (repo working tree is DIRTY)

<compute-node>'s `/lustre/<user>/hermes/SH26` has uncommitted local edits
(config/dask.yaml, worker script) → `git pull` REFUSES. Two working paths:
1. `git fetch origin -q && git checkout <hash> -- <path>` (surgical, keeps
   dirty files) — used for context.py; then ALWAYS `python -m py_compile`
   the deployed file before launching.
2. Two-hop scp for arbitrary files.
Commit + push the change in the local repo first so the hash exists on
origin (user default: commit+push after every verified change).

## Long-run monitoring: cronjob + stable-token monitor script

Pattern used to guarantee "the run is not forgotten while the user works on
other subtasks":
1. Script in `~/.hermes/scripts/` that ssh's to the node and emits ONE STABLE
   token: `RUNNING` while the log lacks the done-marker, `DONE` once
   `grep -c CHEAP_CAMPAIGN_DONE` ≥ 1. (Stable bytes = monitor-script
   suppression; unchanged output → silent tick, no LLM, no delivery.)
2. `cronjob create` with `monitor_script=<name>.sh`, schedule `every 10m`,
   `enabled_toolsets: ["terminal"]`, deliver origin. Prompt instructs: on the
   first (baseline) tick reply one line; on the DONE tick do verify → QA →
   merge PDF → deliver → **remove the job by its job_id** (embed the id in
   the prompt).
3. Verify the script emits the correct current token BEFORE trusting it
   (run it once from the agent host — it must succeed via the same two-hop
   ssh path).

## QA before/after a campaign

- BEFORE a multi-hour batch: after the first plot, spot-check ONE figure with
  vision_analyze (downscaled) — that's how the colorbar-badge collision was
  caught before 25 min of rework.
- AFTER: programmatic per-figure check (JSON sidecar `n_points` sane vs
  expected class size; PIL non-white fraction > 0.05).
- Combined PDF: fetch per-plot PDFs (<compute-node>→144→local via tar), merge with
  `pypdf` (`pip install pypdf` — agent host had no pypdf/qpdf). `gs
  -o out.pdf` WITHOUT `%d` silently keeps only the LAST file; use
  `gs -o part%d.pdf` + verify per-part pagecount, or just pypdf.
