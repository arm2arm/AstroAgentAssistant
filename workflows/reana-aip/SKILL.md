---
name: reana-aip
description: Create REANA workflows using AIP conventions, approved environments, and reproducible workflow structure.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [reana, workflow, reproducibility, astronomy]
    category: workflows
    related_skills: [reana-shboost24]
---

# REANA AIP Workflow

## When to Use
Use this skill when preparing a REANA workflow under AIP conventions.

## Procedure
1. Create a dedicated local workflow directory.
2. Use an approved environment from the AIP REANA environments repository.
3. Set memory to 32GB by default unless explicitly changed.
4. Include all required scripts as workflow inputs.
5. Prefer `reana-client run -w <name>` with the local folder context.

## Pitfalls
- Do not invent custom environments.
- Do not omit external scripts from workflow inputs.

## Verification
- `reana.yaml` references an approved environment.
- Memory is set to 32GB unless intentionally overridden.
