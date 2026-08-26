# Taxonomy Regrouping Pattern for AstroAgentAssistant-Style Skill Repos

Use this when a skills repository has many singleton top-level directories, overlapping generic categories, or domain-specific workflows living under the wrong type.

## Goal

Move from a long, flat directory list to class-level domain groups that make browsing and install paths predictable, while preserving every `SKILL.md` and support file.

## Recommended sequence

1. **Pull and verify clean state**
   - `git pull --ff-only`
   - `git status --short --branch`

2. **Inventory by actual `SKILL.md` files**
   - Parse every `SKILL.md` frontmatter for `name`, `description`, tags, and current top-level directory.
   - Group by current category and print one line per skill: `path | name | description`.
   - Use descriptions and trigger conditions to decide domain/type, not only folder names.

3. **Canonical grouping rules**
   - Domain-specific astronomy/catalog/SHBoost/RAVE/Gaia workflows → `astronomy/`.
   - Educational animations, Manim, explainers, generated visuals, and fractal/video workflows → `creative/`.
   - REANA client config, workflow templates, execution recipes, and REANA best practices → `reana-workflows/`.
   - Hermes/OpenWebUI/API-server/MCP integration and serving infrastructure → `infrastructure/`.
   - Containers, deployment, runtime/service troubleshooting, non-REANA ops → `devops/`.
   - Generic Python data engineering, S3/Parquet/HDF5 caching, and reusable plotting code patterns → `python/`.
   - Generic dense-data visualization not tied to a domain → `data-science/`.
   - Academic research, literature, LaTeX manuscripts, DRP, and paper iteration → `research/`.
   - Accelerator/dt4acc/EPICS/Tango workflows → `science/`.

4. **Move with `git mv`, not delete/recreate**
   - Preserve history and support files using directory-level moves.
   - Move support directories (`references/`, `templates/`, `scripts/`, `assets/`) with the skill.
   - Do not change skill content unless paths inside the skill refer to the old location.

5. **Regenerate README from repository state**
   - Count actual `SKILL.md` files by top-level category after moves.
   - Rewrite the category table and inventory from parsed frontmatter.
   - Remove stale install examples that point to old paths; include examples for the new canonical groups.

6. **Validate after regrouping**
   - `skill_files == unique_skill_names`
   - README claimed count matches actual count.
   - README category rows match actual category counts.
   - Frontmatter parses for all `SKILL.md` files.
   - No duplicate skill names remain.
   - Recommended sections still exist: `When to Use`, `Procedure`/`Overview`, `Pitfalls`, `Verification`.

## Pitfalls

- Do not leave singleton top-level directories when a clear canonical group exists.
- Do not put domain astronomy workflows under generic `data-science/` just because they produce plots.
- Do not scatter REANA skills across `workflows/`, `devops/`, and `data-science/`; use one REANA group.
- Do not collapse genuinely different classes into one category just to reduce counts. A small stable category is fine if it is a real type.
- Do not forget support files: moving only `SKILL.md` can break referenced templates/scripts.

## Good final shape example

A mature AstroAgentAssistant-style repo can reasonably have ~15–20 top-level groups rather than dozens of one-skill roots. Example stable groups:

`agents`, `astronomy`, `creative`, `data-science`, `devops`, `infrastructure`, `mcp`, `media`, `mlops`, `productivity`, `python`, `reana-workflows`, `research`, `science`, `software-development`, plus any genuinely distinct small domain such as `leisure` or `social-media`.
