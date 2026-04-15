---
name: k8s-mcp-docs
description: Access the AIP Kubernetes MCP server documentation at https://mcp-docs.kube.aip.de. The MCP server exposes internal Kubernetes documentation, service endpoints, and infrastructure details. Self-signed certificate, internal network only.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [infrastructure, kubernetes, mcp, documentation, aip, internal]
    category: infrastructure
    related_skills: [hermes-api-server, openwebui-hermes]
---

# AIP Kubernetes MCP Documentation

## When to Use
Use this skill when the user needs information about the AIP Kubernetes infrastructure, service endpoints, deployments, or internal documentation. This MCP server is only accessible from the internal AIP network.

## Procedure

### 1. Connect to the MCP server
```python
# Via Hermes native MCP client
# Configure in ~/.hermes/config.yaml:
# mcp:
#   servers:
#     - name: k8s-docs
#       url: https://mcp-docs.kube.aip.de
#       # or stdio mode if provided
```

### 2. Discover available tools
```python
# After connection, the MCP server registers tools such as:
# - get_service_docs(service_name)
# - list_deployments()
# - get_pod_status(namespace, pod_name)
# - describe_endpoint(service)
```

### 3. Query documentation
```python
# Example tool calls (after MCP connection is established):
# result = await mcp.call('get_service_docs', {'service': 'argocd'})
# result = await mcp.call('list_deployments', {'namespace': 'monitoring'})
```

## Known Issues

- **Self-signed certificate**: The server uses a self-signed certificate — add to trust store or use `--no-verify` if supported.
- **Internal network only**: This server is not accessible from outside the AIP network.
- **URL path unknown**: The correct URL path was not confirmed — the user should verify the endpoint path before use.

## Pitfalls
- Do NOT attempt to access this server from an external network — it is internal-only.
- Do NOT assume the URL path without confirmation — the MCP server path should be verified by the AIP team.
- The self-signed certificate requires explicit trust configuration.

## Verification
- MCP server connects and registers tools (non-empty tool list).
- At least one tool call succeeds with non-empty response.
- Tools return structured documentation or status information.