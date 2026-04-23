---
name: mcporter-cli
description: Use the mcporter CLI for ad-hoc MCP server discovery, testing, schema inspection, and tool calls without changing Hermes configuration.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [mcp, mcporter, node, cli, debugging, infrastructure]
    category: infrastructure
    related_skills: [hermes-native-mcp, docs-mcp-at-aip]
---

# mcporter CLI

## When to Use
Use this skill when you want to inspect or call MCP servers from the terminal without first wiring them into Hermes native MCP configuration.

Typical cases:
- quick testing of an HTTP MCP endpoint
- debugging a server before adding it to `mcp_servers`
- listing tools and schemas for a server
- making ad-hoc MCP tool calls with structured JSON output

## Procedure

### 1. Check prerequisites
```bash
command -v npx
npx -y mcporter list --output json || true
```

### 2. List configured MCP servers
```bash
npx -y mcporter list --output json
```

### 3. Inspect an ad-hoc HTTP MCP server
```bash
npx -y mcporter list \
  --http-url https://docs-mcp-server.kube.aip.de/mcp \
  --name docs \
  --output json
```

### 4. Inspect tools and schemas
```bash
npx -y mcporter list docs --schema --output json
```

### 5. Call a tool
```bash
npx -y mcporter call docs.search_docs \
  library=dask \
  query='read_parquet partitions' \
  limit:3 \
  --output json
```

### 6. Use as a fallback when native MCP is unavailable
If Hermes native MCP tools are unavailable in the current process, use mcporter to:
1. verify the endpoint is alive
2. verify tool discovery
3. perform ad-hoc calls while deciding whether to add the server to `mcp_servers`

### 7. TLS trust fix for internal HTTPS endpoints
If `mcporter` reports:
- `unable to verify the first certificate`

and the same endpoint works with low-level debugging, the usual cause is a missing trusted intermediate certificate.

Preferred fix:
```bash
NODE_EXTRA_CA_CERTS=/path/to/custom-ca-bundle.pem \
  npx -y mcporter list \
  --http-url https://docs-mcp-server.kube.aip.de/mcp \
  --name docs \
  --output json
```

This preserves verification while allowing Node to trust the internal chain.

## Pitfalls
- Prefer `--output json` for automation and debugging.
- Ad-hoc URLs are excellent for testing, but they do not make tools natively available in Hermes sessions by themselves.
- If a server works only with insecure TLS bypasses, fix trust rather than relying on insecure settings long-term.
- For interactive OAuth flows, a PTY may be required.

## Verification
- `mcporter list --http-url ... --output json` returns server status `ok`.
- `mcporter call ... --output json` returns structured tool output.
- The same server can then be promoted into Hermes `mcp_servers` config if desired.
