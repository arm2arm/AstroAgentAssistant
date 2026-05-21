#!/usr/bin/env bash
# Launch opencode TUI with project config
set -euo pipefail
REPO_DIR="/home/hermes/tmp/lumi-assistant"
OPENCODE_BIN="${OPENCODE_BIN:-$HOME/.local/bin/opencode}"
CONFIG="$REPO_DIR/config/opencode.json"

if [ ! -x "$OPENCODE_BIN" ]; then
  echo "opencode binary not found: $OPENCODE_BIN" >&2
  exit 2
fi
if [ ! -f "$CONFIG" ]; then
  echo "Missing project config: $CONFIG" >&2
  exit 2
fi

export OPENCODE_CONFIG="$CONFIG"
cd "$REPO_DIR"
# Exec into the opencode TUI (TTY required). Hermes should start this with pty=true
exec "$OPENCODE_BIN"
