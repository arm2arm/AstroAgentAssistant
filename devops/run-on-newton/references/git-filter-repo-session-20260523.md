# Git-filter-repo & large-repo remediation — session notes (2026-05-23)

Purpose
- Concise, copy-pasteable recipe and checklist for using a mirrored clone + git-filter-repo to remove large data/model blobs and successfully push a cleaned history to a remote (GitHub). Captures pitfalls we hit on Newton (141.33.4.144) and the exact remediation sequence.

Summary of the problem we fixed
- Repository contained large model/data blobs (data/, mlartifacts/, large .xgb/.model files) and very large packfiles in .git/objects/pack, causing `git push --mirror` to fail with remote errors like:
  - "Connection to github.com closed by remote host"
  - "send-pack: unexpected disconnect while reading sideband packet"
  - "remote unpack failed: index-pack failed"
- Additional local hazards: a branch literally named `refs/heads/origin/main` shadowing remote refs; unrelated histories between local main and origin/main.

High-level safe policy (always follow)
1. Create a local safety backup branch of any branch you will rewrite: `git branch backup/main-before-force-$(date +%s)`.
2. Avoid blind force-pushes of a large mirror until you confirm pack size reduction locally.
3. Prefer pushing a single cleaned branch to restore service quickly; mirror-push only after full filtering + gc + repack and local verification.

Reproducible remediation recipe (works from Newton, adjust paths)

1) Make a bare mirrored clone (if you don't have one yet):

- From the original repo directory:
  git clone --mirror /path/to/repo /lustre/<user>/hermes/mlflow-filtered-YYYYMMDD.git

2) (Optional) Download git-filter-repo helper if not installed:

- Official script approach (example path used in session):
  curl -L https://raw.githubusercontent.com/newren/git-filter-repo/main/git-filter-repo -o /lustre/<user>/hermes/git-filter-repo
  chmod +x /lustre/<user>/hermes/git-filter-repo

3) Run git-filter-repo conservatively on the branch you want to clean first (fast, low-risk):

- Example: clean only the backup branch that contains large files
  cd /lustre/<user>/hermes/mlflow-filtered-XXXX.git
  /lustre/<user>/hermes/git-filter-repo --path data --invert-paths --refs 'refs/heads/backup/main-local-before-force-<ts>' --force

- Or do a mirror-wide cleanup (session used this):
  /lustre/<user>/hermes/git-filter-repo --invert-paths \
    --path data --path mlartifacts \
    --path-glob '*.xgb' --path-glob '*.model' --path-glob '*.joblib' \
    --path-glob '*.h5' --path-glob '*.ckpt' --path-glob '__pycache__' \
    --path-glob '*.ipynb_checkpoints' --strip-blobs-bigger-than 100M --force

Notes
- Prefer `--invert-paths` when you want to *remove* these paths from history.
- Use `--refs 'refs/heads/NAME'` to limit the work to a specific branch when debugging.
- `--strip-blobs-bigger-than 100M` is an effective catch-all to drop any remaining big objects.

4) Clean up local bookkeeping and shrink repo:

  git reflog expire --expire=now --all
  git for-each-ref --format='%(refname)' refs/original | xargs -r -n1 git update-ref -d
  git gc --prune=now --aggressive
  git repack -ad --window=10 --depth=0 -l

5) Verify size reduction locally (important):

  git count-objects -vH     # quick pack summary
  du -sh .                  # total repo dir size
  ls -la .git/objects/pack   # inspect packfiles
  find . -type f -size +100M # find remaining big files, if any

6) Push a small cleaned branch first (fast restore):

- From the bare mirror, to push the cleaned backup branch to origin/main without mirror semantics:
  git -c remote.origin.mirror=false push --force origin \
    refs/heads/backup/main-local-before-force-1779529293:refs/heads/main

- If you don't have a bare mirror, clone a temporary work tree from the cleaned mirror, create a branch, and push.

7) When mirror is small enough, push the mirror (destructive):

  git -c core.compression=0 -c pack.threads=8 -c pack.window=10 -c pack.depth=0 \
    -c http.postBuffer=1048576000 push --mirror origin --progress

Troubleshooting tips (what we hit)
- "fatal: --mirror can't be combined with refspecs" — don't pass refspecs when using --mirror; instead run `git -c remote.origin.mirror=false push --force origin <src>:refs/heads/<dst>` to push a single branch from a bare mirror.
- Remote unpack/index-pack failures usually indicate the remote rejected the large pack (disk/quota/memory limits or host-side checks). Fix by shrinking the pack locally before retry.
- If you see repetitive noise in SSH output like "/home/arm2arm/.bashrc: line 13: module: command not found", this is from the remote shell initialization. For automation, either:
  - Run remote commands with a clean environment: `ssh host 'env -i bash -lc "commands"'`, or
  - Source the appropriate profile that provides `module` (e.g. `source /etc/profile.d/modules.sh`) before running cluster-specific commands.
- If `git-filter-repo` reports "Some branches outside the refs/remotes/ hierarchy were not removed", it may mean non-remote-local branches still exist — delete or rename them explicitly (session ran `git branch -d <name>` guidance).

Session-specific script (reproducible sequence used on Newton)

1) Create mirror and download helper (run once):

  git clone --mirror /lustre/<user>/Projects/AutoML/mlflow mlflow-filtered-YYYYMMDD.git
  curl -L https://raw.githubusercontent.com/newren/git-filter-repo/main/git-filter-repo -o ~/hermes/git-filter-repo
  chmod +x ~/hermes/git-filter-repo

2) Run a mirror-wide filter (long-running; run in background with notify_on_complete):

  cd mlflow-filtered-YYYYMMDD.git
  ~/hermes/git-filter-repo --invert-paths --path data --path mlartifacts \
    --path-glob '*.xgb' --path-glob '*.model' --path-glob '*.joblib' --path-glob '*.h5' \
    --path-glob '*.ckpt' --path-glob '__pycache__' --path-glob '*.ipynb_checkpoints' \
    --strip-blobs-bigger-than 100M --force

3) Repack and push cleaned single branch (fast restore):

  git reflog expire --expire=now --all
  git for-each-ref --format='%(refname)' refs/original | xargs -r -n1 git update-ref -d
  git gc --prune=now --aggressive
  git repack -ad --window=10 --depth=0 -l
  git -c remote.origin.mirror=false push --force origin \
    refs/heads/backup/main-local-before-force-1779529293:refs/heads/main

4) Once everything is small, push full mirror:
  git -c core.compression=0 -c pack.threads=8 -c pack.window=10 -c pack.depth=0 \
    -c http.postBuffer=1048576000 push --mirror origin --progress

Quick checklist before any destructive push
- Created a backup branch of local main
- Verified cleaned pack size (git count-objects, du -sh)
- Confirmed remote SSH connectivity and that remote disk/quota allows large unpack
- Confirmed no ambiguous local refs (rename branches like `origin/main`)

Recommended .gitignore to add after cleanup

# Ignore large data and model artifacts
data/
mlartifacts/
*.xgb
*.model
*.joblib
*.h5
*.ckpt
__pycache__/
*.ipynb_checkpoints

Notes for skills authors
- Add this reference under `devops/run-on-newton/references/` so run-on-newton users have a pragmatic repair checklist.
- When orchestrating long-running filter-repo runs from the agent, use background=true with notify_on_complete=true and a post-check phase that runs gc + repack + a small test push before attempting a mirror push.

References
- git-filter-repo: https://github.com/newren/git-filter-repo
- BFG Repo-Cleaner: https://rtyley.github.io/bfg-repo-cleaner/

-- end
