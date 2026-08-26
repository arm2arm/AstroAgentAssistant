# Newton manual Dask temp-directory note

Use this when a Newton job connects to a manually launched Dask cluster via `/lustre/<user>/tmp/scheduler.json` and shuffle/checkpoint steps fail with `OSError: [Errno 28] No space left on device` even though Lustre quota is healthy.

## Core finding

`dask worker --local-directory /scratch` does **not** guarantee that `partd` shuffle files go to `/scratch`.

In the May 2026 Newton session:
- worker `local_directory` was `/scratch/dask-scratch-space/...`
- but `partd.File()` on workers still created temp files under `/tmp/tmp....partd`
- worker env had `TMPDIR`, `TMP`, and `TEMP` unset
- `tempfile.gettempdir()` resolved to `/tmp`
- one worker host had much less free `/tmp` space than the other, which explained intermittent `Errno 28`

## Practical rule

For temp-heavy Dask / papermill jobs on Newton, redirect **all** temp variables and worker local directories explicitly to `/lustre/<user>/temp` (or a host-specific subdirectory under it) instead of relying on `/tmp`.

Example worker launch pattern:

```bash
mkdir -p /lustre/<user>/temp/${HOSTNAME}/tmp
mkdir -p /lustre/<user>/temp/${HOSTNAME}/dask-local

TMPDIR=/lustre/<user>/temp/${HOSTNAME}/tmp \
TMP=/lustre/<user>/temp/${HOSTNAME}/tmp \
TEMP=/lustre/<user>/temp/${HOSTNAME}/tmp \
DASK_TEMPORARY_DIRECTORY=/lustre/<user>/temp/${HOSTNAME}/tmp \
dask worker \
  --scheduler-file /lustre/<user>/tmp/scheduler.json \
  --nworkers 16 \
  --nthreads 2 \
  --local-directory /lustre/<user>/temp/${HOSTNAME}/dask-local \
  --interface ib0
```

## Verification pattern

After restart, verify from a Dask client on Newton:
- worker `local_directory` points into `/lustre/<user>/temp/...`
- `tempfile.gettempdir()` on workers resolves into `/lustre/<user>/temp/...`
- `partd.File().path` also lands in `/lustre/<user>/temp/...`

If only `local_directory` changed but `partd` still writes to `/tmp`, the worker environment was not updated correctly.

## Notes

- This is a Newton/manual-Dask operational pattern, not a general statement about Dask everywhere.
- Lustre-backed temp storage may be slower than node-local scratch, but it is preferable here when `/tmp` causes hard failures.
