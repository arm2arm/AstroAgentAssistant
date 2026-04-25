---
name: dtwin-burnin-tests
category: science
description: Run comprehensive burn-in tests on the dt4acc Digital Twin IOC to verify EPICS PV stability, throughput, and read/write resilience
---

# dtwin-burnin-tests

Run comprehensive burn-in tests on the dt4acc Digital Twin (dtwin) IOC.

## Prerequisites
- dtwin IOC running: `apptainer run --cleanenv pyat-as-twin-softioc.sif </dev/null > /tmp/dtwin-ioc.log 2>&1 &`
- IOC log shows "All initialization complete"
- SIF at: `/tmp/dtwin-build/pyat-as-twin-softioc.sif`

## Critical Known Issues

### IOC Startup Crashes (Zero Logs)
Primary known cause:
1. `softioc.interactive_ioc(globals())` opens the Python `>>>` console, which is fragile for headless/container launches and can exit immediately when stdin is closed.

**Current status note:** on the current GitHub `dt4acc`/`dt4acc-lib` code, `dt4acc.custom_epics.ioc.server` imports cleanly with `softioc` and `p4p` installed, so do **not** assume a missing `initialize_bpm_pvs` symbol is the root cause. Verify imports first, then focus on the launch path / interactive IOC behavior.

**Fix / first check:** SIF is read-only — patch via sdef `%post` or bind-mount a patched startup script if needed. Check imports first:
```bash
apptainer exec --cleanenv pyat-as-twin-softioc.sif /twin/python/venv/bin/python3 -c "from dt4acc.custom_epics.ioc.server import *"
```

### Stale Mounts Block New IOC Starts
Old Apptainer/squashfuse processes leave mounts blocking new starts.
**Kill stale processes:**
```bash
fuser -km /tmp/apptainer/mnt/*/mount 2>/dev/null
pkill -9 -f squashfuse 2>/dev/null
```

### PV Access Constraints
- Container p4p is **server-side only** — no `Client` class inside container
- Use `listRefs()` from inside the container
- Use `pvget`/`pvput` from host for client operations
- `--network host` requires root/sudo (cannot use without sudo)

## Test Procedure

### Step 1: Verify IOC Running
```bash
tail -20 /tmp/dtwin-ioc.log
# Look for: "✓ iocRun: All initialization complete"
```

### Step 2: Discover PVs
```bash
apptainer exec --cleanenv pyat-as-twin-softioc.sif /twin/python/venv/bin/python3 -c "
from p4p import listRefs
import time
time.sleep(2)
refs = sorted(listRefs())
print(f'Total PVs: {len(refs)}')
for ref in refs:
    print(ref)
"
```

### Step 3: Run Burn-in Test Script
Create `/tmp/dtwin_burnin_test.py` on host, then execute inside container:
```bash
apptainer exec --cleanenv \
  --bind /tmp/dtwin_burnin_test.py:/dtwin_burnin_test.py \
  pyat-as-twin-softioc.sif \
  /twin/python/venv/bin/python3 /dtwin_burnin_test.py 2>&1 | tee /tmp/dtwin_burnin_output.txt
```

Burn-in script should:
- Read all PVs from `listRefs()` 
- Cycle read/write 1000 iterations over first 20 PVs
- Track: total reads, total writes, error count, throughput (reads/sec), read latency (min/max/avg)
- Write-read echo test: write a value, read it back, verify match
- Save results to `/tmp/dtwin_burnin_results.json`

### Step 4: Review Results
```bash
cat /tmp/dtwin_burnin_results.json | python3 -m json.tool
```

## Success Criteria
- [ ] IOC starts cleanly with "All initialization complete"
- [ ] `listRefs()` returns > 0 PVs
- [ ] 1000 iterations complete without fatal errors
- [ ] Error count < 1% of total operations
- [ ] Write-Read echo values match
- [ ] Sustained throughput > 100 reads/sec

## Related Skills
- `dtwin-setup` — Build and run the dtwin IOC