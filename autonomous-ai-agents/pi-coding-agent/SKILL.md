---
name: pi-coding-agent
description: "Reusable Hermes skill: spawn a focused 'pi' coding subagent to run tests, implement fixes, and run reviewers using a safe, TDD-first workflow."
version: 1.1.0
author: Hermes Agent (Hermi)
license: MIT
metadata:
  hermes:
    tags: [subagent, automation, test-driven, ci, review]
---

# pi-coding-agent

Purpose
- Provide a reusable, auditable template for spawning a "pi" coding agent (subagent) that runs tests, attempts minimal fixes, and runs spec/quality reviews following the subagent-driven-development pattern.

Why use it
- Standardises how we dispatch implementer + reviewer subagents
- Saves and verifies artifacts (pytest logs, branch, commit SHA, diffs)
- Enforces safety gates (branch only, limited fix attempts, no system installs without explicit approval)

What the skill provides
- A clear checklist (TDD -> implement -> spec review -> quality review -> integration)
- Example delegate_task payloads and templates under `templates/`
- Verification and artifact collection steps
- A references/ directory for session-specific recipes and common external-dependency pitfalls

Quick start
1. Load the skill in any run that will orchestrate subagents:
   - `skill_view("pi-coding-agent")` to read this doc
2. Use the included `templates/delegate_task_payload.json` as a starting point for implementer or reviewer tasks.
3. Edit the template `context` fields to describe the exact failing test, repo path, and commands.

Defaults / safety
- Workdir: must be provided by caller (absolute path)
- Branch naming: pi/auto-fix-<timestamp>
- Max automated attempts per failing test: 3
- Toolsets used by default: ["terminal","file"]
- No network installs or privileged operations without explicit human approval

Templates (where to find them)
- templates/delegate_task_payload.json — JSON skeleton for delegate_task implementer/reviewer
- templates/implementer-checklist.txt — concise list of steps the implementer subagent should follow

Verification artifacts (what the pi agent will produce)
- /tmp/pi-<repo>-pytest-<ts>.txt — full pytest output
- git branch name and local commit SHA(s)
- git diff --name-only and small patch snippets
- concise runbook with commands and exit codes

Example usage (high level)
- Create a controller session that reads the failing test/traces
- Fill `templates/delegate_task_payload.json` with: goal, context (spec + failing trace + where to edit), workdir, toolsets
- Call `delegate_task(...)` with the payload
- On completion: verify artifacts written and, if tests still fail, dispatch another implementer run (up to 3 attempts)

Session-learned patterns (new)
- External-dep smoke-tests are common in hardware/host integration repos. When tests import packages like `at` or expect local checkouts (dt4acc, dt4acc-lib, lat2db), the controller should not attempt global installs by default.
- Preferred safe triage pattern:
  1. Reproduce: run `pytest -q --collect-only` to capture import/collection errors and save to /tmp.
  2. Narrow: run `pytest -q -k "not <smoke-dir-or-tag>"` to exercise pure-Python unit tests while you prepare host deps.
  3. Prepare host deps only after explicit approval: either create an isolated .venv and install user-approved packages, or prepare a DTWIN_ROOT with local checkouts and run the repo-provided wrapper script.

Pitfalls and gotchas (to include in delegate payloads)
- "No module named 'at'" often means the pyAT toolbox isn't installed or the test expects a local workspace with dt4acc repos. Do NOT assume a single pip install fixes everything — smoke-tests frequently need local checkouts and data files.
- Running `pytest` at repo root can trigger host-level smoke-tests in multiple directories (e.g., dtwin-host-smoke-test and science/dtwin-host-smoke-test). Narrow selection with -k or by path to avoid noisy collection errors.
- If a smoke-test script contains a _resolve_repo_root() that raises SystemExit when required repos are missing, automated subagents must capture that behaviour and fail gracefully.

References
- See `references/dtwin-smoke-test.md` for a session-specific reproduction recipe, exact pytest output sample, and three safe remediation options (skip, minimal venv install, prepare DTWIN_ROOT + run wrapper script). Use that document when creating delegate_task context for implementers.

Support files added in this session
- references/dtwin-smoke-test.md — practical reproduction steps, common fixes (at shim, DTWIN_ROOT), and artifact checklist.

Notes for maintainers
- Keep templates small and explicit. Subagents should NOT be allowed to read the entire repo by default — give them only the file paths they need.
- If you want CI integration (push branch, open PR), require an explicit separate approval step.
- When a session surfaces a recurring external-dependency pattern (like dtwin smoke-tests), add a new references/<topic>.md entry and point to it from this SKILL.md.

