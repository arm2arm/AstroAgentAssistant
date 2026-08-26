# CMD extinction correction — photutils (F. Anders)

## The problem discovered Aug 2026

A flat extinction ratio like `bprp0 = (bp - rp) - 1.33 * AV` or `mg = g - 5*log10(d) + 5` was used to produce a CMD plot. User said "the CMD is wrong." The resulting plot showed a washed-out sequence with no clean main sequence turn-off or red clump.

**Root cause**: Flat extinction coefficients do not match Gaia bandpasses. The correct approach uses **temperature-dependent 2D polynomials** in (Teff, AV) for each Gaia EDR3 filter: A_G(Teff,AV), A_BP(Teff,AV), A_RP(Teff,AV).

## Correct implementation

```python
# From src/photutils.py — import these functions:
from photutils import MG0, BPRP0

# Dereddened absolute magnitude (TEMPERATURE-DEPENDENT)
df["mg0"]   = MG0(df["phot_g_mean_mag_march2021"], df["AV50"], df["dist50"], df["teff50"])

# Dereddened color index (TEMPERATURE-DEPENDENT)
df["bprp0"] = BPRP0(df["phot_bp_mean_mag"], df["phot_rp_mean_mag"], df["AV50"], df["teff50"])
```

Then use `mg0` and `bprp0` directly in plots — no further correction needed.

## Coefficient source

Coefficients come from [SVO Filter Profile Service](http://svo2.cab.inta-csic.es/theory/fps3/index.php?mode=browse&gname=GAIA&gname2=GAIA3) (F. Anders 2020-21), fitted to Gaia EDR3 transmission curves.

## Session context

Discovered when user said "the CMD is wrong check paper and make a right plot" — the original notebook `src/all_plots.ipynb` already used `photutils.MG0()` and `photutils.BPRP0()`. The new `starhorse2026.plots.plot_cmd()` function was using flat ratios instead. Fix: replaced with photutils imports.

## Column requirements for CMD

| Column | Source | Notes |
|--------|--------|-------|
| `phot_g_mean_mag_march2021` | Gaia DR3 | G-band magnitude |
| `phot_bp_mean_mag` | Gaia DR3 | BP band |
| `phot_rp_mean_mag` | Gaia DR3 | RP band |
| `AV50` | SH26 fit | Median 50th percentile extinction |
| `dist50` | SH26 fit | Distance in kpc |
| `teff50` | SH26 fit | Effective temperature in K (required for temp-dependent correction) |

## CMD plot settings (from original notebook)

```python
mask = (df['bprp0'] > -2) & (df['teff50'] > 2000)
plt.hexbin(df.loc[mask,'bprp0'], df.loc[mask,'mg0'],
           gridsize=200, cmap='Greys', norm=LogNorm(), mincnt=1)
plt.gca().invert_yaxis()
```

- x-range: -2 to 4 (BP-RP)_0
- y-range: inverted, bright at top (default Matplotlib auto-fit is fine)
- gridsize: 200 for production quality
- colormap: Greys
- norm: LogNorm(), mincnt=1
