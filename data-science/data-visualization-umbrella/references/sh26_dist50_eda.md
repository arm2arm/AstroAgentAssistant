# SH26 dist50 EDA (session notes)

This reference contains the session-specific notes used by the `data-visualization-umbrella` skill for the SH26 dist50 exploratory data analysis performed on 2026-06-13.

Locations
- Data cache (example): /home/hermes/projects/SH26/data/sh26_cache_200k.parq/
- Image output dir (convention): /home/hermes/projects/SH26/img/

Column discovery
- Look for columns with keywords: dist50, dist50_sh21, parallax, phot_g, teff50, logg50, met50.
- If dist5 requested but absent, default to dist50 and explicitly record the substitution in outputs.

Quick commands
- Load sample: pd.read_parquet('/home/hermes/projects/SH26/data/sh26_cache_200k.parq/part.0.parquet')
- Read whole dataset: pd.read_parquet('/home/hermes/projects/SH26/data/sh26_cache_200k.parq/')

Plot filenames used by the EDA scripts
- dist50_histograms.png
- dist50_sh26_vs_sh21_full.png
- dist50_inner_dist50lt6_sh26_vs_sh21.png
- residual_vs_distance_binned.png
- residual_vs_gmag_binned.png
- residual_vs_parallax_snr.png
- dist50_vs_parallax_distance.png
- sky_abs_resid_dist50.png
- cdf_abs_residuals.png
- binned_bias_vs_distance.csv

Notes
- Use Matplotlib colormaps available across environments (magma, inferno, viridis). Avoid non-standard aliases like 'mako'.
- Parallax inversion is naive; for robust comparisons use Bailer-Jones or a Bayesian prior-based approach.
- Save figures with dpi=150 and include a small stats textbox with median bias, std, and N.

