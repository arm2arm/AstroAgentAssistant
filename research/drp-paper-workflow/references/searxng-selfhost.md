# SearXNG Self-Hosting Reference

## Trigger
When the built-in `web_search`/`web_extract` backends are unavailable, rate-limited, or the user explicitly wants a self-hosted metasearch engine as a fallback. SearXNG is a privacy-respecting, open-source alternative to Google/DuckDuckGo that proxies results from multiple engines.

## Verified: Official Docker Image

**Working command (verified 2026-07-27):**
```bash
docker run -d --name searxng -p 8080:8080 searxng/searxng:latest
```

**Common failures — avoid these image names:**
- `searxng/searxng-docker` → pull denied (repo archived/renamed) → HTTP 403
- `ghcr.io/searxng/searxng-docker` → requires Docker login → denied

Use `searxng/searxng:latest` from Docker Hub only.

## Quick Health Check
```bash
sleep 15
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080
# Expect: 200 (confirms container is running)
```

## JSON API — Critical Pitfall (Verified)

By default, the official Docker image **blocks JSON API access** from non-browser clients.

```bash
curl -s "http://localhost:8080/search?q=cat&format=json"
# Returns HTTP 403 Forbidden (not JSON)
```

### Fix: Mount a Custom `settings.yml`

Create `settings.yml`:
```yaml
server:
  bind_address: "127.0.0.1"
  secret_key: "changeme"
  base_url: "http://localhost:8080"

search:
  safe_search: 0
  default_http_method: "GET"

fetch_traits:
  search_leveraging: false

rate_limit:
  enable: false
```

Launch with config:
```bash
mkdir -p ./searxng-config
curl -o ./searxng-config/settings.yml https://raw.githubusercontent.com/searxng/searxng/master/standalone/docker/data/settings.yml
# Edit settings.yml to add the above overrides (or replace entirely)

docker run -d --name searxng -p 8080:8080 \
  -v ./searxng-config/settings.yml:/etc/searxng/settings.yml \
  searxng/searxng:latest
```

### Verify JSON After Patch
```bash
sleep 15
curl -s "http://localhost:8080/search?q=test&format=json" | python3 -m json.tool | head -20
# Should return valid JSON with results array
```

## CLI Usage (with JSON working)

```bash
# Search
curl -s "http://localhost:8080/search?q=cat&format=json" | python3 -c \
  "import json,sys; [print(r.get('content','?'), r.get('url','?')) for r in json.load(sys.stdin).get('results',[])]"

# Pipe to jq
curl -s "http://localhost:8080/search?q=cat&format=json" | jq '.results[] | {title, url}'
```

## Notes
- The web UI at `http://localhost:8080` always works — the 403 only affects the `/search?format=json` endpoint.
- This is a known change in SearXNG 1.0+ where JSON access is disabled by default for security.
- For agent/programmatic use, always mount a custom `settings.yml`.

## Integration with web_search_backend
Once SearXNG is running with JSON enabled, it can serve as a local metasearch proxy. The built-in `web_search` tool does not natively support SearXNG endpoints — use `curl` or `python requests` directly against `http://localhost:8080/search?q=...&format=json`.