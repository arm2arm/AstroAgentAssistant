---
name: dask-mcp-docs-first
description: Generate or review Dask Python code only after consulting indexed MCP documentation, using strict version lookup and focused query templates for current APIs and best practices.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [python, dask, mcp, docs, parallel-computing, code-generation]
    category: python
    related_skills: [python-mcp-docs-first, docs-mcp-at-aip, s3-parquet-sampling, dask-hvplot-datashader-scientific-plots]
---

# Dask MCP Docs First

## When to Use
Use this skill when writing, fixing, reviewing, or explaining Python code that uses Dask.

Apply it to:
- `dask.dataframe`
- `dask.array`
- distributed client/scheduler usage
- Parquet or S3 workflows with Dask
- Dask + Datashader pipelines
- performance and best-practice questions

## Procedure

### 1. Resolve the indexed Dask version first
Always start with:
```text
mcp_docs_find_version(library="dask")
```

Record the best match. If unversioned docs are also available, treat them as the current reference unless the task requires a pinned version.

### 2. Run focused documentation queries before coding
Do not rely on one broad search. Use several targeted queries matching the requested operation.

If the source data comes from **S3 or TAP**, assume a local Parquet cache should be created after reduction. If the dataset is huge, keep Dask as the default processing layer and aim for an effective working footprint around **32GB RAM**.

#### Core ingestion / dataframe queries
- `read_parquet partitions`
- `read_parquet storage options`
- `dataframe best practices`
- `persist best practices`
- `repartition partition size`
- `map_partitions metadata`
- `categorize dataframe`

#### Distributed execution queries
- `distributed client scheduler`
- `localcluster example`
- `client persist compute`
- `avoid large graph`
- `dashboard diagnostics`

#### Performance / correctness queries
- `best practices avoid full shuffle`
- `known divisions set_index`
- `lazy evaluation compute persist`
- `metadata meta parameter`
- `partition size guidance`

#### Array / mixed-workload queries
- `dask array chunking best practices`
- `overlap map_blocks`
- `array persist compute`

#### Dask + Datashader queries
- `datashader dask dataframe aggregation`
- `points canvas dask`
- `shade export image`

#### Dask + hvPlot queries
- `hvplot rasterize dask dataframe`
- `hvplot datashade dask dataframe`
- `hvplot large data scientific plots`

### 3. Pull deeper page content if results are important
For any result that appears central to the answer, fetch the page and read it more closely:
```text
mcp_docs_fetch_url(url="<result-url>")
```

### 4. Write the code only after grounding it
Use the MCP results to determine:
- API names
- argument names
- recommended workflow order
- whether to use `persist()`, `compute()`, repartitioning, metadata hints, or a distributed client

### 5. Output standard for Dask code
When returning code:
- include all imports explicitly
- avoid deprecated or guessed APIs
- keep the graph simple unless the task truly needs more complexity
- prefer clear partition-aware code
- avoid eager conversion to pandas too early
- cache reduced S3/TAP-derived tabular results locally as Parquet
- prefer `hvplot` for scientific plotting and combine it with `rasterize=True` / `datashade=True` when density or scale demands it
- mention the consulted Dask docs version briefly when relevant

Example note:
> Grounded in docs MCP results for Dask 2024.0.0 / current indexed docs.

### 6. Required review checklist before finalizing
Before presenting Dask code, check:
- Did I look up the indexed Dask version?
- Did I search for the exact API/topic rather than answering from memory?
- Did I avoid unnecessary `.compute()` calls?
- Did I consider partition sizing / repartitioning where relevant?
- Did I avoid patterns likely to create very large graphs?
- If using `map_partitions`, did I confirm metadata handling?

## Pitfalls
- Do not answer Dask API questions from memory when MCP docs are available.
- Do not jump straight from `read_parquet` to `.compute()` unless the user explicitly wants an in-memory local result.
- Do not use one vague search query and stop.
- Do not ignore metadata requirements for `map_partitions`-style transformations.
- Do not assume older blog-post idioms are the same as current Dask best practices.

## Verification
- `mcp_docs_find_version(library="dask")` was checked first.
- At least two focused Dask documentation queries were used before coding.
- The final code aligns with the retrieved documentation and follows current Dask best practices.
