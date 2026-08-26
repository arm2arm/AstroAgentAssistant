---
name: reana-cmd-plot-workflow
summary: REANA workflow that caches a large S3 Parquet dataset and plots bprp0 vs mg0 as a hex-bin PNG. (Rehomed into reana references)

Content: Full skill content archived under reana-cmd-plot-workflow; see original skill for session scripts and notes. Key points:
- Uses anonymous S3 read with `storage_options={"anon": True, "client_kwargs": {"endpoint_url": "https://s3.data.aip.de:9000"}}`
- Caches a local parquet (`shboost_cache.parquet`) to avoid repeated full reads
- Sample ~200k rows for plotting; hexbin plot saved as `cmd.png`
- `reana.yaml` provided with environment image and resources
- Pitfalls: `reana-client create` bug, `REANA_WORKON` env var, large dataset first-run cost, token expiry

For full original content and session notes see: references/reana-cmd-plot-workflow-session-notes.md
