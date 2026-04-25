---
name: gaiadr3-aip-query-api
category: data-science
description: Query the Gaia DR3 PostgreSQL database at gaia.aip.de via its Daiquiri REST API. Includes CSRF handling, queue names, and result fetching.
triggers:
  - "how many stars in gaiadr3"
  - "query gaia aip database"
  - "gaia.aip.de query"
  - "gaiadr3 count"
---

# Gaia@AIP DR3 Query API

Query the Gaia DR3 PostgreSQL database at `https://gaia.aip.de/` programmatically via its Daiquiri REST API.

## Quick Reference

```bash
# 1. Get CSRF token + session cookie
curl -s -c /tmp/gaia_cookies.txt "https://gaia.aip.de/query//sql/" > /dev/null
CSRF=$(grep csrftoken /tmp/gaia_cookies.txt | awk '{print $7}')

# 2. Submit async query job (POST /query/api/jobs/)
#    Queue names are NOT what the UI shows:
#    - "30 Seconds" -> default (no queue param, times out at 30s)
#    - "5 Minutes"  -> "5m"
#    - "2 Hours"    -> "2h"
curl -s -b /tmp/gaia_cookies.txt -c /tmp/gaia_cookies.txt \
    -X POST \
    -H "Referer: https://gaia.aip.de/query//sql/" \
    -H "Content-Type: application/json" \
    -H "X-CSRFToken: $CSRF" \
    -H "X-Requested-With: XMLHttpRequest" \
    -d '{"query": "SELECT COUNT(*) FROM gaiadr3.gaia_source", "query_language": "postgresql", "queue": "5m"}' \
    "https://gaia.aip.de/query/api/jobs/"

# 3. Poll for completion
JOB_ID="<id_from_step2>"
for i in $(seq 1 20); do
    sleep 5
    PHASE=$(curl -s -b /tmp/gaia_cookies.txt -c /tmp/gaia_cookies.txt \
        -H "Referer: https://gaia.aip.de/query/$JOB_ID/" \
        -H "X-CSRFToken: $CSRF" \
        -H "X-Requested-With: XMLHttpRequest" \
        "https://gaia.aip.de/query/api/jobs/$JOB_ID/" | \
        python3 -c "import sys,json; print(json.load(sys.stdin).get('phase'))")
    echo "[$((i*5))s] Phase: $PHASE"
    [ "$PHASE" = "COMPLETED" ] && break
    [ "$PHASE" = "ERROR" ] && break
done

# 4. Fetch results (JSON)
curl -s -b /tmp/gaia_cookies.txt -c /tmp/gaia_cookies.txt \
    -H "Referer: https://gaia.aip.de/query/$JOB_ID/" \
    -H "X-CSRFToken: $CSRF" \
    -H "X-Requested-With: XMLHttpRequest" \
    "https://gaia.aip.de/query/api/jobs/$JOB_ID/rows/?limit=10&offset=0"
```

## Key Findings

- **API base**: `https://gaia.aip.de/query/api/jobs/`
- **POST**: create job (returns `{"id": "<uuid>", ...}`)
- **GET /{id}/**: job status (phase: QUEUED → EXECUTING → COMPLETED/ERROR)
- **GET /{id}/rows/**: JSON results (fields: `count`, `results`, `next`, `previous`)
- **Query language**: `postgresql` (not `adql` even though UI defaults to ADQL)
- **Queue names**: counterintuitive — `"5m"`, `"2h"`, or omit for default (30s, times out on large queries)
- **CSRF**: extract from cookie jar (`csrftoken` cookie), send via `X-CSRFToken` header
- **Required headers**: `X-Requested-With: XMLHttpRequest`, `Referer: https://gaia.aip.de/query//sql/`
- **TAP endpoints** (`/query/tap/sync/`, `/query/tap/async/`) return HTML, not JSON — do NOT use
- **/query/sync/** returns 405 Method Not Allowed — do NOT use
- **Default 30s queue** times out on COUNT queries over large tables → use `"5m"` queue
- **Table schema**: `gaiadr3.gaia_source` (verified working) — 153 columns
- **Table count**: `gaiadr3.gaia_source` = **1,811,709,771 sources** (as of 2026-04-14)
- **Metadata**: `curl -s "https://gaia.aip.de/metadata/gaiadr3/gaia_source/"` — full column list with types/units/descriptions
- **Column names include**: solution_id, designation, source_id, random_index, ref_epoch, ra, ra_error, dec, dec_error, parallax, parallax_error, parallax_over_error, pm, pmra, pmra_error, pmdec, pmdec_error, 11 astrometric correlation columns, astrometric quality columns, phot_g/rp/bp magnitudes & fluxes & flux errors, radial_velocity, rv_template_teff/logg/fe_h, vbroad, grvs_mag, rvs_spec_sig_to_noise, l, b, ecl_lon, ecl_lat, classprob_dsc_combmod_*, teff/logg/mh_gspphot with *_lower/*_upper, distance_gspphot, azero/ag/ebpminrp_gspphot, in_qso_candidates, in_galaxy_candidates, non_single_star, has_xp_continuous, has_xp_sampled, has_rvs, has_epoch_photometry, has_epoch_rv, has_mcmc_gspphot, has_mcmc_msc, in_andromeda_survey, libname_gspphot, pos

## Example Queries

```sql
-- Count all sources
SELECT COUNT(*) FROM gaiadr3.gaia_source

-- Count with filter
SELECT COUNT(*) FROM gaiadr3.gaia_source WHERE phot_g_mean_mag < 16

-- Sample rows
SELECT * FROM gaiadr3.gaia_source LIMIT 10
```