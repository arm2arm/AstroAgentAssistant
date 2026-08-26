---
name: s3-storage
description: "S3/MinIO operations: connectivity, transfers, read benchmarks, and matplotlib visualization templates."
version: 1.0.0
---

# S3 Storage Operations & Benchmarking

## When to Load

- Testing S3/MinIO endpoint connectivity
- Uploading/downloading data to S3 buckets
- Comparing read performance between S3 endpoints
- Benchmarking object storage backends

## S3 Connectivity Testing

### Preferred: mc CLI

```bash
mc alias set <alias> <url> <access_key> <secret_key>
mc mb <alias>/<bucket>
mc cp <file> <alias>/<bucket>/
mc ls <alias>/<bucket>/
mc rm <alias>/<bucket>/<file>
mc rb <alias>/<bucket>
```

### Fallback: boto3 (when mc unavailable)

Install: `pip install boto3`

```python
import boto3
from botocore.config import Config

s3 = boto3.client(
    's3',
    endpoint_url='http://<host>:<port>',
    aws_access_key_id='<key>',
    aws_secret_access_key='<secret>',
    config=Config(retries={'max_attempts': 3}, signature_version='s3v4')
)

# Test: list buckets, create bucket, upload, list objects, download, delete
buckets = s3.list_buckets()['Buckets']
s3.create_bucket(Bucket='test')
s3.put_object(Bucket='test', Key='hello.txt', Body='content')
objs = s3.list_objects_v2(Bucket='test')['Contents']
resp = s3.get_object(Bucket='test', Key='hello.txt')
data = resp['Body'].read().decode()
s3.delete_object(Bucket='test', Key='hello.txt')
s3.delete_bucket(Bucket='test')
```

**Known issues with mc CLI:**
- mc may not be installed. Download from `https://dl.min.io/client/mc/release/linux-amd64/mc`
- Writing to `/usr/local/bin/mc` may fail due to permissions — use `~/bin/mc`
- Some mc binaries segfault on certain architectures — fallback to boto3 immediately
- curl may return HTML instead of binary (redirect issue) — use `-L` flag

## Benchmarking S3 Read Performance

Run the benchmark script at `scripts/s3_read_benchmark.py`:

```bash
python3 ~/.hermes/skills/s3-storage/scripts/s3_read_benchmark.py
```

The benchmark tests:
1. Single small object latency (box plot, 20 repeats)
2. Sequential full dataset read throughput (horizontal bar chart)
3. Concurrent read throughput at 1/4/8/16 workers (grouped bar chart + scaling curve)

Outputs:
- `results/s3_read_benchmark.png` — 2x2 matplotlib dashboard plot
- `results/s3_read_benchmark.json` — raw numeric data for further analysis

### Custom Endpoints

Edit the `ENDPOINTS` dict at the top of the script:

```python
ENDPOINTS = {
    "endpoint_name": {
        "url": "http://host:port",
        "key": "access_key",
        "secret": "secret_key",
        "bucket": "bucket_name",
    },
}
```

### Custom Parameters

```python
REPEATS = 20              # repeats per test
CONCURRENT_LEVELS = [1, 4, 8, 16]  # concurrency levels for parallel test
```

## Uploading to S3

### With mc CLI

```bash
mc mb <alias>/<bucket> --ignore-existing
mc cp -r <local_dir> <alias>/<bucket>/
```

### With boto3

```python
import boto3, os
from botocore.config import Config

s3 = boto3.client(
    's3',
    endpoint_url='http://<host>:<port>',
    aws_access_key_id='<key>',
    aws_secret_access_key='<secret>',
    config=Config(retries={'max_attempts': 3}, signature_version='s3v4')
)

base = '/path/to/local/dir'
for root, dirs, files in os.walk(base):
    dirs[:] = [d for d in dirs if d != '.git']
    for f in files:
        fp = os.path.join(root, f)
        rel = os.path.relpath(fp, base)
        s3.upload_file(fp, 'bucket-name', rel)
```

## Plot Customization Tips

The benchmark script uses matplotlib with:
- Blue (#2563eb) for first endpoint, Red (#dc2626) for second
- White background, sans-serif fonts
- 2x2 grid: box plot | sequential bar | parallel bar | scaling curve
- Data labels on bars, error bands on line chart

## Support Files

| File | Description |
|------|-------------|
| `scripts/s3_read_benchmark.py` | Full benchmark runner with matplotlib visualization |
| `references/endpoints.md` | Known S3 endpoint configurations |
