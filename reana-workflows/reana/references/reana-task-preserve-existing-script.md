# REANA operator task mode: preserve existing scripts

## Session learning

During a RAVE DR6 nearest-100-stars REANA smoke test, `reana_operator.py task` was invoked with:

```bash
python reana_operator.py task \
  --project /tmp/rave-nearest100-reana \
  --task "Query RAVE DR6 nearest 100 stars and create a publication-style summary plot" \
  --script analysis.py \
  --output rave_dr6_nearest100_summary.png \
  --run
```

The project already contained a real `analysis.py`. Because `--task` was present and neither `--code` nor `--command` was supplied, the helper generated placeholder scaffold code and overwrote the existing script (when `--force` was also present). The workflow finished successfully but produced only the placeholder output, so declared outputs were missing at download time.

## Durable rule

Task-front-door helpers must distinguish between:

1. **existing implementation**: preserve `--script` and only generate/update `reana.yaml`, environment report, `.reanaignore`, etc.;
2. **missing implementation**: write a safe placeholder scaffold and do not submit until real code is added, unless the user explicitly supplied `--code` or `--command`.

## Implementation pattern

```python
project = Path(ns.project).resolve()
script = ns.script or "analysis.py"
script_path = project / script

if ns.task and not ns.code and not ns.command and not script_path.exists():
    code = make_placeholder(ns.task)
else:
    code = ns.code  # None means preserve existing script in scaffold layer
```

Then the lower-level scaffold command should only write script content when `code` is not `None`, or create a default script only when the script path does not exist.

## Verification checklist

- Create a temporary project with a real `analysis.py`.
- Run `reana_operator.py task --project <tmp> --task ... --script analysis.py --output output.txt --force`.
- Assert `analysis.py` still contains the original implementation.
- Validate generated `reana.yaml`.
- For live runs, inspect logs for the expected implementation output before trusting workflow status.

## Related pitfall

A workflow status of `finished` only means the submitted command exited successfully. If the wrong script was submitted, `finished` can still be misleading. Always verify declared outputs were downloaded and non-empty.
