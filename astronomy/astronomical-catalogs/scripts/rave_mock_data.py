#!/usr/bin/env python3
"""
Generate realistic mock RAVE DR6 / Gaia DR3 data for any rank range by parallax.

Usage:
    python3 scripts/rave_mock_data.py --start 101 --end 200 --output /tmp/rave_mock.csv
    
    # Defaults: ranks 1-100 (nearest 100 stars)
    python3 scripts/rave_mock_data.py

This generates parallax values that approximate the real Gaia DR3 distribution,
with RA/Dec uniformly distributed on the sphere, and realistic column values.
"""
import argparse
import numpy as np
import pandas as pd


def simulate_rave_data(start_rank: int, end_rank: int, seed: int = 42) -> pd.DataFrame:
    """Generate mock data for stars ranked start_rank..end_rank by parallax.
    
    Parallax follows an approximate inverse-distance distribution for a uniform
    stellar density in the solar neighbourhood:
      parallax(r) ≈ 1/r  →  parallax(rank) ∝ 1/rank^(1/3) for uniform density
    But we use a simpler linear interpolation calibrated to Gaia DR3 known values:
      rank 100 → ~0.7 mas, rank 200 → ~0.25 mas, rank 1000 → ~0.08 mas
    """
    n = end_rank - start_rank + 1
    np.random.seed(seed)
    
    # Calibrate parallax range based on rank
    # Gaia DR3 approximate values:
    # rank 10: ~5 mas, rank 50: ~1.5 mas, rank 100: ~0.7 mas
    # rank 200: ~0.25 mas, rank 500: ~0.1 mas, rank 1000: ~0.05 mas
    # Fit: log(parallax) ≈ a - b * log(rank)
    
    # Simple approximation using power-law
    # parallax ≈ k * rank^(-alpha), alpha ≈ 0.33 for uniform density
    # Using known points: rank=100, parallax=0.7 → k = 0.7 * 100^0.33 ≈ 3.1
    k = 3.1
    alpha = 0.33
    
    ranks = np.arange(start_rank, end_rank + 1)
    parallax = k * (ranks ** (-alpha))
    
    # Add small scatter (measurement noise + density variations)
    parallax *= np.random.uniform(0.95, 1.05, n)
    parallax = np.clip(parallax, 0.01, 10.0)  # sanity bounds
    
    # RA/Dec uniformly on sphere
    ra = np.random.uniform(0, 360, n)
    dec = np.degrees(np.arccos(np.random.uniform(-1, 1, n)))
    
    # Galactic coordinates (ICRS → Galactic, ICRS epoch J2000)
    ra_rad = np.radians(ra)
    dec_rad = np.radians(dec)
    x_eq = np.cos(dec_rad) * np.cos(ra_rad)
    y_eq = np.cos(dec_rad) * np.sin(ra_rad)
    z_eq = np.sin(dec_rad)
    x_gal = -0.05485948*x_eq - 0.87343709*y_eq - 0.48383502*z_eq
    y_gal =  0.49410943*x_eq - 0.44482963*y_eq + 0.74698228*z_eq
    z_gal = -0.86766615*x_eq - 0.19807637*y_eq + 0.45598378*z_eq
    l = np.degrees(np.arctan2(y_gal, x_gal)) % 360.0
    b = np.degrees(np.arcsin(np.clip(z_gal, -1, 1)))
    
    # G magnitude: brighter stars (higher parallax) tend to be closer and can be brighter
    # but we don't know absolute magnitudes, so use a rough correlation
    dist_pc = 1000.0 / parallax  # distance in pc
    # Random absolute magnitudes (mix of dwarfs, giants, white dwarfs)
    abs_mag = np.random.normal(5.0, 3.0, n)  # M_G distribution
    # Apparent magnitude: m = M + 5*log10(d/10)
    phot_g_mean_mag = abs_mag + 5.0 * np.log10(dist_pc / 10.0)
    phot_g_mean_mag = np.clip(phot_g_mean_mag, 0, 22)
    
    # BP-RP colour: roughly correlated with G magnitude (bluer stars are brighter)
    # Add scatter for different stellar types
    bp_rp = np.random.uniform(-0.1, 1.5, n)
    
    # Parallax error: closer stars have better measurements
    # sigma_pi/pi ≈ 10-20% for Gaia DR3 typical stars
    plx_err_frac = np.random.uniform(0.01, 0.20, n)
    parallax_over_error = 1.0 / plx_err_frac
    
    df = pd.DataFrame({
        'source_id': [f"Gaia DR3 {i:09d}" for i in range(start_rank, end_rank + 1)],
        'ra': ra,
        'dec': dec,
        'l': l,
        'b': b,
        'parallax': parallax,
        'parallax_over_error': parallax_over_error,
        'phot_g_mean_mag': phot_g_mean_mag,
        'bp_rp': bp_rp,
    })
    
    return df


def main():
    parser = argparse.ArgumentParser(description='Generate mock RAVE/Gaia nearest-star data')
    parser.add_argument('--start', type=int, default=1, help='Start rank (default: 1)')
    parser.add_argument('--end', type=int, default=100, help='End rank (default: 100)')
    parser.add_argument('--seed', type=int, default=42, help='Random seed (default: 42)')
    parser.add_argument('--output', type=str, default='/tmp/rave_mock_data.csv', help='Output CSV path')
    args = parser.parse_args()
    
    df = simulate_rave_data(args.start, args.end, args.seed)
    df.to_csv(args.output, index=False)
    print(f"Generated {len(df)} rows (ranks {args.start}-{args.end})")
    print(f"Parallax range: {df['parallax'].min():.3f} - {df['parallax'].max():.3f} mas")
    print(f"RA range: {df['ra'].min():.1f} - {df['ra'].max():.1f} deg")
    print(f"Dec range: {df['dec'].min():.1f} - {df['dec'].max():.1f} deg")
    print(f"Saved to {args.output}")


if __name__ == '__main__':
    main()
