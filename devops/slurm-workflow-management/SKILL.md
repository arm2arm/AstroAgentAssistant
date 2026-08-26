---
name: slurm-workflow-management
description: Manage SLURM cluster access, submit jobs, monitor runs, and collect outputs reproducibly.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [slurm, cluster, devops, jobs, templates]
---

# SLURM Workflow Management

Overview
- Class-level skill for connecting to SLURM clusters over SSH, preparing a reproducible working directory, submitting jobs (sbatch / job arrays), monitoring (squeue/sacct/scontrol/sstat), debugging failures, and transferring results.
- Includes ready-to-use job script templates and a session-specific reference folder for cluster quirks.

When to use
- Any task that requires remote cluster job execution (batch or array), debugging failed jobs, or packaging reproducible job submission scripts.

Triggers
- User provides SSH access to a cluster and asks the agent to run jobs.
- User sets a project-specific default workdir for all cluster activity.

Assumptions
- Cluster exposes SSH with passwordless key login when keys are installed.
- SLURM binaries (sbatch, squeue, sinfo, sacct) are available on the login node.
- A shared filesystem is available for storing job outputs (e.g., /scratch, /lustre).

Core principles
- Always run jobs and write outputs under the project's declared default workdir when the user supplies one. Do not write elsewhere unless the user explicitly permits it.
- Use small smoke jobs first to validate environment (modules, python, I/O) before running expensive workloads.
- Use clear, descriptive job names and structured output filenames including job name and JOBID (e.g. --output=${WORKDIR}/logs/%x_%j.out).
- Version and record the runtime environment (conda env yaml or container hash) in job logs.

Step-by-step pattern
1. Connect via SSH (BatchMode=yes for non-interactive checks):
   - ssh -o BatchMode=yes -o ConnectTimeout=10 user@cluster 'which sbatch; sbatch --version'
2. Probe cluster:
   - sinfo -s  (list partitions and limits)
   - scontrol show config | egrep 'MaxTime|DefMemPerCPU'
   - df -h <shared_fs>
3. Create or respect default workdir (user-declared):
   - mkdir -p $WORKDIR && chmod 700 $WORKDIR && chown $USER: $WORKDIR
   - Always use $WORKDIR for job scripts, outputs, and temporary files unless user instructs otherwise.
4. Upload or write job script templates to $WORKDIR.
5. Submit a smoke job (5 min) that prints environment, checks python/modules, creates a tiny file on the shared filesystem, and writes a short log.
6. Monitor the smoke job: squeue -u $USER; tail -f ${WORKDIR}/smoke-<JOBID>.out; sacct for accounting after completion.
7. Iterate: adjust partition, resources, or environment commands (source /etc/profile.d/modules.sh) if modules not available in batch shells.
8. Submit production jobs with explicit resources and meaningful outputs. Use job arrays for embarrassingly parallel tasks and --dependency for chained workflows.

Templates and references
- This skill ships with several templates in templates/ and session-specific notes in references/. Use them as canonical starting points.

Pitfalls and fixes (captured from sessions)
- "module: command not found" in non-interactive shells: run `source /etc/profile` or `source /etc/profile.d/modules.sh` at the top of your sbatch script before `module load`. The templates/papermill_sbatch_template.sh includes this check.
- Invalid partition: always query `sinfo -s` first and choose an available partition. If a script used a partition name that doesn't exist, change it and resubmit.
- Respect user-declared default_workdir requirements: some users require every run to happen under a given path — encode this into the job scripts and the working commands.
- sacct field availability mismatch: requesting unsupported fields (e.g. "Command") causes sacct to error. Use `/usr/bin/sacct --helpformat` on the cluster to list valid fields before composing long queries. The references/find_job_script_and_workdir.md contains a robust recipe for locating submit scripts that avoids unsupported fields.

Best practices (quick)
- Put logs in ${WORKDIR}/logs with `--output=${WORKDIR}/logs/%x_%A_%a.out` for arrays.
- Use `%x` (job name), `%j` (job ID), `%A` (array master ID), `%a` (array index) placeholders in SBATCH output names.
- Use small interactive `srun --pty` allocations to debug environment issues before long runs.
- Keep environment activation commands and module loads inside the script (not in .bashrc) to ensure reproducibility.

See the templates/ and references/ files included with this skill for ready-to-run examples and the Newton session notes.

Session-specific diagnostics and new guidance (added 2026-05-31 / updated 2026-06-03):
- Added references/newton-srv-diagnostics.md with a concise reproduction of a common failure mode we observed on Newton where SLURM clients are configured to use DNS SRV (_slurmctld._tcp) for controller discovery and DNS SRV lookups may fail transiently. The reference contains exact diagnostic commands, what each failure message means, and recommended fallbacks (local slurm.conf, SLURM_CONF override, or admin DNS fix).
- Added templates/papermill_sbatch_template.sh: a papermill-focused SBATCH template that includes runtime sanity checks (verify DASK_SCHEDULER_ADDRESS reachability from the compute node, ensure module/load is done inside the job script, write environment and request info to the log, and use safe papermill flags for DRY_RUN/debugging).
- Added references/find_job_script_and_workdir.md: concise, copyable recipe for locating a failed job's submit script and effective runtime working directory using sacct and local filesystem probes (sacct fields: WorkDir, SubmitLine, Partition; if SubmitLine contains an sbatch path, read that file; search common log locations for slurm-<JOBID> files). Includes command examples and cautions about fields that do not exist (e.g. "Command" is not a valid sacct field on some systems).

Why this change:
- During interactive troubleshooting we observed an operator-friendly diagnostic pattern that reliably finds the submit script and runtime directory for failed jobs without needing captured stdout from the job. This follows a small number of sacct queries and local file reads and avoids fragile assumptions about sacct field availability.

Where to look in the skill now:
- references/newton-srv-diagnostics.md — diagnostic checklist and commands to run as a non-admin user.
- templates/papermill_sbatch_template.sh — a hardened papermill sbatch example with logging and Dask connectivity checks.
- references/find_job_script_and_workdir.md — exact commands and examples used in the Newton session (2026-06-03) to locate the sbatch script and working directory for JOBID 509484.

Keep the rest of this skill as the canonical SLURM workflow guidance; these references are intended to be practical, copy-and-run artifacts to speed future debugging.

