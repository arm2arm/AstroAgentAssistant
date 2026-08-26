# Custom-only skills repository cleanup pattern

Use this when a public skills repository should contain only project-specific/team-developed skills, not stock Hermes skills or third-party/vendor skill packs.

## Trigger

- User asks to keep only internally developed skills.
- Repo was bulk-synced from a local skill registry and may contain bundled or vendor skills.
- README inventory claims a custom public repository, but categories include generic stock/vendor domains.

## Robust procedure

1. Create a safety branch before deletions:

```bash
git branch backup/pre-stock-cleanup-$(date -u +%Y%m%d-%H%M%S)
```

2. Read the Hermes bundled manifest as the source of truth for stock skills:

```bash
~/.hermes/skills/.bundled_manifest
```

Each line has the shape:

```text
skill-name:content-md5
```

Compare by frontmatter `name:`, not by directory name.

3. Parse every repository `SKILL.md`:

- frontmatter `name`
- frontmatter `author`
- relative path
- optional content digest for exact-match checks

4. Remove candidates in two classes:

- `name` appears in `.bundled_manifest` → stock Hermes skill.
- author clearly marks third-party/vendor provenance, e.g. `Orchestra Research`, `community`, or another non-project maintainer.

5. Keep project-developed adaptations even if the topic is generic, when the content is clearly team/project-specific. Do not remove by topic alone.

6. Delete whole skill directories, then remove empty parent directories bottom-up.

7. Regenerate README inventory from remaining `SKILL.md` files. Update the README preamble to explicitly say the repository excludes stock Hermes and third-party vendor skills.

8. Verify:

```text
- skill count equals README claim
- category count equals README claim
- duplicate skill names = 0
- frontmatter errors = 0
- bundled/third-party hits = 0
- focused secret scan passes
```

9. Commit with a message like:

```text
chore: keep only <team>-developed skills
```

## Pitfalls

- Do not trust directory names; always parse frontmatter `name:`.
- Do not remove a skill just because it is about a generic topic. Remove only if it is bundled/vendor, or explicitly non-team authored.
- Do not rely only on content hashes; locally edited stock skills may no longer match the bundled md5 but still have a bundled name.
- Make a backup branch before deleting many files.
- README category counts must be regenerated after pruning; stale counts hide accidental removals.
