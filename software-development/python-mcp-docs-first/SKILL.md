---
name: python-mcp-docs-first
description: When writing or revising Python code, consult the docs MCP server first for indexed libraries and base API usage on the latest available indexed documentation.
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [python, mcp, docs, dask, pandas, datashader, coding]
    related_skills: [dask-mcp-docs-first, pandas-datashader-mcp-docs-first, docs-mcp-at-aip, native-mcp, mcporter, hermes-agent]
---

# Python MCP Docs First

Use this skill whenever a task involves **writing, editing, reviewing, or explaining Python code** and one or more libraries may be available in the docs MCP server.

## Primary Goal

Before writing Python that depends on external libraries, consult the **docs MCP server** and ground the code in the **latest available indexed documentation**.

This is especially important for:
- `dask`
- `pandas`
- `datashader`
- `hvplot`
- `holoviz`
- `reana`
- any other library indexed on the docs MCP server

## Trigger Conditions

Load this skill when the user asks to:
- write Python code
- fix Python code
- modernize Python code to a library's latest API
- explain how to use a Python library
- create workflows/scripts/notebooks that use Dask or other indexed Python libraries

Even if the task seems simple, check MCP docs first when a library is involved.

## Required Approach

### 1. Identify candidate libraries
- Extract likely libraries from the user's request, existing code, imports, stack traces, or repo files.
- If Dask is involved, treat it as high priority and consult MCP docs before writing code.

### 1a. Auto-load specialized companion skills when relevant
- If the task is primarily about **Dask**, also load `dask-mcp-docs-first` and follow its stricter query templates.
- If the task is primarily about **pandas + Datashader** plotting or dataframe-to-visualization pipelines, also load `pandas-datashader-mcp-docs-first`.
- If the task involves **HDF5 on S3**, also load `hdf5-on-s3-cached`.
- If the task is primarily about **large scientific plotting**, also load `dask-hvplot-datashader-scientific-plots`.
- Treat this skill as the general umbrella skill and delegate to the more specialized companion skill whenever one clearly matches the task.

### 2. Use the docs MCP server first
Prefer native MCP tools when available:
- `mcp_docs_list_libraries`
- `mcp_docs_find_version`
- `mcp_docs_search_docs`
- `mcp_docs_fetch_url`

### 3. Resolve version strategy
- If the user specified a version, search for that exact version or the closest supported match.
- If the user did **not** specify a version, use the **latest available indexed version**.
- If unversioned docs are available, treat them as the current/latest reference unless a version-specific result is more appropriate.

### 4. Search for concrete API details before coding
Search for the exact concepts you need, e.g.:
- Dask: `read_parquet`, `persist`, `repartition`, `map_partitions`, scheduler/client usage, best practices
- Pandas: IO args, dtype handling, nullable/pyarrow backends
- Datashader: aggregation pipeline, Canvas usage, shading/export steps

### 5. Then write the Python
- Base API names, keyword arguments, and patterns on the MCP docs results.
- Prefer robust, current, idiomatic usage rather than legacy habits.
- Include explicit imports and keep examples runnable.

### 6. State grounding when useful
- When the code depends on a potentially version-sensitive API, briefly mention which MCP docs/library/version informed the implementation.
- Keep this brief unless the user asks for a detailed explanation.

## Recommended Query Pattern

For each important library:
1. `mcp_docs_find_version(library="<name>")`
2. `mcp_docs_search_docs(library="<name>", query="<specific API or best-practice question>")`
3. If needed, `mcp_docs_fetch_url(url="<result-url>")` for deeper reading

### Dask-first pattern
For Dask tasks, always try queries like:
- `read_parquet partitions`
- `persist best practices`
- `repartition partition size`
- `map_partitions metadata`
- `distributed client scheduler`
- `dataframe best practices`
- `avoid large graph`

Use multiple focused queries instead of one vague broad query.

## Fallback Strategy

If native MCP tools are unavailable in the current process:
1. Use `mcporter` against the docs MCP server.
2. If necessary, use direct MCP HTTP calls from the terminal.
3. If the library is not indexed there, say so explicitly and then fall back to other sources/tools.

Do **not** pretend the MCP docs covered a library if they did not.

## Output Standard

When producing Python code:
- use current documented APIs when available
- avoid deprecated/guesswork patterns
- keep code runnable and minimal
- include imports explicitly
- if the task is version-sensitive, mention the consulted MCP library/version in one short line

## Pitfalls

- Do not answer from memory when MCP docs are available.
- Do not assume older Dask/DataFrame idioms still apply unchanged.
- Do not use one weak search query and stop if results are poor; retry with narrower API-focused wording.
- Do not overstate certainty if MCP results are sparse or ambiguous.
- Do not skip version lookup for Dask unless the user explicitly says version does not matter.

## Minimal Example Workflow

User asks: "Write Python to read Parquet with Dask and aggregate by column."

Expected behavior:
1. Check `dask` with `mcp_docs_find_version`
2. Search Dask docs for `read_parquet` and aggregation/best-practice details
3. Optionally check `pandas` docs if dtype/output behavior matters
4. Write the script using the documented current API
5. Briefly note the docs basis if version-sensitive

## Success Criteria

This skill is being followed correctly when Python answers are:
- grounded in MCP documentation
- aligned with the latest indexed library behavior
- automatically routed to the specialized companion skill when the task is clearly Dask-specific or pandas/Datashader-specific
