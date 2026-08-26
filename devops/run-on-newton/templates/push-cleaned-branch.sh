#!/usr/bin/env bash
# Usage: push-cleaned-branch.sh <mirror-repo-dir> <src-branch-ref> <dest-branch>
# Example: push-cleaned-branch.sh /lustre/<user>/hermes/mlflow-filtered-20260523.git \
#             refs/heads/backup/main-local-before-force-1779529293 main

set -euo pipefail
mirror_dir="$1"
src_ref="$2"
dest_branch="$3"

cd "$mirror_dir"
# Ensure we're not treating this as a mirror for a single-branch push
git -c remote.origin.mirror=false push --force origin "$src_ref":refs/heads/"$dest_branch"

echo "Pushed $src_ref to origin/$dest_branch from mirror $mirror_dir"