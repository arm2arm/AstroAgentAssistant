Session notes: git push failure on Newton (arm2arm@nnewl4) — remote hung up while sending large pack.

Observed symptoms
- git push or git push --force to github.com closed connection during send-pack.
- Local repository contained a local branch named like the remote (refs/heads/origin/main), causing ambiguity.
- Local and remote had unrelated histories (git refused to merge with "refusing to merge unrelated histories").
- Repo contains many large binary artifacts and large .git/objects/pack files which make pack transfer fail or time out.

Safe repro (read-only) commands
- cd /lustre/<user>/Projects/AutoML/mlflow
- git show-ref | sed -n '1,200p'
- git fetch origin --prune
- git --no-pager log --oneline --decorate --graph --left-right origin/main...main -n 50
- find . -type f -size +50M -printf '%s %p\n' | sort -nr | sed -n '1,200p'

Remediation paths (summary)
1) Clean history (recommended)
   - Make a mirror clone: git clone --mirror /path/to/repo /tmp/repo.git
   - Use git-filter-repo to remove large directories (example):
       git filter-repo --invert-paths --path data/ --path data/mlartifacts/ --path-glob '*/model.*' --force
   - git reflog expire --expire=now --all && git gc --prune=now --aggressive
   - Inspect size reduction, then push the mirror to origin (force) or to a test branch first.

2) Create a source-only repo
   - rsync only source files into a fresh repo, commit, and push (force) to origin/main if desired.

3) Use Git LFS (if you must keep large files under version control)
   - Install git-lfs, git lfs track patterns, then use `git lfs migrate import` to move history.
   - GitHub LFS may incur storage/bandwidth limits and requires configuration.

Safety checklist before destructive actions
- Create a backup branch: git branch backup/main-before-force-$(date +%s)
- Verify refs: git show-ref; git branch -a --verbose
- Inspect divergence: git --no-pager log --left-right origin/main...main -n 50
- List big files: find . -type f -size +50M
- Work in a mirror clone, not the working copy; test pushes to a temporary branch first.

Operational tips
- Do not keep GB-scale artifacts in git. Use S3/MinIO/artifact registries and store pointers in the repo.
- Rename accidental local branches named like remotes (e.g. `origin/main`) to avoid ambiguity: `git branch -m 'origin/main' 'local-origin-main'`.
- When remote hangs during push, the cause is often oversized packfiles. Clean history rather than repeating force-pushes.

References
- git-filter-repo: https://github.com/newren/git-filter-repo
- BFG Repo-Cleaner: https://rtyley.github.io/bfg-repo-cleaner/
- GitHub LFS docs: https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage

Example quick commands (non-destructive checks)
- git show-ref | sed -n '1,200p' > ~/mlflow-show-ref-backup.txt
- git branch -m 'origin/main' 'local-origin-main'  # if present
- git branch backup/main-before-force-$(date +%s)
- git fetch origin --prune
- find . -type f -size +50M -printf '%s %p\n' | sort -nr | head

Notes: keep backup branches and tags; do not delete them until you verify the cleaned history and remote state are correct.
