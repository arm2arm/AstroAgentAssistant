Find submit script and runtime working directory for a failed Slurm job (copyable recipe)

Context
- Use when sacct shows a FAILED job and you need to know which sbatch script was used and what the job's effective working directory was.
- Works without root and without relying on fragile sacct fields that some Slurm builds omit.

Step-by-step
1. Ask sacct for basic fields including WorkDir and SubmitLine:

   /usr/bin/sacct -j <JOBID> -o JobID,JobName,WorkDir,SubmitLine,Partition -P -n

   Notes:
   - The SubmitLine often contains the sbatch command used, e.g. "sbatch /home/user/run_job.sbatch".
   - Some environments do not expose SubmitLine; if missing, query other fields or rely on your project conventions.

2. If SubmitLine contains an sbatch path, inspect that file directly:

   sed -n '1,240p' /path/to/run_job.sbatch

   - Look for cd commands and explicit module loads. These reveal the effective runtime directory and environment.
   - If the file is inaccessible, check file ownership or ask the job submitter.

3. If SubmitLine is missing or empty, search common submit directories for scripts mentioning the job name or job ID pattern:

   grep -R "<JOBNAME>\|<JOBID>" -n $HOME $HOME/projects /lustre/$USER 2>/dev/null | head -n 200

   - Adjust paths ($HOME/projects, /lustre/$USER) to your site's conventions. Limit recursion depth if needed.

4. Check standard log paths for slurm output files (often under $HOME/logs or $WORKDIR/logs):

   ls -la $HOME/logs/slurm-${JOBID}* $WORKDIR/logs/*${JOBID}* 2>/dev/null || true

   - These files contain stdout/stderr that often reveal the exact script path and working directory.

5. As a last resort, search the filesystem for files modified near the job End time (from sacct) under likely project directories. This is heavier but sometimes needed.

Caveats and pitfalls
- "Command" is not a universally available sacct field; requesting unsupported fields causes sacct to error. Use `sacct --helpformat` to inspect valid fields on your cluster.
- SubmitLine can be truncated in accounting logs; preferto reading the file when present.
- Some clusters rewrite WorkDir to a canonical path (e.g., $HOME), while others show the directory the job actually cd'd into. Always verify in the job stdout.

Quick example (JOBID 509484):
- sacct -j 509484 -o JobID,JobName,WorkDir,SubmitLine -P -n
  -> SubmitLine: sbatch /home/arm2arm/run_papermill_safer_validate.sbatch
- sed -n '1,240p' /home/arm2arm/run_papermill_safer_validate.sbatch
  -> contains `cd /lustre/<user>/ipython/SH2025/reana` so that's where papermill ran.

Reference: updated 2026-06-03 — produced from a real Newton session. Keep the commands generic and explicit to avoid cluster-specific surprises.
