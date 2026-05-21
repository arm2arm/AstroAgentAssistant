---
name: opencode-lumi
description: "Hermes skill wrapper for running Lumi / opencode configs (project: lumi-assistant). Provides one-shot and interactive helpers and enforces safe defaults."
version: 0.1.1
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [opencode, lumi, autonomous, coding, wrapper]
---

# opencode-lumi

This skill provides small Hermes-friendly wrappers and templates to run the Lumi (lumi-assistant) opencode configuration located at /home/hermes/tmp/lumi-assistant. It supports:

- One-shot runs: call opencode run "prompt" with the project's config loaded.
- Interactive TUI launches (background, pty) for iterative work.
- A safe default binary resolver that prefers $HOME/.local/bin/opencode.

Usage examples (Hermes terminal tool):

- One-shot (no PTY):
  terminal(command='OPENCODE_CONFIG=/home/hermes/tmp/lumi-assistant/config/opencode.json $HOME/.local/bin/opencode run "Review this README"')

- Launch interactive TUI:
  terminal(command='OPENCODE_CONFIG=/home/hermes/tmp/lumi-assistant/config/opencode.json $HOME/.local/bin/opencode', background=true, pty=true)

Added scripts:
- scripts/run_opencode_one_shot.sh
- scripts/launch_opencode_interactive.sh
- scripts/review_pr.sh

Safety and permissions
- The skill will not change opencode permissions. It surfaces whether opencode auth is configured and reports denied actions from opencode.

