#!/bin/bash
#SBATCH --partition=debug
#SBATCH --job-name=papermill-safer-validate
#SBATCH --output=${WORKDIR:-$HOME}/logs/papermill-safer-validate-%j.out
#SBATCH --error=${WORKDIR:-$HOME}/logs/papermill-safer-validate-%j.err
#SBATCH --time=02:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=128G

# Minimal environment sanity checks
set -euo pipefail
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1

# Ensure modules are available in non-interactive shells
if [ -f /etc/profile.d/modules.sh ]; then
  source /etc/profile.d/modules.sh || true
fi

# User-configurable working directory; default to $HOME if unset
WORKDIR=${WORKDIR:-$HOME}
mkdir -p "$WORKDIR/logs"

# Log runtime info
echo "Job: $SLURM_JOB_NAME, ID: $SLURM_JOB_ID" > "$WORKDIR/logs/papermill_runtime_$SLURM_JOB_ID.log"
echo "Host: $(hostname)" >> "$WORKDIR/logs/papermill_runtime_$SLURM_JOB_ID.log"
echo "Allocated nodes: $SLURM_JOB_NODELIST" >> "$WORKDIR/logs/papermill_runtime_$SLURM_JOB_ID.log"

echo "Environment (python): $(python3 --version 2>&1)" >> "$WORKDIR/logs/papermill_runtime_$SLURM_JOB_ID.log"

echo "DASK_SCHEDULER_ADDRESS=${DASK_SCHEDULER_ADDRESS:-unset}" >> "$WORKDIR/logs/papermill_runtime_$SLURM_JOB_ID.log"

# Verify Dask scheduler reachability (skip if unset)
if [ -n "${DASK_SCHEDULER_ADDRESS:-}" ]; then
  echo "Checking Dask scheduler connectivity..." >> "$WORKDIR/logs/papermill_runtime_$SLURM_JOB_ID.log"
  python3 - <<PYCHECK >> "$WORKDIR/logs/papermill_runtime_$SLURM_JOB_ID.log" 2>&1 || true
import socket,sys
addr='${DASK_SCHEDULER_ADDRESS}'
try:
    host=addr.split('://')[-1].split(':')[0]
    port=int(addr.split(':')[-1])
    s=socket.create_connection((host,port),timeout=5)
    s.close()
    print('Dask scheduler reachable')
except Exception as e:
    print('Dask scheduler NOT reachable:', e)
    # Do not fail here; leave diagnostic info in the log for postmortem
PYCHECK
fi

# Move to project dir if set inside script
cd /lustre/<user>/ipython/SH2025/reana

# Run papermill with explicit kernel
python3 -m papermill \
  sh2026_join_out.safer.ipynb \
  sh2026_join_out.safer.executed.ipynb \
  -k python3
