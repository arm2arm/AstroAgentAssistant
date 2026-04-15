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
hermes skills tap add arm2arm/AstroAgentAssistant
```

Then search and install skills from it.

### Install examples

Browse/search:

```bash
hermes skills browse
hermes skills search shboost
hermes skills search reana
```

Install specific skills:

```bash
hermes skills install arm2arm/AstroAgentAssistant/astronomy/shboost24-cmd
hermes skills install arm2arm/AstroAgentAssistant/astronomy/gaia-aip-de-adql
hermes skills install arm2arm/AstroAgentAssistant/workflows/reana-aip
hermes skills install arm2arm/AstroAgentAssistant/infrastructure/openwebui-hermes
```

Suggested starter bundle for the current AIP-style setup:

```bash
hermes skills install arm2arm/AstroAgentAssistant/astronomy/data-aip-de-s3
hermes skills install arm2arm/AstroAgentAssistant/astronomy/shboost24-cmd
hermes skills install arm2arm/AstroAgentAssistant/workflows/reana-aip
hermes skills install arm2arm/AstroAgentAssistant/infrastructure/hermes-api-server
```

### Load a skill in a session

```bash
hermes -s shboost24-cmd
hermes -s reana-aip -s data-aip-de-s3
```

Or ask Hermes directly in chat to use a named skill.

## Security scanning

This repository includes a GitHub Actions workflow at:

- `.github/workflows/secret-scan.yml`

It runs `gitleaks` on:
- pushes to `main`
- pull requests
- manual workflow dispatch

This helps catch accidentally committed API keys, tokens, passwords, and private keys in both the working tree and git history available to the runner.

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

### Astronomy
- **rave-dr6** — RAVE DR6 TAP query via pyvo (nearest stars, RA/Dec, galactic projections)
- **gaia-aip-de-adql** — Gaia DR3 @AIP Daiquiri REST API (1.8B sources, async jobs)
- **shboost24-cmd** — SHboost24 CMD plotting with local Parquet caching
- **starhorse-access** — StarHorse distance estimation
- **data-aip-de-s3** — AIP S3 bucket access and dataset listing

### Workflows
- **reana-aip** — REANA workflows with AIP conventions (approved envs, 32GB memory)
- **reana-shboost24** — REANA workflows for SHboost24 CMD analysis
- **reana-serial-python** — REANA serial Python analysis template

### Python
- **cmd-plotting** — Colour-magnitude diagram plotting conventions
- **s3-parquet-sampling** — S3 Parquet sampling, local caching, and PNG plotting
- **seaborn-paper-plots** — Publication-quality seaborn figures

### Infrastructure
- **openwebui-hermes** — Hermes ↔ Open WebUI integration
- **hermes-api-server** — Hermes API server setup
- **k8s-mcp-docs** — AIP Kubernetes MCP documentation server

### Research
- **arxiv-research** — arXiv paper search, retrieval, BibTeX, and Semantic Scholar citations
- **mnras-latex-portable** — MNRAS LaTeX manuscript build and packaging
- **2026-agentic-astronomy-literature** — Curated literature on AI agents in astronomy

### Productivity & GitHub
- **nextcloud-caldav** — AIP Nextcloud calendar management via CalDAV
- **github-pr-workflow** — Full PR lifecycle (create, review, merge)

## AIP-specific operational defaults currently encoded in this repo

- SHboost24 public S3 endpoint: `https://s3.data.aip.de:9000`
- SHboost24 parquet glob: `s3://shboost2024/shboost_08july2024_pub.parq/*.parquet`
- REANA environment source repo: `https://gitlab-p4n.aip.de/punch_public/reana/environments`
- Common observed REANA environments:
  - `gitlab-p4n.aip.de:5005/p4nreana/reana-env:py311-astro.9845`
  - `gitlab-p4n.aip.de:5005/p4nreana/reana-env:py311-astro-ml.2891a60c`
- REANA convention: default memory `32GB`
- Plotting convention for SHboost24 CMDs:
  - local Parquet cache
  - PNG only
  - original axes
  - y-axis inverted only
  - `hexbin` density with `512x512` grid
