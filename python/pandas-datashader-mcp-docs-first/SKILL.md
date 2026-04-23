---
name: pandas-datashader-mcp-docs-first
description: Write or review pandas and Datashader plotting code only after consulting indexed MCP documentation, using focused query templates for current IO, dtype, aggregation, and rendering APIs.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [python, pandas, datashader, mcp, docs, plotting, visualization]
    category: python
    related_skills: [python-mcp-docs-first, dask-mcp-docs-first, dask-hvplot-datashader-scientific-plots, docs-mcp-at-aip, s3-parquet-sampling]
---

# Pandas + Datashader MCP Docs First

## When to Use
Use this skill when writing, fixing, reviewing, or explaining Python code that uses pandas, Datashader, or both together for analysis and plotting.

Apply it to:
- `pandas.read_parquet`, dtype/backend, IO behavior
- dataframe reshaping/filtering before visualization
- Datashader `Canvas`, aggregation, `shade`, export steps
- pandas + Datashader plotting pipelines
- pandas/Dask/Datashader interoperability questions

## Procedure

### 1. Resolve indexed versions first
Start by checking what MCP has indexed:
```text
mcp_docs_find_version(library="pandas")
mcp_docs_find_version(library="datashader")
```

If unversioned docs are available, treat them as the current reference unless the task needs a pinned version.

### 2. Run focused documentation queries before coding
Do not use a single broad query. Use multiple narrow API-level queries.

If the data originates from **S3 or TAP**, prefer a local Parquet cache for repeated downstream analysis. For large tabular data, prefer a Dask DataFrame plus `hvplot`/Datashader rather than eager pandas plotting.

#### Pandas queries
- `read_parquet dtype_backend`
- `read_parquet filesystem storage_options`
- `nullable dtypes`
- `pyarrow backend`
- `groupby aggregation examples`
- `merge join best practices`
- `categorical dtype`

#### Datashader queries
- `Canvas points aggregation`
- `Canvas line aggregation`
- `shade how log eq_hist`
- `Image export to_pil`
- `transfer functions shade set background`
- `dask dataframe aggregation`
- `datashader pipeline example`

#### Interop queries
- `datashader pandas dataframe example`
- `datashader dask dataframe example`
- `parquet to datashader pipeline`
- `canvas plot width plot height`
- `hvplot rasterize datashade`
- `hvplot scientific plotting large data`

### 3. Fetch central pages when version-sensitive
If a result appears central, fetch it for closer reading:
```text
mcp_docs_fetch_url(url="<result-url>")
```

### 4. Then write the code
Ground the implementation in the MCP docs results to choose:
- correct `read_parquet` arguments
- whether `dtype_backend` / filesystem behavior matters
- current Datashader pipeline order
- current rendering/export idioms
- whether a pandas DataFrame or Dask DataFrame is more appropriate

### 5. Output standard
When returning code:
- include imports explicitly
- avoid deprecated or guessed pandas/Datashader APIs
- keep the plotting pipeline clear and minimal
- prefer `hvplot` as the default scientific plotting layer when interactive/scalable plotting is useful
- use Dask + hvPlot + Datashader for large dense datasets
- cache reduced S3/TAP-derived tabular results locally as Parquet
- mention the consulted docs basis briefly if version-sensitive

Example note:
> Grounded in docs MCP results for pandas current indexed docs and Datashader current indexed docs.

### 6. Required review checklist before finalizing
Before presenting code, check:
- Did I look up pandas and/or Datashader in MCP first?
- Did I search for the exact API/topic rather than answering from memory?
- Did I confirm the current Datashader rendering/export path?
- Did I choose pandas vs Dask input appropriately?
- Did I avoid outdated dtype/backend assumptions for pandas parquet IO?

## Pitfalls
- Do not answer pandas or Datashader API questions from memory when MCP docs are available.
- Do not assume old Datashader examples still reflect the current API shape.
- Do not collapse all queries into one vague search.
- Do not ignore dtype/backend behavior when parquet IO is central to the task.
- Do not overstate certainty if indexed docs are sparse.

## Verification
- `mcp_docs_find_version` was used for pandas and/or Datashader first.
- At least two focused documentation queries were used before coding.
- The final code aligns with the retrieved MCP documentation and current plotting workflow.
