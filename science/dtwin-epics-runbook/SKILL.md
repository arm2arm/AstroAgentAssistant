---
name: dtwin-epics-runbook
description: EPICS-first runbook for dt4acc using the current local-repo workflow, with host-side smoke test first and direct EPICS startup for the faster path.
version: 1.0.0
---

# dtwin-epics-runbook

Use this runbook when the goal is to get **dt4acc running via EPICS first**.

This is currently the preferred path because the developers report that **EPICS startup is faster** than the TANGO route.

## Trigger Conditions
- User wants to run `dt4acc` quickly
- User wants the fastest current dtwin startup path
- User wants to avoid the extra TANGO prerequisites
- User wants a practical workflow for the repos already present on disk

## Why EPICS First
Compared with the SOLEIL TANGO setup, the EPICS path avoids these extra prerequisites:
- Tango DB container
- private SOLEIL data in `~/Documents/dt4acc_soleil_twin_data`
- additional TANGO runtime wiring

## Current Recommended Order
1. Run the host smoke test first
2. Start the EPICS version in the foreground
3. Inspect PVs interactively
4. Only then move on to TANGO or containers if needed

## Expected Repository Layout
```text
/tmp/dtwin-build/
├── dt4acc/
├── dt4acc-lib/
└── lat2db/
```

## Step 1: Create and activate a venv
```bash
cd /tmp/dtwin-build
python3 -m venv .venv-dt4acc-epics
source .venv-dt4acc-epics/bin/activate
```

## Step 2: Install dependencies and local repos
```bash
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install transitions accelerator-toolbox softioc p4p
python3 -m pip install -e /tmp/dtwin-build/dt4acc-lib
python3 -m pip install -e /tmp/dtwin-build/lat2db
python3 -m pip install -e /tmp/dtwin-build/dt4acc
```

## Step 3: Run the public/core smoke test first
```bash
/tmp/dtwin-build/run_dtwin_host_smoke_test.sh /tmp/dtwin-build
```

### Expected success indicators
- `dt4acc-lib` tests pass
- lattice loads successfully
- tune changes after perturbation
- final line shows `success: True`

If this passes, then the core public stack is healthy and later failures are more likely EPICS runtime/startup issues than code regressions.

## Step 4: Start the EPICS twin directly
```bash
source /tmp/dtwin-build/.venv-dt4acc-epics/bin/activate
cd /tmp/dtwin-build/dt4acc
python scripts/bessyii/dt4acc_softioc.py
```

## Step 5: Verify the IOC is alive
At the interactive prompt, run:
```python
dbl()
```

This should list available PVs.

Also watch for startup messages such as:
- `All PVs set up`
- `iocRun: All initialization complete`
- `PVXS QSRV2 is loaded`
- `Running server`

## Important Current Behavior
The EPICS startup path currently uses:
```python
softioc.interactive_ioc(globals())
```

This means:
- **foreground interactive launch is the safest mode**
- headless/background startup may be fragile
- seeing a Python prompt `>>>` is expected

## Known Acceptable Warning
You may see:
```text
Environment variable MONGODB_URL is not defined, using default: mongodb://localhost:27017/bessyii
```

For the current BESSY II public EPICS path, this warning is acceptable if startup otherwise succeeds.

## Fast Troubleshooting

### Check imports
```bash
python -c "import dt4acc.custom_epics.ioc.server; print('server import OK')"
```

### Re-run the smoke test
```bash
/tmp/dtwin-build/run_dtwin_host_smoke_test.sh /tmp/dtwin-build
```

### Restart EPICS in foreground
```bash
cd /tmp/dtwin-build/dt4acc
python scripts/bessyii/dt4acc_softioc.py
```

## Upstream Note
A cleaner upstream install flow is being prepared on:
- `dt4acc/dt4acc:dev/feature/updated-readme`

The developers indicate it is **not yet fully merged into `dev/main`**. The likely future install flow will be:
```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install \
   "dt4acc-lib @ git+https://github.com/dt4acc/dt4acc-lib.git" \
   "dt4acc[epics,bessyii] @ git+https://github.com/dt4acc/dt4acc.git"

dt4acc_bessyii
```

Treat that as near-future guidance until the pending PRs are merged.

## Pitfalls
1. Do **not** start with TANGO if your goal is the fastest path.
2. Do **not** interpret a TANGO failure as a dt4acc core failure before running the host smoke test.
3. Do **not** assume headless EPICS startup is reliable yet.
4. Do **not** expect the SOLEIL TANGO path to work from public repos alone.

## Related Skills
- `dtwin-host-smoke-test` — validates the core public stack first
- `dtwin-setup` — broader container/Apptainer workflow
- `dt4acc-container-troubleshooting` — container and TANGO troubleshooting
