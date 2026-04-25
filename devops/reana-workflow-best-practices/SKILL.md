---
name: reana-workflow-best-practices
description: How to write a correct REANA workflow YAML that complies with the organization’s policies.
author: Hermi (sorgenfresser)
---

## Goal
Provide a concise, copy‑paste ready template and a checklist for creating REANA workflows that:
* Use an **approved environment** from `https://gitlab-p4n.aip.de/punch_public/reana/environments`.
* Declare **inputs** (files that must be bundled, e.g. scripts, data files).
* Set **resources** with the default **32 GB memory** (as required by the user).
* List **outputs** so REANA knows which artefacts to retrieve.
* Avoid custom environments – always reference an existing one.

## Template
```yaml
# ------------------------------------------------------------
# REANA workflow definition – replace placeholders where noted
# ------------------------------------------------------------
inputs:
  files:
    - <your_script.py>          # list every file the workflow needs
    # - <additional_input.dat>
    # - <config.yaml>

workflow:
  type: serial
  specification:
    steps:
      - name: <step_name>
        environment: <approved_environment>
        commands:
          - <install_cmd>   # e.g. pip install --quiet dask[dataframe] s3fs matplotlib seaborn pyarrow
          - python <your_script.py>
        resources:
          memory: 32gb            # mandatory default
          runtime: <hh:mm:ss>     # adjust as needed
        env:
          # optional runtime environment variables
          # EXAMPLE_VAR: value
        outputs:
          files:
            - <output_file.ext>

outputs:
  files:
    - <output_file.ext>
```
### Replace the placeholders:
| Placeholder | What to put |
|------------|--------------|
| `<your_script.py>` | The Python script (e.g. `plot_cmd.py`). |
| `<step_name>` | A short, descriptive name (e.g. `plot`). |
| `<approved_environment>` | One of the environments from the organisation’s repo, e.g. `gitlab-p4n.aip.de:5005/p4nreana/reana-env:py311-astro-ml.2891a60c`. |
| `<install_cmd>` | Any package installation needed (keep it a single line). |
| `<hh:mm:ss>` | Expected maximum runtime (e.g. `02:00:00`). |
| `<output_file.ext>` | The file you want REANA to keep (e.g. `cmd.png`). |

## Checklist before `reana-client create`
1️⃣ **All needed files are listed under `inputs.files`.**
2️⃣ **Environment matches an entry in the approved repo** (no custom Dockerfile). 
3️⃣ **Memory is set to `32gb`.**
4️⃣ **Runtime (`runtime:`) is reasonable; too short may cause premature termination.**
5️⃣ **Outputs are declared both inside the step (`outputs.files`) and at the top‑level (`outputs.files`).**
6️⃣ **No stray keys** – the REANA validator will warn about unexpected properties (e.g. `env` at the top level is invalid; keep `env` inside the step). 

## Common pitfalls & fixes
* **Missing input files** → REANA cannot find your script and fails with *"can't open file"*. Add the file to `inputs.files`.
* **Wrong environment name** → REANA rejects the workflow. Verify the exact tag from the repo.
* **Outputs not declared** → REANA will not expose the artefact; add the file name under both `outputs.files` sections.
* **Memory not 32 GB** → violates policy; adjust `resources.memory`.

## Example (the one you need for the CMD plot)
```yaml
inputs:
  files:
    - plot_cmd.py

workflow:
  type: serial
  specification:
    steps:
      - name: plot
        environment: gitlab-p4n.aip.de:5005/p4nreana/reana-env:py311-astro-ml.2891a60c
        commands:
          - pip install --quiet dask[dataframe] s3fs matplotlib seaborn pyarrow
          - python plot_cmd.py
        resources:
          memory: 32gb
          runtime: 02:00:00
        env:
          S3_ENDPOINT: https://s3.data.aip.de:9000
          S3_BUCKET: shboost2024
          S3_PREFIX: shboost_08july2024_pub.parq/
        outputs:
          files:
            - cmd.png

outputs:
  files:
    - cmd.png
```
Save this skill and refer to it whenever you need to write a new REANA workflow.
