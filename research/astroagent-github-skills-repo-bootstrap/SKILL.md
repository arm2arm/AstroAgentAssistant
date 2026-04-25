---
name: astroagent-github-skills-repo-bootstrap
description: Scaffold a shareable GitHub repository for Hermes skills focused on AstroAgent, astronomy workflows, REANA, Open WebUI integration, and local dataset operations.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [github, skills, astronomy, astroagent, repository, knowledge-base]
    related_skills: [github-repo-management, hermes-agent, llm-wiki]
---

# AstroAgent GitHub Skills Repo Bootstrap

Use this skill when the user wants to create a shareable GitHub repository of Hermes skills for astronomy/astroinformatics work, especially around AstroAgent, AIP datasets, REANA, and Open WebUI integration.

## When to Use
- The user wants a GitHub-hosted Hermes skills repository
- The repo should be structured for team sharing and future `hermes skills tap add owner/repo`
- The content mixes reusable procedures with small reference files and templates
- The user already has GitHub access configured and wants a local repo scaffold fast

## Procedure
1. Load the existing repo if provided; otherwise clone it locally via SSH or HTTPS.
2. If SSH clone fails with `Host key verification failed`, fix GitHub trust first:
   - `mkdir -p ~/.ssh && chmod 700 ~/.ssh`
   - `ssh-keyscan github.com >> ~/.ssh/known_hosts`
   - `chmod 600 ~/.ssh/known_hosts`
   - verify with `ssh -T git@github.com`
3. Clone into a local folder chosen by the user, e.g. `/home/hermes/astroagent`.
4. Create the top-level starter layout:
   - `astronomy/`
   - `workflows/`
   - `python/`
   - `infrastructure/`
   - `research/`
   - `agents/`
5. Add a root `README.md` that explains:
   - what the repo is for
   - the top-level categories
   - how to add the repo as a Hermes tap
   - skill authoring expectations (`When to Use`, `Procedure`, `Pitfalls`, `Verification`)
6. Add starter skills as small, focused scaffolds instead of one giant omnibus skill.

## Recommended Starter Repo Layout
```text
astroagent/
├── README.md
├── astronomy/
│   ├── shboost24-cmd/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── starhorse-access/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── gaia-aip-de-adql/
│   │   ├── SKILL.md
│   │   └── references/
│   └── data-aip-de-s3/
│       ├── SKILL.md
│       └── references/
├── workflows/
│   ├── reana-aip/
│   │   ├── SKILL.md
│   │   ├── templates/
│   │   └── references/
│   └── reana-shboost24/
│       ├── SKILL.md
│       └── templates/
├── python/
│   ├── cmd-plotting/
│   │   ├── SKILL.md
│   │   └── templates/
│   └── seaborn-paper-plots/
│       └── SKILL.md
├── infrastructure/
│   ├── openwebui-hermes/
│   │   ├── SKILL.md
│   │   └── references/
│   └── hermes-api-server/
│       └── SKILL.md
├── research/
│   └── 2026-agentic-astronomy-literature/
│       ├── SKILL.md
│       └── references/
└── agents/
    └── astroagent-concept/
        └── SKILL.md
```

## Content Guidance
- Put procedures in `SKILL.md`
- Put stable background material in `references/`
- Put reusable runnable snippets in `templates/`
- Keep each skill narrow and composable
- Prefer many focused skills over one giant astronomy skill

## Pitfalls
- SSH clone may fail initially because GitHub is not in `known_hosts`; fix host-key trust first.
- Existing repos may already contain `.gitignore`; patch or extend it instead of assuming a clean replacement.
- Do not put secrets or credentials in skills; use skill frontmatter/env requirements instead.
- Do not turn a full research wiki into one skill; procedural skills should stay execution-oriented.

## Verification
- `git -C <repo> status --short --branch` shows the expected new files
- `search_files(pattern='SKILL.md', target='files', path='<repo>')` lists the scaffolded skills
- `read_file(<repo>/README.md)` confirms usage instructions and tap guidance are present

## Example Follow-up
After scaffolding, suggest:
- refine the starter skills with exact local conventions
- commit the repo
- push to GitHub
- test installability with `hermes skills tap add owner/repo`
