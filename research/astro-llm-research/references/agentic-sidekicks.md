Agentic sidekicks: concise integration recipe

Context
- Agentic sidekicks are per-user assistants (Hermes-style profiles) that help researchers (especially astronomers) bridge the gap from ad-hoc code to publication-grade Digital Research Products (DRPs).

Goals
- Produce patchable artifacts (README, CITATION.cff, .fair-metadata/, reana.yaml, Dockerfile) rather than ephemeral chat outputs.
- Detect and recommend incremental maturity transitions (L0->L1->L2->L3->L4).
- Capture assistant provenance in .fair-metadata/provenance.yaml with entries: {timestamp, assistant_id, file_changed, summary}.

Minimal integration steps
1. Provision a per-user Hermes profile with restricted skills relevant to the domain (astronomy: catalog access, Snakemake templates, REANA manifests).
2. Provide a small set of templates under templates/ for common DRP artifacts (README template, CITATION.cff, basic reana.yaml, Dockerfile minimal). These templates should live in a project-specific skill or the DRP packaging skill.
3. When the assistant proposes a change, require it to write the artifact file under a temporary branch and add an entry to .fair-metadata/provenance.yaml with assistant metadata.
4. CI gate: any assistant-driven commit that modifies metadata, container specs, or workflow manifests must pass automated CI checks before being merged into a release branch. CI should validate schema and run a minimal workflow test.
5. Registry hook: when a DRP is ready for registration, the assistant produces a registry-ready manifest (DRP-Hub metadata) and packages the release for upload.

Provenance example entry (YAML)
- timestamp: 2026-06-02T12:34:56Z
  assistant_id: hermes:arm2arm:profile-default
  file_changed: .fair-metadata/metadata.yaml
  summary: "Assistant filled title, authors, and added PUNCH4NFDI tags from project template."

Pitfalls
- Do not treat assistant suggestions as final: require human review, CI validation, and a recorded provenance entry before merging.
- Avoid storing long conversation transcripts inside FAIR metadata — keep provenance records concise and link to session IDs instead.

References
- DRP-Hub registry patterns
- REANA reana.yaml manifest conventions
- L0-L4 maturity model (internal DRP skill)
