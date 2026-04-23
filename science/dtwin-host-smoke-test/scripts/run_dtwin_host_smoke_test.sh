#!/usr/bin/env bash
set -euo pipefail

DTWIN_ROOT="${1:-/tmp/dtwin-build}"
VENV_PATH="${DTWIN_SMOKE_VENV:-$DTWIN_ROOT/.venv-dtwin-smoke}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if [[ ! -d "$DTWIN_ROOT/dt4acc" || ! -d "$DTWIN_ROOT/dt4acc-lib" || ! -d "$DTWIN_ROOT/lat2db" ]]; then
  echo "Expected dt4acc, dt4acc-lib, and lat2db repos under: $DTWIN_ROOT" >&2
  exit 2
fi

if [[ ! -f "$DTWIN_ROOT/dtwin_host_smoke_test.py" ]]; then
  echo "Missing smoke-test python script: $DTWIN_ROOT/dtwin_host_smoke_test.py" >&2
  exit 2
fi

echo "== preparing venv =="
"$PYTHON_BIN" -m venv "$VENV_PATH"
source "$VENV_PATH/bin/activate"

python -m pip install --upgrade pip setuptools wheel
python -m pip install pytest transitions accelerator-toolbox softioc p4p
python -m pip install -e "$DTWIN_ROOT/dt4acc-lib"
python -m pip install -e "$DTWIN_ROOT/lat2db"
python -m pip install -e "$DTWIN_ROOT/dt4acc"

echo "== running dt4acc-lib tests =="
pytest -q "$DTWIN_ROOT/dt4acc-lib/tests"

echo "== running host-side dtwin smoke test =="
python "$DTWIN_ROOT/dtwin_host_smoke_test.py" "$DTWIN_ROOT"
