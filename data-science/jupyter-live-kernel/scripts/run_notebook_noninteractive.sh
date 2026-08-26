#!/bin/bash
# run_notebook_noninteractive.sh
# Wrapper to run a notebook non-interactively using an explicit conda env's jupyter.
# Writes timestamped output notebook and a log file in the same directory as the input.

set -euo pipefail
if [ "$#" -lt 1 ]; then
  echo "Usage: $0 /path/to/notebook.ipynb [kernel_name]"
  exit 2
fi
IN="$1"
KERN=${2:-python3}
DIR=$(dirname "$IN")
BASE=$(basename "$IN" .ipynb)
TS=$(date +%Y%m%d_%H%M%S)
OUT="$DIR/${BASE}_run_${TS}.ipynb"
LOG="$DIR/${BASE}_run_${TS}.log"

# Explicit conda env path used by this user in prior sessions
CONDA_ENV_BIN="/lustre/<user>/SOFTWARE/conda/sh25/bin"
JUPYTER_BIN="$CONDA_ENV_BIN/jupyter"
PAPERMILL_BIN="$CONDA_ENV_BIN/papermill"

echo "START: $(date)" > "$LOG"
# Use papermill if available (better error semantics), else nbconvert
if [ -x "$PAPERMILL_BIN" ]; then
  echo "Using papermill" >> "$LOG"
  "$PAPERMILL_BIN" "$IN" "$OUT" -k "$KERN" 2>&1 | tee -a "$LOG"
  RC=${PIPESTATUS[0]}
else
  echo "Using jupyter nbconvert" >> "$LOG"
  "$JUPYTER_BIN" nbconvert --to notebook --execute "$IN" --output "$OUT" --ExecutePreprocessor.timeout=36000 --ExecutePreprocessor.kernel_name="$KERN" 2>&1 | tee -a "$LOG"
  RC=${PIPESTATUS[0]}
fi

echo "EXIT:$RC" | tee -a "$LOG"
echo "DONE: $(date)" >> "$LOG"
echo "OUT_NB:$OUT"
echo "LOG:$LOG"
exit $RC
