Newton SLURM DNS SRV diagnostics (session: 2026-05-31)

Problem observed
- SLURM clients (sinfo/squeue/sacct) failing with:
  - resolve_ctls_from_dns_srv: res_nsearch error: Unknown host
  - fetch_config: DNS SRV lookup failed
  - fatal: Could not establish a configuration source
- /etc/slurm/slurm.conf absent on login nodes (config distributed via DNS SRV: _slurmctld._tcp)

User-level diagnostic checklist (non-admin)
1. Confirm client binaries exist:
   which sbatch squeue sacct scontrol
2. Run a quick sinfo -s (may fail if DNS SRV broken):
   sinfo -s
   If you see the "resolve_ctls_from_dns_srv" error, continue below.
3. Check DNS resolution on the login node:
   cat /etc/resolv.conf
   host -t SRV _slurmctld._tcp || dig +short SRV _slurmctld._tcp
   If these commands show no SRV records or DNS errors, DNS SRV lookups are failing.
4. Check for local slurm.conf fallback:
   ls -l /etc/slurm/slurm.conf
   If present, try: SLURM_CONF=/etc/slurm/slurm.conf sinfo -s
5. Search for recent slurm-*.out job logs to inspect job output without querying the controller:
   find ~ /lustre -type f -name "slurm-*.out" -mtime -7 -ls
6. Inspect job accounting (if sacct works) or re-run sacct once DNS is healthy.

Workarounds and fallbacks
- If SRV records are missing and you cannot contact admins immediately:
  1. Locate a canonical slurm.conf on the cluster (often on the management node or shared path). If readable, set SLURM_CONF to that path for client commands:
     export SLURM_CONF=/path/to/slurm.conf
     sinfo -s
  2. If a Dask scheduler or other services your job needs run on login node, ensure the job's SBATCH script verifies connectivity from the compute node (see papermill template): try a small smoke job with netcat or curl to the scheduler host from a compute node.

Administrator actions (to request)
- Restore/repair DNS SRV entries for _slurmctld._tcp pointing to the controller host(s).
- Ensure slurmctld services are running and reachable from login nodes.
- If DNS-based config is intended, add redundant nameservers or fallback copies of slurm.conf on login nodes.

Useful commands (copy-paste)
- DNS SRV lookup:
  host -t SRV _slurmctld._tcp || dig +short SRV _slurmctld._tcp
- Try client using a known slurm.conf:
  SLURM_CONF=/path/to/slurm.conf sinfo -s
- Find recent slurm logs (non-admin):
  find ~ /lustre -maxdepth 4 -type f -name "slurm-*.out" -mtime -7 -ls

Notes
- Transient DNS failures happen; retrying sinfo after a minute is a valid first step. The presence of many slurm-*.out files in /lustre shows jobs were running recently even if the controller momentarily couldn't be contacted.
- Do NOT capture 'sinfo is broken' as a permanent skill restriction — capture the diagnostic + retry/fallback pattern instead.
