#!/usr/bin/env python3
"""
scripts/eda_sh26.py
Runnable EDA script for SH26 dist50 quality checks.
Produces the canonical set of plots and a CSV summary in the project's img/ directory.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

DATA_PATH = '/home/hermes/projects/SH26/data/sh26_cache_200k.parq/'
IMG_DIR = '/home/hermes/projects/SH26/img'

os.makedirs(IMG_DIR, exist_ok=True)

# Load data
print('Loading parquet...')
df = pd.read_parquet(DATA_PATH)
print('Rows, cols:', df.shape)

# Column heuristics
cols = list(df.columns)

def find(cols, keywords):
    return [c for c in cols if any(k in c.lower() for k in keywords)]

dist_col = next((c for c in cols if c.lower()=='dist50'), None)
old_col = next((c for c in cols if 'sh21' in c.lower() and 'dist50' in c.lower()), None)
parallax_col = next((c for c in cols if 'parallax' in c.lower()), None)

use_cols = [c for c in [dist_col, old_col, parallax_col] if c]
print('Using columns', use_cols)

# Basic filters
if dist_col is None:
    raise RuntimeError('dist50 column not found')

df = df[df[dist_col].notna() & (df[dist_col]>0) & (df[dist_col]<1000)]

# Compute parallax distance if present
if parallax_col:
    df['d_parallax_kpc'] = np.where(df[parallax_col]>0, 1.0/(df[parallax_col]/1000.0), np.nan)

# 1) dist histograms
plt.figure(figsize=(10,4))
plt.subplot(1,2,1)
plt.hist(df[dist_col].clip(0,50), bins=100, color='C0')
plt.xlabel('dist50 [kpc] (clipped at 50)')
plt.subplot(1,2,2)
plt.hist(df[dist_col][df[dist_col]>0], bins=np.logspace(-2, np.log10(df[dist_col].max()+1), 100), color='C0')
plt.xscale('log')
plt.xlabel('dist50 [kpc] (log)')
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, 'dist50_histograms.png'), dpi=150, bbox_inches='tight')
plt.close()

# ... other plots follow the notebook patterns used in session
print('Script scaffold written; fill with additional plots as needed')
