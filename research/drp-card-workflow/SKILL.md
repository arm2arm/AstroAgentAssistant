---
name: drp-card-workflow
description: "Full lifecycle for creating reproducible DRP cards: scaffolding with reana.yaml, Beamer/LaTeX or Python workflows, GitLab publishing, and DRP-Hub registration via REST API. Covers the complete path from project creation to share link."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [drp, hub, cards, reana, yaml, workflow, punch4nfdi, latex, beamer]
    homepage: https://drphub-p4n.aip.de
    related_skills: [latex-paper-workflow, latex-compilation-pitfalls, reana-aip]
---

# DRP Card Workflow

Create a reproducible research product (DRP) with a reana.yaml workflow, push to GitLab, and register it on DRP-Hub. This covers the full lifecycle from scaffolding to publication.

## When to Use

- User asks to create a "DRP card" or "DRP product" with REANA workflow
- User says "register this on DRP-Hub" or "create a card for this project"
- User needs a reana.yaml for an existing project
- User wants to publish a research artifact as a reproducible product

## Prerequisites

1. **GitLab access:** Either SSH key for `git@gitlab-p4n.aip.de` or GitLab API token with `api` scope
2. **DRP Hub credentials:** API token set via `DRPHUB_TOKEN` env var, or service token via `DRPHUB_SERVICE_TOKEN`
3. **OpenCode available** (optional): for agent-assisted project scaffolding and code review

## Step 1: Scaffold Project

Create a minimal project structure:

```bash
mkdir -p ~/projects/<project-slug>/
cd ~/projects/<project-slug>/
```

Required files:
- `reana.yaml` — REANA workflow specification (see templates below)
- `drp_card.yaml` — DRP Hub card metadata
- `.gitignore` — Exclude LaTeX build artifacts, Python caches
- `README.md` — Project description and usage

## Step 2: Write reana.yaml

### LaTeX / Beamer Projects

```yaml
version: "0.9.0"
workflow:
  type: "container"
  specification:
    inputs:
      files:
        - slides.tex        # ALL source files needed for compilation
      runtime:
        kind: "container"
        spec:
          image: "docker.io/teocamp/texlive-full:latest"
    outputs:
      files:
        - slides.pdf        # Compiled PDF output
    steps:
      - name: build
        commands:
          - pdflatex -interaction=nonstopmode slides.tex
          - pdflatex -interaction=nonstopmode slides.tex
        engine: "sh"
```

**Key notes:**
- Run `pdflatex` TWICE for bibliography and cross-reference resolution
- `teocamp/texlive-full:latest` has all LaTeX packages (tikz, pgfplots, amsmath, etc.)
- `inputs.files` lists ALL files needed — missing inputs cause workflow failure
- `outputs.files` lists the compiled PDFs

### Python / Analysis Projects

```yaml
version: "0.9.0"
workflow:
  type: "container"
  specification:
    inputs:
      files:
        - analysis.py
        - data/
      runtime:
        kind: "container"
        spec:
          image: "docker.io/library/python:3.11-slim"
    outputs:
      files:
        - results/output.parquet
        - figures/plot.png
    steps:
      - name: setup
        commands:
          - pip install --quiet pandas pyarrow matplotlib
        engine: "sh"
      - name: analyze
        commands:
          - python analysis.py
        engine: "sh"
```

### General Template

```yaml
version: "0.9.0"
workflow:
  type: "container"
  specification:
    inputs:
      files:
        - <your-source-files>
      runtime:
        kind: "container"
        spec:
          image: "<docker-image>"
    outputs:
      files:
        - <output-files>
    steps:
      - name: <step-name>
        commands:
          - <commands>
        engine: "sh"
```

## Step 3: Write drp_card.yaml

### Required Fields

| Field | Description | Example |
|-------|-------------|---------|
| `title` | Human-readable title | `"Sine Wave Explorer"` |
| `description` | Brief description | `"Interactive sine wave visualization..."` |
| `version` | Semantic version | `"1.0.0"` |
| `authors` | Author list with name + affiliation | See below |
| `gitUrl` | Git repository URL | `"https://gitlab-p4n.aip.de/..."` |
| `workflowFile` | Path to reana.yaml in repo | `"reana.yaml"` |
| `entryCommand` | Command to run the workflow | `"reana-client run -w <name>"` |
| `license` | SPDX license identifier | `"MIT"` |
| `tags` | Array of search tags | `[physics, education, sine-wave]` |

### Author Format
```yaml
authors:
  - name: "Author Name"
    affiliation: "Institution"
```

### Optional but Recommended
| Field | Description |
|-------|-------------|
| `dependencies` | List of files the card depends on (e.g., `[reana.yaml]`) |
| `hasReana` | Set to `true` when a reana.yaml exists |
| `envImage` | Container image ref from approved AIP list |
| `releaseTag` | Version tag (e.g., `v1.0.0`) |
| `citationCffUrl` | URL to CITATION.cff file |

### Complete Example
```yaml
title: "Sine Wave Explorer"
description: "Interactive sine wave visualization for 11th-grade physics students"
version: "1.0.0"
authors:
  - name: "Arman Khalatyan"
    affiliation: "AIP Potsdam"
gitUrl: "https://gitlab-p4n.aip.de/arm2arm/sine-wave-drp"
workflowFile: "reana.yaml"
entryCommand: "reana-client run -w sine-wave-explorer"
license: "MIT"
tags: [physics, education, sine-wave, trigonometry, beamer]
dependencies:
  - reana.yaml
hasReana: true
```

## Step 4: Verify Locally

Before pushing to GitLab, verify the workflow works:

### LaTeX Projects
```bash
rm -f *.aux *.log *.nav *.snm *.toc *.out *.vrb
pdflatex -interaction=nonstopmode slides.tex
pdflatex -interaction=nonstopmode slides.tex
# Confirm: Output written on slides.pdf (N pages, XXXXX bytes).
```

### Python Projects
```bash
python analysis.py
# Confirm output files exist
ls -lh results/ figures/
```

## Step 5: GitLab Publishing

1. **Initialize git repo** (if not already):
   ```bash
   git config user.name "Author Name"
   git config user.email "author@institution.de"
   git init
   git add -A
   git commit -m "chore: initial commit — DRP card scaffolding"
   ```

2. **Add remote and push:**
   ```bash
   git remote add origin git@gitlab-p4n.aip.de:arm2arm/<project-slug>.git
   git branch -M main
   git push -u origin main
   ```

3. **Visibility:** Must be `public` or `internal` (DRP-Hub clones the repo at registration time)

## Step 6: Register on DRP-Hub

After the card YAML is committed and pushed, register via the DRP Hub REST API:

1. **Source the `drphub-cards` skill** — it has the API client function `drphub_request()`
2. **Build the product payload** using `drphub_request("POST", "/products", body={...})`
3. **Key fields for the POST body:**
   - `title`, `description`, `tags`, `category` (analysis/tool/data/workflow/service/publication)
   - `workflow_file` — MUST match the path in the repo
   - `entry_command` — the real run command
   - `env_image` — container image ref from the approved AIP list
   - `has_reana: true`
4. **After POST, GET the product back** and confirm the git/env fields round-trip correctly
5. **Tell the user the share link:** `https://drphub-p4n.aip.de/share/<product-id>`

## Pitfalls

1. **Missing reana.yaml:** DRP cards MUST have a `reana.yaml` when claiming REANA reproducibility. The `hasReana: true` flag must match.
2. **Wrong workflow type:** `type: "container"` uses a single container image. `type: "reana"` uses the REANA workflow engine. Use `container` for simple builds.
3. **pdflatex needs two passes:** Always run pdflatex twice for bibliography/cross-reference resolution.
4. **Image tag not digest-pinned:** For reproducibility, use image digests when possible, not mutable tags.
5. **GitLab not public:** DRP-Hub clones the repo at registration time. Private projects fail.
6. **Workflow file path mismatch:** `workflowFile` in the card must exactly match the path in the repo.
7. **Entry command must work:** `entryCommand` should be a real command that users can run.
8. **Share link format:** The Hub's only public card-view route is `/share/:cardId`. `/product/<id>` does NOT exist and returns 404.

## Procedure Summary

1. Scaffold project directory with `reana.yaml`, `drp_card.yaml`, `.gitignore`, `README.md`
2. Implement the workflow (compile code, run analysis, etc.)
3. Verify locally: `pdflatex` for LaTeX, run Python scripts, check outputs
4. Push to GitLab (public/internal visibility)
5. Register via DRP Hub REST API (`POST /products`)
6. Verify the share link works
7. Deliver the share URL to the user
