---
name: skills-repo-maintenance
description: Maintain the AstroAgentAssistant skills repository by auditing secrets, checking README coverage, reviewing overlapping skills, and keeping skill metadata consistent.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [github, maintenance, skills, repository, auditing, taxonomy]
    category: github
    related_skills: [github-pr-workflow, astro-agent-assistant-repo]
---

# Skills Repo Maintenance

## When to Use
Use this skill when maintaining the public skills repository itself: adding skills, reviewing overlap, auditing for secrets, syncing README inventory entries, and checking issue reports against the actual repository state.

## Procedure

### 1. Pull the latest repo state
```bash
cd /tmp/AstroAgentAssistant
git pull --ff-only
```

### 2. Audit for secrets before every push
```bash
grep -rP '(akhalatyan|Aac3|api_key|apikey|secret|password|passwd)' \
  --include='*.md' --include='*.yaml' --include='*.py' .
```

Manually distinguish between real secrets and safe placeholders.

### 3. Check README coverage
Whenever a new public skill is added, verify that the README inventory mentions it in the correct section.

### 4. Review overlap and taxonomy
When skills overlap:
- choose one canonical umbrella skill
- create specialized companion skills only when scope is clearly different
- add `related_skills` links so users can navigate between them
- clarify naming in README when confusion is likely

### 5. Keep issue reports actionable
If an issue is too vague:
- reproduce the repo state first
- identify the exact files involved
- convert the vague problem into a concrete skill split, rename, merge, or metadata change

### 6. Verify new/updated skills
Each public skill should have:
- frontmatter
- `## When to Use`
- `## Procedure`
- `## Pitfalls`
- `## Verification`

### 7. Commit and push cleanly
```bash
git add .
git commit -m "docs: maintain skills repo"
git push
```

## Pitfalls
- Do not push example credentials that look real.
- Do not add new public skills without README updates.
- Do not let taxonomy drift create multiple overlapping skills with unclear roles.
- Do not close an issue until the repo state actually reflects the intended fix.

## Verification
- Secret scan passes.
- README and skill files stay in sync.
- New skills are placed in the correct top-level category.
- Canonical and specialized skill roles are clear from names and descriptions.
