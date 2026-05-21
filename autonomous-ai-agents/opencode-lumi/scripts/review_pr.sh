#!/usr/bin/env bash
# PR review helper: clone PR and run opencode review
set -euo pipefail
REPO_DIR="/home/hermes/tmp/lumi-assistant"
TMPDIR=$(mktemp -d /tmp/opencode_review_XXXX)
OPENCODE_BIN="${OPENCODE_BIN:-$HOME/.local/bin/opencode}"
CONFIG="$REPO_DIR/config/opencode.json"

if [ "$#" -lt 1 ]; then
  echo "Usage: review_pr.sh <git_url_or_local_path> [branch]" >&2
  exit 2
fi

GIT_URL=$1
BRANCH=${2:-}

git clone "$GIT_URL" "$TMPDIR/repo"
cd "$TMPDIR/repo"
if [ -n "$BRANCH" ]; then
  git fetch origin "$BRANCH" && git checkout FETCH_HEAD
fi

echo "Running opencode review in $TMPDIR/repo"
OPENCODE_CONFIG="$CONFIG" "$OPENCODE_BIN" run "Review this PR vs main. Provide a short summary, list of bugs, suggested fixes, and tests to add." -f $(git diff origin/main --name-only | tr '\n' ' ')

# Copy results back
cp -r "$TMPDIR" /tmp/opencode_review_results || true

echo "Results in /tmp/opencode_review_results"
