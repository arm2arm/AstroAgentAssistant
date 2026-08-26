Rehomed from skill `reana-cmd-plot-workflow-external-script`.

Summary:
- Explains using an external Python script referenced via `inputs.files` to avoid inline YAML script parsing errors when running large S3 Parquet plots.
- Template: include `plot_cmd.py` under inputs, set environment image, and run `python3 plot_cmd.py --force-refresh`.
- Notes: use Dockerized reana-client for execution; verify S3 endpoint and storage_options for anonymous access.

Original archived at ~/.hermes/skills/.archive/reana-cmd-plot-workflow-external-script (full SKILL.md).