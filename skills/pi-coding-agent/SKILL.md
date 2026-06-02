---
name: pi-coding-agent
description: "Reusable Hermes skill: spawn a focused 'pi' coding subagent to run tests, implement fixes, and run reviewers using a safe, TDD-first workflow."
version: 1.0.0
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
- Enforces safety gates (branch only, limited fix attempts, no system installs)

What the skill provides
- A clear checklist (TDD -> implement -> spec review -> quality review -> integration)
- Example delegate_task payloads and templates under `templates/`
- Verification and artifact collection steps

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

Notes for maintainers
- Keep templates small and explicit. Subagents should NOT be allowed to read the entire repo by default — give them only the file paths they need.
- If you want CI integration (push branch, open PR), require an explicit separate approval step.

If you'd like, I can now:
- Customize the templates for a specific repo (provide path)
- Demonstrate the pi agent by running a one-off test run on a repo you name
- Add extra templates (linter-run, security-scan, test-mocks)
