# S3 Bucket Cleanup — Paginated Delete Recipe

**Session**: 2026-07-22
**Source**: Multi-iteration debugging of `BucketNotEmpty` errors on MinIO-compatible endpoints

## Problem

`boto3` `delete_objects()` with a single `list_objects_v2()` call silently fails on endpoints with many objects. The error:

```
botocore.exceptions.ClientError: An error occurred (BucketNotEmpty) when calling the DeleteBucket operation:
The bucket you tried to delete is not empty
```

Even though `list_objects_v2` returns objects, the deletion doesn't actually remove them all.

## Root Cause

MinIO-compatible S3 endpoints paginate responses. A single `list_objects_v2()` call returns at most 1000 objects (the `MaxKeys` default). If there are more objects, they are NOT returned. The deletion only attempts to delete what was returned.

**But**: in our case, even 1000 objects caused issues — likely because the API requires explicit pagination and doesn't auto-advance.

## Solution

Use `get_paginator()` to exhaust all pages, then batch-delete in groups of 1000:

```python
def cleanup(s3, bucket):
    """Delete all objects then the bucket, using proper pagination."""
    try:
        paginator = s3.get_paginator("list_objects_v2")
        all_keys = []
        for page in paginator.paginate(Bucket=bucket):
            if "Contents" in page:
                all_keys.extend(page["Contents"])
        # Delete in batches of 1000 (S3 API max per call)
        for i in range(0, len(all_keys), 1000):
            batch = all_keys[i:i+1000]
            s3.delete_objects(
                Bucket=bucket,
                Delete={"Objects": [{"Key": o["Key"]} for o in batch]},
            )
        s3.delete_bucket(Bucket=bucket)
    except Exception as e:
        print(f"    Cleanup: {e}")
```

## Verification

Always verify cleanup actually worked:

```python
# After cleanup, verify bucket is empty
paginator = s3.get_paginator("list_objects_v2")
for page in paginator.paginate(Bucket=bucket):
    if "Contents" in page:
        print(f"  WARNING: {len(page['Contents'])} objects still present!")
```

## When This Matters

- **Always** when the bucket may contain >1000 objects
- **Always** when running benchmarks that create many small files (e.g., 1KB×1000 = 1000 objects)
- **Never** when manually managing a handful of objects (but still good practice)

## Alternatives

| Approach | Pros | Cons |
|----------|------|------|
| Paginated delete (above) | Reliable, works with all S3 APIs | Requires code |
| `mc rb --force bucket` | One command | Requires mc binary (may segfault) |
| `s3:// URL with AWS CLI` | Familiar syntax | Requires awscli setup |
| boto3 client-side delete in loop | Simple | Very slow for large buckets |