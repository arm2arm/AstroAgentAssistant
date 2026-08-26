# SH26 Dask review (2026-08)

## Problem
A 50M-row joined Parquet catalog was initially handled with an all-column/over-wide Dask path. A 3-worker × 4.5GB configuration completed narrow plots but restarted workers on a 4-column Galactic derived plot. The failure signature was repeated worker memory warnings followed by `KilledWorker`; the compressed partitions expanded sharply during decompression and transformation.

## Validated correction
- 2 workers × 6 threads each
- 7 GB per worker, 14 GB total budget
- `dd.read_parquet(columns=needed, engine="pyarrow", split_row_groups=True, blocksize="32MB")`
- one graph cache per exact column tuple
- schema metadata union across all parts
- compute only the current plot; release its pandas frame before continuing

A real-data smoke run of P11 (2 pushed columns) and P34 (4 pushed columns plus Galactic derivation) completed 2/2 successfully in 10.9 s. Dask paused briefly at ~81% worker memory but did not restart workers. The project’s full registry smoke tests passed 40/40 on synthetic data.

## Verification checklist

1. Run a narrow comparison plot and the widest derived plot on the real dataset.
2. Confirm logs show `Dask read: N columns (pushdown)` rather than an all-column read.
3. Confirm no `KilledWorker`, worker restart, or OS `-9` termination.
4. Check output count and sidecars; use a temporary output directory for smoke tests.
5. Run all registered synthetic smoke tests before a full 50M-row suite.
6. Only then launch the full suite; inspect the final summary and runtime.

## Interpretation
`memory_limit` is a worker limit, not a guarantee against OS-level pressure. The partition size and transient decompression/transform allocations matter. Fewer workers with more memory each can be safer than more workers with small limits, provided the process-wide cap is preserved.
