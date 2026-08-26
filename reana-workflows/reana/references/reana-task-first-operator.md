# REANA task-first operator implementation notes

Use this reference when maintaining or extending the AstroAgentAssistant `reana-operator` / `reana-client-failover` skills.

## Durable pattern

When the user provides an executable scientific/computational task, prefer the REANA path by default:

1. Create a clean project directory.
2. Write or identify the main script, normally `analysis.py`.
3. Detect Python imports via `ast`.
4. Read `requirements.txt` if present.
5. Accept explicit `--package <name>` declarations for packages the task needs but import detection may miss.
6. Select a modeled REANA environment profile, defaulting to the AIP astro/ML image:
   `gitlab-p4n.aip.de:5005/p4nreana/reana-env:py311-astro-ml.2891a60c`.
7. Compare requested packages to the curated profile availability model.
8. Generate `reana.yaml` with runtime `pip install --quiet ...` only for packages not modeled as available.
9. Write `reana-env-report.md` describing detected imports, standard-library imports, profile-provided packages, and runtime-installed packages.
10. Validate and run via `reana-client`, with native→Docker failover.

## Important CLI shape

```bash
python reana-workflows/reana-operator/scripts/reana_operator.py task \
  --project /tmp/my-reana-task \
  --task "short task description" \
  --code 'from pathlib import Path; Path("output.txt").write_text("hello\n")' \
  --output output.txt \
  --environment-profile astro-ml \
  --run --timestamp
```

If code is not ready, omit `--code`; the helper may create a safe placeholder `analysis.py`, generate a task-specific `reana.yaml`, and instruct the user to replace the script before submission.

## Environment profiles

Maintain these as curated availability models, not formal lockfiles:

- `astro-ml`: `gitlab-p4n.aip.de:5005/p4nreana/reana-env:py311-astro-ml.2891a60c`; default scientific Python / astronomy / ML-adjacent tasks.
- `astro`: `gitlab-p4n.aip.de:5005/p4nreana/reana-env:py311-astro`; astronomy without heavy ML dependencies.
- `python`: `python:3.11-slim`; minimal image, install explicit packages.

Expose them with:

```bash
python reana-workflows/reana-operator/scripts/reana_operator.py envs
```

## Validation and smoke tests

Local tests should cover:

- `envs` lists profiles.
- a script importing available libs such as `numpy`, `pandas`, `matplotlib` produces no extra `pip install`.
- a script importing a missing lib such as `healpy` generates `pip install --quiet healpy && python3 analysis.py`.
- `task` placeholder mode writes the task description into `analysis.py` and validates.
- no `REANA_ACCESS_TOKEN` appears in generated files.

Live smoke test, if dev credentials are available:

```bash
python reana-workflows/reana-operator/scripts/reana_operator.py task \
  --project /tmp/reana-task-live \
  --workflow reana-task-envaware \
  --task 'environment-aware REANA smoke test' \
  --code 'import numpy as np; from pathlib import Path; Path("output.txt").write_text("sum=" + str(np.arange(5).sum()) + "\n")' \
  --output output.txt \
  --environment-profile astro-ml \
  --run --timestamp
```

Expected result: workflow reaches `finished`; downloaded `output.txt` contains `sum=10`.

## Pitfalls

- Do not hard-code or print `REANA_ACCESS_TOKEN`; pass it through the environment only.
- Native `reana-client` must run from the project directory with `-f reana.yaml`; Docker mode mounts the project at `/workspace` and uses `/workspace/reana.yaml`.
- Avoid injecting `cd "$REANA_WORKSPACE"` into generated commands on the AIP dev backend; live smoke tests showed parameter expansion failures for that pattern.
- Keep `reana-env-report.md` as provenance input so users understand why packages were or were not installed.
