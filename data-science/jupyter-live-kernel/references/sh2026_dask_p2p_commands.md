# Dask P2P shuffle diagnostic and mitigations

This file captures the small, re-runnable commands and the sbatch wrapper we used during the session. Keep it in the skill references and update as you discover better defaults.

## Quick tail (avoid .bashrc noise)

ssh arm2arm@newton "bash --norc -c 'tail -n 400 /home/arm2arm/logs/papermill-production-509479.err'"

## Safe scp copy of patched notebook

scp -o BatchMode=yes -o StrictHostKeyChecking=accept-new ./sh2026_join_out.optimized.ipynb arm2arm@newton:/lustre/<user>/ipython/SH2025/reana/sh2026_join_out.optimized.ipynb

## Robust sbatch wrapper (example)

#!/bin/bash
#SBATCH --time=04:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem=128G
#SBATCH --output=/home/arm2arm/logs/papermill-optimized-%j.out
#SBATCH --error=/home/arm2arm/logs/papermill-optimized-%j.err

set -euo pipefail
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
# Use absolute python/papermill to avoid interactive shell issues
/PATH/TO/conda/env/bin/python3 -m papermill \
  /lustre/<user>/ipython/SH2025/reana/sh2026_join_out.optimized.ipynb \
  /lustre/<user>/ipython/SH2025/reana/sh2026_join_out.optimized.executed.$SLURM_JOB_ID.ipynb \
  -k python3
