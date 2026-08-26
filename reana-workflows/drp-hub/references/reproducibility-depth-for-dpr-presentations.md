# Reproducibility depth for DRP-Hub presentations

Use when preparing DRP/DRP-Hub talks, papers, or educational material that explains what “reproducible” should mean in practice.

## Core distinction

DRP maturity (L0–L4) and reproduction depth are separate axes:

- **Maturity** asks whether the product has the expected metadata, packaging, evidence, provenance, and publication state.
- **Depth** asks how much of the scientific result is rerun.

A DRP can be L3-validated for a narrow smoke-test scope or for a deeper end-to-end workflow. The card must state which one.

## Practical depth ladder

| Depth | Meaning | Typical evidence |
|---|---|---|
| D0 Inspect | Reader can inspect paper/card/metadata/files. | Links, metadata, README, file inventory. |
| D1 Plot replay | Reader can regenerate at least key published/tutorial plots. | Command/notebook, public table/subset, expected figure files. |
| D2 Workflow replay | Declared workflow runs on sample or public data. | Workflow manifest, pinned environment, input IDs, outputs. |
| D3 Validation replay | Run is validated with checks and provenance. | Logs, checksums/comparisons, container digest, run ID, provenance record. |
| D4 Full production | Large-scale/raw/full survey or detector processing is rerun. | Production-scale workflow records, compute/storage provenance, review. |

## Minimum reader promise

For a paper that publishes data and code, the reasonable baseline expectation is:

> A reader should be able to regenerate at least the key plots/figures supporting the paper, using the published code and released data or a documented subset.

This is stronger than “the repository exists” and weaker than “rebuild the full production result from raw observations/events.”

## Examples

### LHC-CMS open data tutorials

Good first depth: tutorial/histogram replay.

- Read NanoAOD or tutorial data.
- Apply object selection.
- Produce a known histogram/plot.
- L3 evidence can be a REANA/CI run on the tutorial sample with logs and expected outputs.
- Do **not** imply full CMS detector reconstruction unless that is explicitly in scope.

### Gaia DR3 / SHBoost24-style astronomy

Good first depth: plot replay or one-label smoke validation.

- Use released Gaia DR3-derived data/sample files.
- Run one documented command, e.g. a one-label training/inference path.
- Produce a diagnostic plot or MLflow/local artifact.
- L3 evidence records source commit, data sample, container/environment, output artifact, and run/provenance record.
- Full catalogue rebuilding, e.g. all 217M sources, is a deeper optional claim, not the baseline.

## Slide-flow recommendation

For fluent DRP-Hub decks:

1. Motivation: paper + code + data still do not tell the reader what can be rerun.
2. DRP concept: package workflow, code, environment, data references, metadata, validation, outputs.
3. L0–L4 maturity: cumulative evidence gates.
4. Reproduction depth: D0–D4 ladder and the “plot replay first” principle.
5. Architecture/services: DRP-Hub, REANA, PUNCH-AAI, Compute4PUNCH, Storage4PUNCH.
6. Semantic discovery/integration: Conzept points to topics; DRP-Hub exposes maturity/actions.
7. Governance: assistant support is useful, but evidence/provenance/human review approve maturity changes.

## Pitfall to avoid

Do not say a product is “not reproducible” merely because full raw-data reprocessing is too expensive. Instead say: “validated for plot replay / smoke workflow / full production,” and record what is excluded.
