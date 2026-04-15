---
name: github-pr-workflow
description: Full pull request lifecycle — create branches, commit changes, open PRs, monitor CI status, auto-fix failures, and merge. Works with gh CLI or falls back to git + GitHub REST API via curl.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [github, pull-request, git, ci-cd, code-review, pr]
    category: github
    related_skills: [github-code-review, github-issues, github-repo-management, github-auth]
---

# GitHub PR Workflow

## When to Use
Use this skill for any PR lifecycle task: opening a PR, checking CI status, fixing CI failures, getting PR reviews, merging, or squashing.

## Procedure

### 1. Create a feature branch
```bash
git checkout -b feat/my-feature
# or
gh pr create --branch feat/my-feature
```

### 2. Commit changes
```bash
git add .
git commit -m "feat: add RAVE DR6 TAP query skill

- Query RAVE DR6 via pyvo run_sync
- Add RA/Dec and galactic projections
- Cache results as Parquet"
```

### 3. Push
```bash
git push -u origin feat/my-feature
```

### 4. Open a PR
```bash
gh pr create \
  --title "feat: RAVE DR6 TAP query skill" \
  --body "## Summary
Query RAVE DR6 catalog via TAP and plot RA/Dec and galactic projections.
## Changes
- Add astronomy/rave-dr6/SKILL.md
- Add references/ for query examples
## Testing
- Tested locally with 100 nearest stars
Closes #<issue>" \
  --base main
```

### 5. Check CI status
```bash
gh pr check
# or
gh api repos/:owner/:repo/commits/$COMMIT/status
```

### 6. Get PR reviews
```bash
gh pr view --reviews
```

### 7. Merge
```bash
gh pr merge --admin --merge
# or squash:
gh pr merge --squash --body "Closes #<issue>"
```

### 8. Auto-fix CI failures (example: linting)
```bash
# Run linter locally and push fixes
pre-commit run --all-files
git add -p  # review auto-fixes
git commit -m "fix: resolve linting issues"
git push
```

## gh CLI vs git fallback

The `gh` CLI is preferred. If not available, use the GitHub REST API:

```bash
# Create PR via API
curl -s -X POST "https://api.github.com/repos/$OWNER/$REPO/pulls" \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "...", "head": "feat:branch", "base": "main", "body": "..."}'
```

## PR Templates

Place `.github/pull_request_template.md` in the repo root:
```markdown
## Summary
<!-- What does this PR do? -->

## Changes
<!-- List the files changed -->

## Testing
<!-- How was this tested? -->

## Checklist
- [ ] Tests pass
- [ ] Docs updated
- [ ] Breaking changes documented
```

## Pitfalls
- Do NOT push directly to `main` — always use feature branches and PRs.
- Do NOT use `git push -f` on shared branches — it breaks other collaborators.
- PR descriptions should reference the issue: `Closes #<number>`.
- Squash merge is preferred for clean history, but use merge commit for multi-commit feature PRs.

## Verification
- `gh pr create` returns a PR URL.
- CI checks reach `success` state.
- PR merges cleanly into `main`.