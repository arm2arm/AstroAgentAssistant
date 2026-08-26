Newton cluster session notes (session date: 2026-05-20)

- Host tested: 141.33.4.144 (node name nnewl4)
- SSH: user arm2arm connects passwordless when key added.
- Shared filesystem: /lustre mounted (3.1P, ~42% used), path /lustre/<user> exists and is owned by arm2arm.
- Default workdir required by user: /lustre/<user>/hermes. It did not exist initially; agent created it and set 700 permissions.
- SLURM: /usr/bin/sbatch present, version slurm 23.11.11
- Partition names present (from sinfo -s): debug, normal, huge, tiny, many, gpu, a100, rtx800, sp48, ansys, taurus, taurus2sh, test24ex, test24, fast24, wrap, etc.
- Observed issues & fixes:
  - "module: command not found" printed in the login shell and in non-interactive commands: resolution: load modules via explicit sourcing in sbatch scripts (e.g. source /etc/profile.d/modules.sh) or ensure environment init runs in non-interactive shells.
  - Partition mismatch: script used partition "short" which does not exist; resubmitted using "debug" or user-selected partition.
- Smoke job pattern used:
  - Create smoke.sh in /lustre/<user>/hermes
  - sbatch smoke.sh
  - Monitor with squeue/sacct and inspect logs under /lustre/<user>/hermes

Actionable recommendations for future runs
- Use partition=debug for short smoke tests.
- Place all job scripts and outputs under /lustre/<user>/hermes. Use /lustre/<user>/hermes/logs for log files.
- Prepend `source /etc/profile` or `source /etc/profile.d/modules.sh` in job scripts when using Environment Modules.

