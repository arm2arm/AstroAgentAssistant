---
name: dtwin-host-smoke-test
description: Reproducible host-side smoke test for the dt4acc digital twin stack using local dt4acc, dt4acc-lib, and lat2db repos without MongoDB, TANGO, or Apptainer.
version: 1.0.0
---

# dtwin-host-smoke-test

Run a **reproducible host-side smoke test** for the current GitHub `dt4acc` stack.

This validates the core digital-twin logic without requiring:
- MongoDB
- TANGO
- Apptainer / SIF images
- container networking

It is the **fastest verified first check** before debugging containerized or facility-integrated deployment paths.

## Trigger Conditions
- User asks to sanity-check `dt4acc`, `dt4acc-lib`, or `lat2db`
- User wants to know whether the current digital-twin code still works
- User wants a reproducible smoke test before trying EPICS/TANGO/container workflows
- User reports dtwin startup issues and you need to separate **core-code health** from **deployment issues**

## What This Smoke Test Verifies
1. `dt4acc-lib` installs and its unit tests pass
2. `lat2db` converts the packaged BESSY II JSON lattice into a pyAT sequence
3. `dt4acc` can load its packaged BESSY II resources directly from the repo
4. `SimulatorBackend` can compute tune / track / twiss on the host
5. `CommandRewriter` can translate a lattice quadrupole command to a device current command
6. `TranslatingCommandExecutionEngine` can apply a magnet perturbation, change tune, and restore baseline

## Repository Layout Expected
By default the scripts expect:

```text
/tmp/dtwin-build/
├── dt4acc/
├── dt4acc-lib/
├── lat2db/
├── run_dtwin_host_smoke_test.sh
└── dtwin_host_smoke_test.py
```

You may also pass a different repo root as the first argument.

## Included Files
- `scripts/run_dtwin_host_smoke_test.sh`
- `scripts/dtwin_host_smoke_test.py`

## Quick Start

### 1. Copy or link the helper scripts into your repo root

If you want the exact verified versions from this skill, write them out from the skill files or use the already-created copies under `/tmp/dtwin-build/`.

### 2. Run the wrapper

```bash
/tmp/dtwin-build/run_dtwin_host_smoke_test.sh /tmp/dtwin-build
```

Or from another root:

```bash
/path/to/run_dtwin_host_smoke_test.sh /path/to/dtwin-root
```

## What the Wrapper Does

The shell wrapper:
1. creates a dedicated virtual environment
2. installs the verified Python dependencies
3. installs local editable versions of:
   - `dt4acc-lib`
   - `lat2db`
   - `dt4acc`
4. runs the `dt4acc-lib` test suite
5. runs the host-side dtwin smoke test

## Expected Successful Output

Look for output similar to:

```text
== running dt4acc-lib tests ==
16 passed

== running host-side dtwin smoke test ==
lattice_elements: 1093
track_points: 1094
twiss_points: 1094
device_translation: Q1PDR.set_current -> 16 lattice target(s)
success: True
```

A JSON results file should be written to:

```text
/tmp/dtwin-build/dtwin_smoke_test_results.json
```

## Interpretation

If this smoke test passes, then the following are working:
- local package installation
- packaged BESSY II lattice/config resources
- pyAT optics calculation
- dt4acc backend logic
- command translation and command execution engine

If a later **EPICS**, **TANGO**, **MongoDB**, or **container** workflow fails, the problem is likely in the deployment/runtime layer rather than the core host-side logic.

## Troubleshooting

### Issue: `dt4acc-lib` tests fail
This usually means a true library regression in the current repos. Start with the failing test names before touching deployment code.

### Issue: `ModuleNotFoundError`
Ensure the wrapper installed editable local repos successfully:
- `dt4acc-lib`
- `lat2db`
- `dt4acc`

### Issue: lattice JSON not found
Check this file exists:

```text
<repo-root>/dt4acc/src/dt4acc/custom_facility/bessyii/resources/storage_ring/input/bessy2_storage_ring_reflat.json
```

### Issue: no tune change after perturbation
That indicates the command translation / backend update / optics recalculation chain is broken. Investigate:
- `dt4acc_lib/bl/command_rewritter.py`
- `dt4acc/core/bl/translating_command_execution_engine.py`
- `dt4acc_lib/pyat_simulator/simulator_backend.py`
- BESSY II lookup tables under `resources/storage_ring/created/`

### Issue: MongoDB warning appears
A warning like this can still appear:

```text
Environment variable MONGODB_URL is not defined, using default: mongodb://localhost:27017/bessyii
```

That is acceptable for this smoke test. The current host-side path uses packaged repo resources and does **not** require a running MongoDB instance.

## Known Good Observations From Verification
During verification on this system:
- Python 3.12.3
- Apptainer 1.4.5 installed (not required for this smoke test)
- `dt4acc-lib` tests: **16 passed**
- lattice elements: **1093**
- track points: **1094**
- twiss points: **1094**
- example translation: `Q1M2D1R -> Q1PDR.set_current`
- inverse mapping count for that device command: **16 lattice targets**
- tune changed after perturbation and returned exactly to baseline after restore

## Pitfalls
1. **Do this before container debugging.** It cleanly separates code regressions from deployment regressions.
2. **Do not require MongoDB for this first smoke test.** That is unnecessary for the verified host-side path.
3. **This does not validate TANGO.** The TANGO integration tests are a separate stage and may require extra non-public SOLEIL inputs.
4. **The SOLEIL TANGO twin needs external prerequisites not present in the public repos:**
   - start the Tango DB container first:
     ```bash
     apptainer run oras://gitlab-registry.synchrotron-soleil.fr/software-control-system/containers/apptainer/tango:latest
     ```
   - ensure SOLEIL configuration/lattice data exists in:
     ```text
     ~/Documents/dt4acc_soleil_twin_data
     ```
5. **This does not validate headless EPICS launch behavior.** `softioc.interactive_ioc(globals())` can still be fragile in headless contexts even if this smoke test passes.
6. **lat2db may install an external `uuid` package, but the host smoke test should still import the standard-library `uuid`.** If needed, verify with:
   ```bash
   python -c "import uuid; print(uuid.__file__)"
   ```

## Recommended Next Step After Success
After this smoke test passes, proceed in this order:
1. EPICS IOC startup check
2. TANGO server/integration tests
3. container / Apptainer workflow
4. facility-specific MongoDB-backed deployment

## Related Skills
- `dtwin-setup` — broader Apptainer/container workflow
- `dt4acc-container-troubleshooting` — MongoDB/container startup failures
- `dtwin-burnin-tests` — IOC burn-in after runtime startup works
