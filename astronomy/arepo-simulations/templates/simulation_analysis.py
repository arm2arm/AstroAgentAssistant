#!/usr/bin/env python3
"""
simulation_analysis.py — Template for full simulation snapshot analysis

Usage:
    python3 simulation_analysis.py <hdf5_file> <output_dir>

Covers: particle stats, velocity analysis, density analysis, temperature estimation,
        2D projections, and summary statistics output.

Requires: h5py, numpy, matplotlib (in project venv)
"""
import sys
import os
import argparse
import h5py
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# ── Constants ──
MU = 0.6             # mean molecular weight (ionized H+He)
M_P = 1.67262e-24    # proton mass [g]
K_B = 1.38065e-16    # Boltzmann constant [erg/K]
CM_TO_PC = 3.24078e-17
CM_TO_KPC = 3.24078e-20


def compute_temperature(ue, mu=MU):
    """Internal energy (erg/g) → temperature (K) for ideal gas."""
    return (2.0 / 3.0) * ue * mu * M_P / K_B


def inspect_hdf5_file(filepath):
    """Inspect and analyze a snapshot file."""
    print(f"Analyzing: {filepath}")
    print(f"Size: {os.path.getsize(filepath):,} bytes")
    
    with h5py.File(filepath, 'r') as f:
        # ── Header ──
        hdr = dict(f['Header'].attrs)
        print(f"\n=== HEADER ===")
        for k, v in hdr.items():
            if isinstance(v, np.ndarray):
                print(f"  {k}: {v.tolist()}")
            else:
                print(f"  {k}: {v}")
        
        # ── Particle type summary ──
        print(f"\n=== PARTICLE TYPES ===")
        for ptype_name in ['PartType0', 'PartType1', 'PartType2',
                          'PartType3', 'PartType4', 'PartType5']:
            if ptype_name in f and isinstance(f[ptype_name], h5py.Group):
                datasets = list(f[ptype_name].keys())
                print(f"  {ptype_name}/: {len(datasets)} datasets: {', '.join(datasets)}")
        
        # ── PartType0 analysis ──
        if 'PartType0' not in f:
            print("  No PartType0 found, stopping.")
            return
        
        ptype = f['PartType0']
        n_particles = len(ptype)
        print(f"\n=== PartType0: {n_particles:,} particles ===")
        
        # Coordinates
        coords = ptype['Coordinates'][:]  # Mpc/h
        print(f"\nCoordinates (Mpc/h):")
        print(f"  Min: {coords.min(axis=0)}")
        print(f"  Max: {coords.max(axis=0)}")
        print(f"  Range: {coords.max(axis=0) - coords.min(axis=0)}")
        
        # Velocity
        if 'Velocities' in ptype:
            vel = ptype['Velocities'][:]  # cm/s
            vel_kms = vel * 1e-5  # km/s
            print(f"\nVelocities (km/s):")
            print(f"  Vx: [{vel_kms[:,0].min():.3f}, {vel_kms[:,0].max():.3f}] σ={vel_kms[:,0].std():.3f}")
            print(f"  Vy: [{vel_kms[:,1].min():.3f}, {vel_kms[:,1].max():.3f}] σ={vel_kms[:,1].std():.3f}")
            print(f"  Vz: [{vel_kms[:,2].min():.3f}, {vel_kms[:,2].max():.3f}] σ={vel_kms[:,2].std():.3f}")
            vel_mag = np.sqrt(np.sum(vel_kms**2, axis=1))
            print(f"  |V|: [{vel_mag.min():.3f}, {vel_mag.max():.3f}] median={np.median(vel_mag):.3f}")
        
        # Density
        if 'Density' in ptype:
            dens = ptype['Density'][:]  # g/cm³
            log_dens = np.log10(dens)
            print(f"\nDensity (g/cm³):")
            print(f"  Min: {dens.min():.3e}")
            print(f"  Max: {dens.max():.3e}")
            print(f"  Median: {np.median(dens):.3e}")
            print(f"  log10: μ={np.mean(log_dens):.2f}, σ={np.std(log_dens):.2f}")
        
        # Smoothing length
        if 'Hsml' in ptype:
            hsml = ptype['Hsml'][:]  # cm
            hsml_pc = hsml * CM_TO_PC
            hsml_kpc = hsml * CM_TO_KPC
            print(f"\nSmoothing Length (pc):")
            print(f"  Min: {hsml_pc.min():.4f}")
            print(f"  Max: {hsml_pc.max():.4f}")
            print(f"  Median: {np.median(hsml_pc):.4f}")
        
        # Internal energy → Temperature
        if 'InternalEnergy' in ptype:
            ue = ptype['InternalEnergy'][:]  # erg/g
            T = compute_temperature(ue)
            print(f"\nTemperature (K):")
            print(f"  Min: {T.min():.2e}")
            print(f"  Max: {T.max():.2e}")
            print(f"  Median: {np.median(T):.2e}")
            print(f"  Mean: {np.mean(T):.2e}")
        
        # ── Zoom-in detection ──
        box_size = hdr.get('BoxSize', None)
        if box_size is not None:
            coord_range = coords.max(axis=0) - coords.min(axis=0)
            ratio = box_size / coord_range.max()
            print(f"\n=== BOX vs ZOOM ===")
            print(f"  BoxSize: {box_size} Mpc/h")
            print(f"  Zoom region: ~{coord_range.max() * 1000:.0f} kpc/h")
            print(f"  Zoom ratio: {ratio:.0f}:1")
            if ratio > 100:
                print(f"  *** Zoom-in simulation detected ***")
        
        # ── Generate plots ──
        if os.path.exists(output_dir):
            generate_plots(filepath, coords, vel, dens, ue, T, hdr, output_dir)


def generate_plots(filepath, coords, vel, dens, ue, T, hdr, output_dir):
    """Generate diagnostic plots for the snapshot."""
    # Create figure with subplots
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle(
        f"Snapshot Analysis: {os.path.basename(filepath)}\n"
        f"z={hdr.get('Redshift', 'N/A'):.4f} | "
        f"{len(coords):,} particles | "
        f"Box={hdr.get('BoxSize', 'N/A')} Mpc/h",
        fontsize=14, fontweight='bold', color='white'
    )
    
    log_dens = np.log10(dens)
    
    # 1. X vs Y projection
    ax = axes[0, 0]
    ax.scatter(coords[:, 0] * 1000, coords[:, 1] * 1000,
               c=log_dens, cmap='viridis', s=0.5, alpha=0.6)
    ax.set_xlabel('X (kpc/h)')
    ax.set_ylabel('Y (kpc/h)')
    ax.set_title('X vs Y')
    ax.set_aspect('equal')
    plt.colorbar(ax.collections[0], ax=ax, label='log₁₀(ρ) g/cm³')
    
    # 2. Velocity magnitude distribution
    ax = axes[0, 1]
    if 'Velocities' in list(vel.dtype.names if hasattr(vel.dtype, 'names') else ['']):
        pass  # simplified
    if vel is not None:
        vel_mag = np.sqrt(np.sum(vel[:, :3]**2, axis=1))  # cm/s
        vel_mag_kms = vel_mag * 1e-5
        ax.hist(vel_mag_kms, bins=100, color='skyblue', alpha=0.7, edgecolor='black')
        ax.set_xlabel('|V| (km/s)')
        ax.set_ylabel('Count')
        ax.set_title('Velocity Distribution')
    
    # 3. Density distribution
    ax = axes[0, 2]
    ax.hist(log_dens, bins=100, color='orange', alpha=0.7, edgecolor='black')
    ax.set_xlabel('log₁₀(ρ) g/cm³')
    ax.set_ylabel('Count')
    ax.set_title('Density Distribution')
    ax.axvline(np.mean(log_dens), color='red', linestyle='--', alpha=0.5)
    
    # 4. Temperature distribution
    ax = axes[1, 0]
    ax.hist(T, bins=100, color='purple', alpha=0.7, edgecolor='black')
    ax.set_xlabel('Temperature (K)')
    ax.set_ylabel('Count')
    ax.set_title('Temperature Distribution')
    ax.axvline(np.median(T), color='red', linestyle='--', alpha=0.5)
    ax.set_xscale('log')
    
    # 5. X vs Z projection
    ax = axes[1, 1]
    ax.scatter(coords[:, 0] * 1000, coords[:, 2] * 1000,
               c=log_dens, cmap='viridis', s=0.5, alpha=0.6)
    ax.set_xlabel('X (kpc/h)')
    ax.set_ylabel('Z (kpc/h)')
    ax.set_title('X vs Z')
    ax.set_aspect('equal')
    plt.colorbar(ax.collections[0], ax=ax, label='log₁₀(ρ) g/cm³')
    
    # 6. Smoothing length vs density
    if 'Hsml' in list(hsml.dtype.names if hasattr(hsml.dtype, 'names') else ['']):
        pass  # simplified
    ax = axes[1, 2]
    hsml = ptype['Hsml'][:]
    hsml_pc = hsml * CM_TO_PC
    ax.scatter(dens, hsml_pc, c=log_dens, cmap='viridis', s=0.5, alpha=0.6)
    ax.set_xlabel('Density (g/cm³)')
    ax.set_ylabel('Smoothing Length (pc)')
    ax.set_title('Smoothing Length vs Density')
    ax.set_xscale('log')
    ax.set_yscale('log')
    
    plt.tight_layout()
    out_name = os.path.splitext(os.path.basename(filepath))[0] + '_analysis.png'
    out_path = os.path.join(output_dir, out_name)
    fig.savefig(out_path, dpi=150, bbox_inches='tight', facecolor='black')
    print(f"Saved plot: {out_path}")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(
        description='Analyze astrophysical simulation snapshot'
    )
    parser.add_argument('file', help='Path to HDF5 snapshot file')
    parser.add_argument('output_dir', help='Directory for output plots')
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    inspect_hdf5_file(args.file)
    print("\nDone!")


if __name__ == '__main__':
    main()
