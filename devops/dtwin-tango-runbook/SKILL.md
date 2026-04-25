---
name: dtwin-tango-runbook
description: SOLEIL-oriented TANGO runbook for dt4acc, including Tango DB container startup, private data prerequisites, and the recommended debug order after the public host smoke test.
version: 1.0.0
---

# dtwin-tango-runbook

Use this runbook when the goal is to start or debug the **TANGO version** of the `dt4acc` digital twin.

## Trigger Conditions
- User wants to run the SOLEIL TANGO twin
- User wants to debug TANGO startup
- User asks why the public repos are not enough for the TANGO path
- User already validated the public/core stack and now needs the facility-specific TANGO stage

## Key Difference vs EPICS
The TANGO path is **not** the fastest current startup path.

Developers report that, for now, the **EPICS version starts faster**. Use TANGO only when you specifically need the TANGO device-server workflow.

## Critical Extra Prerequisites
The public repos alone are **not sufficient** for the SOLEIL TANGO twin.

You additionally need:

### 1. Tango DB container running first
```bash
apptainer run oras://gitlab-registry.synchrotron-soleil.fr/software-control-system/containers/apptainer/tango:latest
```

### 2. Private SOLEIL data present locally
```text
~/Documents/dt4acc_soleil_twin_data
```

This data is intentionally **not in git**, because the SOLEIL lattice/configuration is not public.

## Recommended Debug Order
1. Validate the public/core stack first with the host smoke test
2. Confirm the Tango DB container is running
3. Confirm `~/Documents/dt4acc_soleil_twin_data` exists and is populated
4. Only then start/debug the TANGO twin

## Step 1: Validate the public/core stack first
Before touching TANGO, run:
```bash
/tmp/dtwin-build/run_dtwin_host_smoke_test.sh /tmp/dtwin-build
```

If this fails, fix the public/core stack first. Do **not** start with TANGO debugging.

## Step 2: Start Tango DB container
In a dedicated terminal:
```bash
apptainer run oras://gitlab-registry.synchrotron-soleil.fr/software-control-system/containers/apptainer/tango:latest
```

Keep it running.

## Step 3: Verify private data directory
Check:
```bash
test -d ~/Documents/dt4acc_soleil_twin_data && echo OK || echo MISSING
```

If missing, the SOLEIL TANGO twin cannot be expected to start correctly.

## Step 4: Prepare Python environment
If using the local-repo workflow:
```bash
cd /tmp/dtwin-build
python3 -m venv .venv-dt4acc-tango
source .venv-dt4acc-tango/bin/activate
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install -e /tmp/dtwin-build/dt4acc-lib
python3 -m pip install -e /tmp/dtwin-build/lat2db
python3 -m pip install -e /tmp/dtwin-build/dt4acc
```

You will also need the TANGO-specific Python/runtime pieces appropriate to the developer workflow in use.

## Step 5: Start/debug the TANGO server path
The public repo contains the TANGO code under:
```text
src/dt4acc/custom_tango/ioc/
```

Relevant components include:
- `server_manager.py`
- `single_server.py`
- device setup / controller modules under `devices/`

The integration tests in:
```text
dt4acc/tests/tango_tests/
```
show the intended behavior and expected device model.

## What TANGO Tests Intend To Validate
The TANGO tests cover:
- device export/reachability
- twiss/orbit/tune propagation
- quadrupole write → recalculation
- steerer kick → orbit change
- reset behavior after divergence

These tests are meaningful only after the TANGO runtime prerequisites are satisfied.

## Fast TANGO Triage Checklist
If the TANGO twin does not start, check these in order:

### A. Public/core stack healthy?
```bash
/tmp/dtwin-build/run_dtwin_host_smoke_test.sh /tmp/dtwin-build
```

### B. Tango DB running?
Was this started first?
```bash
apptainer run oras://gitlab-registry.synchrotron-soleil.fr/software-control-system/containers/apptainer/tango:latest
```

### C. Private SOLEIL data present?
```bash
ls -ld ~/Documents/dt4acc_soleil_twin_data
```

### D. TANGO-specific env/runtime configured?
Check `TANGO_HOST`, developer instructions, and whatever startup wrapper the current developer branch expects.

## What Not To Assume
1. Do **not** assume public GitHub repos alone are enough for the SOLEIL TANGO path.
2. Do **not** interpret a TANGO startup failure as proof that `dt4acc` itself is broken.
3. Do **not** start with TANGO when EPICS would answer the user’s immediate need faster.
4. Do **not** skip the Tango DB container step.

## Upstream Documentation Note
Developers are improving the `dt4acc` READMEs on:
- `dt4acc/dt4acc:dev/feature/updated-readme`

But they also said this is **not fully ready yet**, because required PRs still need to land in `dev/main`.

So for the TANGO path, prefer direct developer guidance over assuming the README branch is already the final stable workflow.

## Recommended Practical Strategy
- If the user wants something working quickly: use `dtwin-epics-runbook`
- If the user specifically needs SOLEIL TANGO: use this runbook and verify the private prerequisites first

## Related Skills
- `dtwin-epics-runbook` — faster current path
- `dtwin-host-smoke-test` — validate public/core stack before TANGO
- `dt4acc-container-troubleshooting` — TANGO/container prerequisite issues
- `dtwin-setup` — broader dtwin setup context
