---
name: memory-bounded-parquet-analysis
title: Memory-bounded Dask/Parquet analysis and plotting
description: Use Dask for large Parquet data safely.
version: 1.0.0
author: Hermes Curator
license: MIT
metadata:
  hermes:
    tags:
      - dask
      - parquet
      - memory
      - performance
    related_skills:
      - data-visualization-umbrella
tags:
  - dask
  - parquet
  - memory
  - performance
  - plotting
---

# Memory-bounded Dask/Parquet analysis

## When to use

Use for large astronomy or scientific catalogs where loading the full table into pandas is unsafe, especially when a plotting suite materializes one selected column subset at a time.

## Core workflow

1. **Inspect the project before changing the loader.** Identify the CLI entry point, plot specification contract, existing quality-cut behavior, data partition layout, and current tests.
2. **Define a total RAM budget.** Treat the user’s budget as process-wide, not per worker. Choose worker count and per-worker memory so their sum remains below the ceiling, leaving practical headroom for scheduler/client overhead.
3. **Read metadata once.** Validate the dataset path and union schema field names across Parquet parts. Never compute `len(ddf)` merely to report row count.
4. **Project columns at the read boundary.** Build `dd.read_parquet(..., columns=needed, engine="pyarrow", split_row_groups=True, blocksize=...)` for the current plot. Do not build an all-column graph and slice it later.
5. **Cache task graphs, not full data.** Cache by the exact sorted column tuple. Avoid `persist()` unless the working set is explicitly bounded and the reuse is demonstrated.
6. **Materialize one plot at a time.** Compute the selected columns to pandas only when the renderer requires it; derive coordinates/calibrations after projection; release the DataFrame before the next plot.
7. **Verify with the widest real plot.** Compressed Parquet partitions can expand dramatically during pandas/Dask transforms. Run both a narrow plot and the widest derived plot, inspect worker restart/pause warnings, and tune block size or worker count before running the full suite.
8. **Keep empty-data guards and full registry smoke tests.** Shared hexbin/histogram helpers should render a clear “No data” panel rather than fail on an empty mask.

## Validated SH26 pattern

For the 50M-row joined SH26 catalog, the stable reference configuration was 2 workers × 6 threads × 7 GB (14 GB total) with 32 MB Parquet partitions. This completed a 2-column comparison plot and a 4-column Galactic derived plot without worker death. A 3 × 4.5 GB layout restarted workers on the wider plot because decompression and transformation overhead exceeded the worker limit.

This is a validation example, not a universal machine setting: re-measure on the target host and dataset.

## CLI and reproducibility

Expose compact controls such as:

```text
plots --all --data DATASET --memory 14GB --threads 12
```

Define `--memory` as total budget in help text. Record dataset path, quality-cut mode, memory budget, selected columns, derived quantities, and Git revision in per-plot provenance sidecars.

## 402M-row scale: aggregate Dask-side, not client-side

For catalogs too big to materialize even one plot's columns at full scale, binned plot families (2D/1D histograms, sky maps, binned mean/std) should be computed **per partition on the workers and combined by a single addition** — raw rows never cross to the client, only the small binned table does. Pattern (validated in SH26 v0.2.0, `src/sh26/aggregate.py`):

- Per-partition function takes a pandas partition, returns a fixed-shape counts/sums table (e.g. `np.histogram2d` result, per-bin `[n, sum, sumsq]`).
- Combine with `sum([delayed(part_fn)(p, ...) for p in ddf.to_delayed()]).compute()` — exact for integer counts because binning is a per-point decision and the combine is pure addition.
- Bin conventions must match the numpy reference exactly (half-open `[lo, hi)`, rightmost edge inclusive) so results equal `np.histogram*` on the materialized frame to the last count; test against that reference.
- Resolve `int` bin specs with two cheap dask `min()`/`max()` reduces on the scheduler, never by pulling rows.
- Sky density without healpy: a uniform `(l, sin b)` pixel grid has exactly equal solid angle per pixel (dΩ = cos b dl db = dl d(sin b)) — a dependency-free fallback for Mollweide-style maps.
- Add a `client=` injection seam to the loader so tests/demos can run the same code path with zero cluster processes (see pytest deadlock pitfall above).

## Pitfalls

- **dask-expr API drift breaks code at RUNTIME in untested branches (hit 2026-08-25):** this dask build (2026.x, dask-expr enabled) removed `Series.notna()` — use `Series.notnull()`. It only raised `AttributeError` in the `dist_cut` code path that no test exercised; the test suite was fully green. Verify new code paths in branches tests don't cover (conditional flags like dist cuts) with a one-off script against the fixture, and grep new code for `notna` after dask upgrades.

- Worker `memory_limit` is not a guarantee against OS-level memory pressure; oversized decompressed partitions can still kill workers.
- Smaller Parquet block size improves safety but may increase scheduler and metadata overhead; validate runtime on the actual suite.
- A schema read from only the first part can miss columns in heterogeneous datasets; union metadata across parts.
- A loader that silently drops missing columns can hide broken plot specifications. Prefer explicit per-plot missing-column handling or a documented skip guard.
- Global science cuts in the loader can silently change figure semantics. Keep cuts explicit and opt-in unless the analysis contract requires them.
- **pytest + dask.distributed LocalCluster deadlocks (hit 2026-08-25, SH26 test suite):** several `LocalCluster` instances (one per session-scoped fixture or per test) inside ONE pytest process hang the whole run — every file and every pair of files passes in ~4 s in isolation, but the combined run stalls for 10+ min. Nanny worker-subprocess clusters fail with "Nanny failed to start worker process"; in-process (`processes=False`) shared clusters still hang. Robust fix for small-fixture tests: don't spawn any cluster at all — add a `client=` injection seam to the loader (a marker object makes `compute()` fall back to dask's threads scheduler via `dask.config.set({"scheduler": "threads"})`, restored in the fixture teardown; the loader's `close()` must never close a client it doesn't own). Scheduler choice is irrelevant to what the tests verify (pushdown, masks, derived columns, dtypes) at 2000-row scale. Also: `pdf.memory_usage(deep=True)` in a hot path is minutes-to-hours on 402M-row object-dtype columns — estimate from dtypes (itemsize × len, constant factor for object) instead.

## Supporting detail

See `references/sh26_dask_review_2026-08.md` for the SH26 failure signature, configuration comparison, and verification checklist. See `references/agent_stage_verification_2026-08.md` for the post-stage verification checklist to run after any coding-agent stage (claimed-but-missing deletions, untested branches with dead APIs, recomputing self-reported counts).
