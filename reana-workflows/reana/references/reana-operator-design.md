# REANA Operator Skill Design

Use this reference when turning natural-language REANA requests into concrete commands or when adding a polished `reana-operator` skill/script.

## Core assumption

For execution, assume the user has already exported credentials in the environment:

```bash
REANA_SERVER_URL=...
REANA_ACCESS_TOKEN=...
```

Do not ask for or write tokens by default. Start operational commands with explicit checks:

```bash
: "${REANA_SERVER_URL:?Set REANA_SERVER_URL}"
: "${REANA_ACCESS_TOKEN:?Set REANA_ACCESS_TOKEN}"
REANA_CLIENT_IMAGE="${REANA_CLIENT_IMAGE:-reanahub/reana-client:0.95.0-alpha.3}"
```

Prefer native `reana-client` if installed; otherwise use a Docker wrapper that passes `REANA_SERVER_URL` and `REANA_ACCESS_TOKEN` as environment variables. Never print the token.

## Natural-language capabilities to support

| User asks | Action | Command pattern |
|---|---|---|
| “Is REANA alive?” / “Which backend am I using?” | Health check | `reana-client ping`; report server URL, versions, authenticated user/status if printed |
| “Job status for X” | Workflow status | `reana-client status -w X` |
| “Show logs for X” / “Why did it fail?” | Logs + diagnosis | `reana-client logs -w X`; tail logs for failed jobs |
| “Recent jobs” | List recent workflows | `reana-client list -v --json`, format table |
| “Recent failed/successful/pending jobs” | Filter list by normalized status | JSON filter on `.status` |
| “Available backends” | Report active env backend and known config profiles | `$REANA_SERVER_URL`, `reana-client ping`, optionally parse `~/.reana/config.yaml` and `.reana/config.yaml` |
| “Run this code on REANA” | Scaffold project + `reana.yaml` + submit | create script file, validate inputs, `reana-client run -w <name> -f reana.yaml` |
| “Create a REANA project” | Scaffold only | make project dir with script, optional requirements, `reana.yaml`, README/next commands |
| “Download outputs from X” | Retrieve artifacts | `reana-client ls -w X`; `reana-client download -w X -o outputs/X` |
| “Rerun the last failed job” | Find failed workflow, rerun local project if available | list/filter failed jobs; use timestamped workflow name if creating a new run |

## Status normalization

Map user terms to likely REANA statuses:

- success/successful/finished/done → `finished`, `succeeded`
- failed/error/broken → `failed`
- pending/queued/waiting → `created`, `queued`, `pending`
- running/active → `running`
- stopped/cancelled → `stopped`, `deleted`, `cancelled`

Default recent-job limit: 10. For Telegram output, present a compact table:

```text
name | run_number | status | created | duration | id
```

## Project scaffold defaults

For a new Python job:

```text
project/
  reana.yaml
  analysis.py
  requirements.txt      # optional
  README.md             # optional, with run/status/log/download commands
```

Safe default `reana.yaml` shape:

```yaml
inputs:
  files:
    - analysis.py
    # - requirements.txt

workflow:
  type: serial
  specification:
    steps:
      - name: run-analysis
        environment: gitlab-p4n.aip.de:5005/p4nreana/reana-env:py311-astro-ml.2891a60c
        kubernetes_memory_limit: "32Gi"
        kubernetes_job_timeout: 7200
        commands:
          - bash -lc 'cd "$REANA_WORKSPACE" && if [ -f requirements.txt ]; then pip install --quiet -r requirements.txt; fi && python3 analysis.py'
        outputs:
          files:
            - output.txt

outputs:
  files:
    - output.txt
```

Prefer separate script files over inline heredocs. Always `cd "$REANA_WORKSPACE"` before running uploaded scripts.

## Validation checklist before running

- `REANA_SERVER_URL` and `REANA_ACCESS_TOKEN` are set.
- `reana.yaml` exists.
- Every file in `inputs.files` exists locally.
- No token/password/API key appears in `reana.yaml`, `.env`, or files being uploaded.
- Workspace does not include `.git/`, `.reana/`, `.env`, private keys, or very large unintended files.
- Memory defaults to `32Gi`/`32gb` unless user explicitly chooses otherwise.
- Timeout is set.
- Outputs are declared.
- Command uses `$REANA_WORKSPACE` for uploaded scripts.

## Recommended helper CLI shape

If implementing a reusable script, expose:

```bash
python scripts/reana_operator.py ping
python scripts/reana_operator.py backends
python scripts/reana_operator.py recent --status failed --limit 10
python scripts/reana_operator.py status <workflow>
python scripts/reana_operator.py logs <workflow> --tail 100
python scripts/reana_operator.py scaffold --project myproj --script analysis.py --output output.txt
python scripts/reana_operator.py validate --project myproj
python scripts/reana_operator.py run --project myproj --workflow myproj-$(date +%Y%m%d-%H%M%S)
python scripts/reana_operator.py download <workflow> --out outputs/
```

Implementation notes:

- Use Python for JSON filtering and table formatting.
- Fall back to Docker if `reana-client` is unavailable.
- Do not print secrets.
- For failed jobs, show a concise status block and last relevant log lines.
- For ambiguous workflow names, list recent candidates rather than guessing destructively.
