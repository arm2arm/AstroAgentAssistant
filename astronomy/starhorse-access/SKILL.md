---
name: starhorse-access
description: Access and document StarHorse-related local datasets and usage conventions.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [astronomy, starhorse, dataset, local-dataset, archive]
    category: astronomy
    related_skills: [gaia-aip-de-adql, data-aip-de-s3]
---

# StarHorse Access

## When to Use
Use this skill when a task involves StarHorse-derived data products, local schema interpretation, or institutional access patterns.

## Procedure
1. Identify the exact StarHorse-related source or release.
2. Check whether access is via local files, gaia.aip.de, data.aip.de, or another service.
3. Record schema, columns, and provenance details.
4. Prefer reproducible access patterns and explicit source identifiers.

## Pitfalls
- Do not assume all StarHorse-like datasets share the same schema.
- Avoid undocumented column-name assumptions.

## Verification
- Data source and access path are explicitly recorded.
- Key columns and caveats are documented.
