# RAVE DR6 nearest-100 stars plotting pattern

## Goal

Generate a small, reproducible, visually legible RAVE DR6 nearest-stars product from the public TAP service. This pattern is useful as a smoke test for TAP access, VOTable parsing, plotting, and REANA execution.

## Query pattern

Use the public TAP sync endpoint:

```text
https://www.rave-survey.org/tap/sync
```

ADQL:

```sql
SELECT TOP 150 source_id, ra, dec, l, b, parallax, phot_g_mean_mag, bp_rp
FROM ravedr6.dr6_x_gaiaedr3
WHERE parallax > 0
  AND ra IS NOT NULL
  AND dec IS NOT NULL
  AND l IS NOT NULL
  AND b IS NOT NULL
  AND phot_g_mean_mag IS NOT NULL
  AND bp_rp IS NOT NULL
ORDER BY parallax DESC
```

Request TOP 150, then keep the nearest 100 finite rows after local validation. A strict TOP 100 query can return fewer than 100 usable rows after finite-value filtering.

## Minimal curl invocation

```bash
curl -fsS -X POST 'https://www.rave-survey.org/tap/sync' \
  -d 'REQUEST=doQuery' \
  -d 'LANG=ADQL' \
  --data-urlencode "QUERY=$QUERY" \
  -d 'FORMAT=votable' \
  -o rave_nearest_candidates.xml
```

RAVE may return VOTable even if another format is requested; parse response content, not the filename extension.

## Parsing without astropy/pyvo

If `pyvo` or `astropy` is unavailable, use namespace-aware `xml.etree.ElementTree` to parse the VOTable. Check:

```python
status = root.find('.//v:INFO[@name="QUERY_STATUS"]', ns)
assert status is not None and status.attrib.get('value') == 'OK'
```

Then read `FIELD/@name` and `TABLEDATA/TR/TD` rows into pandas.

## Plot layout that worked well

Use a white-background, 15x9 inch, 2x3 multi-panel figure:

1. RA/Dec scatter, colored by inverse-parallax distance.
2. Galactic unit-vector projection with Sun marker, colored by Galactic latitude.
3. Distance histogram with median line.
4. CMD-like view: `BP-RP` vs approximate absolute `G`, colored by distance and inverted y-axis.
5. Text summary/caveat panel.

Derived quantities:

```python
df['distance_pc'] = 1000.0 / df['parallax']
df['M_G'] = df['phot_g_mean_mag'] + 5.0 * np.log10(df['parallax']) - 10.0
```

This absolute magnitude estimate is for visualization; mention that it uses simple inverse parallax.

## Expected smoke-test numbers from 2026-06-27

- Rows plotted: 100
- Distance range: 8.216--20.685 pc
- Median distance: 17.317 pc
- RA range: 2.439--359.337 deg
- Dec range: -76.703--2.726 deg

Do not hard-code these values as scientific truth; use them as regression/sanity checks only.

## Required caveat

Always state: RAVE is a southern-hemisphere spectroscopic survey, so the sky footprint is not all-sky complete. This is a RAVE/Gaia cross-match visualization, not a complete nearest-stars census.

## Verification checklist

- TAP response has `QUERY_STATUS=OK`.
- Exactly 100 finite plotted rows after local filtering.
- CSV and Parquet caches are readable.
- PNG is non-empty and visually inspected for label/colorbar overlap.
- Provenance JSON includes endpoint, query file, rows plotted, outputs, and caveats.
- If run on REANA, verify output files download successfully; do not trust `finished` alone.
