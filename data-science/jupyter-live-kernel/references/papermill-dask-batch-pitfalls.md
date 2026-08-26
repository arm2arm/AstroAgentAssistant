# Papermill + Dask batch pitfalls from SH2026 notebook optimization

## Trigger
Use this note when a notebook is executed non-interactively with papermill/SLURM and connects to a remote Dask scheduler.

## Observed failure chain

1. Papermill was invoked with `-p DRY_RUN False -p PARTITION_SIZE_MB 512`.
2. The notebook had no `parameters` cell.
3. Papermill warned:
   - `Passed unknown parameter: DRY_RUN`
   - `Passed unknown parameter: PARTITION_SIZE_MB`
   - `Input notebook does not contain a cell with tag 'parameters'`
4. Early notebook cell called `client.restart()`.
5. On the shared scheduler this failed with scheduler-side assertion:
   - `assert not self.tasks`
6. After guarding restart and continuing, the later final stage still failed with:
   - `RuntimeError('P2P ... failed during transfer phase')`
7. The concrete trigger was the final stage:
   - `final_ddf = final_ddf.repartition(partition_size="512MB").persist()`
   - followed by `final_ddf.to_parquet(...)`

## Durable takeaways

- Adding `shuffle="disk"` to `set_index(...)` is not sufficient proof that all later execution paths avoid P2P transfer logic.
- In Dask expr pipelines, `repartition(partition_size=...)` can force memory-usage estimation and transfer-heavy work late in the graph.
- For wide final tables on a fragile cluster, a safer fallback is:
  - keep checkpointed intermediate parquet stages,
  - avoid final repartition-by-size,
  - `persist()` the current partitioning,
  - write parquet directly.
- Guard or remove `client.restart()` in batch notebooks that connect to shared schedulers.
- If you intend papermill parameter overrides, add a tagged `parameters` cell before submitting jobs.

## Safer notebook adjustment used in this session

A safer variant was created with these changes:
- add a `parameters` cell at top
- wrap `client.restart()` in `try/except`
- keep early `dask.config.set({'dataframe.shuffle.method': 'disk'})`
- replace final `repartition(partition_size="512MB").persist()` with plain `persist()`
- keep final `to_parquet(...)` write

## Dataset scale context

Approximate parquet sizes observed:
- A: 12,288 files, ~40.5 GB
- B: 12,288 files, ~22.6 GB
- C: 12,287 files, ~34.4 GB
- D: 12,288 files, ~24.3 GB
- Gaia: 4,096 files, ~324.0 GB
- SH21: 384 files, ~114.0 GB
- BJ21: 512 files, ~62.6 GB
- W25: 64 files, ~77.9 GB

Intermediate checkpoint sizes from the optimized run:
- tmp_base: 257 parquet files, ~37.0 GB
- tmp_dups: 2 parquet files, ~0.73 GB
- tmp_enriched: 706 parquet files, ~27.3 GB

## Why this matters

At this scale, blindly forcing a final repartition is not a cosmetic optimization; it can be the dominant fragile operation in the notebook. Prefer robust completion over aesthetically uniform output partition sizes.
