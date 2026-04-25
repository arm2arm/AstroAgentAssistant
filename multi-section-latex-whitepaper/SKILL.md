---
name: multi-section-latex-whitepaper
description: Generate comprehensive LaTeX white papers from multiple sources — Markdown sections, existing papers, or user ideas. Converts and assembles into a single compiled PDF.
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [academic-writing, latex, whitepaper, multi-section, paper-merging]
    related_skills: [latex-paper-iteration, iterative-paper-improvement]
---

# Multi-Section LaTeX White Paper Generator

## Trigger Conditions
Use when the user asks to:
- Generate a comprehensive white paper or report with multiple sections
- Convert Markdown sections into a single compiled LaTeX PDF
- Build a large academic document (15+ pages) from modular parts
- Merge multiple papers into a unified manuscript

## Workflow

### Approach: Monolithic main.tex (Recommended)
Write the entire paper as a single `main.tex` file with all sections inlined. This approach proved more reliable than separate section files for iterative improvement workflows.

**Advantages:**
- Simpler to patch and iterate
- Less fragile than chaining `patch` operations across multiple files
- No risk of section files becoming stale or out of sync
- All content in one place for global improvements

**When to use section files:**
- Paper exceeds ~1000 lines of LaTeX
- Multiple authors working on different sections simultaneously
- User explicitly requests modular section files

### Step 1: Read All Sources
Read all source material:
- Existing papers: `read_file(path)` — read FULL files, no pagination
- Markdown sections: `read_file(path)` for each section
- User ideas: Infill reasonable academic scope, provide realistic structure even if data is synthetic

### Step 2: Plan Merged/Generated Structure
- Identify unique sections, overlapping content, logical flow
- Determine section ordering (Introduction → Related Work → Methodology → Results → Discussion → Conclusion)
- Plan new sections needed (e.g., governance, practical guide, future outlook)
- Map cross-references between sections

### Step 3: Write main.tex
Create a compilable LaTeX document with:
- `\documentclass{article}` with standard packages
- Title, author block, abstract with keywords
- All sections with proper `\\section{}` / `\\subsection{}` markers
- `\label{}` for all sections, figures, tables
- `\cite{}` for references (use placeholders if needed)
- `\\printbibliography` at end

### Step 4: Generate Figures
For each figure referenced in the paper:
1. Write a Python script with `matplotlib.use('Agg')`
2. Use scientific style: professional hex palette, clear labels, legends
3. Execute script, save PNG
4. Reference in LaTeX with `\\includegraphics`

### Step 5: Create references.bib
- Include BibTeX entries for all citations
- Never invent DOIs, page numbers, or experimental results
- Use placeholders like `% TODO: add citation` if reference not provided

### Step 6: Compile
```bash
cd /home/hermes/<article-slug>
pdflatex -interaction=nonstopmode main.tex 2>&1 | tail -10
```
Compile at least twice for bibliography resolution.

## File Structure
```
/home/hermes/<article-slug>/
├── main.tex              ← monolithic (all sections inlined)
├── references.bib        ← BibTeX references
├── figures/
│   ├── generate_*.py     ← figure generation scripts
│   └── *.png             ← generated figures
├── main.aux, .log, .out, .toc
└── sections/             ← OPTIONAL: remove if stale (not used)
```

## LaTeX Standards
- Default to `\documentclass{article}`
- Use standard packages: `amsmath`, `amssymb`, `graphicx`, `booktabs`, `hyperref`, `listings`, `float`, `tabularx`
- Keep macros minimal and readable
- Use labels and cross-references for sections, figures, tables
- Organize content into section files and `\\input{}` them from `main.tex` ONLY if section files are actually used

## Citation Rules
- Never invent references, DOIs, page numbers, or experimental results
- If a citation is needed but not provided, insert a clear placeholder: `% TODO: add citation`
- Keep factual claims appropriately qualified when sources are missing

## Writing Standards
- Formal academic tone, not blog style
- Precise claims, careful wording, logically connected paragraphs
- Topic sentences, clear transitions, explicit definitions
- Avoid hype, vague claims, filler, unsupported assertions
- Maintain notation consistency throughout
- When assumptions are made, state them explicitly
- When limitations exist, describe them honestly

## Style Goals
- Academic, formal, publication-oriented
- Suitable for workshop, conference, preprint, or journal drafting
- Clear enough for technical readers, not needlessly dense
- Prefer strong structure over ornamental language

## Common Pitfalls
- **Sibling conflicts**: If another agent touched the same file, always `read_file` first
- **Pagination on read_file**: Always read full file (or sufficient offset) before writing
- **Section files as dead weight**: If you create `sections/*.tex` but don't `\\input{}` them, remove the stale directory
- **Duplicate packages**: Check for duplicate `\\usepackage` entries
- **biblatex vs BibTeX**: Pick one — use `\\bibliographystyle{plainnat}` + `\\bibliography{references}` for traditional BibTeX
- **Unused packages**: Remove unused `tcolorbox`, `mdframed`, `siunitx` if not referenced in body

## First-Run Behavior (Starting from Scratch)
If starting with just an idea:
1. Infer or ask for the article title
2. Create the slug (lowercase, hyphens, no special chars)
3. Create project directory under `/home/hermes/<article-slug>/`
4. Generate a compilable LaTeX article scaffold
5. Draft the abstract outline and introduction outline
6. Deliver the PDF and report: project path, files created/modified, next step

## Post-Edition Reporting
After each substantial edit, report:
1. Project path
2. Files created or modified
3. Next recommended step