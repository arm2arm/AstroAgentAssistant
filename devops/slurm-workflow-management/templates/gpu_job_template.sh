#!/bin/bash
#SBATCH --job-name=template_gpu_job
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --gres=gpu:1
#SBATCH --mem=64G
#SBATCH --time=12:00:00
#SBATCH --output=${WORKDIR}/logs/%x_%j.out

if [ -f /etc/profile.d/modules.sh ]; then
  source /etc/profile.d/modules.sh
fi

WORKDIR=${WORKDIR:-/lustre/<user>/hermes}
mkdir -p $WORKDIR/logs

module purge
module load cuda/12.0

if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
  source "$HOME/miniconda3/etc/profile.d/conda.sh"
  conda activate torch || true
fi

cd $WORKDIR

nvidia-smi
python train.py --epochs 50 --batch-size 128 --out $WORKDIR/model_$SLURM_JOB_ID/
