# Gaia DR3 Column Names

**CRITICAL:** Gaia DR3 column names use `_error` suffix for error columns, NOT `_err`.

## Photometry
| Correct | Wrong (won't work) |
|---------|---------------------|
| `phot_g_mean_mag` | `g`, `g_mean`, `phot_g_mean` |
| `phot_bp_mean_mag` | `bp`, `bp_mean`, `phot_bp_mean` |
| `phot_rp_mean_mag` | `rp`, `rp_mean`, `phot_rp_mean` |
| `phot_g_mean_mag_error` | `phot_g_mean_mag_err` |
| `phot_bp_mean_mag_error` | `phot_bp_mean_mag_err` |
| `phot_rp_mean_mag_error` | `phot_rp_mean_mag_err` |

## Astrometry
| Correct | Wrong |
|---------|-------|
| `parallax` | `parallax_mas`, `plx` |
| `parallax_error` | `parallax_err`, `plx_err` |
| `pmra` | `pm_ra`, `pmra_mas` |
| `pmra_error` | `pmra_err` |
| `pmdec` | `pm_dec`, `pmdec_mas` |
| `pmdec_error` | `pmdec_err` |

## Derived
- `bp_rp` is computed as `phot_bp_mean_mag - phot_rp_mean_mag` (not a column)

## Session 2026-05-06
- Querying Berkeley 21 with `_err` suffix caused `Unknown column` errors
- Fixed by using `_error` suffix or omitting error columns entirely
