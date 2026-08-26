DRP runnability: concise recipe

Purpose

Capture the minimal, actionable recipe that converts a published DRP from a static bundle into a runnable research object that can be automatically instantiated by REANA, CI, or a user on demand.

Required artifacts

- reana.yaml or equivalent workflow manifest (Snakemake, CWL, Nextflow)
- pinned container image(s) with digest (sha256:...) or pinned tag recorded in versions.yaml
- small, representative sample dataset (<= few MB) and smoke-test scripts
- CITATION.cff and DataCite metadata for DOI landing page
- provenance.yaml recording git commit, assistant id (if modified by an agent), and CI run ids

CI and verification

- include a CI job that runs the smoke test with the sample dataset and reports pass/fail as a badge
- validate metadata completeness (required DataCite fields, presence of CITATION.cff, README) as a separate CI lint job
- run a lightweight VOTable/ObsCore schema validation step as part of CI for catalogue-producing DRPs

Registry exposure

- include a registry manifest that points to: DOI landing page, REANA job template (or documented example invocation), CI badge URL, and container image digest
- mark the DRP entry as "runnable" in the registry metadata when the CI smoke-test is green and the reana.yaml manifest exists

Provenance rule (required)

Any assistant-generated modification must add an entry to provenance.yaml with: timestamp, assistant id (e.g. HermesAgent:v0.1), a one-line description, and a link to the CI run that validated the change.

Notes

- Keep smoke tests small and deterministic; they are for verification not for full-scale reproduction.
- If using institutional archives to mint DOIs, include the DOI in the registry metadata so users can find the archival snapshot tied to the runnable manifest.