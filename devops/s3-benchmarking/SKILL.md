---
name: s3-benchmarking
description: Benchmark read/write performance of S3-compatible storage endpoints (MinIO, VersityGW, rustfs).
---

# S3 Endpoint Benchmarking

Benchmark read/write performance of S3-compatible storage endpoints (MinIO, VersityGW, rustfs, etc.).

## Workflow

1. **Verify connectivity** — use boto3 Python SDK (NOT `mc` CLI — see pitfalls)
2. **Create benchmark bucket** — unique name per run to avoid collisions
3. **Run benchmark phases** — small/medium/large object sizes, write then read
4. **Generate results** — summary table + publication-quality plot
5. **Clean up** — paginated delete of objects, then bucket

## Pitfalls

### mc CLI is unreliable
- `mc` binary often segfaults after download (binary compatibility)
- Installing to `/usr/local/bin/` may fail (permissions/PEP 668)
- **Use boto3 Python SDK instead** — always available, reliable

### Paginated bucket cleanup
- `delete_objects` only handles 1000 keys per call
- MUST paginate through all objects before deleting bucket
- Stale buckets from interrupted runs are common

### Large object timeouts
- 1GB objects take ~30s+ each at ~35 MB/s
- 10 objects × 2 endpoints × 2 repeats = ~40GB transfer
- Run in background (`terminal(background=true)`) with `notify_on_complete=true`
- Consider reducing repeats for 1GB test (2 is enough)

### Bucket name collisions
- Always use unique bucket name per run: `bench-{timestamp}`
- Check existing buckets before creating new one
- Stale benchmark buckets cause `BucketNotEmpty` errors

## Tools

- **Primary**: `boto3` Python SDK (pre-installed in Hermes)
- **Plotting**: matplotlib (use `Agg` backend for non-interactive)

## Test Configurations

Recommended sizes for comprehensive benchmark:

| Name | Object Size | Count | Total | Reps |
|------|------------|-------|-------|------|
| Small | 1 KB | 1000 | 1 MB | 5 |
| Medium | 1 MB | 100 | 100 MB | 5 |
| Large | 1 GB | 10 | 10 GB | 2 |

## Results Metrics

- Throughput (MB/s) — sequential and per-operation
- Operations per second
- Per-object latency (ms)
- Scaling curve (parallel workers)

See `references/benchmark-results.md` for example output and comparison data.
