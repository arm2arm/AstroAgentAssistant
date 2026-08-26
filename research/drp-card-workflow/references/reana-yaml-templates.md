# reana.yaml Templates for DRP Cards

## LaTeX / Beamer Projects

For compiling LaTeX documents (papers, slides, reports):

```yaml
version: "0.9.0"
workflow:
  type: "container"
  specification:
    inputs:
      files:
        - slides.tex
      runtime:
        kind: "container"
        spec:
          image: "docker.io/teocamp/texlive-full:latest"
    outputs:
      files:
        - slides.pdf
    steps:
      - name: build
        commands:
          - pdflatex -interaction=nonstopmode slides.tex
          - pdflatex -interaction=nonstopmode slides.tex
        engine: "sh"
```

### Key points
- `teocamp/texlive-full:latest` has all LaTeX packages (tikz, pgfplots, amsmath)
- Run pdflatex TWICE for bibliography/cross-reference resolution
- `inputs.files` lists ALL files needed — missing inputs cause workflow failure
- `outputs.files` lists the compiled PDFs

## Python / Analysis Projects

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

## DRP Card YAML (with reana.yaml)

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

### Required when reana.yaml exists
- `hasReana: true`
- `dependencies` must include `reana.yaml`

### Required always
- `title`, `description`, `version`, `authors`, `gitUrl`, `workflowFile`, `entryCommand`, `license`, `tags`

## GitLab Publishing

The project must exist on `gitlab-p4n.aip.de` before DRP-Hub registration:
1. SSH key for `git@gitlab-p4n.aip.de` or GitLab API token with `api` scope
2. Visibility must be `public` or `internal` (DRP-Hub clones at registration)
3. `reana.yaml` MUST be at repo root

## DRP Hub Registration

Use `drphub-cards` skill: `drphub_request("POST", "/products", body={...})`.
After POST, GET the product back, then tell the user the share link:
`https://drphub-p4n.aip.de/share/<product-id>`

### CRITICAL: Share link format
- ✅ `/share/<uuid>`
- ❌ `/product/<uuid>` (404 — does not exist)
- ❌ `/products/{id}` (REST-API-only, not a web page)