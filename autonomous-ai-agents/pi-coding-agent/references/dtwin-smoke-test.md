# dtwin smoke-test reference

Why this exists
- Practical notes captured during a pi agent run that triaged and partially fixed pytest collection failures in AstroAgentAssistant.
- Meant to be referenced by the `pi-coding-agent` skill when creating delegate_task payloads for implementers working on similar host-smoke-test failures.

Reproduction (minimal)
1. Repo: AstroAgentAssistant (root path used in example: /home/hermes/tmp/AstroAgentAssistant)
2. Python: 3.11.x; use a venv inside the repo: `python3 -m venv .venv` and activate it.
3. Run `pytest -q --maxfail=1 --showlocals` to reproduce import-time collection errors. Save logs to /tmp.

Common failure modes and fixes
- Missing 'at' import
  - Cause: The repository expects the Accelerator Toolbox API available as a top-level `at` package. The PyPI package named `at` is unrelated and Python2-only; do NOT use it.
  - Fixes:
    1. Preferred: install or provide a pyAT-compatible package that exposes `at` (if available in your environment). If upstream provides `pyat` which exposes the expected top-level names, prefer installing it into the venv.
    2. Safe triage: add a temporary local shim package `at/` that re-exports from `pyat` when present and otherwise supplies minimal stubs for `Lattice` and `All` so pytest collection can proceed. The shim MUST be reviewed and removed once the real dependency is present.
- Missing dt4acc, dt4acc-lib, lat2db
  - Cause: Smoke tests expect local checkouts of these repos (or packages installed into the venv).
  - Fixes:
    1. Preferred: clone the three repositories under a DTWIN_ROOT (example: /tmp/dtwin-build) and perform editable installs:
       - pip install -e /tmp/dtwin-build/dt4acc
       - pip install -e /tmp/dtwin-build/dt4acc-lib
       - pip install -e /tmp/dtwin-build/lat2db
    2. Alternative: if packages are published, pip install dt4acc dt4acc-lib lat2db into the venv.

Temporary shim pattern (example)
- File: at/__init__.py
- Behavior: try import pyat and re-export Lattice, All; if missing, provide tiny fallback stubs (Lattice implements __len__, enable_6d, set_cavity_phase, get_optics; All is a sentinel object).
- Constraints: shim only helps collection; runtime tests that exercise accelerator simulation will still require full implementations.

Flow for pi subagent runs (recommended)
1. Reproduce: pytest --collect-only, save logs
2. If missing external deps: ask for approval to either (A) clone dt4acc family repos under DTWIN_ROOT or (B) pip-install published packages
3. If quick triage needed: create temporary at/ shim + conftest.py and run collection again to see next missing deps
4. When real deps are provided, remove shim and re-run full tests

Artifacts to save
- /tmp pytest logs (collect and full run)
- branch name and local commit SHAs for any shim or test-only changes
- commit diffs for review
- recorded DTWIN_ROOT path and commit SHAs of cloned checkouts

Caveats
- Do not add long-lived shims to main branches. Prefer local branches for temporary changes and revert once environment is set up.
- The PyPI 'at' package is NOT the Accelerator Toolbox; installing it can introduce Python2 syntax errors and confusion.
