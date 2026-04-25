---
name: astro-agent-assistant-repo
description: Workflow for publishing Hermes skills to arm2arm/AstroAgentAssistant GitHub repo — credential audit, SKILL.md authoring, README update, commit, and push.
version: 1.0.0
license: MIT
created: 2026-04-15
tags: [hermes, skills, github, publishing, security]
hermes:
  domain: software-development
  conversations: []
metadata:
  github: arm2arm/AstroAgentAssistant
  git_url: git@github.com:arm2arm/AstroAgentAssistant.git
  branch: main
  skill_dirs: astronomy, workflows, infrastructure, research, python, productivity, mlops, gaming, leisure, social-media, note-taking, data-science, devops, creative, email, github, mcp
---

## When to Use

When publishing skills to the AstroAgentAssistant GitHub repository:
- New skill from scratch → clone repo, write SKILL.md, audit credentials, commit, push
- Publishing from `~/.hermes/skills/` → verify all credentials, commit, push

## Procedure

### 1. Clone / pull latest

```bash
cd /tmp
rm -rf AstroAgentAssistant
git clone git@github.com:arm2arm/AstroAgentAssistant.git
cd AstroAgentAssistant
```

**Current observed local path:** `/tmp/AstroAgentAssistant`

**Current repo layout note:** the public repo now also uses a `science/` top-level directory for digital-twin / accelerator-science skills (for example `science/dtwin-setup`, `science/dtwin-host-smoke-test`, `science/dtwin-epics-runbook`). When publishing new dtwin-related skills, place them under `science/` and update the README inventory accordingly.

### 2. Credential audit — scan ALL published SKILL.md files

Use `grep` for known credential patterns:

```bash
grep -rP '(akhalatyan|Aac3|api_key|apikey|secret|password|passwd)' --include='*.md' --include='*.yaml' --include='*.py' .
```

**Red flags** to look for:
- Personal usernames (e.g. `akhalatyan`) hardcoded in curl examples → replace with `$ENV_VAR`
- Passwords or tokens → replace with `$TOKEN` or `$PASSWORD`
- API keys → replace with `$API_KEY`

**OK / safe patterns:**
- Ellipsis placeholders: `access_key='...'`
- Generic env vars: `$CALDAV_USER`, `$REANA_TOKEN`
- Session/cookie names without values

### 3. Write SKILL.md

Standard format:

```markdown
---
name: <skill-name>
description: One-line description.
version: 1.0.0
license: MIT
created: YYYY-MM-DD
tags: [tag1, tag2]
hermes:
  domain: <category>
metadata:
  related_skills: ["skill-a", "skill-b"]
---

## When to Use
<one sentence>

## Procedure
<numbered steps with exact commands>

## Pitfalls
<common mistakes>

## Verification
<how to confirm it works>
```

### 4. Update README.md

```bash
# Add to README.md skill inventory table:
# | <category> | <name> | <description> | [docs] |
```

### 5. Commit and push

```bash
git add .
git commit -m "feat: add <category>/<name> skill"
git push
```

**If commit fails because git identity is unset**, configure a repo-local identity and retry:

```bash
git config user.name "Hermes Agent"
git config user.email "hermes@arm2arm.dev"
git commit -m "feat: add <category>/<name> skill"
git push
```

Prefer repo-local `git config` here so global git identity is not changed unnecessarily.

## Pitfalls

- **Never push credentials to public GitHub** — always audit with grep before commit
- **URL-encoded paths** in CalDAV: `Persoenlich` = `pers%C3%B6nlich` (UTF-8)
- **REANA client** may not be installed in this environment — check with `which reana-client` before attempting REANA workflows
- **Git push** requires SSH key auth — use `gh auth login --git-protocol ssh` or `git@` URL directly

## Verification

```bash
# Check repo is accessible
git ls-remote git@github.com:arm2arm/AstroAgentAssistant.git

# Verify last push
git log --oneline -3

# Confirm no secrets leaked
grep -rP '(akhalatyan|Aac3)' --include='*.md' .
# Must return empty
```