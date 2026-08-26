# RAVE DR6 TAP Reference

## Verified Working Query Pattern

```bash
curl -s -X POST 'https://www.rave-survey.org/tap/sync' \
  -d 'LANG=ADQL&QUERY=SELECT TOP 100 source_id,ra,dec,l,b,parallax,parallax_over_error,phot_g_mean_mag,bp_rp FROM ravedr6.dr6_x_gaiaedr3 WHERE parallax > 0 ORDER BY parallax DESC&FORMAT=votable' \
  -o result.xml
```

Then parse:
```python
from astropy.io import votable
tbl = votable.parse('result.xml').table
df = tbl.to_pandas()
```

## RAVE DR6 TAP Tables (verified 2026-05-04)

### Primary Gaia Cross-match Tables

| Table | Description | Key Columns |
|-------|-------------|-------------|
| `ravedr6.dr6_x_gaiaedr3` | RAVE DR6 × Gaia EDR3 | source_id, ra, dec, l, b, parallax, parallax_over_error, phot_g_mean_mag, bp_rp |
| `ravedr6.dr6_x_gaiadr2` | RAVE DR6 × Gaia DR2 | Similar but DR2 columns |
| `ravedr6.dr6_xmatch` | General cross-match | Varies |

### Spectroscopic Data

| Table | Description |
|-------|-------------|
| `ravedr6.dr6_sparv` | Spectroscopic parameters (Teff, log g, [Fe/H], RV) |
| `ravedr6.dr6_spectra` | RAVE spectra |
| `ravedr6.dr6_cnn` | CNN-derived parameters |
| `ravedr6.dr6_seismic` | Seismic parameters |

### Auxiliary Tables

| Table | Description |
|-------|-------------|
| `ravedr6.dr6_sparv_aux` | Auxiliary spectroscopic data |
| `ravedr6.dr6_obsdata` | Observation metadata (obs_start_date, etc.) |
| `ravedr6.dr6_classification` | Spectral classification |
| `ravedr6.dr6_madera` | MADERA pipeline results |
| `ravedr6.dr6_irfm` | IRFM parameters |
| `ravedr6.dr6_bdasp` | BDA pipeline results |
| `ravedr6.dr6_gauguin_madera` | Gauguin+MADERA |
| `ravedr6.dr6_gauguin_bdasp` | Gauguin+BDA |
| `ravedr6.dr6_cdr_madera` | CDR+MADERA |
| `ravedr6.dr6_cdr_bdasp` | CDR+BDA |
| `ravedr6.dr6_repeats` | Repeat observations |
| `ravedr6.dr6_fields` | Survey fields |

### Derived Products

| Table | Description |
|-------|-------------|
| `ravedr6.dr6_edr3_orbits` | EDR3 orbits |
| `ravedr6.dr6_orbits` | DR6 orbits |

### RAVE DR6 Contributions

| Table | Description |
|-------|-------------|
| `ravedr6_contrib.ratio_ofe_dwarfs` | Alpha-to-Fe ratios in dwarfs |

## TAP Service Metadata

- **Endpoint**: `https://www.rave-survey.org/tap/`
- **DataLink**: `https://www.rave-survey.org/datalink/links`
- **TAP Schema**: `https://www.rave-survey.org/tap/schemas/`
- **TAP Tables**: `https://www.rave-survey.org/tap/tables/`

## Common Pitfalls

1. **Missing `LANG=ADQL`** → returns error "LANG: This field is required."
2. **Wrong table names** → `gaiadr3.gaia_source` does NOT exist in RAVE schema. Use `ravedr6.dr6_x_gaiaedr3`.
3. **No LIMIT/OFFSET** → TAP uses `TOP N`. For ranked data (e.g., ranks 101–200), query TOP 200 and slice in Python.
4. **Southern bias** → RAVE covers Dec > ~−35°, with some coverage up to Dec ≈ +40°. Always mention this bias.
5. **Column verification** → Use `curl ... &FORMAT=votable` and inspect `<FIELD name="...">` tags before writing queries.
