---
name: external-coder-orchestration
description: "Use when running multi-stage plans via external coding CLIs."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [orchestration, coding-agent, delegation, multi-stage, git]
    related_skills: [subagent-driven-development, deepseek-harness-dsh, opencode-workflow, claude-code, writing-plans]
---

# External Coder Orchestration

Run a **plan** (from writing-plans or a user brief) by dispatching **fresh sessions of an external coding agent CLI** — dsh, opencode, claude-code, codex, or pi — as **background terminal processes** (one bounded task per session), then **verify and commit each stage yourself**.

This is distinct from `delegate_task` (in-process Hermes subagents) and from running a coder once for a single task. It's for when the plan is large (many files / many concerns) and each unit should run in a clean context with an isolated blast radius.

## When to Use
- A multi-part plan must be executed in a real git repo by a coding agent.
- You want each stage in a fresh agent context (no drift from accumulated state) and committed independently.
- The agent is a long-running CLI (minutes to an hour per stage), so it must run in the background and you orchestrate around it.

**Do NOT use for:** a single bounded task (just run the coder once in the foreground); work with no reasoning (use execute_code); anything needing user interaction mid-run.

## Pre-flight (before the first stage)
1. **Tag + backup.** `git tag -a <name> -m "..." HEAD` and push a `backup/pre-<task>-<date>` branch. Multi-stage runs are long; you must be able to revert.
2. **Snapshot the dirty tree.** `git status --short`. Record the user's pre-existing modified/untracked files BY PATH. These stay out of every stage commit.
3. **Establish a test baseline.** Run the project's suite once and record the exact interpreter + command + pass count (e.g. `PYTHONPATH=src /path/venv/bin/python3 -m pytest tests -q` → `52 passed`). Every stage prompt gets this line.
4. **Decide the permission mode.** Agents default to approval-gated. For unattended background runs, the agent must be allowed to edit (e.g. dsh `DSH_PERMISSION_MODE=danger-full-access`); the blast radius is bounded by the ground rules below + per-stage commits.
5. **Do NOT let the agent rewrite shared-remote history** (filter-repo / BFG / force-push). Defer history surgery to an explicit user decision.

## Per-Stage Prompt Contract
Every stage prompt carries the same ground rules, then ONE bounded scope:
- "cd <repo> first."
- **(a)** NEVER `git commit`/`git push` — the orchestrator commits; git read-only (log/diff/show) is fine.
- **(b)** Do NOT touch the user's pre-existing dirty files — list them by exact path.
- **(c)** Tests must stay green — give the EXACT interpreter + command + baseline count; fix any breakage you cause.
- **(d)** Minimal diffs, match existing style.
- **Scoped, condition-gated destructive steps.** Phrase deletions as "delete X ONLY if you verify nothing imports X". A correct executor refuses when the condition fails — that refusal is right, not a failure.
- **End with a machine-scannable report:** every file added/changed/removed with a one-line reason + the final test-result line.
- **Bound the scope.** "Do NOT start on [later-stage items] — those are separate stages."

Run each stage as `terminal(background=true, notify_on_complete=true)` with a generous timeout. Continue working (or wait) between stages; never poll the agent's private session internals.

## Verify-Then-Commit (the core discipline)
**The agent's final report is a self-report, not verified fact.** Before committing a stage:
1. **Re-run the test suite yourself** with the venv interpreter. Confirm the pass count (or expected delta for test-adding stages).
2. **Spot-check the riskiest diffs** (`git diff <file>` for the algorithm-heavy or schema-changing edits) — not a full read.
3. **Verify claimed deletions/renames actually happened.** Real case: a stage reported a file "removed" that was still tracked on disk — the orchestrator had to finish the `git rm`. Executors also stop short of a claimed step or miscount cheap claims (page counts, file counts) — recompute those independently and cheaply (e.g. count PDF pages with pypdf, resolve all citation keys, run the CLI `--help`).
4. **Commit ONLY the stage's work, excluding the user's dirty files:**
   `git add -A -- . ':!path/to/user_file_a' ':!path/to/user_file_b'`
   then `git commit -m "stageN/<plan>: <scope> (agent-<name>-implemented)"`. Attribute the implementation to the agent + stage in the message.
5. Only then launch the next stage (it starts from a clean, committed base).

## Monitoring
- Watch `git status --short` / `git diff --stat` in the worktree and the process output for progress. Do NOT try to decode the agent's private session log (compressed/opaque format) — it wastes time and burns approval-gated commands.
- A healthy long run shows the worktree changing and the process alive; a silent process with a growing session file is usually still working. Give slow local-model runs real time before declaring a stall.

## Red Flags — Never
- Commit the user's pre-existing dirty files into a stage commit.
- Trust the agent's "done / deleted / N pages" without a cheap independent check.
- Let the agent push or rewrite shared-remote history.
- Peek into the agent's internal session store to monitor progress.
- Start stage N+1 while stage N has an unverified failure.
- Run one giant unbounded prompt — split the plan into stages with explicit "don't start later items" fences.

## Related
- `deepseek-harness-dsh`, `opencode-workflow`, `claude-code`, `codex` — how to actually run/configure each agent.
- `subagent-driven-development` — the in-process `delegate_task` variant with two-stage review.
- `writing-plans` — producing the plan this skill executes.
