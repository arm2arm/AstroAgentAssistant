# Gaia EDR3 Temperature-Dependent Extinction Coefficients

Coefficients from F. Anders (2020-21), inherited from [pysvo](https://github.com/fjaellet/pysvo).
Correspond to Gaia EDR3 transmission curves:
http://svo2.cab.inta-csic.es/theory/fps3/index.php?mode=browse&gname=GAIA&gname2=GAIA3&asttype=

## Usage

For CMD plotting (MG0, BPRP0), pass all four parameters: observed mag, A_V, distance, T_eff.

```python
from starhorse2026.photutils import MG0, BPRP0

mg0 = MG0(G_obs, AV, dist, Teff)      # absolute G magnitude
bprp0 = BPRP0(BP_obs, RP_obs, AV, Teff)  # dereddened BP-RP color
```

## Coefficients

### A_G (Gaia G-band)
2D polynomial: `polyval2d(Teff, AV, coeffs)` where coeff shape is (3,3,3):

```
[[ 7.17833016e-01, -1.88633321e-02,  5.77430628e-04],
 [ 2.84726306e-05, -1.65986478e-06,  3.29897761e-08],
 [-4.70938509e-10,  2.76393659e-11, -5.56454892e-13]]
```
Return: `polyval2d(Teff, AV, coeffs) * AV`

### A_BP (Gaia Blue Photometer)
```
[[ 9.59835295e-01, -1.16380247e-02,  3.50836411e-04],
 [ 1.82122771e-05, -9.17453966e-07,  1.43568978e-08],
 [-2.90443152e-10,  1.41611091e-11, -2.10356011e-13]]
```
Return: `polyval2d(Teff, AV, coeffs) * AV`

### A_RP (Gaia Red Photometer)
```
[[ 5.87378504e-01, -6.37597056e-03,  8.71180628e-05],
 [ 4.71862901e-06, -7.42096958e-09, -4.51905872e-09],
 [-7.99119123e-11,  2.80843682e-13,  7.23076354e-14]]
```
Return: `polyval2d(Teff, AV, coeffs) * AV`

## Implementation

Full Python module at `src/starhorse2026/photutils.py` (copied from original `src/photutils.py`).

Key formulas:
- `MG0 = G_obs - A_G(Teff, A_V) - (5 * log10(dist) + 10)`
- `BPRP0 = (BP_obs - A_BP) - (RP_obs - A_RP)`
- Filters `RP < -5` or `BP < -5` as NaN

## Why Not Flat A_V?

A flat `E(BP-RP)/A_V = 1.33` or `A_G/A_V = 2.5` approximation does NOT capture the
temperature dependence of extinction in Gaia bands. This is especially important for:
- Hot stars (Teff > 7000K): A_G/A_V differs significantly from 2.5
- Cool stars (Teff < 4000K): A_BP and A_RP respond differently to A_V
- CMD main sequence turn-off: flat correction smears the turn-off region
- Red clump identification: flat correction shifts positions, causing misidentification

The polynomial coefficients account for wavelength-dependent extinction across the full
Gaia passband, which varies with stellar temperature.
