---
name: dtwin
title: dt4acc Digital Twin — Setup, Smoke Testing, EPICS/TANGO Runbooks, and Burn-in
description: >-
  Umbrella for the dt4acc Digital Twin (particle accelerator simulation) covering
  Apptainer builds, host-side smoke tests, EPICS and TANGO runbooks, container
  troubleshooting, and burn-in testing.
author: Hermes Agent
date: 2026-04-30
tags: [dtwin, dt4acc, accelerator, epics, tango, apptainer]
---

# dt4acc Digital Twin

This umbrella skill covers the full dt4acc Digital Twin lifecycle: host-side validation, EPICS/TANGO runtime paths, container deployment, and reliability testing.

---

## 1. Host-Side Smoke Test (Run First!)

**Purpose**: Validate core dt4acc code health before touching EPICS, TANGO, or containers. Separates **code regressions** from **deployment regressions**.

**What it verifies**:
1. `dt4acc-lib` installs and unit tests pass (16 tests)
2. `lat2db` converts BESSY II JSON lattice into pyAT sequence
3. `dt4acc` loads packaged BESSY II resources
4. `SimulatorBackend` computes tune/track/twiss on host
5. `CommandRewriter` translates lattice commands to device commands
6. `TranslatingCommandExecutionEngine` applies perturbation, changes tune, restores baseline

**Repository layout**:
```
/tmp/dtwin-build/
├── dt4acc/
├── dt4acc-lib/
├── lat2db/
├── run_dtwin_host_smoke_test.sh
└── dtwin_host_smoke_test.py
```

**Run**:
```bash
/tmp/dtwin-build/run_dtwin_host_smoke_test.sh /tmp/dtwin-build
```

**Expected success**:
```
== running dt4acc-lib tests ==
16 passed
== running host-side dtwin smoke test ==
lattice_elements: 1093
track_points: 1094
twiss_points: 1094
device_translation: Q1PDR.set_current -> 16 lattice target(s)
success: True
```

**If this passes but EPICS/TANGO/container fails → the problem is deployment, not code.**

---

## 2. EPICS Runbook (Fastest Path)

**Why EPICS first**: Developers report EPICS startup is faster than TANGO. Avoids TANGO DB container, private SOLEIL data, and extra runtime wiring.

**Steps**:
```bash
# 1. Create venv
cd /tmp/dtwin-build
python3 -m venv .venv-dt4acc-epics
source .venv-dt4acc-epics/bin/activate

# 2. Install deps and local repos
python3 -m pip install transitions accelerator-toolbox softioc p4p
python3 -m pip install -e /tmp/dtwin-build/dt4acc-lib
python3 -m pip install -e /tmp/dtwin-build/lat2db
python3 -m pip install -e /tmp/dtwin-build/dt4acc

# 3. Run smoke test first
/tmp/dtwin-build/run_dtwin_host_smoke_test.sh /tmp/dtwin-build

# 4. Start EPICS twin (foreground interactive)
cd /tmp/dtwin-build/dt4acc
python scripts/bessyii/dt4acc_softioc.py
```

**Verify**: At the `>>>` prompt, run `dbl()` to list PVs.

**Acceptable warning**: `Environment variable MONGODB_URL is not defined, using default: mongodb://localhost:27017/bessyii` — fine for public EPICS path.

**Known behavior**: Uses `softioc.interactive_ioc(globals())` → foreground interactive is safest; headless/background may be fragile.

---

## 3. TANGO Runbook (SOLEIL-Specific)

**Critical extras vs EPICS**:
1. **Tango DB container** must start first:
   ```bash
   apptainer run oras://gitlab-registry.synchrotron-soleil.fr/software-control-system/containers/apptainer/tango:latest
   ```
2. **Private SOLEIL data** must exist locally:
   ```
   ~/Documents/dt4acc_soleil_twin_data
   ```

**Debug order**:
1. Validate public/core stack (smoke test)
2. Confirm Tango DB container running
3. Confirm private data directory present
4. Only then start/debug TANGO twin

**TANGO code location**: `src/dt4acc/custom_tango/ioc/` (server_manager.py, single_server.py, devices/)

---

## 4. Apptainer/SIF Container Setup

**Important**: Pre-built images from registry are **AMD64 only**. ARM64 hosts must build from source.

**Build from source**:
```bash
cd /tmp
git clone https://codebase.helmholtz.cloud/digital-twins-for-accelerators/containers/pyat-softioc-digital-twin.git dtwin-build
cd dtwin-build
git submodule update --init --recursive
# (nested submodule in lat2db/scripts/bessy2reflat may fail — ignore)

# Fix broken uuid.py BEFORE building (CRITICAL)
# Add to sdef %post section:
find /twin/python/venv/lib/python3.12/site-packages -name 'uuid.py' \
  -exec cp /usr/lib/python3.12/uuid.py {} \; 2>/dev/null || true

apptainer build --fakeroot pyat-as-twin-softioc.sif recipies/pyat-as-twin-softioc.sdef
```

**Run**:
```bash
cd /tmp/dtwin-build
nohup apptainer run --cleanenv pyat-as-twin-softioc.sif </dev/null > /tmp/dtwin-ioc.log 2>&1 &
sleep 10; tail -20 /tmp/dtwin-ioc.log
```

**Verify IOC running**: Look for `✓ All initialization complete`, `✓ PVXS QSRV2 is loaded`

**Test PV access**:
```bash
apptainer exec --cleanenv pyat-as-twin-softioc.sif \
  /twin/python/venv/bin/python3 -c "from p4p import listRefs; import time; time.sleep(2); refs = listRefs(); print(f'Found {len(refs)} PVs')"
```

**PV constraints**: Container p4p is **server-side only** — use `listRefs()` inside container, `pvget`/`pvput` from host. `--network host` requires root.

---

## 5. Container Troubleshooting

### Characteristic crash: `TypeError: Accelerator.__init__() missing 1 required keyword-only argument: 'energy'`
**Cause**: MongoDB has no accelerator data loaded.

**Fix for HIFIS Docker path**:
```bash
cd /tmp/dt4acc-docker
docker compose -f docker-compose.yml -f docker-compose-hifis.yml up -d
```

### Stale mounts block new starts
```bash
fuser -km /tmp/apptainer/mnt/*/mount 2>/dev/null
pkill -9 -f squashfuse 2>/dev/null
```

### IOC startup crashes (zero logs)
**Cause**: `softioc.interactive_ioc(globals())` opens blocking Python `>>>` prompt. With `</dev/null`, script may exit silently.

**Fix**: SIF is read-only — patch via sdef `%post` or bind-mount a patched startup script. Check imports first:
```bash
apptainer exec --cleanenv pyat-as-twin-softioc.sif /twin/python/venv/bin/python3 -c "from dt4acc.custom_epics.ioc.server import *"
```

---

## 6. Burn-in Tests

Run after IOC is running and PVs are discovered:
```bash
# Create burn-in script on host, then execute inside container
apptainer exec --cleanenv \
  --bind /tmp/dtwin_burnin_test.py:/dtwin_burnin_test.py \
  pyat-as-twin-softioc.sif \
  /twin/python/venv/bin/python3 /dtwin_burnin_test.py 2>&1 | tee /tmp/dtwin_burnin_output.txt
```

**Success criteria**:
- [ ] IOC starts cleanly with "All initialization complete"
- [ ] `listRefs()` returns > 0 PVs
- [ ] 1000 iterations without fatal errors
- [ ] Error count < 1% of total operations
- [ ] Write-Read echo values match
- [ ] Sustained throughput > 100 reads/sec

---

## Recommended Debug Order

1. **Host smoke test** → separates code vs deployment issues
2. **EPICS startup** → fastest working path
3. **TANGO tests** → only if you specifically need TANGO device-server workflow
4. **Apptainer/SIF workflow** → for containerized deployment
5. **Burn-in tests** → verify reliability after runtime works

## Known Pitfalls
1. Do this before container debugging
2. Do not require MongoDB for the first smoke test
3. Do not assume public repos alone are enough for SOLEIL TANGO
4. Do not skip the uuid.py fix in sdef
5. Do not assume headless EPICS startup is reliable
6. Container filesystem is read-only at runtime
7. EPICS CA uses UDP broadcasts — don't cross container boundaries without `--network host`
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
