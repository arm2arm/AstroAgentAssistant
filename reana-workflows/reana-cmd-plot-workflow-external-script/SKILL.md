---
name: reana-cmd-plot-workflow-external-script
description: |
  Create a REANA workflow that runs a large S3 Parquet data plot using an external Python script.
  The script is stored as a separate file and referenced in the workflow inputs.
  This avoids inline script blocks that cause YAML parsing errors.
---
steps:
  - |
    1. **Prepare the script**: Write the full Python script (e.g., `shboost_plot_cached.py`) to the workflow directory.
    2. **Add the script to inputs** in `reana.yaml`:
       ```yaml
       inputs:
         files:
           - shboost_plot_cached.py
       ```
    3. **Reference the environment** using the organisation‑provided REANA environment (no custom envs):
       ```yaml
       environment:
         repo: https://gitlab-p4n.aip.de/punch_public/reana/environments
         name: py311-astro
       ```
    4. **Define commands** as a list – avoid a single long `bash -c` line:
       ```yaml
       commands:
         - pip install --quiet pandas dask[complete] numpy matplotlib seaborn s3fs
         - python shboost_plot_cached.py --force-refresh
       ```
    5. **Set resources** (default 32 GB RAM as per policy):
       ```yaml
       resources:
         memory: 32gb
         runtime: 02:00:00
       ```
    6. **Specify outputs** (PNG plot and GIF animation):
       ```yaml
       outputs:
         files:
           - shboost_cmd.png
           - shboost_population_animation.gif
       ```
    7. **Run the workflow** with the REANA client Docker image:
       ```bash
       export REANA_SERVER_URL="https://reana-dev.kube.aip.de"
       export REANA_ACCESS_TOKEN="<your-token>"
       sg docker -c "docker run -i --rm \
         -e REANA_SERVER_URL=$REANA_SERVER_URL \
         -e REANA_ACCESS_TOKEN=$REANA_ACCESS_TOKEN \
         -v $(pwd)/<workflow-dir>:/workspace \
         reanahub/reana-client:0.95.0-alpha.3 \
         run -w <workflow-name> -f /workspace/reana.yaml"
       ```

pitfalls:
  - Inline `bash -c "cat <<'PY' ... PY"` blocks break YAML parsing; always use separate script files.
  - Ensure the script is listed under `inputs.files` so REANA stages it.
  - Remember the mandatory 32 GB memory allocation; do not override without explicit policy change.
  - Verify the environment string matches the organization‑provided repo and name.

verification:
  - After `run`, use `reana-client logs -w <workflow>` to confirm the script executed and outputs are produced.
  - Check that `shboost_cmd.png` and `shboost_population_animation.gif` appear in the workflow outputs.
