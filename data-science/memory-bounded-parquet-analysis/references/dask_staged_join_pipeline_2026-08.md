# Staged-cache Dask join pipeline (SH26 402M-row 134-col join, 2026-08-20)

Validated rewrite of a repeatedly-crashing 402M-row multi-table join on a 96-core / 754 GB exclusive node (<compute-node>), after two full runs died on unmanaged-memory worker kills and a tmpfs p2p-shuffle fill.

## User-specified algorithm (kept verbatim)

1. **Prepare inputs**: preselect columns, cast to float32, normalize key (`ID`→`source_id`), apply suffixes (`_sh21`, `_bj21`, `_w25`) — write each normalized table to a cache dir.
2. **All tables at 1 GB partitions** (`repartition(partition_size="1GB")` at every cache write).
3. **Every join goes to cache** (one parquet dir per stage).
4. **Final output to the planned output folder** (new tagged dir; never overwrite prior good outputs).

## Structure (5 cells of work + verify)

```
Stage 0  normalize  8 input tables → cache/<name>.f32.parq   (1GB parts, f32, preselected)
Stage 1  base       A×C + B×D left-joins → concat → cache/base.parq
                   groupby(source_id).size() → cache/dups.parq
Stage 2  enrich 1   base × Gaia(13 cols incl. PM)            → cache/enr1.parq
Stage 3  enrich 2   enr1 × SH21(24)                          → cache/enr2.parq  (widest, ~160 GB)
Stage 4  final      enr2 × BJ21(7) × W25(6) × dups
                   → repartition 1GB → FINAL/<tagged output>  (134 cols, f32)
Verify   134-col count, MISSING stats by SHBOOST, dup report, assert no float64 remains
```

**Key pattern: each stage cell ends with `client.restart()`** — frees all worker memory between stages (no drift between stage peaks), and makes any crash cheap to resume: re-run from the last cached stage, earlier stages are never recomputed.

## Config

- `Client(processes=True, n_workers=24, threads_per_worker=4, memory_limit="30GB", dashboard_address=":8787", local_directory="<lustre>/dask-sh26")` — 24×30=720 GB of 754; 24×4=96 cores.
- **`local_directory` MUST be on a large persistent disk** (Lustre), never the tmpfs `/tmp` — the p2p shuffle spill goes there. This run's predecessor died with `P2POutOfDiskError` after filling a 378 GB tmpfs.
- Memory thresholds tighter than the defaults that OOM'd: target 0.85 / spill 0.90 / pause 0.95 / terminate 0.99 (the 0.92/0.98/0.995/0.999 combo left too little unmanaged headroom when numpy arenas held ~16 GB unmanaged).
- float32 everywhere: `astype({"col":"float32"})` on all float64 cols before EVERY parquet write; verify cell asserts zero float64 in the final schema.

## Column preselection done right

- Read **parquet metadata only** (`pyarrow.parquet.ParquetDataset(p).schema`) to get per-table column lists — no compute, instant on TB-scale inputs.
- Preselect against the *known final schema* of the previous good output, not against "everything": A/B 51 cols (dropped `__index_level_0__` artifact), C/D 31 (`ID`→`source_id`), Gaia 13 (unique names, no suffix), SH21 24, BJ21 7, W25 6.
- Arithmetic check before writing: `AB + (CD-1) + 2 + (GA-1) + (SH-1) + (BJ-1) + (W25-1) + 1 = 134` — join columns collapse, flags (SHBOOST/MISSING) and `dups` are added. An explicit count assert in the verify cell catches schema drift.
- Suffix renames happen in Stage 0 (at the read boundary), so joins are plain `on="source_id"` merges — no `set_index(shuffle="p2p")` chains; fewer shuffles, smaller graphs (the old notebook's 43 MiB / 417k-task graph came from repeated index shuffles of a 24,576-partition table).

## Diagnostics that bit (avoid)

- **Port-scanning the node's python ports to "find" the scheduler floods its log** with `numpy ArrayMemoryError: Unable to allocate 6.59 EiB` (garbage TCP handshakes parsed as frame lengths) for minutes to hours, masking all real progress. Use the known dashboard address or the Client object.
- **`to_parquet(overwrite=True)` with a stale prior output**: when asking "is the job finished?", stat the part files — parts dated weeks old mean the current run wrote nothing new yet (or the run died before the write). Notebook cell outputs are NOT ground truth: a saved notebook can hold a completed stats cell AND a later crash traceback from different runs.
- tmux pane capture of a Dask run is dominated by warning spam — grep for progress markers (`Wrote:`, stage names, `=== ` report headers) with a blocklist of traceback lines, or read the papermill/tee log file instead.

## Resume semantics

Any stage failure: re-run the notebook; stages whose cache dirs already exist could be skipped (this rewrite does not auto-skip — re-running a stage is idempotent since every cache write is `overwrite=True`). Full-restart cost is amortized by Stage 0 being cheap (column projection + cast, no joins).
