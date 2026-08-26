---
name: s3-storage-benchmark
description: Run comprehensive S3-compatible storage benchmarks — read speed comparison, synthetic write/read across object sizes (1KB, 1MB, 1GB), with automated plot generation and cleanup.
category: benchmarking
---

# S3 Storage Benchmark

Run S3-compatible object storage benchmarks comparing two endpoints across read speed, synthetic write, and synthetic read workloads.

## What it does

- **Read speed comparison**: Single-object latency, sequential full read, parallel reads (1/4/8/16 workers)
- **Synthetic write/read**: Three sizes — Small (1KB×1K), Medium (1MB×100), Large (1GB×10)
- Generates publication-quality plots (PNG) and raw JSON data
- Auto-creates temp buckets per run, cleans up afterward

## Prerequisites

- Python 3.11+ with `boto3`, `matplotlib`
- Two S3-compatible endpoints with credentials
- ~15 GB free space for large object tests

## Quick Start

```bash
# Run all benchmarks
python3 scripts/run_s3_benchmark.py

# Run specific test types
python3 scripts/run_s3_benchmark.py --test read-speed
python3 scripts/run_s3_benchmark.py --test synthetic

# Help
python3 scripts/run_s3_benchmark.py --help
```

## Configuration

Edit `scripts/run_s3_benchmark.py` to configure endpoints:

```python
ENDPOINTS = {
    "RustFS (9000)": {
        "url": "http://141.33.4.155:9000",
        "key": "access_key",
        "secret": "secret_key",
    },
    "VersityGW (7070)": {
        "url": "http://141.33.4.155:7070",
        "key": "access_key",
        "secret": "secret_key",
    },
}
```

## Expected Runtime

| Test | Duration |
|------|----------|
| Read speed comparison | ~5 minutes |
| Synthetic (no large objects) | ~5 minutes |
| Full synthetic (with 1GB objects) | ~25-30 minutes |

### Why large objects are slow

- RustFS write: ~35 MB/s → ~5 min per 1GB object
- VersityGW write: ~75 MB/s → ~3 min per 1GB object
- Read: ~75-95 MB/s → ~2-3 min per 1GB object
- Total: 10 objects × 2 sizes × 2 endpoints × 2 repeats = 80 large object operations

## Output

Results saved to `results/` directory:

| File | Description |
|------|-------------|
| `s3_read_benchmark.png` | 4-subplot read speed comparison dashboard |
| `s3_read_benchmark.json` | Raw read benchmark data (single_obj, sequential, parallel) |
| `s3_synthetic_benchmark.png` | 4-subplot synthetic write/read performance dashboard |
| `s3_synthetic.json` | Raw synthetic data (write+read for Small/Medium/Large) |

## Pitfalls

### S3 bucket cleanup requires pagination

MinIO-compatible S3 endpoints return paginated object listings. A single `list_objects_v2` call may not return all objects. **Must paginate through all pages** and delete in batches of 1000 (the S3 API maximum per `delete_objects` call).

```python
# WRONG — fails on >1000 objects or if page is truncated
s3.delete_objects(Bucket=bucket,
    Delete={'Objects': [{'Key': o['Key']} for o in s3.list_objects_v2(Bucket=bucket)['Contents']]})

# CORRECT — paginate and batch
paginator = s3.get_paginator("list_objects_v2")
all_keys = []
for page in paginator.paginate(Bucket=bucket):
    if "Contents" in page:
        all_keys.extend(page["Contents"])
for i in range(0, len(all_keys), 1000):
    batch = all_keys[i:i+1000]
    s3.delete_objects(Bucket=bucket,
        Delete={'Objects': [{"Key": o["Key"]} for o in batch]})
```

### mc (MinIO client) may segfault on some systems

The `mc` binary may segfault on certain architectures or when the downloaded binary is incompatible. **Workaround**: use `boto3` directly — it's already installed in the Hermes environment and works reliably.

```bash
# If mc is unavailable or segfaults, use python instead:
python3 -c "
import boto3
s3 = boto3.client('s3', endpoint_url='http://host:port',
    aws_access_key_id='key', aws_secret_access_key='secret')
# All S3 operations work via boto3
"
```

### 1GB object benchmarks take significant time

If the user asks for a quick benchmark, only run Small and Medium tests. Always communicate expected runtime before starting Large tests.

## Benchmark Configuration

Read speed:
- 20 repeats per test
- Single object: ~11 bytes
- Sequential: full dataset read
- Parallel: ThreadPoolExecutor with 1, 4, 8, 16 workers

Synthetic:
- Small (1KB×1000): 5 repeats
- Medium (1MB×100): 5 repeats
- Large (1GB×10): 2 repeats (to keep runtime reasonable)
- Data: `os.urandom()`, no compression
