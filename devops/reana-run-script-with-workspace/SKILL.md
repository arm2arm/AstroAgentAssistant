---
name: reana-run-script-with-workspace
description: Run a Python (or other) script in a REANA workflow ensuring the script is found via $REANA_WORKSPACE.
author: Hermi (sorgenfresser)
---

## Purpose
When a workflow includes custom scripts uploaded as input files, REANA executes steps in a working directory that may not be the same as the workspace root. Using `$REANA_WORKSPACE` guarantees the script path resolves correctly.

## Steps
1. **Declare the script as an input file** in the `reana.yaml`:
   ```yaml
   inputs:
     files:
       - my_script.py
   ```
2. **Reference the script in the command** using `$REANA_WORKSPACE`:
   ```yaml
   commands:
     - bash -c "cd $REANA_WORKSPACE && pip install --quiet <deps> && python my_script.py [--args]"
   ```
   * The `cd $REANA_WORKSPACE` part moves to the workspace root where the uploaded file resides.
   * You can chain installation and execution in a single `bash -c` to keep the step atomic.
3. **Set resources** (memory 32 GB, runtime as needed) and compute backend:
   ```yaml
   compute_backend: kubernetes
   resources:
     memory: 32gb
     runtime: 02:00:00
   ```
4. **Upload the script** before starting the workflow:
   ```bash
   reana-client upload -w <workflow_name> <path/to/my_script.py>
   ```
5. **Start the workflow**:
   ```bash
   reana-client start -w <workflow_name>
   ```

## Example `reana.yaml`
```yaml
environment:
  repo: https://gitlab-p4n.aip.de/punch_public/reana/environments
  name: py311-astro
inputs:
  files:
    - shboost_plot_cached.py
workflow:
  type: serial
  specification:
    - name: cmd_plot
      type: run
      environment: gitlab-p4n.aip.de:5005/p4nreana/reana-env:py311-astro-ml.2891a60c
      commands:
        - bash -c "cd $REANA_WORKSPACE && pip install --quiet pandas dask[complete] numpy matplotlib seaborn s3fs && python shboost_plot_cached.py --force-refresh"
      compute_backend: kubernetes
      resources:
        memory: 32gb
        runtime: 02:00:00
      outputs:
        files:
          - shboost_cmd.png
          - shboost_population_animation.gif
```

## Pitfalls & Tips
* **Never** assume the current directory is `$REANA_WORKSPACE`; always `cd` explicitly.
* If you need additional files (data, config), list them under `inputs/files`.
* Combine `pip install` and script execution in one `bash -c` to avoid separate steps that could lose the working directory.
* Verify the script name matches exactly (case‑sensitive) in the `inputs` list.
* Use `--force-refresh` or similar flags in the script to control caching behavior.
* Remember REANA validates the `environment` block; keep it from the organisation repo.

## When to use
* Any REANA workflow that runs a custom script uploaded by the user.
* When the script relies on relative file paths or needs to be executed from the workspace root.
* To avoid the "File not found" error caused by the script being in a different directory than the step's default working directory.
---
