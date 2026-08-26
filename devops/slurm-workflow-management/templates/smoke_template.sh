#!/bin/bash
#SBATCH --job-name=smoke_test
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:05:00
#SBATCH --output=${WORKDIR}/smoke-%j.out
#SBATCH --error=${WORKDIR}/smoke-%j.err

WORKDIR=${WORKDIR:-/lustre/<user>/hermes}
mkdir -p $WORKDIR

if [ -f /etc/profile.d/modules.sh ]; then
  source /etc/profile.d/modules.sh
fi

cd $WORKDIR

echo "JOBID: $SLURM_JOB_ID"
echo "Host: $(hostname)"
echo "Date: $(date)"
echo "Workdir: $(pwd)"
python -c "import sys; print(sys.executable, sys.version)"
if type module &>/dev/null; then module avail || true; else echo "module command not available in non-interactive shell"; fi

df -h /lustre || true

echo "hello" > $WORKDIR/smoke_test_$SLURM_JOB_ID.txt
ls -l $WORKDIR/smoke_test_$SLURM_JOB_ID.txt || true

echo "DONE"
