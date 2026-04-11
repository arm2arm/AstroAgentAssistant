---
name: gaia-aip-de-adql
description: Query gaia.aip.de using ADQL/TAP with reproducible query capture and astronomy-aware caveats.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [astronomy, gaia, adql, tap, virtual-observatory]
    category: astronomy
    related_skills: [starhorse-access, data-aip-de-s3]
---

# gaia.aip.de ADQL

## When to Use
Use this skill when users need natural-language-to-ADQL help, TAP query generation, or gaia.aip.de workflow support.

## Procedure
1. Identify the target table and required columns.
2. Translate the scientific intent into explicit ADQL.
3. Capture the exact query text for provenance.
4. Explain assumptions, filters, joins, and limits.

## Pitfalls
- Avoid ambiguous joins.
- Always state row limits and filtering conditions.
- Watch for unit and epoch assumptions.

## Verification
- Final ADQL query is shown explicitly.
- The target table/service is named.
- Query assumptions are documented.
