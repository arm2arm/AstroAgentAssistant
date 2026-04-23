---
name: python-mcp-docs-first
description: When writing or revising Python code, consult the docs MCP server first for indexed libraries, especially Dask, and base API usage on the latest available documentation.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [python, mcp, docs, dask, pandas, datashader, coding]
    category: python
    related_skills: [docs-mcp-at-aip, reana-serial-python, s3-parquet-sampling]
---

# Python MCP Docs First

## When to Use
Use this skill whenever a task involves writing, editing, reviewing, or explaining Python code and one or more libraries may be available on the AIP docs MCP server.

This is especially important for:
- `dask`
- `pandas`
- `datashader`
- `hvplot`
- `holoviz`
- `reana`
- any other indexed library on `docs-mcp-server.kube.aip.de`

## Procedure

### 1. Identify candidate libraries
- Extract likely libraries from the user's request, existing code, imports, stack traces, or repository files.
- If Dask is involved, treat it as high priority and consult MCP docs before writing any code.

### 2. Query the docs MCP server first
Prefer native MCP tools when available:
- `mcp_docs_list_libraries`
- `mcp_docs_find_version`
- `mcp_docs_search_docs`
- `mcp_docs_fetch_url`

Recommended sequence for each important library:
1. `mcp_docs_find_version(library="<name>")`
2. `mcp_docs_search_docs(library="<name>", query="<specific API or best-practice question>")`
3. `mcp_docs_fetch_url(url="<result-url>")` if deeper reading is needed

### 3. Resolve version strategy
- If the user specified a version, search for that exact version or the closest supported match.
- If the user did not specify a version, use the latest available indexed version.
- If unversioned docs are also available, treat them as the current reference unless a version-specific page is clearly more appropriate.

### 4. Use focused API searches before coding
Avoid broad vague queries. Search for the exact API or best-practice topic.

Examples:

**Dask**
- `read_parquet partitions`
- `persist best practices`
- `repartition partition size`
- `map_partitions metadata`
- `distributed client scheduler`
- `dataframe best practices`
- `avoid large graph`

**Pandas**
- `read_parquet dtype_backend`
- `pyarrow backend`
- `nullable dtypes`

**Datashader**
- `Canvas points aggregation`
- `shade export image`
- `dask dataframe aggregation`

### 5. Then write the Python
- Base API names, keyword arguments, and patterns on the MCP docs results.
- Prefer current, documented, idiomatic usage rather than remembered legacy habits.
- Include explicit imports and keep examples runnable.

### 6. Mention the grounding when it matters
If the code depends on a version-sensitive API, briefly note which library/version from the MCP docs informed the implementation.

Example:
> Grounded in docs MCP results for Dask 2024.0.0.

### 7. Fallbacks if native MCP tools are unavailable
1. Use `mcporter` against the same docs MCP server.
2. If needed, use direct MCP HTTP calls from the terminal.
3. If the library is not indexed there, say so explicitly and only then fall back to other sources.

## Pitfalls
- Do not answer from memory when MCP docs are available.
- Do not assume older Dask idioms are still the best current approach.
- Do not stop after one weak search query; retry with narrower, API-focused wording.
- Do not overstate certainty when MCP results are sparse or ambiguous.
- Do not skip version lookup for Dask unless the user explicitly says version does not matter.

## Verification
- `mcp_docs_find_version` returns a sensible library/version match.
- `mcp_docs_search_docs` returns relevant results for the targeted API question.
- The produced Python uses APIs and patterns aligned with the documentation retrieved from MCP.
