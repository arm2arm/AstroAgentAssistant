# REANA Operator Pattern

Use this pattern when turning a set of narrow REANA skills into a practical front-door operator skill.

## User intents to support

- Check one workflow/job status by name or UUID.
- Show available/active backends: current `REANA_SERVER_URL`, token configured yes/no, native `reana-client` availability, Docker fallback, and any local `~/.reana/config.yaml` profiles.
- List recent workflows with optional status filters: success/finished, failed/error, running/active, pending/queued/created, stopped/cancelled.
- Show logs for a workflow, especially failed jobs.
- Download outputs or list workspace files.
- Scaffold a new project from code/script/command with an appropriate `reana.yaml`.
- Validate `reana.yaml` before submission.
- Submit/run the project using environment credentials.

## Durable implementation choices

- Assume credentials are already exported as `REANA_SERVER_URL` and `REANA_ACCESS_TOKEN`.
- Never write or print `REANA_ACCESS_TOKEN`; display only `Token configured: yes/no`.
- Prefer native `reana-client` if installed; otherwise use Docker with `REANA_CLIENT_IMAGE`, defaulting to a known client image.
- Use separate script files (`analysis.py`, `run.sh`) instead of inline heredoc blocks in YAML.
- Commands that run uploaded code should explicitly `cd "$REANA_WORKSPACE"`.
- Default AIP resources: `kubernetes_memory_limit: "32Gi"`, `kubernetes_job_timeout: 7200` unless the user requests otherwise.
- Generate `.reanaignore` to avoid uploading `.git/`, `.env`, `.reana/`, caches, virtualenvs, and outputs.

## CLI shape that worked well

```bash
python reana_operator.py ping
python reana_operator.py backends
python reana_operator.py recent --status failed --limit 10
python reana_operator.py status <workflow>
python reana_operator.py logs <workflow> --tail 100
python reana_operator.py scaffold --project myproj --script analysis.py --output output.txt
python reana_operator.py validate --project myproj
python reana_operator.py run --project myproj --workflow myproj-001
python reana_operator.py download <workflow> --out outputs/
```

## Validation checklist

- `--help` works for the top-level command and subcommands.
- Scaffold creates `reana.yaml`, `.reanaignore`, and the target script when code is supplied.
- Generated YAML parses with PyYAML.
- `validate --project <dir>` catches missing input files and obvious token leakage.
- `backends` works without credentials and does not print token values.
- Python helper passes `python -m py_compile`.
- README inventory and skill audit still report no duplicate names, no frontmatter errors, and no README count mismatch.
