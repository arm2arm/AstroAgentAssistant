# templates/sbatch_run_notebook.sh
#!/bin/bash
#SBATCH --job-name=notebook-run
#SBATCH --output=/lustre/<user>/ipython/SH2025/reana/notebook_%j.log
#SBATCH --time=04:00:00
#SBATCH --mem=32G

# Either source conda or call binary directly
# source /opt/.../conda.sh
# conda activate /lustre/<user>/SOFTWARE/conda/sh25

PAPERMILL_BIN="/lustre/<user>/SOFTWARE/conda/sh25/bin/papermill"
IN="/lustre/<user>/ipython/SH2025/reana/sh2026_join.ipynb"
OUT="/lustre/<user>/ipython/SH2025/reana/sh2026_join_pm_${SLURM_JOB_ID}.ipynb"

"$PAPERMILL_BIN" "$IN" "$OUT" -k python3
