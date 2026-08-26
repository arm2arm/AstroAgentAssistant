---
name: nasa-ads-citations
description: Guide for verifying and extracting BibTeX metadata from NASA Astrophysics Data System (ADS). Includes verified API endpoints, search strategies, and CrossRef fallback.
---

# NASA ADS Citation Verification

## Purpose
Verify, correct, and extract BibTeX metadata for astronomy/astrophysics papers from NASA ADS, with CrossRef as fallback.

## Workflow

### 1. Know the ADS API Endpoints

| Endpoint | Purpose | Status |
|----------|---------|--------|
| `https://ui.adsabs.harvard.edu/abs/{bibcode}/abstract` | View paper details in browser | Often JS-rendered, may timeout |
| `https://ui.adsabs.harvard.edu/api/search?` | Search API | Returns HTTP 202 (async), not directly usable |
| `https://ui.adsabs.harvard.edu/api/article?bibcode=` | **Best option** for single bibcode lookup | Check if available |
| `https://api.crossref.org/works/{doi}` | **Fallback** — CrossRef DOI lookup | Most reliable, fast |
| `http://export.arxiv.org/api/query?` | arXiv search by query/author/title | Good for arXiv IDs |

### 2. Primary Method: CrossRef DOI Lookup

CrossRef is the most reliable endpoint. Use it to verify:
- Author list
- Journal, volume, pages
- Year of publication
- Title
- arXiv ID (in `arxiv_id` field)

```python
import requests
doi = "10.1051/0004-6361/202451427"
resp = requests.get(f"https://api.crossref.org/works/{doi}")
d = resp.json()['message']
print(f"Pages: {d.get('page','?')}")
print(f"Volume: {d.get('volume','?')}")
print(f"Authors: {[a.get('family') for a in d.get('author',[])]}")
print(f"Year: {d.get('published-print',{}).get('date-parts',[[None]])[0][0]}")
print(f"arXiv: {d.get('link',[])[0].get('URL','?')}")  # if present
```

### 3. Secondary Method: arXiv API

Use when you have the arXiv ID or need to find a paper by author/title:

```python
# Search by arXiv ID
resp = requests.get("http://export.arxiv.org/api/query?id_list=2407.06963")
# Search by author+title
resp = requests.get("http://export.arxiv.org/api/query?search_query=au:Anderson+AND+ti:Gaia&max_results=5")
```

### 4. ADS Search Strategy

When CrossRef/DOI lookups are ambiguous or you need the ADS bibcode:

1. **Known DOI** → CrossRef lookup first (returns journal, volume, pages, authors)
2. **Known author + title keywords** → arXiv API search, then check arXiv page for ADS bibcode reference
3. **Known volume + first page** → Construct potential ADS bibcode (format: `YYYYJournal...Volume...Page`)

ADS bibcode format: `YYYYJournal...Volume...Page`
- `2024A&A...691A..98K` = Year 2024, A&A, Volume 691, Article A98, first author with surname starting K

### 5. Common Pitfalls

- **ADS API is flaky** — direct API calls often time out or return 202 (async). Don't rely on it.
- **CrossRef DOI matching can be wrong** — always verify the title matches the intended paper, not just the DOI format.
- **Author name variations** — ADS and CrossRef may format names differently (e.g., "Maiz-Apellániz" vs "Maiz Apellániz" vs "Maiz-Apellaniz"). Always cross-check the title.
- **Wrong paper in bib entry** — a bib entry can have the correct title but wrong author (as happened with Zhang et al. misattributed to Maiz-Apellániz). Always verify author + title match.
- **Page numbers in A&A** — use `A94`, `A215`, etc. — not numeric pages.
- **Gaia Collaboration papers** — author field should be `{Gaia Collaboration}`, NOT individual names.
- **Consortium/community papers can return garbage authors** — e.g. Galaxy 2022 (10.1093/nar/gkac247) returns a broken leading author (`",  and Afgan, Enis and ..."`, hundreds of names). Use the collective form `{The Galaxy Community}` instead of pasting the raw list.
- **"Website" citations often have a real proceedings paper** — Binder is not `\url{https://mybinder.org}`: it is a SciPy 2018 proceedings paper (doi 10.25080/Majora-4af1f417-011, pages 113–120). Before citing a tool as @misc+URL, check CrossRef/the project docs for a citable paper.

### 5b. Batch verification (shell one-liners)

Fast pattern for verifying many DOIs at once with `curl` + `jq` (no Python needed):

```bash
# Author lists for a batch of DOIs
for doi in 10.1073/pnas.1708290115 10.1126/science.1213847; do
  echo "--- $doi"
  curl -s --max-time 15 "https://api.crossref.org/works/$doi" | \
    jq -r '.message.author | map(.family + ", " + (.given // "")) | join(" and ")'
done

# Full metadata line: DOI || title || journal || vol || issue || pages || year
curl -s "https://api.crossref.org/works/$doi" | jq -r '.message |
  [.DOI, .title[0], (.["container-title"][0] // "?"), (.volume // "?"),
   (.issue // "-"), (.page // "?"), (.issued["date-parts"][0][0]|tostring)] | join(" || ")'
```

### 6. BibTeX Entry Template

```bibtex
@article{citationkey,
  author  = {Author, A. and Coauthor, B.},
  title   = {{T}itle {W}ith {C}aps},
  journal = {Journal},
  year    = {YYYY},
  volume  = {NNN},
  pages   = {PPP},
  doi     = {10.xxxx/xxxxx},
  note    = {ADS: YYYYJournal...Vol...Page; arXiv:xxxx.xxxxx}
}
```

### 7. Verification Checklist

For each reference, verify:
- [ ] Title matches the paper being cited
- [ ] Author list is correct (not just surname)
- [ ] Journal, volume, and pages match ADS/CrossRef
- [ ] DOI resolves to the correct paper
- [ ] ADS bibcode is constructible and valid format
- [ ] arXiv ID is listed in the note

### 8. Author Name Conventions

- Individual authors: `Last, F.` or `Last, F. and Coauthor, A.`
- Gaia Collaboration: always use `{{Gaia Collaboration}}` (double braces for single-name author)
- Names with special characters: use LaTeX escapes (e.g., `Ma{\\'i}z-Apell{\\'a}niz`)
- For natbib with `a` ordering (A&A style), ensure `bibpunct` is set: `\bibpunct{(}{)}{;}{a}{}{,}`

### 9. When All Else Fails

If CrossRef + arXiv both fail:
1. Check the paper's arXiv abstract page (`https://arxiv.org/abs/YYYY.NNNNN`) — ADS bibcode is often listed in the metadata
2. Try the ADS abstract page directly (`https://ui.adsabs.harvard.edu/abs/{potential_bibcode}/abstract`)
3. Search the journal's publisher site for the specific volume/article
4. As a last resort, ask the user for the ADS bibcode directly
