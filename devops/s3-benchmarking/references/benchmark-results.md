# S3 Endpoint Benchmark Results (2026-07-22)

## Endpoints Tested
- **RustFS** (port 9000) — `rustfsadmin2026` / `rustfsadmin2026`
- **VersityGW** (port 7070) — `versitygwadmin2026` / `versitygwadmin2026`

## Read Performance Summary

| Test | RustFS (9000) | VersityGW (7070) | Winner |
|------|--------------|-------------------|--------|
| Small object read | 1.6 ms | 1.7 ms | RustFS |
| Sequential full read (1.4 MB) | 46.1 MB/s | 37.6 MB/s | RustFS |
| Parallel 1 worker | 43.2 MB/s | 33.9 MB/s | RustFS |
| Parallel 4 workers | 79.2 MB/s | 66.3 MB/s | RustFS |
| Parallel 8 workers | 78.9 MB/s | 65.9 MB/s | RustFS |
| Parallel 16 workers | 78.7 MB/s | 66.4 MB/s | RustFS |

**Winner: RustFS consistently ~18-20% faster on reads**

## Synthetic Benchmark Summary

### Small (1KB × 1000 = 1 MB)
- Write: both <1 MB/s (inefficient for tiny objects)
- Read: RustFS 0.5 MB/s, VersityGW 0.4 MB/s

### Medium (1MB × 100 = 100 MB)
- Write: VersityGW 52.6 MB/s, RustFS 23.1 MB/s
- Read: RustFS 77.4 MB/s, VersityGW 72.6 MB/s

### Large (1GB × 10 = 10 GB)
- Write: VersityGW 75.3 MB/s, RustFS 34.5 MB/s (2.2× faster)
- Read: VersityGW 94.5 MB/s, RustFS 74.8 MB/s (1.3× faster)
- Write latency: RustFS 31s/obj, VersityGW 14s/obj

**Key insight: VersityGW dominates large object writes, RustFS wins on reads**

## Artifacts
- Plot: `results/s3_read_benchmark.png`
- Synthetic plot: `results/s3_synthetic_benchmark.png`
- Raw data: `results/s3_read_benchmark.json`, `results/s3_synthetic.json`
