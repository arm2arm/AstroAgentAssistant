# Repo-wide Skill Test Reporting

Use this reference when maintaining a public skills repository and the user asks to test/review every skill, produce a diagram, or create a report artifact.

## Goal

Create a reproducible `tests/` folder that contains both machine-readable and human-readable reports without leaking secrets.

Recommended outputs:

```text
tests/run_skill_tests.py
tests/skill_test_results.json
tests/skill_test_results.csv
tests/support_file_test_results.csv
tests/secret_scan_summary.json
tests/skill_test_result_diagram.png
tests/skill_test_report.md
tests/skill_test_report.pdf
```

## Safe Static Test Scope

For every `SKILL.md`:

- parse YAML frontmatter
- require `name` and `description`
- check description length
- check non-empty body
- check standard sections:
  - `When to Use`
  - `Procedure`
  - `Pitfalls`
  - `Verification`
- detect duplicate skill names
- record quality notes separately from failures:
  - missing author
  - missing license
  - missing canonical-routing note for example skills

For support files:

- Python: parse with `ast.parse` or `python -m py_compile`
- YAML/JSON: parse with safe loaders
- Avoid running arbitrary scripts by default; support scripts may need credentials, network, containers, or destructive side effects.

## Secret-Safe Reporting

Do not include secret values in reports. For secret-like findings, store only:

- file path
- line number
- pattern label
- placeholder-like boolean
- short hash/fingerprint of the matched token

Treat placeholder examples such as `REANA_ACCESS_TOKEN=token`, `<token>`, `${TOKEN}`, `your-api-key`, `xxxx`, and `[REDACTED]` as placeholder-like, but still count them separately.

A report is publishable only when serious secret hits are zero. Placeholder-like hits may remain if clearly examples and no secret value is written.

## Diagram Pattern

Generate a per-category horizontal stacked bar chart:

- green = PASS
- amber = WARN
- red = FAIL

Keep it white-background and publication-readable. Save as:

```text
tests/skill_test_result_diagram.png
```

## PDF Report Pattern

If `reportlab` is not installed, use `matplotlib.backends.backend_pdf.PdfPages` to produce a compact PDF with:

1. title/metadata page
2. diagram page
3. WARN/FAIL detail pages

Save as:

```text
tests/skill_test_report.pdf
```

## Interpretation

- `PASS`: structural checks passed.
- `WARN`: usable skill but missing standardized sections or quality metadata.
- `FAIL`: parse/syntax/duplicate-name failure that should be fixed before publication.

Do not overstate static tests as live functional tests. Say exactly what was tested.

## Commit Practice

Before commit:

1. run the harness
2. assert skill/support failures are zero, unless explicitly documenting known failures
3. assert serious secret hits are zero
4. run the repository's normal audit script if available
5. commit the generated report artifacts under `tests/`
