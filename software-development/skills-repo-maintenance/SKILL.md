---
name: skills-repo-maintenance
description: Maintain the AstroAgentAssistant-style public skills repository by auditing secrets, syncing README coverage, resolving vague issues into concrete skill changes, and keeping taxonomy consistent.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [github, maintenance, skills, repository, auditing, taxonomy]
    related_skills: [astro-agent-assistant-repo, github-issues, github-pr-workflow]
---

# Skills Repo Maintenance

## When to Use
Use this skill when maintaining a public Hermes skills repository itself: triaging issues, adding or splitting skills, auditing for secrets, syncing README inventory entries, and checking whether issue reports match the actual repository state.

## Procedure

### 1. Pull and inspect the current repo state
```bash
cd /tmp/AstroAgentAssistant
git pull --ff-only
git status --short
git log --oneline -3
```

### 2. Compare issues against the actual repository
Before fixing an issue, inspect the relevant files and README entries.

Use this pattern especially for vague issues:
- read the issue body
- inspect the current skill files
- determine whether the problem is real, outdated, incomplete, or underspecified
- convert vague complaints into concrete changes (new skill, split taxonomy, README clarification, metadata links)

### 3. Audit for secrets before every push
```bash
grep -rP '(<user>|Aac3|api_key|apikey|secret|password|passwd)' \
  --include='*.md' --include='*.yaml' --include='*.py' .
```

Manually distinguish real secrets from placeholders or explanatory text.

### 4. Keep README coverage synchronized
Whenever a new public skill is added or a taxonomy changes, update the README inventory in the correct section.

### 5. Maintain taxonomy explicitly
When skills overlap:
- choose one canonical umbrella skill
- add specialized companion skills only when their scope is clearly different
- add `related_skills` links between umbrella and specialized skills
- clarify the split in the umbrella skill itself
- reflect the split in the README

Example pattern learned from practice:
- canonical query/discovery skill
- focused plotting/analysis skill
- polished presentation/public-talk skill

### 6. Resolve auth/config issues with dedicated setup skills
If an issue is really about credentials or environment configuration, create a dedicated setup skill rather than burying the instructions in an execution skill.

Example pattern learned from practice:
- separate REANA workflow skills from REANA client config/auth skill
- then link the workflow skills back to the setup skill

### 7. Improve issue quality when the repo needs ongoing maintenance
If issue quality is poor or too vague, add issue templates such as:
- bug report
- skill request / improvement proposal

This reduces future ambiguity and makes maintenance easier.

### 8. Verify every public skill has the expected structure
Check that each new or heavily edited skill includes:
- frontmatter
- `## When to Use`
- `## Procedure`
- `## Pitfalls`
- `## Verification`

### 9. Commit and push cleanly
```bash
git add .
git commit -m "docs: maintain skills repo"
git push
```

### 11. Bootstrap a New Skills Repository

When scaffolding a shareable GitHub repository for Hermes skills (e.g., for astronomy/astroinformatics workflows, REANA, Open WebUI integration):

### Procedure
1. Fix SSH host-key trust first if needed: `ssh-keyscan github.com >> ~/.ssh/known_hosts`
2. Clone into a local folder
3. Create top-level category dirs: `astronomy/`, `workflows/`, `python/`, `infrastructure/`, `research/`, `agents/`
4. Add a root `README.md` explaining the repo purpose, categories, and how to add as a Hermes tap
5. Add starter skills as focused scaffolds (not one giant skill)

### Layout convention
See `references/repo-scaffold-example.md` for the recommended directory structure.

## 12. Publish Skills to the AstroAgentAssistant Repo

When publishing new or updated skills to the arm2arm/AstroAgentAssistant GitHub repo:

### Procedure
1. Clone/pull latest repo
2. Credential audit — grep ALL SKILL.md files for credential patterns (<user>, Aac3, api_key, secret, password)
3. Write SKILL.md with standard format (frontmatter, When to Use, Procedure, Pitfalls, Verification)
4. Update README.md skill inventory
5. Commit and push (use repo-local git identity to avoid changing global)

### Repository layout note
The public repo also uses a `science/` top-level directory for digital-twin/accelerator-science skills. Place dtwin-related skills there and update README inventory accordingly.

## 13. Remove Standard/Bundled Skills from the Repo

When cleaning the public repo to keep only custom-developed skills:

### Procedure
1. Read `~/.hermes/skills/.bundled_manifest` as the source of truth
2. Parse `name:` frontmatter from every SKILL.md (never trust directory names — same skill can exist in multiple paths)
3. Identify and remove directories matching bundled names
4. Clean empty directories
5. Rewrite README inventory to match remaining custom skills only
6. Commit and push

## 11. Mass-sync local skill registry to repo (new skills)
When the local registry has grown and needs a full sync to the repo:

```bash
# From agent session:
python3 << 'EOF'
import subprocess, os, shutil

local_skills_dir = os.path.expanduser("~/.hermes/skills")
repo_path = "/tmp/AstroAgentAssistant"

copied = 0
skipped = 0

for root, dirs, files in os.walk(local_skills_dir):
    for f in files:
        if f == 'SKILL.md':
            rel = os.path.relpath(root, local_skills_dir)
            # Only handle categories (depth 1) and subcategories (depth 2+)
            parts = rel.split('/')
            if len(parts) >= 1:
                repo_dest = os.path.join(repo_path, rel, f)
                os.makedirs(os.path.dirname(repo_dest), exist_ok=True)
                if not os.path.exists(repo_dest):
                    shutil.copy2(os.path.join(root, f), repo_dest)
                    copied += 1
                else:
                    skipped += 1

# Also copy DESCRIPTION.md files for category dirs
for root, dirs, files in os.walk(local_skills_dir):
    for f in files:
        if f == 'DESCRIPTION.md':
            rel = os.path.relpath(root, local_skills_dir)
            repo_dest = os.path.join(repo_path, rel, f)
            os.makedirs(os.path.dirname(repo_dest), exist_ok=True)
            if not os.path.exists(repo_dest):
                shutil.copy2(os.path.join(root, f), repo_dest)

print(f"Copied {copied} SKILL.md files, {skipped} already in repo")
EOF
```

Then count everything and update the README:

```bash
cd /tmp/AstroAgentAssistant
# Count all SKILL.md files grouped by category
find . -name 'SKILL.md' | xargs -I{} sh -c '
  d=$(dirname "{}" | cut -d/ -f2)
  echo "$d"
' | sort | uniq -c | sort -rn
```

## Pitfalls
- Do not assume the issue description matches the current repo state.
- Do not add new public skills without README updates.
- Do not let taxonomy drift create multiple overlapping skills with unclear roles.
- Do not mix authentication/setup guidance into task-execution skills when a dedicated setup skill is clearer.
- Do not close or consider an issue resolved until the repository structure reflects the intended fix.
- **Mass sync caveat:** Empty category directories (with only DESCRIPTION.md, no SKILL.md) are harmless — they're just category shells. Also, skills in subdirectories (e.g., `mlops/cloud/`, `software-development/plan/`) will be placed under their top-level category by the `find` approach, matching the existing repo taxonomy.

## References

- `references/astroagent-audit-checklist.md` — concrete audit checklist for AstroAgentAssistant-style repositories: inventory/README consistency, duplicate taxonomy, frontmatter parsing, section coverage, secret-like hit classification, and bundled-skill leakage checks.
- `references/class-level-canonicalization-pattern.md` — pattern for turning many narrow, overlapping skills into canonical class-level umbrella skills while preserving legacy examples through `## Canonical Routing` notes.
- `references/custom-only-skill-repo-cleanup.md` — procedure for pruning a public skills repository to only team-developed skills by comparing frontmatter names against `.bundled_manifest`, removing third-party/vendor-authored entries, regenerating README counts, and auditing before push.
- `references/repo-wide-skill-test-reporting.md` — pattern for creating a `tests/` folder with per-skill static test results, CSV/JSON outputs, a test-result diagram, a PDF report, and sanitized secret-scan summaries.

## Verification
- Secret scan passes.
- README and skill files stay in sync.
- Canonical and specialized skill roles are clear from names, descriptions, and related links.
- Vague issues are converted into concrete, reviewable repository changes.

## Reference Patterns
- See `references/repo-audit-cleanup-pattern.md` for a complete audit-cleanup pattern: inventory drift, frontmatter validation, duplicate-name/content detection, canonical taxonomy cleanup, support-file preservation, README regeneration, credential review, section normalization, and final validation checks.
- See `references/taxonomy-regrouping-pattern.md` for regrouping flat/singleton skill repositories into stable class-level domain groups using `git mv`, canonical category rules, README regeneration, and validation checks.
- When adding operational helper scripts to skills repositories, require both local no-token tests and at least one live smoke test if credentials/backends are available. Local scaffold/YAML-parse tests can miss native-vs-Docker path bugs and backend-specific YAML validation warnings.
