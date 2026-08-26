# SH26 Mollweide QA and refinement notes

- Use Galactic `l` wrapped to [-180,180), `l=0°` centered; mark GC/anti-GC and state orientation/seam.
- Render masked/no-data cells grey; use `min_n=50` for 512×256 per-cell medians and record it in sidecars.
- `LogNorm` is for positive counts only; median extinction uses linear normalization.
- `np.isfinite` alone is insufficient. Apply physical ranges before residuals: distance (0,100) kpc, A_V (-1,20) mag, Teff (2500,50000) K, logg (-1,6), [M/H] (-3,1), mass (0,20) solar masses.
- Record `Δ=SH26-reference`; BJ21 `r_med_geo_bj21` is pc and must be scaled by 0.001 to kpc.
- Do not rebuild the canonical PDF from `paper/figures/` alone when separately appended pages (P103–P106) exist; replace intended page indices in the committed bundle and audit page count and labels.
