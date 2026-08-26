# Class-Level Canonicalization Pattern for Skills Repositories

Use this after a session reveals many narrow, overlapping skills for one domain.

## Goal

Move the repository toward class-level skills with rich `SKILL.md` files and optional `references/`, `templates/`, and `scripts/` support files. Preserve useful narrow examples, but make the canonical route obvious.

## Pattern

1. Inventory the overlapping skills by access pattern or workflow class, not by historical task name.
2. Add a small set of canonical class-level skills first. Examples from astronomy data access:
   - umbrella/front-door skill for routing;
   - generic TAP/ADQL/pyvo access;
   - S3/Parquet object-storage access;
   - source-specific skill only when service behavior is genuinely special, e.g. Gaia@AIP or RAVE DR6;
   - plotting/cache skill for reusable visualization conventions.
3. Add support files under the canonical skills:
   - `scripts/` for deterministic probes or validators;
   - `templates/` for reusable starter analysis/plot scripts;
   - `references/` for condensed service notes, caveats, or session-specific findings.
4. Patch legacy/example skills with a short `## Canonical Routing` section instead of deleting them immediately:
   - state that the skill is a specialized or legacy example;
   - list the canonical skills to use for new work;
   - keep dataset-specific details in place.
5. Regenerate README from actual `SKILL.md` files, then audit frontmatter, duplicate names, section coverage, README counts, and secret-like patterns.
6. Commit one coherent change that explains the new routing and any tested probes.

## Testing

Run at least lightweight checks:

- syntax/compile check for helper scripts;
- deterministic local fixture test for templates;
- one tiny live probe when a public endpoint is available, e.g. `SELECT TOP 1` for TAP;
- if a dependency is missing locally, use an alternate minimal probe that tests the service rather than recording the missing package as a durable failure.

## Pitfalls

- Do not create one more narrow task skill when the real need is an umbrella.
- Do not delete old examples in the same pass unless the user explicitly asks; first add canonical routing.
- Do not encode transient setup failures as permanent limitations. Capture the fallback/probe pattern instead.
- Do not let README inventory drift after adding support-rich canonical skills.
