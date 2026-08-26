# Dask LocalCluster template

Use this template for single-node Dask runs inside SBATCH allocations.

#!/bin/bash
#SBATCH --job-name=dask_local
#SBATCH --nodes=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=120G

module load anaconda
source activate myenv
python run_dask_local.py
