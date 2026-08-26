# F0 quality-tier diagnostics (50M gate, 2026-08-22)

Use when characterising a science-ready / “cream-of-the-crop” SH26 sample. The point is to report **named, purpose-dependent tiers**, not one hidden global cut.

## Validated 50M direct-scan recipe

Input: `data/sh26_joined_50m.parq` (50,000,025 rows; older 50M schema contains `sh_outflag_sh21`, not stored current `SH_OUTFLAG`). Use PyArrow batch scanning, not Dask, when simultaneously calculating RUWE thresholds and compact maps.

Required raw columns include:

- convergence and sky: `MISSING,l,b,ruwe`;
- astrometry: `parallax_lindegren2021,parallax_error_fabricius2021`;
- posterior/flag inputs: `nummodels,AV95,dist16,dist50,dist84,AV16,AV50,AV84,teff16,teff50,teff84,logg16,logg84,met16,met84,mass16,mass50,mass84`;
- availability: `SHBOOST,radial_velocity`;
- CMD: Gaia `G,BP,RP` columns.

Derive the current four-digit SH_OUTFLAG with `sh26.flags.sh_outflag` semantics when the stored raw column is unavailable. Do **not** compare it to `sh_outflag_sh21` as an equality requirement: it is a cross-release stability diagnostic only.

RUWE diagnostics must be evaluated on converged rows with finite `l,b,ruwe`:

- `ruweflag`: `ruwe > ruwe_threshold(l,b,crowding=True)`;
- `ruwe2`: `ruwe > ruwe_threshold(l,b,crowding=False)`.

`ruwe2` is a strict superset. It is a potential-unresolved-binary diagnostic, so retain high-RUWE stars for binary/population diagnostics and exclude them only in an explicitly named single-star tier.

## Recommended named ladder

1. `converged`: `MISSING == False`.
2. `posterior_clean`: `converged & SH_OUTFLAG == '0000'`.
3. `astrometry_clean`: `posterior_clean & parallax / parallax_error > 10 & ruwe <= 1.4`.
4. `precision_single_star`: `astrometry_clean & ruwe2 == False & 0.5*(dist84-dist16)/dist50 <= 0.20`.
5. `precision_single_star_shboost`: previous tier plus `SHBOOST == True`; this is an XP/ML-availability tier, not a generic superiority claim.
6. `precision_single_star_6d`: previous tier plus finite radial velocity.

For the validated 50M input, counts were:

| tier | rows | fraction of 40,719,146 converged |
|---|---:|---:|
| posterior_clean | 38,062,612 | 93.48% |
| astrometry_clean | 7,722,461 | 18.97% |
| precision_single_star | 7,335,692 | 18.02% |
| + SHBOOST | 6,740,120 | 16.55% |
| + RV | 2,144,737 | 5.27% |

The distance half-width cut changed the RUWE2-clean count by only 317 after parallax S/N >10 in this sample. Do not generalise this without remeasuring on a different catalogue version.

## Required products and QA

Produce compact HEALPix maps (`nside=64` is adequate for initial QA) with denominators and numerators for: converged, RUWE flag, RUWE2 flag, and the chosen explicit tier. Also produce:

- RUWE distribution and distributions of `RUWE / local threshold`;
- per-digit SH_OUTFLAG rates;
- a dereddened CMD of the precision single-star tier using `photutils.MG0` and `photutils.BPRP0` (temperature-dependent Gaia EDR3 extinction corrections; never a fixed `E(BP-RP)/A_V` ratio).

Programmatic QA: selection counts must be monotonic down the ladder; the RUWE2 rate must be at least the crowding-inclusive RUWE-flag rate; sum of HEALPix denominators must equal the relevant row count. Perform visual QA for nonblank maps, readable colorbars, and no title/colorbar overlaps.

## Sources

- Anders et al. 2022, StarHorse Gaia EDR3: arXiv:2111.01860.
- Khalatyan et al. 2024, SHBoost: A&A 691 A98, doi:10.1051/0004-6361/202451427.
- Castro-Ginard et al. 2024, Gaia DR3 unresolved binaries: A&A 688 A1, doi:10.1051/0004-6361/202450172.
