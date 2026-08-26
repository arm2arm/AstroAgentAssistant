#!/usr/bin/env python3
"""Generic direct-plot runner for the full 402M catalog (<compute-node>).

Bypasses the Dask CLI (which MemoryErrors on 402M via
repartitiontofewer — see references/full-402m-direct-plotting.md).
Reads only the plot's pushed columns via pyarrow.dataset, applies the
hard MISSING==False convergence filter, computes derived columns, and
calls the registry's make() with a standard PlotContext.

Usage (on <compute-node>):
    /lustre/<user>/SOFTWARE/conda/sh25/bin/python run_p_direct.py 1

Adapt DATA/OUTDIR/SRC if the catalog or repo path changes.
"""
import sys, time, importlib
from pathlib import Path

SRC = "/lustre/<user>/hermes/SH26/src"
DATA = "/lustre/<user>/ipython/SH2025/reana/final/combined/sh26_final_joined_v190826"
OUTDIR = "/lustre/<user>/hermes/sh26_full/figures"
sys.path.insert(0, SRC)

PID = int(sys.argv[1]) if len(sys.argv) > 1 else 1
log = lambda *a: print(time.strftime("%H:%M:%S"), *a, flush=True)
t0 = time.time()

# Go through the registry — NEVER import sh26.plots.pNN directly
# (module names are pNN_<slug>, e.g. p01_cmd).
from sh26.registry import registry
spec = registry.spec(PID)
make_fn = registry.make_fn(PID)
from sh26.lazy_catalog import _resolve, _derive

cols = _resolve(spec.columns, spec.derived, quality_cuts=False)
log("P%02d %s: %d columns -> %s" % (PID, spec.name, len(cols), cols))

import pyarrow.dataset as ds
d = ds.dataset(DATA, format="parquet")
t1 = time.time()
tbl = d.to_table(columns=cols)
log("read %d rows in %.1fs" % (tbl.num_rows, time.time() - t1))

import pandas as pd
pdf = tbl.to_pandas()
del tbl
n0 = len(pdf)
# Hard convergence filter — matches LazyCatalog.get() semantics
pdf = pdf[pdf["MISSING"] == False]  # noqa: E712
log("converged: %d -> %d" % (n0, len(pdf)))

if spec.derived:
    pdf = _derive(pdf, spec.derived)
keep = [c for c in (*spec.columns, *spec.derived) if c in pdf.columns]
pdf = pdf[keep].copy()

from sh26.context import PlotContext
ctx = PlotContext(outdir=Path(OUTDIR), dataset=DATA,
                  extra={"loader": "pyarrow-direct", "quality_cuts": False,
                         "memory_budget": "direct"})
t1 = time.time()
paths = make_fn(pdf, ctx)
log("P%02d make() %.1fs -> %s" % (PID, time.time() - t1, paths))
log("P%02d COMPLETE in %.1fs total" % (PID, time.time() - t0))
