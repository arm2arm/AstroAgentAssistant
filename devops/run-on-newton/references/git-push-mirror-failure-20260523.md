Summary of 2026-05-23 Git mirror push failure and safe workaround

Context
- On Newton (141.33.4.144) we prepared a bare mirror of a large repo at /lustre/<user>/hermes/mlflow-filtered-1779534103.git and ran git push --mirror origin to replace the GitHub remote with the cleaned mirror.
- The push produced large pack transfer activity but ultimately failed on the remote with: "remote unpack failed: index-pack failed" and multiple "remote rejected ... (failed)" responses. The push produced `sideband` messages in git trace and the remote closed or rejected refs during unpack.

Diagnosis
- Mirror still contained very large packfiles / objects (mirror size ≈9.4 GB) even after filtering a single branch; other refs retained large objects.
- Remote side (GitHub) rejected unpack/index-pack because the server-side unpack could not process the large pack or encountered resource constraints.
- Full --mirror attempted to update many refs (some large) at once; remote-side rejection left partial failure and prevented a complete mirror update.

Safe, reproducible workaround used successfully
1) Preserve local state
   - Create a backup branch of your local main before any destructive action:
     git branch backup/main-local-before-force-$(date +%s)

2) Push only the cleaned, small branch to restore remote main (instead of --mirror):
   - From the mirror repo (or your repo where the cleaned branch exists):
     git -c remote.origin.mirror=false push --force origin \
       refs/heads/backup/main-local-before-force-1779529293:refs/heads/main --progress
   - Explanation: disabling remote.origin.mirror avoids the git client treating this repo as a mirror and rejecting refspecs. This pushes a single branch (force) and avoids transferring the entire mirror pack.
   - Result: small pack (~<1 MiB) transferred and origin/main was updated to the cleaned SHA. Confirm with: git ls-remote origin refs/heads/main

3) If you need a true mirror on the remote
   - Use git-filter-repo (or BFG) to remove large files across all refs in the mirror repo, then run a full gc and repack on the mirror before attempting --mirror push:
     git clone --mirror /path/to/repo repo.git
     cd repo.git
     # remove paths (example)
     git-filter-repo --path data/ --invert-paths --force
     # rewrite all refs as needed (adjust paths/filters accordingly)
     git reflog expire --expire=now --all
     git gc --prune=now --aggressive
     # verify size small and no large packfiles
     du -sh .
     # dry-run push to see what would change
     GIT_TRACE_PACKET=1 GIT_TRACE=1 git push --mirror --dry-run origin
   - Only when the mirror pack size is reduced and dry-run looks correct, run the real push. If the mirror is still very large, split work into per-branch pushes or push to a temporary private repo first.

Notes & pitfalls
- Ambiguous local refs (branches named like "origin/main") can cause surprising git behaviour. Rename them before filtering/pushing: git branch -m "origin/main" "local-origin-main".
- If a client returns "fatal: --mirror can't be combined with refspecs" it means remote.origin.mirror is set on a repo or you attempted to use --mirror alongside explicit refspecs; use -c remote.origin.mirror=false to override behavior for a single push.
- The user's remote shell may print non-critical messages (e.g. from ~/.bashrc). These appear in non-interactive ssh commands; consider running with a clean env or suppressing rc scripts when automating.

Quick checklist before a destructive mirror push
- Create a backup branch of local branches you care about.
- Run git-filter-repo / BFG to remove large paths across all refs.
- Run git reflog expire --expire=now --all && git gc --prune=now --aggressive.
- Confirm pack size is acceptably small (du -sh . and ls .git/objects/pack).
- Run git push --mirror --dry-run origin and inspect planned deletions/creations.
- If dry-run looks correct, run the push with sufficient network stability and time (consider doing it from a machine with reliable, long-lived SSH sessions).

Reproducible commands from the session (examples)
- Rename ambiguous branch:
  git branch -m 'origin/main' 'local-origin-main'

- Create backup:
  git branch backup/main-local-before-force-$(date +%s)

- Filter a single branch (example):
  /path/to/git-filter-repo --path data/ --invert-paths --refs 'refs/heads/backup/main-local-before-force-1779529293' --force

- Push single cleaned branch to origin/main (successfully used in session):
  git -c remote.origin.mirror=false push --force origin \
    refs/heads/backup/main-local-before-force-1779529293:refs/heads/main --progress

- Mirror push dry-run:
  GIT_TRACE_PACKET=1 GIT_TRACE=1 git push --mirror --dry-run origin

References
- This file documents a concrete failure and the minimal workaround applied successfully during the Newton session on 2026-05-23.
- For broader mirror-cleaning guidance see references/git-filter-repo-session-20260523.md
