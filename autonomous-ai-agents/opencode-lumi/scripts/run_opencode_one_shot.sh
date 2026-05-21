#!/usr/bin/env bash
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

PROMPT="$*"
if [ -z "$PROMPT" ]; then
  echo "Usage: run_opencode_one_shot.sh <prompt>" >&2
  exit 2
fi

OPENCODE_CONFIG="$CONFIG" "$OPENCODE_BIN" run "$PROMPT"
