# DRP Paper: Digital Research Products Framework

Create and maintain the DRP white paper project covering the framework for reproducible science on DRP-Hub with full REANA integration.

## When to Use

- User asks to create or modify the DRP paper/white paper
- User references "DRP paper," "Digital Research Products," "drp_service," or "dictation-to-repo"
- User wants to generate a comprehensive academic paper with full REANA integration and iterative improvement

## Project Location

```
/home/hermes/digital-research-products-framework/
├── main.tex              ← monolithic paper (all sections inlined)
├── references.bib        ← BibTeX references
├── main.pdf              ← compiled output
├── figures/
│   ├── repo_structure_diagram.png    ← repository architecture (layered)
│   ├── maturity_model.png             ← maturity model staircase
│   ├── architecture_diagram.png       ← full REANA architecture
│   ├── generate_repo_diagram.py
│   ├── generate_maturity_model.py
│   └── generate_architecture_diagram.py
├── main.aux, .log, .out, .toc, .bbl, .blg
```

**CRITICAL:** Never create or use `sections/` subdirectory. All content goes in monolithic `main.tex`. Remove stale `sections/` if it exists.

## Paper Structure (10 Sections)

1. **Introduction** — DRP paradigm, reproducibility crisis, PUNCH4NFDI context
2. **Related Work** — FAIR principles, REANA/Snakemake platforms, research infrastructure
3. **DRP Framework and Standards** — Repository structure, governance files, FAIR metadata
4. **DRP Maturity Model (L0-L4)** — Progressive reproducibility with REANA integration
5. **DRP-Hub and Astro Card Hub Platform** — Card registry, repo linker, workflow launcher
6. **drp_service Workflow Orchestrator** — Central workflow engine, intent recognition, auto-generation
7. **Quality Assurance and Governance** — Quality checklist, roles, contribution workflow
8. **Practical Development Guide** — Step-by-step conversion, dictation-to-repo pipeline
9. **Future Outlook and Roadmap** — FDO, EOSC, community growth, drp_service evolution
10. **Conclusion** — Summary of framework contributions

## Core Concepts

### drp_service — Central Workflow Orchestrator

The `drp_service` receives ALL user interactions from DRP-Hub and translates them into REANA workflows:

- **Input channels:** Terminal, DRP Card UI, AI Chatbot, Card Generator
- **Workflow selection:** Checks existing `drp_workflows/` for matching workflow
- **Workflow generation:** If no match, auto-generates REANA workflow using templates
- **REANA execution:** Submits workflow to REANA backend automatically
- **Result sync:** Pushes results back to Git, triggers CI/CD, updates DRP-Hub
- **Audit trail:** Logs everything in `provenance.yaml`

### Dictation-to-Repo Pipeline

Users dictate research intent → receive fully functional Git repo with REANA workflow:

1. **Dictation** — User describes intent (terminal, UI, or AI chatbot)
2. **Intent parsing** — drp_service extracts data sources, steps, outputs
3. **Repository generation** — Creates complete DRP structure with governance files
4. **Workflow generation** — Generates reana.yaml or Snakefile from templates
5. **Git commit** — Commits to GitHub/GitLab automatically
6. **CI/CD trigger** — Runs automated tests, FAIR validation, container build
7. **Publication** — Ready for DRP-Hub with one click

### Maturity Model (L0-L4)

Each level inherits all lower-level criteria, with increasing REANA integration:

| Level | Name | REANA Integration |
|-------|-------------|-------------------|
| L0 | Minimal | No workflow |
| L1 | Documented | Basic reana.yaml may exist but not executed |
| L2 | Reproducible | Full REANA integration — runs on any backend |
| L3 | Automated | drp_service integration — every CI/CD triggers REANA |
| L4 | Community | Full dictation-to-repo + federated compute (REANA, S3, SSHFS, Jupyter) |

### Infrastructure Integration

The drp_service integrates with all PUNCH4NFDI services:
- **REANA Backend** — Workflow execution
- **Git Repository** — Version control and CI/CD
- **Jupyter Notebooks** — Interactive development
- **S3 Storage** — Large dataset access and caching
- **SSHFS Mounts** — Interactive file access
- **Terminal Session** — Command-line operations

## Figure Generation

### Three Core Figures

1. **repo_structure_diagram.png** — Layered repository architecture
   - 5 layers: Governance, FAIR Metadata, Workflows, Software & Data, Outputs & Documentation
   - Professional hex palette, color-coded layers, clear labels
   - Script: `figures/generate_repo_diagram.py`

2. **maturity_model.png** — Staircase visualization
   - 5 levels ascending L0→L4, each showing NEW criteria only
   - Professional color palette, arrows between levels
   - Script: `figures/generate_maturity_model.py`

3. **architecture_diagram.png** — Full REANA integration architecture
   - User interaction layer → DRP-Hub → drp_service → Infrastructure
   - Shows all input channels (terminal, UI, AI, generator)
   - Shows drp_service sub-components (workflow gen, executor, registry, sync)
   - Shows infrastructure (REANA, Git, Jupyter, S3, SSHFS, Terminal)
   - Script: `figures/generate_architecture_diagram.py`

### Figure Style Guidelines

- **White background:** `facecolor='white'`
- **Professional palette:** Use hex colors (blues: `#2C5F8A`, `#4A90A4`; greens: `#5BA06B`; reds: `#C8374B`; oranges: `#D4872C`; purples: `#7B68AE`)
- **DPI:** Minimum 200
- **Typography:** 13-15pt titles, 7-11pt labels
- **Clean:** No rainbow gradients, clear legends, consistent spacing

## Compilation

```bash
cd /home/hermes/digital-research-products-framework
pdflatex -interaction=nonstopmode main.tex 2>&1 | tail -10
pdflatex -interaction=nonstopmode main.tex 2>&1 | tail -10  # second pass
```

Output: 20 pages, ~827KB PDF.

## Writing Standards

- **Formal academic tone** — No conversational language
- **Precise claims** — No unsupported assertions
- **Logical flow** — Topic sentences, clear transitions
- **FAIR-compliant** — All claims about FAIR principles accurate
- **No fabricated references** — Only cite what exists in references.bib
- **drp_service** always italicized/code-formatted as `\texttt{drp\_service}`

## Common Pitfalls

- **Sibling conflicts:** Always `read_file` before writing to main.tex
- **Section files:** Never create `sections/` directory — monolithic main.tex only
- **Duplicate packages:** Check for duplicate `\usepackage{hyperref}` before patching
- **Figure kwargs:** FancyArrowPatch uses `arrowstyle=` not `style=` or `linestyle=`
- **Python f-strings:** Use `f"\u2022 {text}"` for bullets, not literal `•`
- **Cleanup:** Remove stale files after changes

## Maintenance

When updating the paper:

1. Read main.tex fully with `read_file` (no pagination)
2. Plan changes (sections, figures, references)
3. For major changes: full `write_file` of main.tex
4. For small changes: `patch` targeted replacements
5. Regenerate figures if content changes
6. Compile twice for bibliography
7. Verify page count and check .log for errors
8. Report: project path, files modified, next step
