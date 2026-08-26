Session notes: running notebooks non-interactively on Newton

Observed problems in session:
- Using nested SSH -c one-liners with embedded variable expansion caused empty
  path variables to be passed to papermill/nbconvert in some runs. The tool
  received '' as the input notebook path which triggered nbformat.NotJSONError.
- .bashrc contains interactive `module` calls which print `module: command not
  found` in non-interactive shells; these are noisy and can interfere with
  parsing wrappers. Prefer calling the conda env binary directly.
- Papermill is installed in the conda env at /lustre/<user>/SOFTWARE/conda/sh25
  (version 2.7.0 in this session). Jupyter binary exists too.

Robust templates (copy and edit)

1) Minimal direct papermill command (one-liner you can paste into scripts):

/lustre/<user>/SOFTWARE/conda/sh25/bin/papermill \
  '/lustre/<user>/ipython/SH2025/reana/sh2026_join.ipynb' \
  '/lustre/<user>/ipython/SH2025/reana/sh2026_join_pm_$(date +%Y%m%d_%H%M%S).ipynb' -k python3

2) Minimal wrapper script (safe):

#!/bin/bash
set -euo pipefail
# Call the conda env binary directly; avoid relying on interactive .bashrc
IN='/lustre/<user>/ipython/SH2025/reana/sh2026_join.ipynb'
OUT='/lustre/<user>/ipython/SH2025/reana/sh2026_join_pm_${TS}.ipynb'
LOG='/lustre/<user>/ipython/SH2025/reana/sh2026_join_pm_${TS}.log'
TS=$(date +%Y%m%d_%H%M%S)
/lustre/<user>/SOFTWARE/conda/sh25/bin/papermill "$IN" "$OUT" -k python3 2>&1 | tee -a "$LOG"

3) SLURM sbatch template snippet:

#!/bin/bash
#SBATCH --job-name=notebook-run
#SBATCH --output=/lustre/<user>/ipython/SH2025/reana/notebook_%j.log
#SBATCH --time=04:00:00
#SBATCH --mem=32G

# Either source conda or call binary directly
# source /opt/.../conda.sh
# conda activate /lustre/<user>/SOFTWARE/conda/sh25

/lustre/<user>/SOFTWARE/conda/sh25/bin/papermill \
  '/lustre/<user>/ipython/SH2025/reana/sh2026_join.ipynb' \
  '/lustre/<user>/ipython/SH2025/reana/sh2026_join_pm_${SLURM_JOB_ID}.ipynb' -k python3

Troubleshooting checklist
- If papermill reports NotJSONError: '' -> check that the input path is non-empty and readable (`[ -s "$IN" ]`).
- Capture full logs and check for kernel tracebacks.
- For Dask-connected notebooks, ensure scheduler/workers availability or modify the notebook to fall back to LocalCluster.

Session-specific paths and findings
- Conda env: /lustre/<user>/SOFTWARE/conda/sh25
- Papermill version observed: 2.7.0
- Notebooks seen: sh2026_join.ipynb (43,820 bytes)
- Log files produced: sh2026_join_run_*.log (short logs showed nbconvert starting and then hanging)
