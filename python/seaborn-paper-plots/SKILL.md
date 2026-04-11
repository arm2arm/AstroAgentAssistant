---
name: seaborn-paper-plots
description: Create clean seaborn/matplotlib plots suitable for papers, notes, and reproducible reports.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [python, seaborn, matplotlib, visualization]
    category: python
    related_skills: [cmd-plotting]
---

# Seaborn Paper Plots

## When to Use
Use this skill when a plot should be clean, reproducible, and suitable for paper drafting.

## Procedure
1. Build the figure from explicit data frames.
2. Set the seaborn theme deliberately.
3. Use readable labels, legends, and output DPI.
4. Export deterministic filenames.

## Pitfalls
- Avoid relying on notebook state.
- Do not hide transformations that affect interpretation.

## Verification
- Plot reproduces from a standalone script.
