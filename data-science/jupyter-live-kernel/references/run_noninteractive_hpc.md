Notes from 2026-05-23 Newton session

Problem observed
- Attempted to run a notebook non-interactively via jupyter nbconvert in user's conda env.
- nbconvert started but produced only the initial "Converting notebook" line in the log. Output notebook was not written.

Root causes & diagnostics
- Common causes: kernel startup failure, long-running/hanging cells (e.g. waiting on Dask scheduler), environment mismatch, or PATH differences in non-interactive shells.
- Specific observations from the session:
  - User's ~/.bashrc contains `module` commands that produce "module: command not found" in non-interactive shells. This noise doesn't usually block conda activation, but it can indicate modules/LMOD is unavailable in that shell and leads to confusing logs.
  - Conda env is activated in .bashrc via `conda activate /lustre/<user>/SOFTWARE/conda/sh25`.
  - Running `jupyter nbconvert` from an SSH non-interactive shell may pick up a different PATH (agent venv) unless ~/.bashrc is sourced explicitly.
  - The notebook starts by creating a Dask client to tcp://141.33.4.144:8786; if no workers/scheduler are responsive this can hang.

Recommended checks before batch runs
1. Confirm kernel python and jupyter executable explicitly (avoid relying on interactive ~/.bashrc default):
   /lustre/<user>/SOFTWARE/conda/sh25/bin/python --version
   /lustre/<user>/SOFTWARE/conda/sh25/bin/jupyter --version

2. Run a single-cell dry-run to confirm kernel startup:
   # execute only first cell via nbconvert (use --to notebook and tag the cell or create a scratch notebook with only the cell)

3. Increase verbosity/logging when diagnosing:
   jupyter nbconvert --to notebook --execute in.ipynb --output out.ipynb --ExecutePreprocessor.timeout=36000 --ExecutePreprocessor.kernel_name=python3 --debug
   or use papermill which often surfaces clearer exit codes/tracebacks.

4. Guard Dask client connections in the notebook for non-interactive use: try except around Client(...), fall back to LocalCluster (see templates/fallback_dask_cell.py).

5. In SLURM/cron/ssh scripts, prefer invoking the env-binary directly instead of relying on interactive activation:
   /lustre/<user>/SOFTWARE/conda/sh25/bin/jupyter nbconvert --to notebook --execute ...

6. Capture logs and write them to workspace (use tee) so logs survive job exit. Always write output notebook with a timestamped filename.

Files added
- templates/fallback_dask_cell.py: code snippet to add to the top of notebooks to make them safe for batch runs.
- scripts/run_notebook_noninteractive.sh: tested wrapper script for ssh/sbatch runs (calls jupyter/papermill from explicit env paths and writes logs).

When to edit notebooks
- If the notebook relies on external services (Dask scheduler), either ensure those services are running in the job context, or modify the notebook to create its own workers (LocalCluster or jobqueue) for reproducible batch runs.

Authors note
- Do not save transient error messages as permanent 'tool broken' claims. The correct durable lesson is: always run batch jobs using explicit interpreter/executable paths, capture logs, and guard external service connections.
