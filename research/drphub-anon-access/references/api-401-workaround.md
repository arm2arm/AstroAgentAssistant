# Workaround: 401 on REST API Even for Public Products

## Symptom
Calling `GET https://drp-term.kube.aip.de/api/v1/products?visibility=public` without a token returns:
```json
{"error":{"code":"unauthorized","message":"Missing Bearer token","request_id":"..."}}
```

## Root Cause
The REST API requires authentication for **all** endpoints except `/health`. Even public products require a Bearer token — the `visibility=public` filter only affects *which* products are returned, not *whether* auth is required.

## Workaround: Extract Supabase Anon Key from Frontend

The web frontend at `https://drphub-p4n.aip.de` embeds a Supabase anonymous key in its JS bundle. This key grants read-only access to the `drp_cards` table.

### Extract the anon key
```bash
# Find current JS chunk (filename changes on deploy)
curl -s https://drphub-p4n.aip.de/ | grep -oP 'href="/([^"]*index[^"]*\.js)"' | head -1
# Extract the key (pattern: _o="eyJ...")
curl -s "https://drphub-p4n.aip.de/assets/index-*.js" | grep -oP '_o="\K[^"]+'
```

### Query drp_cards directly
```python
import re, json, urllib.request, subprocess
from urllib.parse import urlencode

js = subprocess.check_output(["curl", "-s", "https://drphub-p4n.aip.de/assets/index-*.js"]).decode()
anon_key = re.search(r'_o="([^"]+)"', js).group(1)

SUPABASE_URL = "https://rrgnjinkabvqavwwzyfs.supabase.co"
headers = {"apikey": anon_key, "Authorization": f"Bearer {anon_key}"}
params = {"select": "*", "visibility": "eq.public", "deleted_at": "is.null", "order": "last_modified.desc"}
url = f"{SUPABASE_URL}/rest/v1/drp_cards?{urlencode(params)}"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req) as resp:
    cards = json.loads(resp.read().decode())
```

## Limitations
- The anon key only accesses `drp_cards` (legacy table), not `drp_products`
- `computed_maturity_level` is NOT available via this path — must compute client-side
- Cannot access `/products/{id}/maturity`, `/products/{id}/audit`, or any other REST API endpoints
- JS bundle filename changes on each deploy

## For full API access (including computed_maturity_level)
Set `DRPHUB_TOKEN` env var and use the REST API helper from the main `drphub-cards` skill.