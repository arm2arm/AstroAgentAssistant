---
name: astronomical-catalogs
title: Astronomical Catalog Queries — Gaia DR3 and RAVE DR6 via TAP
description: >-
  Unified guide for querying major astronomical catalogs: Gaia DR3 (photometry, astrometry,
  cross-matches) and RAVE DR6 (radial velocities, spectroscopic parameters). Covers TAP
  querying via pyvo/curl, CSV/Parquet caching, CMD/RA-plot visualization, and 3D animations.
author: Hermes Agent
date: 2026-05-07
tags: [astronomy, tap, adql, gaia, rave, catalog, visualization]
category: astronomy
---

# Astronomical Catalog Queries

This umbrella covers querying two major astronomical catalogs available via TAP (ADQL) service:
1. [Gaia DR3](#1-gaia-dr3) — Photometry, astrometry, cross-matches (1.8B sources)
2. [RAVE DR6](#2-rave-dr6) — Radial velocities, spectroscopic parameters (~160k stars)

## Common Patterns (Both Catalogs)

### TAP Query via pyvo
```python
import pyvo
service = pyvo.dal.TAPService('https://<endpoint>/tap/')
query = """
SELECT TOP 100 source_id, ra, dec, l, b, parallax, phot_g_mean_mag, bp_rp
FROM <catalog>.<table>
WHERE parallax > 0
ORDER BY parallax DESC
"""
result = service.run_sync(query)
```

### TAP Query via curl + VOTable parsing
```bash
curl -s -X POST 'https://<endpoint>/tap/sync' \
  -d 'LANG=ADQL&QUERY=SELECT TOP 100 * FROM <table> WHERE parallax > 0 ORDER BY parallax DESC&FORMAT=votable' \
  -o result.xml
```

### VOTable parsing (two methods)
```python
# Method 1: astropy
from astropy.io import votable
df = votable.parse_single_table('result.xml').to_pandas()

# Method 2: namespace-aware ElementTree (if astropy fails)
from xml.etree import ElementTree as ET
def parse_votable(xml_path):
    tree = ET.parse(xml_path); root = tree.getroot()
    ns = '{http://www.ivoa.net/xml/VOTable/v1.3}'
    fields = root.findall(f'.//{ns}RESOURCE/{ns}TABLE/{ns}FIELD')
    names = [f.get('name') for f in fields]
    trs = root.findall(f'.//{ns}TABLEDATA/{ns}TR')
    if not trs: trs = root.findall('.//TABLEDATA/TR')
    rows = []
    for tr in trs:
        tds = tr.findall(f'.//{ns}TD')
        if not tds: tds = tr.findall('.//TD')
        row = {}
        for i, td in enumerate(tds):
            if i < len(names): row[names[i]] = (td.text or '').strip()
        rows.append(row)
    return pd.DataFrame(rows)
```

### Caching to Parquet
```python
parquet_path = '/home/hermes/<catalog>_data.parquet'
df.to_parquet(parquet_path, index=False)
df.head(20).to_csv('/home/hermes/<catalog>_preview.csv', index=False)
```

### Plotting: RA vs Dec
```python
import matplotlib.pyplot as plt
plt.figure(figsize=(12, 5))
sc = plt.scatter(df['ra'], df['dec'], c=df['parallax'], cmap='plasma', s=60,
                 edgecolors='white', linewidths=0.4)
plt.xlabel('RA [deg]'); plt.ylabel('Dec [deg]')
plt.colorbar(sc, label='Parallax [mas]')
plt.savefig('<catalog>_ra_dec.png', dpi=180)
```

### Plotting: Galactic XY Projection
```python
import numpy as np
l_rad = np.radians(df['l'].values)
b_rad = np.radians(df['b'].values)
xgal = np.cos(b_rad) * np.cos(l_rad)
ygal = np.cos(b_rad) * np.sin(l_rad)
plt.figure(figsize=(8, 7))
plt.scatter(xgal, ygal, c=df['parallax'], cmap='plasma', s=70)
plt.scatter(0, 0, c='gold', s=300, marker='o', edgecolors='orange')
plt.annotate('Sun', xy=(0, 0), xytext=(0.07, 0.07), color='darkorange')
plt.xlabel('xgal = cos(b) cos(l)'); plt.ylabel('ygal = cos(b) sin(l)')
plt.axis('equal'); plt.xlim(-1.1, 1.1); plt.ylim(-1.1, 1.1)
plt.savefig('<catalog>_xy.png', dpi=180)
```

### CMD Plotting (Colour-Magnitude Diagram)
```python
import seaborn as sns
sns.hexbin(x=df['bprp0'], y=df['mg0'], gridsize=512, cmap='viridis',
           mincnt=1, linewidths=0.2, reduce_C_function='count')
plt.gca().invert_yaxis()
plt.xlabel('bprp0'); plt.ylabel('mg0')
plt.title('<catalog> CMD')
plt.savefig('<catalog>_cmd.png', dpi=300)
```

---

## 1. Gaia DR3

### TAP Service
```
https://gaia.aip.de/tap/
```

### Basic Query
```python
import pyvo
service = pyvo.dal.TAPService('https://gaia.aip.de/tap/')
query = """
SELECT TOP 100 source_id, ra, dec, l, b, parallax, phot_g_mean_mag, bp_rp
FROM gaiadr3.gaia_source
WHERE parallax > 0
ORDER BY parallax DESC
"""
result = service.run_sync(query)
```

### PostgreSQL REST API via Daiquiri
```bash
# 1. Get CSRF token + session cookie
curl -s -c /tmp/gaia_cookies.txt "https://gaia.aip.de/query//sql/" > /dev/null
CSRF=$(grep csrftoken /tmp/gaia_cookies.txt | awk '{print $7}')

# 2. Submit async query job
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

### Key TAP Pitfalls
- **Use `TOP N` not `LIMIT N`** — AIP service doesn't support LIMIT
- **Filter `WHERE parallax > 0`** for valid distances
- **Keep queries modest** (TOP 100) to avoid timeouts
- **AIP endpoint works reliably** when NOT in DR4 migration; ESA endpoint often rejects queries

### PostgreSQL REST API Key Findings
- **API base**: `https://gaia.aip.de/query/api/jobs/`
- **Query language**: `postgresql` (not `adql`)
- **Queue names**: `"5m"`, `"2h"`, or omit for default (30s, times out)
- **CSRF**: Extract from cookie jar, send via `X-CSRFToken`
- **Required headers**: `X-Requested-With: XMLHttpRequest`, `Referer`
- **TAP endpoints** (`/query/tap/...`) return HTML, not JSON — do NOT use
- **Default 30s queue** times out on COUNT queries → use `"5m"`

### Gaia Column Names
See `references/gaia-column-names.md` for correct column name conventions.

### DR4 Migration — AIP Services Currently Down
As of 2026-05, Gaia@AIP is undergoing migration to DR4. The TAP endpoint (`/tap/`) and PostgreSQL REST API (`/query/api/jobs/`) may return **403/404 or silently return 0 rows**.

**Diagnostic:** If the AIP endpoint returns 403/404, or if a simple `SELECT 1` returns 0 rows → the service is down.

**Fallback strategy:**
1. Try the **ESA Gaia Archive** directly via `astroquery.gaia.Gaia`
2. For cluster CMDs without Gaia, use synthetic photometry from published isochrones (Padova, BaSTI, Dartmouth)

---

## 2. RAVE DR6

### TAP Service
```
https://www.rave-survey.org/tap/
```
Main table for Gaia cross-match: `ravedr6.dr6_x_gaiaedr3`

### Basic Query
```bash
curl -s -X POST 'https://www.rave-survey.org/tap/sync' \
  -d 'LANG=ADQL&QUERY=SELECT TOP 100 source_id,ra,dec,l,b,parallax,phot_g_mean_mag,bp_rp FROM ravedr6.dr6_x_gaiaedr3 WHERE parallax > 0 ORDER BY parallax DESC&FORMAT=votable' \
  -o result.xml
```

### Key Tables
| Table | Description |
|-------|-------------|
| `ravedr6.dr6_x_gaiaedr3` | RAVE DR6 stars × Gaia EDR3 cross-match (RA, Dec, parallax, G mag, BP-RP) |
| `ravedr6.dr6_sparv` | Spectroscopic parameters (Teff, log g, [Fe/H], RV) |
| `ravedr6.dr6_orbits` | Orbital parameters |

### Key Queries
| Query | Purpose |
|-------|---------|
| `TOP 100 ... ORDER BY parallax DESC` | Nearest stars |
| `ORDER BY obs_start_date DESC` | Recent observations |
| `WHERE phot_g_mean_mag < 14` | Bright stars |
| `WHERE pm > 50` | High proper motion |

### CRITICAL POST Format
- **POST must include `LANG=ADQL`** — omitting it returns `LANG: This field is required.`
- **Use RAVE tables, NOT Gaia tables** — querying `gaiadr3.gaia_source` returns `Schema gaiadr3 not found.`
- **Correct endpoint: `https://www.rave-survey.org/tap/`** — the `www.rave-aip.de` host DNS-resolves to NXDOMAIN permanently.

### Ranked Data: Use TOP N + pandas slicing
TAP doesn't support LIMIT/OFFSET. To get ranks N–M:
```python
df_M = result_to_pandas()
df_N_to_M = df_M.iloc[N:M].reset_index(drop=True)
```

### RAVE Survey Coverage Bias
RAVE is a **southern-hemisphere survey** (Declination > ~−35° for most of the sky, with some coverage up to Dec ≈ +40° near the Galactic plane). Any plot of RAVE data will show strong southern declination bias. Always mention this when presenting RAVE results.

### RAVE nearest-100 plotting smoke test
See `references/rave-dr6-nearest100-plot.md` for a complete, REANA-tested pattern for querying `ravedr6.dr6_x_gaiaedr3`, keeping the nearest 100 finite rows after a TOP 150 candidate query, producing a clean multi-panel summary plot, and verifying outputs/provenance.

### Required Columns for CMD Plot
- `bprp0` — colour index (x-axis)
- `mg0` — G magnitude (y-axis, inverted)

### Large Queries
Keep `TOP` modest (e.g., 100–500) to avoid timeout. RAVE DR6 has ~160k sources.

### Network/SSL Workarounds
See `references/tap-network-workarounds.md` for SSL and connection workaround patterns.

### Stellar Parameter Estimation Landscape
See `references/gaia-stellar-parameter-methods.md` for a guide to methods (GSP-Spec, StarHorse, SHBoost, Bailer-Jones, BPASS forward modeling) and writing notes for academic introductions.

### Citation Verification Workflow
When verifying or adding citations for Gaia-related papers, **always use the NASA ADS web interface** as the primary source:
1. **Primary**: `https://ui.adsabs.harvard.edu/abs/<bibcode>/abstract` — ADS abstract pages are authoritative and include full author lists, correct page numbers, and DOIs.
2. **Secondary**: CrossRef API (`https://api.crossref.org/works/<DOI>`) for DOI → metadata lookup when the bibcode is unknown.
3. **arXiv API** (`https://export.arxiv.org/api/query?id_list=<arxiv_id>`) only for arXiv-specific metadata, NOT for published paper details (arXiv entries may lack journal refs, volume, page numbers).

**Pitfalls:**
- **NASA ADS is a JS SPA** — the `/api/search` endpoint returns `202 Accepted` (async) not results. Direct ADS abstract page scraping (via browser) times out. Use the `web_extract` tool on ADS abstract pages when needed, but be prepared for failures.
- **CrossRef is not authoritative for astronomy** — CrossRef often returns papers by different authors when searching author names (e.g., "Maiz-Apellaniz" vs "Maiz Apellániz"). Always cross-check with ADS.
- **Author name variations are common** — Accented characters (é, í, á), spacing (Maiz-Apellániz vs Maiz Apellániz vs Maíz-Apellániz), and consortium papers ("Gaia Collaboration" as primary author) cause major lookup failures. Use the published bibcode when possible.
- **arXiv IDs are NOT paper IDs** — A paper may be on arXiv under one ID but published under a different bibcode in ADS. Always verify the final published version.

**DOI Mismatch Pitfalls (Critical):**
A DOI can resolve to a **completely unrelated paper** — the title in a `.bib` file does NOT guarantee the DOI points to the right paper. Always verify the DOI via CrossRef *before* trusting it.

Verified examples from 2026-05:
| DOI | What it actually resolves to | What was expected |
|-----|------------------------------|-------------------|
| `10.1093/mnras/stad1766` | Bischoff — comet 67P dust/gas (MNRAS 523, 5171) | Supposed to be Maiz-Apellániz BP/RP paper |
| `10.1093/mnras/stad1941` | Zhang, Green & Rix — "220M stars from Gaia BP/RP" | Correct paper for that title |
| `10.1051/0004-6361/202451479` | Temmer — coronal mass ejecta (A&A 695, A58) | Supposed to be Khalatyan SHBoost |
| `10.1051/0004-6361/202451427` | Khalatyan et al. — SHBoost (A&A 691, A98) | Correct paper |

**Rule:** When fixing a broken citation, never trust a DOI blindly. Look up the DOI on CrossRef first, then cross-check with ADS. If the CrossRef result doesn't match the paper you want, the DOI is wrong — find the correct one via ADS bibcode or arXiv search.

**BibTeX key naming convention:** Use `FirstAuthorYear` (e.g., `Zhang2023`, `Anders19`, `Khalatyan24`). Avoid names that are hard to type or search (e.g., `MaizApellaniz2022`). When an entry was misattributed, fix the key too.

**Terminal vs Sandbox API calls:** When looking up DOI metadata, the Python sandbox's `subprocess.run` with `curl` can fail (`TypeError: expected str, bytes or os.PathLike object, not int`). Use the terminal directly for `curl` commands, or use `requests` in the Python sandbox instead.

---

## 3. 3D Animation & Public Talks

### 3D Animation Pipeline
1. Query catalog via TAP
2. Convert to pandas, cache as Parquet
3. Generate frames with varying perspective/depth
4. Render to MP4/GIF using Manim or matplotlib.animation

### Public Talk Visualizations
Create high-impact PNG visualizations:
- Large typography
- High contrast colours
- Clear labels and annotations
- Publication-quality DPI (≥300)

---

## 4. Quick Reference

| Catalog | TAP Endpoint | Main Table | Source Count |
|---------|-------------|------------|--------------|
| Gaia DR3 | `gaia.aip.de/tap/` | `gaiadr3.gaia_source` | 1.8B |
| RAVE DR6 | `www.rave-survey.org/tap/` | `ravedr6.dr6_x_gaiaedr3` | ~160k |

### Common Commands
```python
# Convert TAP result to pandas
df = result.to_table().to_pandas()

# Cache to Parquet
df.to_parquet('catalog_data.parquet', index=False)

# Plot RA-Dec
plt.scatter(df['ra'], df['dec'], c=df['parallax'], cmap='plasma', s=60)

# Plot CMD
sns.hexbin(x=df['bprp0'], y=df['mg0'], gridsize=512, cmap='viridis', mincnt=1)
plt.gca().invert_yaxis()
```