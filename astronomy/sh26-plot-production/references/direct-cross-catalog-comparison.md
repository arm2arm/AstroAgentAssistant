# Direct cross-catalog comparison figures

For requests of the form “catalog A − catalog B for ALL and two sub-populations”, make the population structure explicit: use columns `ALL`, `subset=True`, and `subset=False`, not only overlaid curves.

For paired stellar parameters, use SH21 on x versus SH26 on y with a 1:1 line. Annotate every panel with pairwise N, median Delta, unscaled MAD, RMS, and central 68% interval. Keep the full converged inner-box N separate from finite-pair N; state that non-finite pairs are excluded per parameter in both subtitle and JSON sidecar. If display limits use quantiles, state the quantiles while computing statistics on all finite pairs.

A marginal/distribution-only layout is supplementary and must not replace the explicit ALL paired comparison. For dense 5×3 grids, reserve header space, use single-line column headers, and visually QA the full-catalog page. Every requested parameter row and all three population columns must repeat N and statistics without relying on a remote legend.

## P103 application

The improved P103 uses a 5×3 direct paired SH21/SH26 hexbin grid for d, Av, Teff, log g, and metallicity. Full-catalog QA verified base N=27,508,904, with SHBOOST=True=17,465,111 and SHBOOST=False=10,043,793. Pairwise N is reported separately because finite SH21/SH26 availability is parameter-dependent.
