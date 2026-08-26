#!/bin/bash
#SBATCH --job-name=template_cpu_job
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=04:00:00
#SBATCH --output=${WORKDIR}/logs/%x_%j.out
#SBATCH --error=${WORKDIR}/logs/%x_%j.err

# Ensure modules are available in non-interactive shell
if [ -f /etc/profile.d/modules.sh ]; then
  source /etc/profile.d/modules.sh
fi

# Set project workdir (agent will replace WORKDIR)
WORKDIR=${WORKDIR:-/lustre/<user>/hermes}
mkdir -p $WORKDIR/logs

module purge
module load python/3.11

# Activate conda if needed
if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
  source "$HOME/miniconda3/etc/profile.d/conda.sh"
  conda activate myenv || true
fi

cd $WORKDIR

echo "Starting job on $(hostname) at $(date)"
python run_analysis.py --input $WORKDIR/input.dat --output $WORKDIR/output_$SLURM_JOB_ID.h5
