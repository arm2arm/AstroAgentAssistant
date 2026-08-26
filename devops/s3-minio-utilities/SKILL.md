---
name: s3-minio-utilities
title: S3-Compatible Storage Utilities — boto3, mc CLI, and Project Upload Workflows
description: >-
  General-purpose utilities for S3-compatible storage (MinIO, rustfs, Ceph, AWS S3).
  Covers endpoint testing via boto3, mc CLI troubleshooting, and recursive project
  upload/download workflows. Use when accessing any S3-compatible endpoint,
  uploading benchmark results, project data, or benchmark artifacts to S3.
author: Hermes Agent
date: 2026-07-22
tags: [s3, minio, rustfs, storage, benchmark, upload]
---

# S3-Compatible Storage Utilities

Reusable patterns for working with S3-compatible storage endpoints. Covers boto3 (primary), mc CLI (fallback), and project upload workflows.

---

## 1. Endpoint Testing & Verification

When testing access to any S3-compatible endpoint (MinIO, rustfs, Ceph, etc.), use **boto3** as the primary tool — it's reliable on all architectures.

```python
import boto3
from botocore.config import Config

s3 = boto3.client(
    's3',
    endpoint_url='http://141.33.4.155:9000',  # or https:// for TLS
    aws_access_key_id='YOUR_KEY',
    aws_secret_access_key='YOUR_SECRET',
    config=Config(retries={'max_attempts': 3}, signature_version='s3v4')
)

# Test: list buckets
buckets = s3.list_buckets()['Buckets']
```

### Full Verification Workflow

1. **Connect** — create boto3 client with correct endpoint and credentials
2. **List buckets** — verify connectivity and permissions
3. **Create test bucket** — `s3.create_bucket(Bucket='test-name')`
4. **Upload test file** — `s3.put_object(Bucket='test', Key='hello.txt', Body='test')`
5. **List objects** — `s3.list_objects_v2(Bucket='test')['Contents']`
6. **Download & verify** — `s3.get_object(Bucket='test', Key='hello.txt')['Body'].read()`
7. **Cleanup** — delete object, delete bucket

---

## 2. mc CLI — Known Pitfalls

The MinIO `mc` CLI is available but has **known issues on this host**:

### Pitfall: Binary Segmentation Fault on aarch64

Downloading from `https://dl.min.io/client/mc/release/linux-amd64/mc` gives an **x86_64 binary** that segfaults on ARM64/aarch64 hosts. Even with `curl -L` for redirects, the binary won't run.

**Symptom**: `mc --version` → Segmentation fault (core dumped)

**Resolution**: Skip `mc` entirely and use boto3 instead.

### Pitfall: Installation to System Paths

Commands like `curl -o /usr/local/bin/mc` fail with "Failure writing output to destination" due to permissions — prefer user-level paths (`~/bin/`) or use boto3 directly.

### Pitfall: Redirects Without -L

The MinIO download URL follows a redirect. Without `curl -L`, you get HTML/error text instead of the binary, which appears as a malformed executable.

---

## 3. Project Upload to S3

When uploading a project directory (benchmarks, analysis results, etc.) to S3:

### Recursive Upload (excludes .git/)

```python
import boto3, os
from botocore.config import Config

s3 = boto3.client(
    's3',
    endpoint_url='http://141.33.4.155:9000',
    aws_access_key_id='YOUR_KEY',
    aws_secret_access_key='YOUR_SECRET',
    config=Config(retries={'max_attempts': 3}, signature_version='s3v4')
)

base = '/path/to/project'
bucket = 'target-bucket-name'
count = 0
total = 0

# Create bucket if needed
try:
    s3.create_bucket(Bucket=bucket)
except Exception:
    pass  # bucket may already exist

for root, dirs, files in os.walk(base):
    dirs[:] = [d for d in dirs if d != '.git']  # exclude .git
    for f in files:
        fp = os.path.join(root, f)
        rel = os.path.relpath(fp, base)
        s3.upload_file(fp, bucket, rel)
        count += 1
        total += os.path.getsize(fp)

print(f'Uploaded {count} files, {total:,} bytes total')
```

### Key Decisions
- **Exclude `.git/`** — keeps uploads small and avoids committing version control metadata
- **Use relative paths** — preserves directory structure in the bucket
- **Bucket creation** — wrap in try/except since bucket may already exist
- **Report counts** — always report file count and total bytes for verification

---

## 4. Common S3-Compatible Endpoints (AIP)

| Endpoint | URL | Notes |
|----------|-----|-------|
| aip S3 | `https://s3.data.aip.de:9000` | SSL/TLS, used for shboost, media upload |
| rustfs | `http://141.33.4.155:9000` | HTTP, MinIO-compatible, used for benchmarks |

### Unauthenticated S3 Upload (aip.de)

For `s3.data.aip.de:9000` buckets that allow anonymous access:
```bash
KEY="hermes/$(python3 -c 'import uuid; print(uuid.uuid4().hex[:16])').mp4"
curl -X PUT \
  -H "x-amz-acl: public-read" \
  -T /path/to/file.mp4 \
  "https://s3.data.aip.de:9000/scr4agent/$KEY"
```

---

## 5. Quick Reference

| Task | Tool | Command |
|------|------|---------|
| Test endpoint | boto3 | Create client, list_buckets |
| Upload directory | boto3 | Recursive upload_file() with .git excluded |
| mc CLI | mc | Requires correct architecture binary |
| Unauthenticated PUT | curl | `curl -X PUT -T file URL` (no auth headers) |
| Download object | boto3 | `s3.download_file(bucket, key, local_path)` |
| List objects | boto3 | `s3.list_objects_v2(Bucket=bucket)['Contents']` |
