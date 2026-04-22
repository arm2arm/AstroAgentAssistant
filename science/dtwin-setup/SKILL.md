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

### 3. Patch the SDEF Build File (CRITICAL FIX)

The container's `uuid.py` has Python 2 syntax (`1<<32L`) which breaks `p4p` module. Fix during build:

Open `recipies/pyat-as-twin-softioc.sdef` and **add this block** inside the `%post` section, right after the pip install line:

```
    #  ---------------------------------------------------------
    # Fix broken uuid.py in p4p/softioc packages (Python 2 syntax)
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

### Issue: No PVs registered
- **Cause:** IOC not fully started yet
- **Fix:** Wait 10-15 seconds after startup, then retry PV query.

### Issue: `ModuleNotFoundError: No module named 'p4p.ca'`
- **Cause:** Incorrect import path
- **Fix:** Use `from p4p import listRefs` instead of `from p4p.ca import Client`

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
- `external-repositories/dt4acc/scripts/dt4acc_softioc.py` — IOC startup script
- `external-repositories/dt4acc/src/dt4acc/custom_epics/ioc/server.py` — IOC server code
- `/tmp/dtwin_simple_test.py` — Integration test script

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
- `reana-workflow-best-practices` — for running dtwin on REANA clusters
- `apptainer` — general Apptainer usage patterns
