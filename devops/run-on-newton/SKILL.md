---
name: run-on-newton
description: "Use when you want the agent to run, manage, and fetch SLURM jobs on the Newton cluster (141.33.4.144) using the enforced workdir /lustre/<user>/hermes."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [devops, slurm, cluster, newton, run]
    related_skills: [hermes-agent-skill-authoring, writing-plans]
---

# Run on Newton

## Overview

This skill lets the agent perform common cluster actions on "Newton" (host 141.33.4.144, user arm2arm) in a safe, repeatable way. When invoked with the trigger phrase "run on Newton" (or a close variant), the agent connects over SSH, uses the required default working directory /lustre/<user>/hermes, and can create directories, upload job scripts, submit jobs (sbatch), monitor (squeue, sacct, sstat), fetch outputs, and clean up test artifacts when requested.

Core guarantees:
- Always use /lustre/<user>/hermes as the workdir for jobs and outputs unless the user explicitly overrides in the same command. When inspecting a failed job, prefer sacct WorkDir and SubmitLine, and if SubmitLine references an sbatch path, read that submit script to determine the runtime 'cd' target (see references/find_job_script_and_workdir.md).
- No destructive operations (rm -rf *, deletes) without explicit, repeated user confirmation.
- All remote side-effects are reported with verifiable handles (absolute paths, JOBIDs) and logs are fetched for verification.


## Preconditions
- SSH key-based login as arm2arm@141.33.4.144 must be available and working for the session (the agent uses the same SSH mechanism used in the session).
- The user has authorized the agent to perform actions on their behalf on Newton.

## When to use
- "Run on Newton: submit job.wrap.mpi"
- "Run on Newton: srun interactive"
- "Run on Newton: fetch job 12345"
- Use for job submission, monitoring, output retrieval, and creating job templates.

## Behavior and supported commands
The skill implements a small command language the agent understands when the user prefixes with the trigger. Examples below show intent categories the skill recognizes and the concrete actions the agent will take.

1) submit <local-or-remote-script-path> [--partition=NAME] [--hold|--depend=JOBID]
   - Uploads a local script to /lustre/<user>/hermes if necessary, sets executable bit, runs sbatch with provided partition or default partition wrap.
   - Returns: JOBID, submission stdout, path to realtime SLURM output (if available).

2) test-echo
   - Submits a minimal echo job to wrap (echo "hello world") and returns the JOBID plus the fetched output file contents after completion.

3) monitor JOBID
   - Runs sacct/squeue/scontrol to return job State, ExitCode, Elapsed, MaxRSS, and recent lines of the job output & error files.

4) fetch JOBID [--files pattern]
   - Copies matched output files from /lustre/<user>/hermes to the agent's local session environment (or returns secure paths/URLs if configured to upload to S3). Always returns absolute remote paths and verification via stat/ls output.

5) interactive [--time=HH:MM:SS] [--partition=NAME] [--cpus=] [--mem=]
   - Requests an interactive allocation via srun --pty. Agent will open the allocation and run specified verification commands, then exit the allocation. (Note: interactive allocations are ephemeral and the user will be informed when they start.)

6) list-partitions
   - Returns sinfo and scontrol show partition output summarized: partition name, MaxTime, MaxNodes, nodes list, default mem per CPU.

7) create-template <template-name> [--base=job.wrap.mpi]
   - Writes standard job templates into /lustre/<user>/hermes with clear placeholders and recommended SBATCH flags. Returns path to template.

8) cleanup <pattern> [--dry-run]
   - Lists files that would be removed under /lustre/<user>/hermes matching pattern. Will only delete when user confirms twice explicitly. Always shows sizes and last-modified times before deletion.

## Safety rules
- No destructive action is taken without explicit confirmation. If the user requests cleanup or delete, the agent asks: "Confirm deletion of N files under /lustre/<user>/hermes? Reply YES to proceed." The user must reply YES twice (two-stage confirmation).
- The agent will not change permissions of other users' files. chown/chmod is only used on files the agent created or that belong to arm2arm.
- Any network-facing uploads (S3) will be reported with the full URL returned to the user.

## Templates and paths
- Default workdir: /lustre/<user>/hermes
- Templates shipped with the skill (examples): job.wrap.mpi, smoke.sh, echo_hello.sh
- Log naming convention: %x_%j.out and %x_%j.err stored in the workdir.
- Session references: see references/run_plot_fallback.md for a tested fallback pattern when scp or heredoc quoting cause issues while uploading plotting scripts or fetching immediate artifacts.
- For Newton jobs that attach to a manually launched Dask cluster, see references/newton-manual-dask-tempdirs.md for the temp-directory rule: set TMPDIR/TMP/TEMP and DASK_TEMPORARY_DIRECTORY explicitly, because `--local-directory` alone may still leave `partd` writing shuffle files under `/tmp`.

## Verification checklist (post-action)
- After submit: check squeue (pending/running) and sacct (after completion). Return ExitCode and last 200 lines of output file.
- After fetch: verify file checksum (sha256sum) and return checksum to the user.
- After template creation: return absolute path and ls -l output of the template file.

## Examples (user utterances)
- "run on Newton: submit job.wrap.mpi"
- "run on Newton: test-echo"
- "run on Newton: monitor 508466"
- "run on Newton: fetch 508466 --files '*.out'"
- "run on Newton: create-template job.debug.mpi"

## Implementation notes for the agent

### Session learnings (2026-05-21)

- Recorded: shboost_full_cmd.py workflow, default S3 endpoint, and sbatch wrapper patterns.

- Prefer scp for uploading files to Newton when available. SCP is robust and preserves file contents and executability. Use scp with -o BatchMode=yes and StrictHostKeyChecking=accept-new in automated flows.
- Heredoc (ssh 'cat > file <<'PY' ... PY) is a useful fallback when scp is blocked, but be careful with quoting:
  - Use single-quoted heredoc markers (e.g. <<'PY') to prevent local shell interpolation of $(), variables, or backslashes.
  - Avoid embedding local `$(sed ...)` or other subshell expansions inside the heredoc; instead either upload the file directly or write the full static content.
  - If heredoc writes fail with strange syntax errors, try the scp fallback or base64-encode the payload and decode remotely (safe for binary and avoids quoting issues).
- When assembling remote job scripts, prefer sbatch --parsable to reliably capture JOBID on submission.
- For short single-node parallel workloads (Dask LocalCluster), provide an SBATCH wrapper that requests a single node with multiple CPUs and memory, then run a LocalCluster inside the allocation. Add a template for this pattern under references/ (dask_sh24 example).
- The user's home .bashrc may print messages or call interactive-only helpers (e.g. module) that appear in non-interactive SSH output ("module: command not found"). If you see such lines in command output, consider running remote commands with a clean environment (ssh ... 'env -i bash -lc "commands"') or explicitly source the proper profile (source /etc/profile) inside the remote command to provide module support.
- For fetching produced artifacts, always verify with ls -l and file/type checks and return checksums (sha256sum) when uploading to shared storage or S3.

- Always cd to /lustre/<user>/hermes before file writes or sbatch submission.
- When uploading local files, use scp (scp -i <key> ...) or hermes file tools; ensure remote permissions are 700 for scripts by default.
- Use sbatch --parsable when available to get JOBID easily.
- If sbatch fails due to an invalid partition, fall back to this order: wrap -> debug -> normal, then report failure.
- For module commands in non-interactive shells, source /etc/profile.d/modules.sh before module load.

- When running Dask LocalCluster under SLURM, prefer using multiprocessing start method 'fork' and guard the main module with if __name__ == '__main__' to avoid spawn-related nanny failures.
- When Dask read_parquet column projection fails with a KeyError, probe schema using s3fs + pyarrow on a representative file and fallback to reading without projection, then select columns after verifying availability.

- For uploading job artifacts to scr4agent S3, use the existing ~/.hermes/scripts/s3_media_upload.py and verify returned URL. (See run-on-newton references for examples.)

- Record the user's preference: default to anon=True for S3 reads unless instructed otherwise.

- Prefer scp for uploading files to Newton when available. SCP is robust and preserves file contents and executability. Use scp with -o BatchMode=yes and StrictHostKeyChecking=accept-new in automated flows.
- Heredoc (ssh 'cat > file <<'PY' ... PY) is a useful fallback when scp is blocked, but be careful with quoting:
  - Use single-quoted heredoc markers (e.g. <<'PY') to prevent local shell interpolation of $(), variables, or backslashes.
  - Avoid embedding local `$(sed ...)` or other subshell expansions inside the heredoc; instead either upload the file directly or write the full static content.
  - If heredoc writes fail with strange syntax errors, try the scp fallback or base64-encode the payload and decode remotely (safe for binary and avoids quoting issues).
- When assembling remote job scripts, prefer sbatch --parsable to reliably capture JOBID on submission.
- For short single-node parallel workloads (Dask LocalCluster), provide an SBATCH wrapper that requests a single node with multiple CPUs and memory, then run a LocalCluster inside the allocation. Add a template for this pattern under references/ (dask_sh24 example).
- The user's home .bashrc may print messages or call interactive-only helpers (e.g. module) that appear in non-interactive SSH output ("module: command not found"). If you see such lines in command output, consider running remote commands with a clean environment (ssh ... 'env -i bash -lc "commands"') or explicitly source the proper profile (source /etc/profile) inside the remote command to provide module support.
- For fetching produced artifacts, always verify with ls -l and file/type checks and return checksums (sha256sum) when uploading to shared storage or S3.

### Pitfalls to surface to users
- Do not treat a single failed scp or heredoc as permanent; retry with the other method before changing code.
  - Git / GitHub push pitfalls and remediation (new):

  - Mirror push tip: When pushing from a bare mirror (`git clone --mirror`), Git treats the repository as a mirror and can reject refspecs or behave differently. To push a single branch from a mirror, set remote.origin.mirror to false for the push only: `git -c remote.origin.mirror=false push --force origin <src-ref>:refs/heads/<dest>`.

  - New reference: see references/git-filter-repo-session-20260523.md for a concise bare-mirror workflow checklist and reproducible commands used in the Newton session.

References added in this session:
- references/git-filter-repo-session-20260523.md: step-by-step mirror + filter-repo checklist, troubleshooting, and the exact commands used on Newton to shrink pack files and push the cleaned mirror to GitHub.
- templates/push-cleaned-branch.sh: helper script to push a cleaned branch from a bare mirror without mirror semantics (useful when a mirror was created and you want to push one branch quickly).
  - Ambiguous local branches named like "origin/main": repositories can accidentally contain local branches whose names shadow remote refs (e.g. refs/heads/origin/main). This makes commands ambiguous and prevents predictable push/merge behaviour. Before any push/merge, check for and rename such branches: e.g. `git show-ref | grep "refs/heads/origin/main" && git branch -m "origin/main" "local-origin-main"`.
  - Unrelated histories: if `git merge` reports "refusing to merge unrelated histories", the local and remote tips share no common ancestor. Treat this as a policy decision (which history to keep). Do NOT force-push until you:
    1. create a safety backup branch (example: `git branch backup/main-before-force-$(date +%s)`),
    2. inspect the divergence (`git --no-pager log --oneline --decorate --graph --left-right origin/main...main -n 50`), and
    3. decide whether to preserve remote history, preserve local history, or merge with `--allow-unrelated-histories` (merge may produce many conflicts).
  - Large binary artifacts inside the repository frequently cause `git push` to fail with the remote closing the connection or timing out (pack files become huge). If `find` reveals large files under data/, mlartifacts/, or large .git/objects/pack files, do not attempt a blind force-push. Instead prefer one of the safer remediation paths below.
  - Recommended remediation paths (safe order):
    1. Create a backup branch (already described).
    2. Clean history to remove large files (preferred): use git-filter-repo or the BFG Repo-Cleaner to strip `data/` and other large artifact directories from history, then `git gc --aggressive`. Push the cleaned history (force) only after verifying size reduction locally.
    3. If you only need the source and not history, create a fresh source-only repo (copy source files, add .gitignore to exclude data/* and artifacts) and push that as the new main.
    4. Consider Git LFS or external object storage for large models and artifacts. The skill's templates section should include an example .gitattributes entry and an S3 upload snippet.
  - Force-push policy: force pushes are destructive to remote history. Only perform a force-push after creating a verified backup branch and with explicit user consent. When the repo is large, use longer timeouts, SSH keepalives, and ensure pack size is reasonable — but don’t rely on repeated force-push attempts as a fix for oversized repositories.
  - Verification checklist before any destructive remote action:
    - `git show-ref` and `git branch -a --verbose`
    - `git fetch origin --prune` and `git --no-pager log --left-right origin/main...main -n 50`
    - `find . -type f -size +50M` to list offending files
    - Run a mirror clone and filter in the mirror: `git clone --mirror /path/to/repo repo.git && cd repo.git && git filter-repo --path data/ --invert-paths` (or BFG). Inspect size before pushing.
    - Push cleaned repo to a test branch first, then promote to main with a force push once verified.
  - Small operational reminder: the user's .bashrc on Newton sometimes prints module-related warnings on non-interactive SSH. Use `ssh 'env -i bash -lc "commands"'` if those messages interfere with parsing automation output.


- Avoid assuming a GUI backend on cluster nodes; always use matplotlib Agg for plotting in batch jobs.

(Above additions were captured from an interactive session where scp sometimes timed out, heredoc quoting produced local-shell interpolation errors, and a Dask LocalCluster template was exercised.)

- Always cd to /lustre/<user>/hermes before file writes or sbatch submission.
- When uploading local files, use scp (scp -i <key> ...) or hermes file tools; ensure remote permissions are 700 for scripts by default.
- Use sbatch --parsable when available to get JOBID easily.
- If sbatch fails due to an invalid partition, fall back to this order: wrap -> debug -> normal, then report failure.
- For module commands in non-interactive shells, source /etc/profile.d/modules.sh before module load.

## Notes for maintainers
- This skill depends on the cluster details being correct (host, username, default workdir). Update the frontmatter if Newton moves or username changes.
- Keep templates under references/ in the skill directory if they grow large.


## Verification after creation
- The agent should run a quick non-destructive validation when the skill is used the first time: scontrol show config | grep -i slurm and sinfo -s to confirm partitions available.


