import requests
import json
import re

# DRP Hub API Discovery Script
# Discovers available API endpoints on a DRP Hub instance by grepping the JS bundle
# and testing common paths.

BASE = "https://reana-p4n.aip.de"  # Change as needed
TOKEN = None  # Set to bearer token if needed for authenticated endpoints
HEADERS = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}

print("=== Step 1: Extract API paths from JS bundle ===")
try:
    js_resp = requests.get(f"{BASE}/static/js/main.fbfee2f8.js", timeout=10)
    urls = re.findall(r'"(/api/[^"]*)"', js_resp.text)
    unique_urls = sorted(set(urls))
    print(f"Found {len(unique_urls)} API paths:")
    for u in unique_urls:
        print(f"  {u}")
except Exception as e:
    print(f"Error fetching JS bundle: {e}")

print("\n=== Step 2: Test common API paths ===")
test_paths = [
    "/api/status",
    "/api/config",
    "/api/workflows",
    "/api/workflows/",
    "/api/you",
    "/api/gitlab/projects",
    "/api/gitlab/webhook",
    "/api/login",
    "/api/register",
    "/api/token",
    "/api/oauth/login/",
]

for path in test_paths:
    try:
        resp = requests.get(f"{BASE}{path}", headers=HEADERS, timeout=10)
        content_type = resp.headers.get("content-type", "unknown")
        is_spa = "text/html" in content_type and "doctype" in resp.text
        status = resp.status_code
        preview = ""
        if status in (200, 401, 403):
            try:
                preview = json.dumps(resp.json(), indent=2)[:200]
            except:
                preview = resp.text[:100]
        print(f"  {path:30s} -> {status:3d}  {('SPA' if is_spa else content_type):20s} {preview}")
    except Exception as e:
        print(f"  {path:30s} -> ERROR: {e}")
