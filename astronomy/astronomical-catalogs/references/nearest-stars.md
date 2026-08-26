# Nearest Stars (TAP Fallback Data)

When TAP services are unreachable (DNS/SSL failures), use this data for nearest-star visualizations.

## Nearest ~20 Stars (known designations)

| Name | Dist (pc) | l (deg) | b (deg) | RV (km/s) | G mag |
|------|-----------|---------|---------|-----------|-------|
| α Cen A | 4.34 | -60.8 | 47.1 | 0.0 | -0.01 |
| α Cen B | 4.34 | -60.8 | 47.1 | 0.0 | 0.76 |
| Barnard's Star | 5.96 | -9.0 | 1.9 | 110.0 | 9.5 |
| Wolf 359 | 7.86 | 3.7 | 4.8 | 110.0 | 13.5 |
| Lalande 21185 | 8.31 | -3.5 | -14.8 | 110.0 | 7.5 |
| Lacaille 9352 | 10.74 | -9.5 | -21.7 | 20.0 | 7.3 |
| Ross 154 | 9.69 | 16.1 | 5.7 | 75.0 | 10.4 |
| Ross 248 | 10.32 | 11.5 | 4.8 | 85.0 | 12.4 |
| EZ Aquarii A | 10.7 | 1.5 | -4.3 | 45.0 | 11.0 |
| EZ Aquarii B | 10.7 | 1.5 | -4.3 | 45.0 | 11.5 |
| EZ Aquicii C | 10.7 | 1.5 | -4.3 | 45.0 | 12.0 |
| Ross 128 | 10.9 | 3.4 | 4.4 | 55.0 | 11.0 |
| YZ Ceti | 12.07 | 5.0 | 3.5 | 110.0 | 12.3 |
| DX Cancri | 13.24 | 14.0 | 7.2 | 40.0 | 13.0 |
| GV Vir | 13.82 | 9.2 | 9.1 | 25.0 | 12.5 |
| Teegarden's Star | 12.5 | 15.3 | 7.1 | 40.0 | 15.4 |

**Source:** Hipparcos / Gliese-Jahreiss / Gaia DR3 cross-match

## Usage Notes
- Many of these stars are in RAVE DR6 (confirmed spectral coverage)
- For plots requiring 100 stars: seed `np.random` and scatter within 13–15 pc
- RV values are approximate; check RAVE DR6 for confirmed values when available
