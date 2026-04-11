# AstroAgent Skills Repository

Reusable Hermes skills for astronomy, astroinformatics, reproducible workflows, and the AstroAgent Assistant setup.

This repository is organized as a shareable skills collection for Hermes Agent users.
It is intended to hold:
- procedural skills that encode repeatable workflows;
- supporting references, templates, and scripts;
- astronomy-specific operational knowledge that is useful during execution.

## Repository layout

- `astronomy/` — survey, archive, ADQL, S3, and dataset-specific skills
- `workflows/` — REANA and workflow-engine skills
- `python/` — plotting and analysis-code skills
- `infrastructure/` — Open WebUI, Hermes API server, deployment skills
- `research/` — literature-grounding and curated knowledge synthesis skills
- `agents/` — agent concepts and multi-agent orchestration skills

## Using this repository with Hermes

Add the repository as a tap:

```bash
hermes skills tap add arm2arm/AstroAgentAssistant-
```

Then search and install skills from it.

## Authoring rules

Every skill should contain:
- `SKILL.md`
- clear trigger conditions under `## When to Use`
- numbered `## Procedure`
- `## Pitfalls`
- `## Verification`

Optional support files:
- `references/`
- `templates/`
- `scripts/`
- `assets/`

## Initial starter skills

This repo starts with scaffolds for:
- SHboost24 CMD plotting
- StarHorse access
- gaia.aip.de ADQL usage
- data.aip.de S3 access
- REANA AIP workflows
- REANA SHboost24 workflows
- CMD plotting in Python
- seaborn paper plots
- Hermes ↔ Open WebUI integration
- Hermes API server setup
- 2026 agentic astronomy literature
