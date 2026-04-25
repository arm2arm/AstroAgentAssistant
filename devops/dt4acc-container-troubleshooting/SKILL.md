---
name: dt4acc-container-troubleshooting
description: "Debugging dt4acc digital twin containers — the twin requires accelerator lattice data in MongoDB to initialize, or use HIFIS pre-built images with BESSY II data pre-loaded."
version: 1.0.0
---

# Overview

The HIFIS / Docker dt4acc digital twin container path **requires accelerator lattice and configuration data** in MongoDB. Without it, that containerized path crashes on startup with:

```text
TypeError: Accelerator.__init__() missing 1 required keyword-only argument: 'energy'
```

**Important distinction:** the current GitHub `dt4acc` + `dt4acc-lib` repositories also support a lighter **host-side smoke-test path** that loads BESSY II lattice/configuration from packaged JSON/YAML resources (`bessy2_storage_ring_reflat.json` plus created lookup tables). For basic import, optics, translation, and command-execution smoke tests, MongoDB is **not** required.


## SOLEIL TANGO Twin Prerequisites

For the **TANGO version of the twin** used by the developers, there are extra prerequisites beyond the public Git repos:

1. **Start the Tango database container first**
   ```bash
   apptainer run oras://gitlab-registry.synchrotron-soleil.fr/software-control-system/containers/apptainer/tango:latest
   ```

2. **Provide the SOLEIL configuration data locally** in:
   ```text
   ~/Documents/dt4acc_soleil_twin_data
   ```

3. **Do not expect the SOLEIL lattice/configuration data in git.** It is intentionally not public, so a fresh clone of `dt4acc`/`dt4acc-lib` is not enough to run the TANGO twin end-to-end.

**Implication:** if host-side smoke tests pass but the TANGO twin still cannot start, first verify the Tango DB container is running and the local SOLEIL data directory is present.

**Developer guidance:** for the time being, prefer the **EPICS version** when you want the fastest startup path; the developers report startup is currently much faster there than in the TANGO path.

## Quick Start (HIFIS Pre-built)

The HIFIS GitLab repo at `https://codebase.helmholtz.cloud/digital-twins-for-accelerators/containers/` provides 20 pre-built versions with all dependencies.

### Running the HIFIS containers (BESSY II data pre-loaded)

```bash
cd /tmp/dt4acc-docker
docker compose -f docker-compose.yml -f docker-compose-hifis.yml up -d
```

This starts MongoDB with pre-loaded BESSY II data + dt4acc-twin.
Web UI: `http://localhost:5000`

## Common Problem: Empty interface / No active experiments

### Root cause
The dt4acc-twin container requires accelerator lattice and configuration data in MongoDB. Without it, the container crashes on startup — the `setup_accelerator()` function fails because no machine/energy is available.

### Debugging steps

1. **Check if twin container is actually running:**
   ```bash
   docker compose ps -a dt4acc-twin
   docker compose logs dt4acc-twin --tail=50
   ```

2. **Look for the characteristic crash:**
   ```
   TypeError: Accelerator.__init__() missing 1 required keyword-only argument: 'energy'
   ```
   This means MongoDB has no accelerator data loaded.

3. **Check MongoDB container:**
   ```bash
   docker compose ps -a mongodb-with-initial-files
   docker compose logs mongodb-with-initial-files --tail=20
   ```
   The container should say "done. Server is ready" and import `.dump` files.

### Data import: lat2db

The [`lat2db`](https://github.com/hz-b/lat2db) tool populates MongoDB with accelerator data:

```bash
lat2db --url mongodb://localhost:27017 --machine <machine_name> /path/to/lattice/
```

Imports: accelerator lattice (magnets, elements), BPM configs, orbit data, machine configurations.

## Architecture

```
MongoDB (port 27017) ← lattice data, machine configs, orbit data
    ↓
dt4acc-twin (port 5000) ← FastAPI backend, reads from MongoDB
    ↓
Web UI (port 5000) ← React frontend
```

## Container versions

HIFIS repo publishes images tagged `vX.Y.Z`. Check available tags at:
`https://codebase.helmholtz.cloud/digital-twins-for-accelerators/containers/digital-twin-for-accelerators/-/container_registry`

## Apptainer-based Workflow (pyat-softioc-digital-twin)

The `pyat-softioc-digital-twin` project (different from the pip-based `dt4acc`) packages the BESSY II digital twin as an **Apptainer container** using `pyAT` + `softioc`.

### Repository
`https://codebase.helmholtz.cloud/digital-twins-for-accelerators/containers/pyat-softioc-digital-twin`

### Attempting to Pull Pre-built Image

```bash
# Tag format uses hyphens (dots also tried, both failed on registry):
apptainer pull pyat-softioc-digital-twin.sif oras://registry.hzdr.de/digital-twins-for-accelerators/containers/pyat-softioc-digital-twin:v0-5-3
# Or direct run without pull:
apptainer run oras://registry.hzdr.de/digital-twins-for-accelerators/containers/pyat-softioc-digital-twin:v0-5-3.2898073
```

**⚠️ Known failure modes:**
- `MANIFEST_UNKNOWN` — tag doesn't exist or registry path is wrong
- **Architecture mismatch** — pre-built images are `amd64` only; if host is `arm64`/`aarch64`, Apptainer refuses to run them with `FATAL: ... the image's architecture (amd64) could not run on the host's (arm64)`
- OCI registry (`registry.hzdr.de`) may be unreachable from the host

### Building from Source (arm64 fallback)

When the pre-built image is unavailable or incompatible, build locally from the `.sdef` recipe:

1. **Clone the full repo with submodules:**
   ```bash
   git clone https://codebase.helmholtz.cloud/digital-twins-for-accelerators/containers/pyat-softioc-dtwin.git
   cd pyat-softioc-dtwin
   git submodule update --init --recursive
   # Note: nested submodule in lat2db/scripts/bessy2reflat may fail — ignore, main submodules work fine
   ```

2. **Fix the broken uuid.py BEFORE building** (critical step):
   
   The p4p/softioc packages ship a `uuid.py` with Python 2 syntax (`1<<32L`) that causes `SyntaxError` at runtime. Fix it in the `.sdef` `%post` section:
   
   ```bash
   # Add this to the %post section of recipies/pyat-as-twin-softioc.sdef (after pip install, before cleanup):
   find /twin/python/venv/lib/python3.12/site-packages -name 'uuid.py' -exec cp /usr/lib/python3.12/uuid.py {} \; 2>/dev/null || true
   ```
   
   This replaces any broken uuid.py in the container's site-packages with the system Python 3 version.

3. **Build the SIF image:**
   ```bash
   apptainer build pyat-as-twin-softioc.sif recipies/pyat-as-twin-softioc.sdef
   # Base: ubuntu:24.04, installs Python 3.12, pyAT, lat2db, bact-twin-architecture, dt4acc, softioc, p4p
   ```

4. **Run the twin:**
   ```bash
   apptainer run --cleanenv pyat-as-twin-softioc.sif
   ```

5. **Expected output:**
   - Warning: `MONGODB_URL` not set → uses default `mongodb://localhost:27017/bessyii`
   - Twiss/orbit calculation starts
   - `AcceleratorManager initialized successfully`
   - `All pvs set up`
   - `iocRun: All initialization complete`
   - EPICS 7.0.10.1-DEV loaded, PVXS QSRV2 enabled

6. **Interact via EPICS clients:**
   ```bash
   caget <pv_name>
   caput <pv_name> <value>
   pvget <pv_name>
   ```
   
   **Note:** EPICS CA uses UDP broadcasts. To see PVs from the host, you need host networking (`--network host` which requires root) or run EPICS tools from inside the container via `apptainer exec`.

**Known gotcha — interactive Python console:**
The `dt4acc_softioc.py` runs `softioc.interactive_ioc(globals())` which opens a Python `>>>` prompt after starting the IOC. This blocks clean headless operation. If running non-interactively, redirect stdin from `/dev/null`.

**Known gotcha — container filesystem is read-only:**
Apptainer SIF images are read-only at runtime. You cannot patch files inside the container at runtime (e.g., `cp uuid.py` via `apptainer exec` will fail with "Read-only file system"). The fix must be baked into the `.sdef` build process.

**Key files in .sdef:**
- `%runscript` runs `/twin/python/venv/bin/dt4acc_softioc.py`
- Python venv at `/twin/python/venv/`
- Packages installed from submodules: `lat2db/`, `bact-twin-architecture/`, `dt4acc/`

## Key files in dt4acc codebase

- `custom_epics/ioc/server.py` — EPICS IOC server (optional, for live control)
- `custom_epics/ioc/pv_setup.py` — PV setup from MongoDB config
- `core/command.py` — `setup_accelerator()` entry point
- `core/accelerators/pyat_accelerator.py` — PyAT-based lattice model
- `core/accelerators/accelerator_manager.py` — Accelerator object init (requires `energy` param)
