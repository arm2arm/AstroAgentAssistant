# Repo Audit Cleanup Pattern — AstroAgentAssistant-style Skills Repositories

Use this when auditing a public Hermes skills repository for inventory drift, duplicate skills, frontmatter validity, taxonomy consistency, and accidental credential leakage.

## Audit dimensions

1. **Inventory**
   - Count every `SKILL.md` under the repo excluding `.git`.
   - Parse `README.md` claimed totals and per-category rows.
   - Compare actual top-level category counts to README counts.

2. **Frontmatter**
   - Validate that each `SKILL.md` starts at byte 0 with `---`.
   - Find the closing `---` delimiter.
   - Parse YAML and require at least `name` and `description`.
   - Quote descriptions containing colons, e.g. `description: "Query ... plots: A and B"`.

3. **Duplicates**
   - Detect duplicate `name:` values, not only duplicate directories.
   - Detect exact duplicate file content by hashing `SKILL.md` bytes.
   - Pick canonical class/category locations before deleting duplicates.
   - Preserve support files (`references/`, `scripts/`, `templates/`, `assets/`) by moving them to the canonical skill directory before deleting the duplicate directory.

4. **Secret/privacy scan**
   - Treat broad regex hits as *manual-review candidates*, not proof of secrets.
   - Remove committed app passwords, personal emails used as examples, and user-specific credentials.
   - Keep placeholder/example hits only when clearly non-secret, e.g. `api_key="your-api-key"`, `HF_TOKEN`, `api_key="not-needed"`.
   - Run a focused forbidden scan for known sensitive strings found in the session after cleanup.

5. **README regeneration**
   - Regenerate the README from the actual filesystem after duplicate cleanup.
   - Ensure install examples point to existing skill paths.
   - Validate README totals equal actual `SKILL.md` counts.

6. **Recommended section normalization**
   - For a broad audit pass, ensure every skill has `## When to Use`, `## Overview` or `## Procedure`, `## Pitfalls`, and `## Verification`.
   - Prefer small generic sections over inventing task-specific claims.
   - Do not overwrite rich existing sections.

## Safe deletion/canonicalization rules

- Use `git rm` so deletions are staged and reviewable.
- Do not commit or push unless the user explicitly asks.
- Keep canonical locations by class, e.g. `science/` for dtwin/dt4acc, `research/` for DRP/paper research, `software-development/` for docs-first coding workflows, `python/` for Python data-engineering implementation skills.
- Before deleting a duplicate tree, check whether it has support files not present in the canonical tree.

## Final validation checklist

A successful audit cleanup should report:

- `skill_files == unique_skill_names`
- README claimed skills/categories match actual counts
- no README per-category mismatches
- zero frontmatter parse errors
- zero duplicate skill names
- zero bundled/standard skill names, if the repo is intended to be custom-only
- no known live secret strings in focused scans
- no missing recommended authoring sections, if normalization was in scope

Keep the machine-readable audit JSON and a concise Markdown summary in `/tmp/` or another scratch location; do not commit session-local audit reports unless the user asks.