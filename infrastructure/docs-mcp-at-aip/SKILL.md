---
name: docs-mcp-at-aip
description: Access the AIP documentation MCP server at https://docs-mcp-server.kube.aip.de. Search, scrape, and fetch documentation for 15+ indexed libraries including reana, pandas, snakemake, dask, unsloth, and more. HTTP POST + SSE, self-signed cert, internal network only.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [infrastructure, mcp, documentation, search, aip, internal, reana, pandas, snakemake]
    category: infrastructure
    related_skills: [hermes-api-server, openwebui-hermes, reana-serial-python]
---

# AIP Documentation MCP Server

## When to Use
Use this skill when searching for documentation on libraries and tools used at AIP. The server indexes 15+ libraries including: reana, pandas, snakemake, dask, datashader, unsloth, holoviz, hvplot, crewai, langfuse, flowise, cline, mcp, environments (docker) for reana, aiphpcdocs.

Tasks: API reference lookup, workflow specification examples (reana.yaml), configuration guides, code examples, and version-specific docs.

## Prerequisites
- Internal AIP network access
- Python 3 stdlib + curl (no extra dependencies)

## Procedure

### 1. Connect to the MCP server

The MCP endpoint is `/mcp` on `https://docs-mcp-server.kube.aip.de`.

Configure in `~/.hermes/config.yaml`:
```yaml
mcp:
  servers:
    - name: docs-mcp-aip
      url: https://docs-mcp-server.kube.aip.de/mcp
```

Or use the Hermes native MCP client. The server uses HTTP POST + Server-Sent Events — no extra headers needed beyond the standard MCP JSON-RPC protocol.

### 2. Initialize the connection

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "hermes", "version": "1.0"}
  }
}
```

### 3. Discover available tools

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}
```

### 4. Key tool examples

**List indexed libraries:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {"name": "list_libraries", "arguments": {}}
}
```

**Search documentation:**
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "search_docs",
    "arguments": {
      "library": "reana",
      "query": "workflow specification yaml example",
      "limit": 3
    }
  }
}
```

**Find available versions:**
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "tools/call",
  "params": {
    "name": "find_version",
    "arguments": {"library": "pandas", "targetVersion": "2.x"}
  }
}
```

**Fetch a URL as Markdown:**
```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "method": "tools/call",
  "params": {
    "name": "fetch_url",
    "arguments": {"url": "https://docs.reana.io/reference/reana-yaml/"}
  }
}
```

**Scrape new library docs:**
```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "method": "tools/call",
  "params": {
    "name": "scrape_docs",
    "arguments": {
      "library": "my-lib",
      "url": "https://my-lib.example.com/docs/",
      "maxPages": 100,
      "maxDepth": 3
    }
  }
}
```

## Indexed Libraries

```
aiphpcdocs, cline, crewai, dask, datashader,
environments (docker) for reana, flowise, holoviz, hvplot,
langfuse, mcp, pandas, reana, snakemake, unsloth
```

## Available Tools

| Tool | Description | Read-only? |
|------|-------------|------------|
| `list_libraries` | List all indexed libraries | ✅ |
| `find_version` | Find matching version for a library | ✅ |
| `search_docs` | Search docs for a library | ✅ |
| `fetch_url` | Fetch any URL as Markdown | ✅ |
| `list_jobs` | List indexing job queue | ✅ |
| `get_job_info` | Get specific job details | ✅ |
| `scrape_docs` | Scrape and index new library docs | ❌ |
| `refresh_version` | Re-scrape a library version | ❌ |
| `cancel_job` | Cancel a running job | ❌ |
| `remove_docs` | Remove indexed docs | ❌ |

## Pitfalls

- **Internal network only** — server is not accessible from outside the AIP network.
- **Self-signed certificate** — add `Insecure` flag or import the CA cert if the client rejects it.
- **SSE response format** — the server returns messages as `event: message` followed by `data: <json>` lines. Parse the `data:` lines as JSON.
- **Protocol version** — use `2024-11-05` for compatibility.
- **scrape_docs is destructive** — it re-indexes; use `refresh_version` for updates.

## Verification

- `list_libraries` returns non-empty list of library names.
- `search_docs` with a known library and query returns structured results with URLs.
- `fetch_url` converts a public URL to Markdown.