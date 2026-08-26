#!/usr/bin/env python3
"""
inspect_hdf5_snapshot.py - Automated HDF5 snapshot structure inspector

Usage:
    python3 inspect_hdf5_snapshot.py <path_to_hdf5_file>

If no file is provided, lists all HDF5 files in current directory.

Requires: h5py (in project venv)
"""
import sys
import os
import argparse
import h5py
import numpy as np


def inspect_hdf5_file(filepath):
    """Inspect a single HDF5 snapshot file."""
    print("=" * 70)
    print(f"FILE: {filepath}")
    print(f"SIZE: {os.path.getsize(filepath):,} bytes")
    print("=" * 70)
    
    try:
        with h5py.File(filepath, 'r') as f:
            # ── Full tree structure ──
            print("\n[STRUCTURE]")
            def print_tree(name, obj):
                indent = '  ' * name.count('/')
                if isinstance(obj, h5py.Group):
                    print(f"{indent}{name}/")
                else:
                    print(f"{indent}{name} [{obj.shape}] {obj.dtype}")
            f.visititems(print_tree)
            
            # ── Header metadata ──
            if 'Header' in f:
                print("\n[HEADER]")
                hdr = dict(f['Header'].attrs)
                for k, v in hdr.items():
                    if isinstance(v, np.ndarray):
                        print(f"  {k}: {v.tolist()}")
                    else:
                        print(f"  {k}: {v}")
            
            # ── Particle type summary ──
            print("\n[PARTICLE TYPES]")
            for grp_name in ['PartType0', 'PartType1', 'PartType2', 
                           'PartType3', 'PartType4', 'PartType5']:
                if grp_name in f and isinstance(f[grp_name], h5py.Group):
                    attrs = dict(f[grp_name].attrs)
                    print(f"\n  {grp_name}/")
                    if attrs:
                        print(f"    Attrs: {attrs}")
                    print(f"    Datasets:")
                    for ds_name in f[grp_name].keys():
                        ds = f[grp_name][ds_name]
                        print(f"      {ds_name}: {ds.shape} {ds.dtype}")
            
            # ── Quick stats for PartType0 ──
            if 'PartType0' in f and isinstance(f['PartType0'], h5py.Group):
                print("\n[PartType0 QUICK STATS]")
                ptype = f['PartType0']
                
                if 'Coordinates' in ptype:
                    coords = ptype['Coordinates'][:]
                    print(f"  Coordinates: min={coords.min(axis=0)}, max={coords.max(axis=0)}")
                    print(f"  Range: {coords.max(axis=0) - coords.min(axis=0)}")
                
                if 'Velocities' in ptype:
                    vel = ptype['Velocities'][:]
                    print(f"  Velocities (cm/s): min={vel.min(axis=0)}, max={vel.max(axis=0)}")
                
                if 'Density' in ptype:
                    dens = ptype['Density'][:]
                    print(f"  Density (g/cm³): min={dens.min():.3e}, max={dens.max():.3e}")
                    print(f"  Median: {np.median(dens):.3e}")
                
                if 'InternalEnergy' in ptype:
                    ue = ptype['InternalEnergy'][:]
                    print(f"  InternalEnergy (erg/g): min={ue.min():.3e}, max={ue.max():.3e}")
                
                print(f"\n  Total particles: {len(ptype)}")
                
                # Check if zoom-in
                if 'Header' in f:
                    hdr = dict(f['Header'].attrs)
                    box_size = hdr.get('BoxSize', None)
                    if box_size is not None and 'Coordinates' in ptype:
                        coords = ptype['Coordinates'][:]
                        coord_range = coords.max(axis=0) - coords.min(axis=0)
                        ratio = box_size / coord_range.max()
                        if ratio > 100:
                            print(f"\n  *** ZOOM-IN DETECTED: {ratio:.0f}:1 ***")
                            print(f"  Zoom region: ~{coord_range.max() * 1000:.0f} kpc/h in {box_size} Mpc/h box")
    
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Inspect HDF5 astrophysical simulation snapshot structure'
    )
    parser.add_argument('files', nargs='*', help='HDF5 files to inspect')
    args = parser.parse_args()
    
    if not args.files:
        # List all .hdf5 files in current directory
        files = sorted([f for f in os.listdir('.') if f.endswith('.hdf5')])
        if not files:
            print("No HDF5 files found in current directory.")
            return
        print(f"Found {len(files)} HDF5 files in current directory.\n")
        for f in files:
            inspect_hdf5_file(f)
    else:
        for filepath in args.files:
            if not os.path.exists(filepath):
                print(f"File not found: {filepath}")
                continue
            inspect_hdf5_file(filepath)


if __name__ == '__main__':
    main()
