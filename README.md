# AstroAgent Skills Repository

Custom Hermes Agent skills developed by the AIP team for astronomy, data science, reproducible workflows, AI/ML, devops, and productivity.

Total: **128** custom skills across **34** categories.

## Repository layout

| Directory | Description | Skills |
|---|---|---|
| `agents/` | Skills in agents | 1 |
| `api-server-local-image-support/` | Skills in api-server-local-image-support | 1 |
| `api-server-media-display/` | Skills in api-server-media-display | 1 |
| `dtwin-burnin-tests/` | Skills in dtwin-burnin-tests | 1 |
| `dtwin-host-smoke-test/` | Skills in dtwin-host-smoke-test | 1 |
| `dtwin-setup/` | Skills in dtwin-setup | 1 |
| `fractal-showcase-animation/` | Skills in fractal-showcase-animation | 1 |
| `gaia-dr3-tap-query/` | Skills in gaia-dr3-tap-query | 1 |
| `gaiadr3-aip-query-api/` | Skills in gaiadr3-aip-query-api | 1 |
| `iterative-paper-improvement/` | Skills in iterative-paper-improvement | 1 |
| `latex-paper-iteration/` | Skills in latex-paper-iteration | 1 |
| `leisure/` | Skills in leisure | 1 |
| `manim-020-gotchas/` | Skills in manim-020-gotchas | 1 |
| `mcp/` | --- | 1 |
| `multi-section-latex-whitepaper/` | Skills in multi-section-latex-whitepaper | 1 |
| `openwebui-media-via-s3/` | Skills in openwebui-media-via-s3 | 1 |
| `rave-dr6-recent-observations-plot/` | Skills in rave-dr6-recent-observations-plot | 1 |
| `reana-client-multi-backend/` | Skills in reana-client-multi-backend | 1 |
| `sin-unit-circle-animation/` | Skills in sin-unit-circle-animation | 1 |
| `social-media/` | --- | 1 |
| `media/` | --- | 2 |
| `creative/` | --- | 4 |
| `workflows/` | Skills in workflows | 4 |
| `infrastructure/` | Skills in infrastructure | 5 |
| `productivity/` | Skills in productivity | 5 |
| `reana-workflows/` | Skills in reana-workflows | 5 |
| `science/` | Skills in science | 5 |
| `software-development/` | Skills in software-development | 5 |
| `python/` | Skills in python | 8 |
| `research/` | Skills in research | 8 |
| `astronomy/` | Skills in astronomy | 9 |
| `mlops/` | --- | 9 |
| `devops/` | Skills in devops | 16 |
| `data-science/` | --- | 23 |

## Categories overview

**Agents (1)** — Agent concepts and configuration

**Api-server-local-image-support (1)** — API server local image support for Open WebUI

**Api-server-media-display (1)** — API server media display for HTTP frontends

**Dtwin-burnin-tests (1)** — Burn-in tests for dt4acc EPICS IOC

**Dtwin-host-smoke-test (1)** — Host-side smoke tests for dt4acc stack

**Dtwin-setup (1)** — Apptainer-based dt4acc digital twin build/run

**Fractal-showcase-animation (1)** — Fractal video with music

**Gaia-dr3-tap-query (1)** — Gaia DR3 nearest-100 stars via TAP

**Gaiadr3-aip-query-api (1)** — Gaia DR3 PostgreSQL access via AIP Daiquiri

**Iterative-paper-improvement (1)** — Structured multi-round paper improvement workflow

**Latex-paper-iteration (1)** — Iteratively improve LaTeX research papers

**Leisure (1)** — Nearby places search

**Manim-020-gotchas (1)** — Manim CE 0.20.1 gotchas and API changes

**Mcp (1)** — MCP client (mcporter)

**Multi-section-latex-whitepaper (1)** — Generate comprehensive LaTeX white papers from multiple sections

**Openwebui-media-via-s3 (1)** — Serve images, videos, and audio to Open WebUI via S3

**Rave-dr6-recent-observations-plot (1)** — Recent RAVE DR6 observations RA-Dec plot

**Reana-client-multi-backend (1)** — REANA multi-profile config

**Sin-unit-circle-animation (1)** — Unit circle to sine wave animation

**Social-media (1)** — X/Twitter CLI client

**Media (2)** — Audio, video, GIFs, YouTube, music generation

**Creative (4)** — Animations, ASCII art, diagrams, music, web design, ideation

**Workflows (4)** — REANA workflow templates: client config, serial analysis, SHBoost, AIP environments

**Infrastructure (5)** — AIP infrastructure: MCP servers, Hermes API server, Open WebUI integration

**Productivity (5)** — CalDAV, Linear, Notion, OCR, PDFs, presentations

**Reana-workflows (5)** — REANA workflow templates and best practices

**Science (5)** — dt4acc digital twin build, EPICS/Tango runbooks, host smoke tests

**Software-development (5)** — Coding workflows, MCP docs-first, TDD, debugging, code review

**Python (8)** — Scientific plotting conventions, Dask, Pandas, Parquet/S3 caching

**Research (8)** — arXiv, blog monitoring, LaTeX, literature review, DRP white papers

**Astronomy (9)** — Survey archives, ADQL queries, dataset access (RAVE, Gaia, SHBoost, StarHorse)

**Mlops (9)** — LLM fine-tuning, serving, inference, evaluation, HuggingFace

**Devops (16)** — Docker, dt4acc digital twin, Manim rendering, REANA scripts, Paperclip

**Data-science (23)** — Scientific plotting, Dask, Datashader, REANA workflows, Parquet/S3

## Single skills

| Skill | Description |
|-------|-------------|
| `agents/astroagent-concept/` | Use the AstroAgent concept framing for architecture, positioning, and design discussions. |
| `api-server-local-image-support/` | Fix Open WebUI image display by extending api_server.py to convert standard markdown ![alt](/local/path) images into HTTP URLs via /media/<path> route. Handles the gap between agent-generated image paths and the API server's media serving pipeline. |
| `api-server-media-display/` | Diagnose and fix images not displaying in Open WebUI / API server frontends. |
| `dtwin-burnin-tests/` | Run comprehensive burn-in tests on the dt4acc Digital Twin IOC to verify EPICS PV stability, throughput, and read/write resilience |
| `dtwin-host-smoke-test/` | Reproducible host-side smoke test for the dt4acc digital twin stack using local dt4acc, dt4acc-lib, and lat2db repos without MongoDB, TANGO, or Apptainer. |
| `dtwin-setup/` | Build and run the dt4acc Digital Twin for particle accelerators using Apptainer |
| `fractal-showcase-animation/` | | |
| `gaia-dr3-tap-query/` | Retrieve the nearest 100 stars from Gaia DR3 using the TAP service hosted at AIP (https://gaia.aip.de/tap/). Includes Parquet storage, preview CSV, and RA/Dec & Galactic XY plots. |
| `gaiadr3-aip-query-api/` | Query the Gaia DR3 PostgreSQL database at gaia.aip.de via its Daiquiri REST API. Includes CSRF handling, queue names, and result fetching. |
| `iterative-paper-improvement/` | Structured multi-round improvement workflow for LaTeX academic papers — each round targets specific improvements (structure, prose, figures, compilation). Also covers merging multiple papers and multi-phase iterations (X figure rounds + Y text rounds). |
| `latex-paper-iteration/` | Iteratively improve LaTeX research papers — structural fixes, prose polishing, figure integration, compilation cycles. Also covers merging multiple papers into a unified manuscript. |
| `leisure/find-nearby/` | Find nearby places (restaurants, cafes, bars, pharmacies, etc.) using OpenStreetMap. Works with coordinates, addresses, cities, zip codes, or Telegram location pins. No API keys needed. |
| `manim-020-gotchas/` | >- |
| `mcp/mcporter/` | Use the mcporter CLI to list, configure, auth, and call MCP servers/tools directly (HTTP or stdio), including ad-hoc servers, config edits, and CLI/type generation. |
| `multi-section-latex-whitepaper/` | Generate comprehensive LaTeX white papers from multiple sources — Markdown sections, existing papers, or user ideas. Converts and assembles into a single compiled PDF. |
| `openwebui-media-via-s3/` | Serve images, videos, and audio to Open WebUI by uploading media to the public S3 bucket (scr4agent), then embedding pure markdown URLs. |
| `rave-dr6-recent-observations-plot/` | Retrieve the most recent 100 entries from the RAVE DR6 `dr6_obsdata` table and generate a simple RA‑Dec scatter plot. Handles missing Python dependencies, installs them if necessary, and falls back to astropy for galactic coordinates if needed. |
| `reana-client-multi-backend/` | "Reusable instructions to set up a .reana/config.yaml with dev and prod profiles and run reana‑client via Docker using REANA_PROFILE." |
| `sin-unit-circle-animation/` | > |
| `social-media/xitter/` | Interact with X/Twitter via the x-cli terminal client using official X API credentials. Use for posting, reading timelines, searching tweets, liking, retweeting, bookmarks, mentions, and user lookups. |

## Using this repository with Hermes

Add the repository as a tap:

```bash
hermes skills tap add arm2arm/AstroAgentAssistant
```

Then search and install skills from it.

### Browse and search

```bash
hermes skills browse
hermes skills search shboost
hermes skills search reana
hermes skills search gaia
hermes skills search manim
```

### Install specific skills

```bash
# Astronomy
hermes skills install arm2arm/AstroAgentAssistant/astronomy/rave-dr6-public-talk-visualizations
hermes skills install arm2arm/AstroAgentAssistant/astronomy/gaia-aip-de-adql

# Data science
hermes skills install arm2arm/AstroAgentAssistant/data-science/shboost-cmd-plot
hermes skills install arm2arm/AstroAgentAssistant/data-science/dask-hvplot-datashader-scientific-plots

# DevOps
hermes skills install arm2arm/AstroAgentAssistant/devops/paperclip-oss120b-external
hermes skills install arm2arm/AstroAgentAssistant/devops/dtwin-epics-runbook
hermes skills install arm2arm/AstroAgentAssistant/devops/api-server-local-image-support

# Infrastructure
hermes skills install arm2arm/AstroAgentAssistant/infrastructure/docs-mcp-at-aip

# Research
hermes skills install arm2arm/AstroAgentAssistant/research/drp-paper

# Workflows
hermes skills install arm2arm/AstroAgentAssistant/workflows/reana-serial-python

# Science
hermes skills install arm2arm/AstroAgentAssistant/science/dtwin-epics-runbook

# Python
hermes skills install arm2arm/AstroAgentAssistant/python/python-mcp-docs-first

# Productivity
hermes skills install arm2arm/AstroAgentAssistant/productivity/nextcloud-caldav-calendar-management
hermes skills install arm2arm/AstroAgentAssistant/productivity/linear

# Software development
hermes skills install arm2arm/AstroAgentAssistant/software-development/subagent-driven-development
hermes skills install arm2arm/AstroAgentAssistant/software-development/systematic-debugging
```

### Load a skill in a session

```bash
hermes -s shboost-cmd-plot
hermes -s reana-serial-python-analysis-template -s docs-mcp-at-aip
```

Or simply ask Hermes in chat to use a named skill — it will auto-load the relevant one.

## Security scanning

This repository includes a GitHub Actions workflow at:

- `.github/workflows/secret-scan.yml`

It runs `gitleaks` on:
- pushes to `main`
- pull requests
- manual workflow dispatch

This helps catch accidentally committed API keys, tokens, passwords, and private keys.

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

## AIP-specific operational defaults

- SHBoost public S3 endpoint: `https://s3.data.aip.de:9000`
- SHBoost parquet glob: `s3://shboost2024/shboost_08july2024_pub.parq/*.parquet`
- REANA environment source repo: `https://gitlab-p4n.aip.de/punch_public/reana/environments`
- Common observed REANA environments:
  - `gitlab-p4n.aip.de:5005/p4nreana/reana-env:py311-astro.9845`
  - `gitlab-p4n.aip.de:5005/p4nreana/reana-env:py311-astro-ml.2891a60c`
- REANA convention: default memory `32GB`
- Plotting convention for SHBoost CMDs:
  - local Parquet cache
  - PNG only
  - original axes
  - y-axis inverted only
  - `hexbin` density with `512x512` grid
