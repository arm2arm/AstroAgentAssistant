#!/bin/bash
# scripts/run_notebook_papermill.sh
# Small wrapper to run a notebook with papermill using absolute paths.
set -euo pipefail
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 /path/to/in.ipynb /path/to/out.ipynb"
  exit 2
fi
IN="$1"
OUT="$2"
LOG="${OUT%.*}.log"
# Prefer calling the env binary directly; change this path to match your env
PAPERMILL_BIN="/lustre/<user>/SOFTWARE/conda/sh25/bin/papermill"
if [ ! -x "$PAPERMILL_BIN" ]; then
  echo "Papermill binary not found at $PAPERMILL_BIN" >&2
  exit 3
fi
[ -s "$IN" ] || { echo "Input notebook missing or empty: $IN" >&2; exit 4; }
echo "START: $(date)" > "$LOG"
"$PAPERMILL_BIN" "$IN" "$OUT" -k python3 2>&1 | tee -a "$LOG"
RC=${PIPESTATUS[0]}
echo "EXIT:$RC" | tee -a "$LOG"
exit $RC
