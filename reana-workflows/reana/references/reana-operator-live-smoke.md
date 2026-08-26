# REANA operator live-smoke lessons

Session context: while implementing and live-testing a user-facing REANA operator workflow against the AIP dev backend, the local helper initially passed local no-token tests but exposed several real REANA-client/YAML pitfalls during a live smoke run.

## Durable lessons

1. **Native `reana-client` vs Dockerized client use different paths.**
   - Native client must be run with `cwd` set to the project/workflow directory and should receive `-f reana.yaml`.
   - Dockerized client should mount the project, set `-w /workspace`, and may receive `-f /workspace/reana.yaml`.
   - Do not blindly use `/workspace/reana.yaml` when native `reana-client` is on PATH.

2. **Do not rely on `$REANA_WORKSPACE` expansion in generated serial commands unless already verified for that backend/client.**
   A live dev-backend smoke test failed with:
   `Workflow parameter(s) could not be expanded. Please take a look to 'REANA_WORKSPACE'`.
   The robust generated command for uploaded scripts was simply:
   `bash -lc 'if [ -f requirements.txt ]; then pip install --quiet -r requirements.txt; fi && python3 analysis.py'`

3. **Current dev backend rejected/warned on some older nested keys.**
   The generated YAML should avoid step-level `outputs:` and step-level `resources:` if the REANA validator warns they are unexpected. Use top-level `outputs.files` plus backend-specific keys:
   - `kubernetes_memory_limit: "32Gi"`
   - `kubernetes_job_timeout: 7200`
   - `compute_backend: kubernetes`

4. **Live smoke-test sequence for generated project support.**
   - `ping` must connect.
   - `scaffold` creates `analysis.py`, `.reanaignore`, and `reana.yaml`.
   - `validate` must pass locally.
   - `run` must queue successfully.
   - Poll `status` until `finished` or `failed`.
   - Inspect `logs` on failure.
   - `download` and read `output.txt` to verify real execution.

## Minimal tested `reana.yaml` shape

```yaml
version: 0.9.0
inputs:
  files:
    - analysis.py
workflow:
  type: serial
  specification:
    steps:
      - name: reana-operator-smoke
        environment: gitlab-p4n.aip.de:5005/p4nreana/reana-env:py311-astro-ml.2891a60c
        kubernetes_memory_limit: "32Gi"
        kubernetes_job_timeout: 7200
        compute_backend: kubernetes
        commands:
          - bash -lc 'if [ -f requirements.txt ]; then pip install --quiet -r requirements.txt; fi && python3 analysis.py'
outputs:
  files:
    - output.txt
```

## Verification result from live test

A smoke workflow using the above pattern reached `finished`, logs showed `wrote output.txt`, and `reana-client download` retrieved `output.txt` with the expected content. This is stronger than local scaffold/parse validation and should be preferred before calling a REANA helper production-ready.
