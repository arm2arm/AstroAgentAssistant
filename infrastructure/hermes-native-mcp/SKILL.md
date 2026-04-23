---
name: hermes-native-mcp
description: Configure and use Hermes Agent's built-in MCP client for stdio and HTTP MCP servers, including testing, troubleshooting, and TLS trust fixes for internal HTTPS endpoints.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [mcp, hermes, infrastructure, tools, http, stdio]
    category: infrastructure
    related_skills: [docs-mcp-at-aip, mcporter-cli, hermes-api-server]
---

# Hermes Native MCP

## When to Use
Use this skill when configuring Hermes Agent to connect to MCP servers directly so their tools appear natively in conversations.

Typical cases:
- add a new MCP server to Hermes
- connect to HTTP/StreamableHTTP MCP endpoints
- connect to local stdio MCP servers
- troubleshoot why MCP tools are missing
- fix TLS trust issues for internal HTTPS MCP servers

## Procedure

### 1. Check prerequisites
```bash
python3 - <<'PY'
import importlib.util
print('mcp', importlib.util.find_spec('mcp') is not None)
PY

command -v npx || true
command -v uvx || true
```

If the Python MCP SDK is missing:
```bash
pip install mcp
# or
uv pip install mcp
```

### 2. Configure `~/.hermes/config.yaml`

**HTTP MCP server:**
```yaml
mcp_servers:
  docs:
    url: https://docs-mcp-server.kube.aip.de/mcp
```

**stdio MCP server:**
```yaml
mcp_servers:
  filesystem:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
```

Valid per-server options include:
- `command`
- `args`
- `env`
- `url`
- `headers`
- `timeout`
- `connect_timeout`

A server entry must use either `command` or `url`, not both.

### 3. Verify discovery
```bash
hermes mcp list
hermes mcp test docs
```

In a fresh Hermes process, MCP tools appear with the naming pattern:
- `mcp_<server>_<tool>`

Example:
- `mcp_docs_search_docs`
- `mcp_docs_find_version`

### 4. Use from Hermes
After a restart or fresh session, ask Hermes to use the MCP tools directly.

Example prompt:
```text
Use the docs MCP server to find the best matching indexed version for dask.
```

### 5. Internal HTTPS TLS trust fix
If an internal MCP endpoint works with direct networking but Hermes reports certificate verification failures, prefer fixing trust instead of disabling TLS verification.

Symptoms:
- `CERTIFICATE_VERIFY_FAILED`
- `unable to verify the first certificate`

Reliable local pattern:
1. obtain the missing intermediate certificate
2. append it to a custom CA bundle
3. point Hermes/Python/Node/curl at that bundle via environment variables

Example variables in `~/.hermes/.env`:
```bash
SSL_CERT_FILE=/home/$USER/.hermes/certs/custom-ca-bundle.pem
REQUESTS_CA_BUNDLE=/home/$USER/.hermes/certs/custom-ca-bundle.pem
NODE_EXTRA_CA_CERTS=/home/$USER/.hermes/certs/custom-ca-bundle.pem
CURL_CA_BUNDLE=/home/$USER/.hermes/certs/custom-ca-bundle.pem
```

### 6. Re-test after config changes
```bash
hermes mcp test docs
hermes chat -q "Use the docs MCP server to list three indexed libraries."
```

## Pitfalls
- Tool availability is established at process startup; use a fresh Hermes process if tools do not appear.
- `mcp_servers:` is the correct config key, not `mcp.servers:`.
- Internal HTTPS MCP servers may fail because of missing intermediate CAs, not because the endpoint is down.
- Do not disable TLS verification permanently when a trust-store fix is possible.
- Tool names are prefixed with the server name; look for `mcp_<server>_*`.

## Verification
- `hermes mcp test <name>` connects successfully and lists tools.
- A fresh `hermes chat` session exposes the expected `mcp_<server>_*` tools.
- An actual MCP tool call succeeds from within Hermes.
