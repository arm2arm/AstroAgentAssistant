---
name: reana-shboost24
description: Run SHboost24 plotting and sampling workflows on REANA with cached parquet inputs and explicit script packaging.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [reana, shboost24, astronomy, workflow, parquet]
    category: workflows
    related_skills: [reana-aip, shboost24-cmd]
---

# REANA SHboost24

## When to Use
Use this skill for SHboost24 plotting or data-reduction workflows that need to run on REANA.

## Procedure
1. Prepare the Python analysis script locally.
2. Include the script explicitly in workflow inputs.
3. Use local parquet caching where appropriate.
4. Run through `reana-client run -w <name>`.

## Pitfalls
- Forgetting to include the analysis script as an input is a common failure.
- Avoid ad hoc workflow names when resubmitting fixes to an existing workspace.

## Verification
- Workflow contains the script input.
- Output artifacts and plot filenames are explicitly defined.
