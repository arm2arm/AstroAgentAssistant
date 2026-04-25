---
name: reana-workflow-with-env
description: Create a REANA workflow respecting the organization’s environment repository and default memory limit.
author: Hermi (sorgenfresser)
---

## Purpose
This skill helps generate a `reana.yaml` file that
* **always** references an environment from `https://gitlab-p4n.aip.de/punch_public/reana/environments` (choose the most appropriate one for the task).
* Sets **memory** to **32 GB** by default.
* Allows the caller to specify the Docker image, command, and any extra resources.

## Steps
1. Choose an environment URL from the organization’s repository.  Example:
   ```yaml
   environment:
     repo: https://gitlab-p4n.aip.de/punch_public/reana/environments
     name: python-3.12-slim            # replace with the best match
   ```
2. Fill in the workflow specification:
   ```yaml
   workflow:
     type: serial
     specification:
       - name: <step_name>
         type: run
         image: <docker_image>
         command: <bash_command>
         compute_backend: generic
         resources:
           memory: 32gb
           runtime: <hh:mm:ss>
         env:
           # optional custom env vars
         outputs:
           - <output_file>
   ```
3. Save the file as `reana.yaml` in the target directory.

## Example usage
```bash
cat > reana.yaml <<'EOF'
$(reana-workflow-with-env \
    step_name=plot \
    docker_image=python:3.12-slim \
    command='pip install --quiet dask[dataframe] s3fs matplotlib seaborn pyarrow && python plot_cmd.py' \
    runtime=02:00:00 \
    output=cmd.png)
EOF
```
The inline call expands to a fully‑compliant `reana.yaml` that meets the organization’s policy.

## Pitfalls & Tips
* **Never** replace the `environment` block with a custom one – the repository is the single source of truth.
* If the required libraries are not present in the chosen environment, add them to the `command` install step (as shown above).
* Verify the environment name exists in the repo before committing; a typo will cause REANA to reject the workflow.
* Adjust `runtime` as needed for larger datasets, but keep memory at 32 GB unless you have explicit permission to change it.
* If REANA warns about missing "inputs", add an empty `inputs: {}` block at the top of the file.
* When specifying step outputs, use the `outputs:
    files:
      - <filename>` syntax (as REANA expects) and also list top‑level outputs if desired.

* **Never** replace the `environment` block with a custom one – the repository is the single source of truth.
* If the required libraries are not present in the chosen environment, add them to the `command` install step (as shown above).
* Verify the environment name exists in the repo before committing; a typo will cause REANA to reject the workflow.
* Adjust `runtime` as needed for larger datasets, but keep memory at 32 GB unless you have explicit permission to change it.
