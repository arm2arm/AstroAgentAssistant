# SHboost24 dataset notes

Validated public access details observed in local workflows:

- S3 endpoint: `https://s3.data.aip.de:9000`
- Bucket: `shboost2024`
- Main parquet release prefix: `shboost_08july2024_pub.parq/`
- Common parquet glob:

```text
s3://shboost2024/shboost_08july2024_pub.parq/*.parquet
```

- Storage options used successfully in local Python/Dask workflows:

```python
storage_options = {
    "use_ssl": True,
    "anon": True,
    "client_kwargs": {"endpoint_url": "https://s3.data.aip.de:9000"},
}
```

Relevant columns repeatedly used for CMD-style plots:
- `bprp0`
- `mg0`

Practical workflow notes:
- prefer local Parquet caching for sampled or reduced data products;
- keep only required columns before plotting;
- for very large runs, use density plots instead of raw scatter.
