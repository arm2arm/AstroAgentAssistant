---
name: dtwin-setup
category: science
description: Build and run the dt4acc Digital Twin for particle accelerators using Apptainer
---

# dtwin-setup

Build and run the **dt4acc Digital Twin** (BESSY II accelerator simulation) using Apptainer containers on ARM64 Ubuntu systems.

## Trigger Conditions
- User wants to set up a digital twin for particle accelerator simulation
- User mentions `dt4acc`, `dtwin`, `BESSY II`, or `accelerator twin`
- Need to simulate accelerator optics (Twiss parameters, beam orbit) via EPICS

## Prerequisites
- Ubuntu 22.04+ or similar Linux distribution
- Sufficient disk space (≥ 2 GB for SIF image)
- Network access to clone from GitLab: `https://codebase.helmholtz.cloud/digital-twins-for-accelerators/containers/pyat-softioc-digital-twin`
- Root/sudo access for Apptainer installation (or user must be in required groups)

## Step-by-Step Procedure

### 1. Install Apptainer

```bash
# Check if already installed
apptainer --version

# Install if needed
sudo apt update
sudo apt install -y apptainer
```

### 2. Clone Repository and Initialize Submodules

```bash
cd /tmp
git clone https://codebase.helmholtz.cloud/digital-twins-for-accelerators/containers/pyat-softioc-digital-twin.git dtwin-build
cd dtwin-build
git submodule update --init --recursive
```

> **Note:** May see warning `fatal: No url found for submodule path...` for `lat2db/scripts/bessy2reflat` — this is expected and harmless.

> **Important:** Do NOT try to pull the pre-built image from `registry.hzdr.de` — the pre-built `pyat-softioc-digital-twin` image is **AMD64 only** and will fail on ARM64. You must build from source.

### 3. Check/Create SDEF Build File

If `recipies/pyat-as-twin-softioc.sdef` doesn't exist (e.g., the git repo's `.git` directory was lost, or repo was cloned but not initialized), create it from the self-contained template:

```bash\ncd /tmp/dtwin-build\nmkdir -p recipies\ncp ~/.hermes/skills/dtwin-setup/references/sdef-self-contained.sdef recipies/pyat-as-twin-softioc.sdef\n```\n\n**Important:** The SDEF must include:\n- `pip install softioc>=4.1 p4p` (PyPI dependencies, not just local packages)\n- uuid.py Python 2 syntax fix (copies `/usr/lib/python3.11/uuid.py` to override broken package versions)\n- A startup wrapper script that bypasses the interactive Python console (`</dev/null`)
- `%startscript` with `exec /start_ioc.sh` (not just `exec /start.sh` — the script must be created in `%post` first)

### 4. Build the Apptainer Image

```bash\ncd /tmp/dtwin-build\napptainer build --fakeroot pyat-as-twin-softioc.sif recipies/pyat-as-twin-softioc.sdef 2>&1 | tail -50\n```\n\n> **Expected output:** `INFO:    Build complete: pyat-as-twin-softioc.sif`\n> **File size:** ~342 MB\n> **Architecture:** arm64 (native)\n> **Build time:** ~3-5 minutes\n\n> **Note:** The `--fakeroot` flag is required for building as a non-root user.\n\n### 5. Handle Missing Repositories

If the git repo is unavailable (e.g., `codebase.helmholtz.cloud` unreachable), all source repos must exist locally in `/tmp/dtwin-build/`:
- `dt4acc/`
- `bact-twin-architecture/`
- `dt4acc-lib/`\n- `lat2db/`\n\nThese are copied into the container via the `%files` section of the SDEF.
    find /twin/python/venv/lib/python3.12/site-packages -name 'uuid.py' -exec cp /usr/lib/python3.12/uuid.py {} \; 2>/dev/null || true
```

The existing code should look like:
```
    python3 -m pip install -v /build/lat2db/ /build/bact-twin-architecture/ /build/dt4acc/

    #  ---------------------------------------------------------
    # Fix broken uuid.py in p4p/softioc packages (Python 2 syntax)
    find /twin/python/venv/lib/python3.12/site-packages -name 'uuid.py' -exec cp /usr/lib/python3.12/uuid.py {} \; 2>/dev/null || true

    #  ---------------------------------------------------------
    # add /twin/lib so that it will be used by ldconfig
```

### 4. Build the Apptainer Image

```bash
cd /tmp/dtwin-build
apptainer build pyat-as-twin-softioc.sif recipies/pyat-as-twin-softioc.sdef 2>&1 | tail -50
```

> **Expected output:** `INFO:    Build complete: pyat-as-twin-softioc.sif`
> **File size:** ~246 MB
> **Architecture:** arm64 (native)
> **Build time:** ~3-5 minutes

### 5. Run the Digital Twin IOC

```bash
cd /tmp/dtwin-build
nohup apptainer run --cleanenv pyat-as-twin-softioc.sif </dev/null > /tmp/dtwin-ioc.log 2>&1 &
echo "IOC started with PID $!"
```

Wait for startup (typically 10-15 seconds):
```bash
sleep 10
tail -20 /tmp/dtwin-ioc.log
```

### 6. Verify IOC is Running

Look for these lines in the log:
```
✓ softioc initialized
✓ All PVs set up
✓ Starting iocInit
✓ iocRun: All initialization complete
✓ PVXS QSRV2 is loaded, permitted, and ENABLED
✓ EPICS 7.0.10.1-DEV
```

### 7. Test PV Access

Run this test script inside the container:

```bash
cd /tmp/dtwin-build
apptainer exec --cleanenv pyat-as-twin-softioc.sif /twin/python/venv/bin/python3 -c "
from p4p import listRefs
import time
time.sleep(2)
refs = listRefs()
print(f'Found {len(refs)} PVs')
for ref in sorted(refs)[:10]:
    print(f'  {ref}')
"
```

Or run the full integration test:
```bash
apptainer exec --cleanenv \
  --bind /tmp/dtwin_simple_test.py:/dtwin_simple_test.py \
  pyat-as-twin-softioc.sif \
  /twin/python/venv/bin/python3 /dtwin_simple_test.py
```

## Troubleshooting

### Issue: `SyntaxError: invalid decimal literal` in uuid.py
- **Cause:** Container's `uuid.py` has Python 2 syntax
- **Fix:** Ensure the uuid.py patch is in your sdef file. Rebuild the image.

### Issue: `FATAL: container creation failed: network requires root`
- **Cause:** Trying to use `--network host` without root
- **Fix:** Run without `--network host` (EPICS CA broadcasts still work inside container). To expose PVs to host, use `--network host` with sudo or add user to required groups.

### Issue: IOC crashes with zero logs on startup
- **Cause 1:** `softioc.interactive_ioc(globals())` opens a blocking `>>>` Python prompt. Even with `</dev/null`, the script may exit silently before iocInit completes.
- **Fix:** Check the SIF's `%startscript` section — it must exec a wrapper that patches `interactive_ioc` to call `ioc_init()` instead, or use `exec` to bypass the prompt. If logs are truly empty, the IOC may be failing during import (e.g., missing function).
- **Cause 2:** Missing function references (e.g., `initialize_bpm_pvs` not found in `pv_setup` module). Check for `NameError` in imports by running the script interactively inside the container: `apptainer exec --cleanenv pyat-as-twin-softioc.sif /twin/python/venv/bin/python3 -c "from dt4acc.custom_epics.ioc.server import *"`.

### Issue: IOC won't start — stale Apptainer/squashfuse processes
- **Cause:** Old IOC runs leave mounted squashfuse sessions that block new mounts.
- **Fix:** Kill stale processes: `fuser -km /tmp/apptainer/mnt/*/mount 2>/dev/null; pkill -9 -f squashfuse 2>/dev/null; fuser -km /tmp/dtwin* 2>/dev/null`. Then retry startup.
- **Detection:** If `apptainer run` fails silently or IOC exits immediately with no log output, stale mounts are likely the culprit.
- **Prevention:** Always stop the IOC properly before restarting: `kill $(pgrep -f pyat-as-twin-softioc) 2>/dev/null; sleep 2; fuser -km /tmp/apptainer/mnt/*/mount 2>/dev/null`

### Issue: No PVs registered
- **Cause:** IOC not fully started yet
- **Fix:** Wait 10-15 seconds after startup, then retry PV query.

### Issue: `ModuleNotFoundError: No module named 'p4p.ca'` or `from p4p.client import Client` fails
- **Cause:** The container's p4p installation is **server-side only** — it publishes PVs but includes no client modules
- **Fix:** Use `from p4p import listRefs` to query PVs from inside the container. For read/write operations, use EPICS client tools on the **host** (`pvget`, `pvput`) or install p4p with client support on the host and connect to the IOC's EPICS endpoints
- **Important:** Connection resilience tests (connect/read/close cycles) cannot be run from inside the container — they require client modules that aren't present

## Key PV Categories

| Category | Example PVs |
|----------|-------------|
| Cavity | `CAVH4T8R:Cm:set`, `CAVH3T8R:Cm:set` |
| BPM | `MDIZ2T5G` |
| Master Clock | `MCLKHX251C` |
| Orbit | Various orbit corrector PVs |
| Twiss | Alpha/Beta parameter PVs |
| Tune | Horizontal/Vertical tune PVs |

## Useful Commands

```bash
# Check SIF file
ls -lh pyat-as-twin-softioc.sif

# View running IOC log
tail -f /tmp/dtwin-ioc.log

# Exec into container (interactive shell)
apptainer exec --cleanenv pyat-as-twin-softioc.sif /bin/bash

# Query specific PV from host (requires p4p installed on host)
python3 -c "
from p4p import listRefs
import time
time.sleep(2)
refs = listRefs()
print([r for r in refs if 'CAVH' in r])
"
```

## Files Referenced
- `recipies/pyat-as-twin-softioc.sdef` — Apptainer build recipe
- `scripts/bessyii/dt4acc_softioc.py` — host-side EPICS startup script in the current GitHub `dt4acc` repo
- `src/dt4acc/custom_epics/ioc/server.py` — EPICS IOC server code
- `/tmp/dtwin_simple_test.py` — Integration test script

## Additional smoke-test note

For quick validation of the current GitHub `dt4acc`/`dt4acc-lib` codebase, you can skip MongoDB and container startup entirely and smoke-test the core stack on the host by:
1. installing `dt4acc-lib`, `dt4acc`, `lat2db`, `softioc`, `p4p`, `accelerator-toolbox`, and `transitions` into a venv,
2. loading `src/dt4acc/custom_facility/bessyii/resources/storage_ring/input/bessy2_storage_ring_reflat.json`,
3. building a PyAT lattice via `lat2db.tools.factories.pyat.factory`,
4. constructing `SimulatorBackend` + `CommandRewriter`, and
5. verifying tune/twiss/track reads plus a small magnet write/restore cycle.

This is a good first check before debugging container-specific issues.

## Upstream installation note (pending merge)

A developer-maintained README update currently lives on branch:
- `dt4acc/dt4acc:dev/feature/updated-readme`
- detailed docs: `README_details.rst`

The developer indicates the new installation flow is **not yet fully merged into `dev/main`** because two pull requests are still pending. Once those land, the preferred git-based install is expected to be:

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install \
   "dt4acc-lib @ git+https://github.com/dt4acc/dt4acc-lib.git" \
   "dt4acc[epics,bessyii] @ git+https://github.com/dt4acc/dt4acc.git"

dt4acc_bessyii
```

Treat this as **upstream guidance / near-future workflow**, not yet guaranteed for `dev/main` until the pending PRs are merged.

## Pitfalls

1. **Never skip the uuid.py fix** — the container ships with broken Python 2 syntax that breaks p4p
2. **Submodule warning is normal** — `lat2db/scripts/bessy2reflat` fails to recurse but doesn't affect functionality
3. **Container is read-only at runtime** — you cannot patch files inside the SIF; fixes must be in the sdef `%post` section
4. **EPICS CA uses UDP broadcasts** — they don't cross container boundaries without `--network host`
5. **MongoDB not required** for basic operation — the IOC uses default `mongodb://localhost:27017/bessyii` but can run without it
6. **Interactive console blocks PVs** — the `dt4acc_softioc.py` opens a Python `>>>` prompt; run with `</dev/null` to bypass

## Verification Checklist

- [ ] Apptainer installed (`apptainer --version` returns 1.4+)
- [ ] Repository cloned with submodules
- [ ] uuid.py fix applied to sdef
- [ ] SIF image built (~246 MB, arm64)
- [ ] IOC started and log shows "All initialization complete"
- [ ] PVs registered (listRefs returns > 0)
- [ ] EPICS protocol running (PVXS QSRV2 enabled)

## Related Skills
- `dtwin-host-smoke-test` — first-pass host-side validation of the current dt4acc stack without MongoDB, TANGO, or Apptainer
- `reana-workflow-best-practices` — for running dtwin on REANA clusters
- `apptainer` — general Apptainer usage patterns
