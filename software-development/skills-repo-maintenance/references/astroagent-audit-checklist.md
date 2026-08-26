# AstroAgentAssistant Repository Audit Checklist

Use this when asked to audit or maintain an AstroAgentAssistant-style public skills repository.

## Inputs

- Work from the actual checkout path the user requested. Do not assume `/tmp/AstroAgentAssistant`; common durable paths include `/home/hermes/projects/AstroAgentAssistant`.
- Confirm clean git state before making changes.

## Core audit probes

Run or reproduce these checks from the repository root:

1. **Inventory counts**
   - Count all `SKILL.md` files excluding `.git`.
   - Count unique `name:` frontmatter values.
   - Group skill files by top-level directory.
   - Parse README inventory rows and compare stated counts with actual counts.

2. **Duplicate taxonomy**
   - Detect duplicate skill names across paths.
   - Detect exact duplicate `SKILL.md` content by hash.
   - Prefer canonical class-level homes over root-level one-off duplicates. For this repo, accelerator/digital-twin skills usually belong under `science/`; DRP paper skills usually belong under `research/`.

3. **Frontmatter validity**
   - YAML frontmatter must parse as a mapping and include `name` and `description`.
   - Quote descriptions containing colons, e.g. `description: "... plots: Galactic projection ..."`; unquoted colons commonly break YAML parsing.
   - Check name format: lowercase/hyphen/underscore, <=64 chars.

4. **Authoring structure**
   - Report missing recommended sections separately from fatal errors:
     - `## When to Use`
     - `## Procedure` or `## Overview`
     - `## Pitfalls` / `## Common Pitfalls`
     - `## Verification` / `## Verification Checklist`

5. **Secret/privacy scan**
   - Scan for credential-like patterns, but classify results as *manual-review hits*, not automatic leaks.
   - Placeholders like `your-api-key`, `hf_xxxxx`, `api_key="not-needed"`, and environment variable examples are usually benign.
   - Personal usernames/emails are not passwords but may still be privacy-sensitive in a public repo.

6. **Bundled-skill leakage**
   - Compare parsed skill names with `~/.hermes/skills/.bundled_manifest` when available.
   - Report any overlap as bundled/standard skills that should usually not be published in the custom repo.

## Reporting shape

Summarize:

- git status and branch
- tracked file count
- `SKILL.md` count and unique skill-name count
- README claimed counts vs actual counts
- duplicate names and exact duplicate content groups
- frontmatter errors
- missing recommended sections counts
- secret-like/manual-review hits
- concrete recommended fixes in priority order

## Safe first fixes

If the user asks to proceed after an audit, the safest first pass is:

1. Fix broken frontmatter.
2. Remove exact duplicate directories only after choosing canonical locations.
3. Regenerate README inventory from actual skill files.
4. Review privacy-sensitive identifiers before public push.
5. Normalize high-value skills to the standard section structure.
