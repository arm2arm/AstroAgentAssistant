# AstroAgent Skills Repository

Reusable Hermes Agent skills for astronomy, data science, reproducible workflows, AI/ML, devops, and productivity.

This repository is organized as a shareable skills collection. It holds:
- procedural skills that encode repeatable workflows;
- supporting references, templates, scripts, and assets;
- domain-specific knowledge (astronomy, data science, MLOps, etc.).

## Repository layout

| Directory | Description | Skills |
|---|---|---|
| `agents/` | Agent concepts and configuration | 1 |
| `astronomy/` | Survey archives, ADQL queries, dataset access (RAVE, Gaia, SHBoost, StarHorse) | 9 |
| `autonomous-ai-agents/` | Multi-agent orchestration (Claude Code, Codex, OpenCode, Hermes) | 4 |
| `creative/` | Animations, ASCII art, diagrams, music, web design, ideation | 16 |
| `data-science/` | Scientific plotting, Dask, Datashader, REANA workflows, Parquet/S3 | 24 |
| `devops/` | Docker, dt4acc digital twin, Manim rendering, REANA scripts, Paperclip | 17 |
| `dogfood/` | Systematic web QA testing | 1 |
| `email/` | Email management via CLI | 1 |
| `gaming/` | Minecraft modpack servers, Pokemon emulation | 2 |
| `github/` | GitHub workflows (PRs, issues, code review, repo mgmt, skill maintenance) | 9 |
| `infrastructure/` | AIP infrastructure: MCP servers, Hermes API server, Open WebUI integration | 5 |
| `leisure/` | Nearby places search | 1 |
| `mcp/` | MCP client (native, mcporter) | 2 |
| `media/` | Audio, video, GIFs, YouTube, music generation | 6 |
| `mlops/` | LLM fine-tuning, serving, inference, evaluation, HuggingFace | 22 |
| `note-taking/` | Obsidian vault management | 1 |
| `productivity/` | CalDAV, Linear, Notion, OCR, Google Workspace, PDFs, presentations | 12 |
| `python/` | Scientific plotting conventions, Dask, Pandas, Parquet/S3 caching | 8 |
| `reana-workflows/` | REANA workflow templates and best practices | 5 |
| `red-teaming/` | LLM red-teaming and safety evaluation | 1 |
| `research/` | arXiv, blog monitoring, LaTeX, literature review, polymarket, DRP white papers | 13 |
| `science/` | dt4acc digital twin build, EPICS/Tango runbooks, host smoke tests | 5 |
| `smart-home/` | Philips Hue smart home control | 1 |
| `social-media/` | X/Twitter CLI client | 2 |
| `software-development/` | Coding workflows, MCP docs-first, TDD, debugging, code review | 11 |
| `workflows/` | REANA workflow templates: client config, serial analysis, SHBoost, AIP environments | 4 |
| `api-server-local-image-support/` | API server local image support for Open WebUI | 1 |
| `api-server-media-display/` | API server media display for HTTP frontends | 1 |
| `dtwin-burnin-tests/` | Burn-in tests for dt4acc EPICS IOC | 1 |
| `dtwin-host-smoke-test/` | Host-side smoke tests for dt4acc stack | 1 |
| `dtwin-setup/` | Apptainer-based dt4acc digital twin build/run | 1 |
| `fractal-showcase-animation/` | Fractal video with music | 1 |
| `gaia-dr3-tap-query/` | Gaia DR3 nearest-100 stars via TAP | 1 |
| `gaiadr3-aip-query-api/` | Gaia DR3 PostgreSQL access via AIP Daiquiri | 1 |
| `iterative-paper-improvement/` | Structured multi-round paper improvement workflow | 1 |
| `latex-paper-iteration/` | Iteratively improve LaTeX research papers | 1 |
| `manim-020-gotchas/` | Manim CE 0.20.1 gotchas and API changes | 1 |
| `multi-section-latex-whitepaper/` | Generate comprehensive LaTeX white papers from multiple sections | 1 |
| `openwebui-media-via-s3/` | Serve images, videos, and audio to Open WebUI via S3 | 1 |
| `rave-dr6-recent-observations-plot/` | Recent RAVE DR6 observations RA-Dec plot | 1 |
| `reana-client-multi-backend/` | REANA multi-profile config | 1 |
| `sin-unit-circle-animation/` | Unit circle to sine wave animation | 1 |

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

# MLOps / LLM
hermes skills install arm2arm/AstroAgentAssistant/mlops/unsloth
hermes skills install arm2arm/AstroAgentAssistant/mlops/gguf-quantization

# Infrastructure
hermes skills install arm2arm/AstroAgentAssistant/infrastructure/docs-mcp-at-aip

# Research
hermes skills install arm2arm/AstroAgentAssistant/research/drp-paper
hermes skills install arm2arm/AstroAgentAssistant/research/arxiv

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

## Categories overview

**Agents (1)** — Agent concepts and configuration

**Astronomy (9)** — RAVE DR6 animations and plots, Gaia DR3 queries, SHBoost dataset access, StarHorse

**Autonomous AI Agents (4)** — Claude Code, Codex, OpenCode, Hermes agent orchestration

**Creative (16)** — Manim animations, ASCII art, architecture diagrams, Excalidraw, p5.js, web design, music, comics, infographics

**Data Science (24)** — Scientific plotting (Dask/hvPlot/Datashader), S3 Parquet, REANA workflows, RAVE/Gaia/SHBoost, sine/cosine animations

**DevOps (17)** — Docker, dt4acc digital twin, Manim rendering, Paperclip setup, REANA scripts, webhooks, Telegram auth troubleshooting

**Email (1)** — Himlaya CLI for IMAP/SMTP

**Gaming (2)** — Minecraft modpack servers, Pokemon EMU

**GitHub (9)** — PR lifecycle, issues, code review, repo management, skill maintenance, auth, codebase inspection

**Infrastructure (5)** — AIP documentation MCP, Hermes API server, native MCP, mcporter CLI, Open WebUI integration

**Media (6)** — Audio, video, GIFs, YouTube, music generation, Songsee spectrograms

**MLOps (22)** — Fine-tuning (Axolotl, TRL, Unsloth, PEFT, GRPO), serving (vLLM, llama-cpp), HuggingFace, evaluation, quantization, MaaS

**Productivity (12)** — CalDAV, Linear, Notion, Google Workspace, OCR, PDFs, presentations, image descriptions, maps

**Python (8)** — Scientific plotting conventions, Dask, Pandas, Parquet/S3 caching, MCP docs-first, HDF5 on S3

**Research (13)** — arXiv, blog monitoring, LaTeX/MNRAS (portable build), literature review, polymarket, LLM wiki, DRP white papers, LaTeX iteration, multi-section papers

**Science (5)** — dt4acc digital twin build, EPICS/Tango runbooks, host smoke tests

**Software Development (11)** — MCP docs-first, TDD, subagent-driven dev, debugging, code review, planning, testing

**Workflows (5)** — REANA workflow templates: client config, serial analysis, SHBoost, dev setup, self-learn

## Single skills

| Skill | Description |
|-------|-------------|
| `api-server-local-image-support/` | Fix Open WebUI image display via local path → HTTP URL conversion |
| `api-server-media-display/` | API server media display for HTTP frontends |
| `dogfood/` | Systematic web QA testing |
| `dtwin-burnin-tests/` | Burn-in tests for dt4acc EPICS IOC |
| `dtwin-host-smoke-test/` | Host-side smoke tests for dt4acc stack |
| `dtwin-setup/` | Apptainer-based dt4acc digital twin build/run |
| `fractal-showcase-animation/` | Fractal video with music |
| `gaia-dr3-tap-query/` | Gaia DR3 nearest-100 stars via TAP |
| `gaiadr3-aip-query-api/` | Gaia DR3 PostgreSQL access via AIP Daiquiri |
| `iterative-paper-improvement/` | Structured multi-round paper improvement workflow |
| `latex-paper-iteration/` | Iteratively improve LaTeX research papers |
| `leisure/` | Nearby places search |
| `manim-020-gotchas/` | Manim CE 0.20.1 gotchas and API changes |
| `multi-section-latex-whitepaper/` | Generate comprehensive LaTeX white papers from multiple sections |
| `note-taking/` | Obsidian vault management |
| `openwebui-media-via-s3/` | Serve images, videos, and audio to Open WebUI via S3 |
| `rave-dr6-recent-observations-plot/` | Recent RAVE DR6 observations RA-Dec plot |
| `reana-client-multi-backend/` | REANA multi-profile config |
| `red-teaming/` | LLM red-teaming and safety evaluation |
| `sin-unit-circle-animation/` | Unit circle to sine wave animation |
| `smart-home/` | Philips Hue smart home control |
| `social-media/` | X/Twitter CLI client |

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
