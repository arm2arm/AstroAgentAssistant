---
name: docs-mcp-at-aip
description: Access the AIP documentation MCP server at https://docs-mcp-server.kube.aip.de. Search, scrape, and fetch documentation for 15+ indexed libraries including reana, pandas, snakemake, dask, unsloth, and more. HTTP POST + SSE, internal network only.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [infrastructure, mcp, documentation, search, aip, internal, reana, pandas, snakemake]
    category: infrastructure
    related_skills: [hermes-native-mcp, mcporter-cli, python-mcp-docs-first, dask-mcp-docs-first, pandas-datashader-mcp-docs-first, hermes-api-server, openwebui-hermes, reana-serial-python]
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
mcp_servers:
  docs:
    url: https://docs-mcp-server.kube.aip.de/mcp
```

Or use the Hermes native MCP client. The server uses HTTP POST + Server-Sent Events — no extra headers needed beyond the standard MCP JSON-RPC protocol.

### 1a. Auto-load specialized companion skills when the docs task turns into code generation
- If the user is asking to **write general Python code** from these docs, also load `python-mcp-docs-first`.
- If the task is primarily about **Dask**, also load `dask-mcp-docs-first`.
- If the task is primarily about **pandas + Datashader** plotting or dataframe-to-visualization pipelines, also load `pandas-datashader-mcp-docs-first`.
- Treat this skill as the documentation-access umbrella skill and hand off code-generation guidance to the more specialized companion skill whenever one clearly matches.

### 1b. TLS trust fix for hosts missing the intermediate chain

The endpoint may fail TLS verification on some hosts because the server does not always provide the full intermediate chain. A reliable local fix is to build a CA bundle that includes the GEANT intermediate and point Hermes, Python, curl, and Node at it:

```bash
mkdir -p ~/.hermes/certs
curl -fsSL http://crt.harica.gr/HARICA-GEANT-TLS-R1.cer -o ~/.hermes/certs/HARICA-GEANT-TLS-R1.cer

python3 - <<'PY'
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from pathlib import Path

src = Path.home()/'.hermes/certs/HARICA-GEANT-TLS-R1.cer'
out = Path.home()/'.hermes/certs/HARICA-GEANT-TLS-R1.pem'
cert = x509.load_der_x509_certificate(src.read_bytes())
out.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
print(out)
PY

python3 - <<'PY'
import certifi
from pathlib import Path

bundle = Path.home()/'.hermes/certs/custom-ca-bundle.pem'
bundle.write_text(Path(certifi.where()).read_text() + '\n' + (Path.home()/'.hermes/certs/HARICA-GEANT-TLS-R1.pem').read_text())
print(bundle)
PY
```

Then add to `~/.hermes/.env`:

```bash
SSL_CERT_FILE=/home/$USER/.hermes/certs/custom-ca-bundle.pem
REQUESTS_CA_BUNDLE=/home/$USER/.hermes/certs/custom-ca-bundle.pem
NODE_EXTRA_CA_CERTS=/home/$USER/.hermes/certs/custom-ca-bundle.pem
CURL_CA_BUNDLE=/home/$USER/.hermes/certs/custom-ca-bundle.pem
```

This preserves TLS verification instead of disabling it.

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

## Verified Connection Details

Discovered through systematic testing (hostname probing, path enumeration, header negotiation):

| Property | Value |
|---|---|
| **Hostname** | `docs-mcp-server.kube.aip.de` (NOT `mcp-docs.kube.aip.de` which 404s) |
| **MCP endpoint** | `/mcp` (HTTP POST + SSE) |
| **Protocol version** | `2024-11-05` |
| **Required headers** | `Content-Type: application/json` + `Accept: application/json, text/event-stream` |
| **Response format** | SSE — parse `data:` line as JSON (strip `data: ` prefix) |
| **Server version** | 0.1.0 |
| **DNS** | `141.33.165.5` (IPv4 only) |

### Verified curl commands

**Initialize:**
```bash
curl -sk -m 5 -X POST "https://docs-mcp-server.kube.aip.de/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"hermes","version":"1.0"}}}'
```

**List libraries:**
```bash
curl -sk -m 10 -X POST "https://docs-mcp-server.kube.aip.de/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"list_libraries","arguments":{}}}'
```

**Search docs:**
```bash
curl -sk -m 10 -X POST "https://docs-mcp-server.kube.aip.de/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"search_docs","arguments":{"library":"reana","query":"workflow specification","limit":3}}}'
```

## Pitfalls

- **Internal network only** — server is not accessible from outside the AIP network.
- **Incomplete certificate chain on some hosts** — the endpoint may fail TLS verification until the GEANT intermediate is trusted locally. Prefer a custom CA bundle over disabling verification.
- **Wrong hostname** — `mcp-docs.kube.aip.de` returns 404 — always use `docs-mcp-server.kube.aip.de`.
- **Wrong Accept header** — omitting `text/event-stream` causes `32000 Not Acceptable` error.
- **SSE parsing** — responses are SSE format: `event: message\ndata: {...}\n\n`. Extract the JSON from the `data:` line.
- **scrape_docs is destructive** — it re-indexes; use `refresh_version` for updates.

## Verification

- `list_libraries` returns non-empty list of library names.
- `search_docs` with a known library and query returns structured results with URLs.
- `fetch_url` converts a public URL to Markdown.