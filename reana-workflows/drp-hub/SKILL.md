---
name: drp-hub
description: Digital Research Product Hub — federated infrastructure for reproducible science in particle physics & astrophysics. PUNCH4NFDI consortium project.
---

# DRP Hub — Digital Research Product for Reproducible Science

## Identity
**DRP** = Digital Research Product for Reproducible Science.
A federated infrastructure platform enabling FAIR (Findable, Accessible, Interoperable, Repeatable) research products.
Provided by the **PUNCH4NFDI consortium**, operated by **Leibniz Institute for Astrophysics Potsdam (AIP)**.
- **URL:** https://drphub-p4n.aip.de
- **Consortium:** https://www.punch4nfdi.de/

## What is a DRP?
A **Digital Research Product** is a fully reproducible, containerized research workflow (often powered by **REANA**) that packages:
- Data processing/analysis code
- Computational environment (Docker containers)
- Input/output data references
- Step-by-step instructions
- Results (plots, tables, publications)

Researchers can **run, reproduce, extend, and share** complete analyses — not just share notebooks or scripts.

## Key Features
1. **Federated hub** — browse and discover digital research products across institutions and domains
2. **REANA-aware workflow layer** — DRP entries can be connected to executable workflow environments rather than treated as static metadata only
3. **Domain focus** — particle physics, astrophysics, cosmology, nuclear physics, and hadron physics
4. **Learning tracks and exemplars** — e.g., open-data tutorial products that double as training material
5. **Community features** — sign in to create, bookmark, share, and manage DRPs
6. **Registry/discovery features** — maturity indicators, metadata exposure, and OAI-PMH discovery endpoints
7. **FAIR principles** — products are framed as Findable, Accessible, Interoperable, Reusable/Repeatable research objects

## DRP Maturity Model (L0-L4)
Use the DRP maturity model whenever the user asks for "levels", "maturity", or a slide/paper explanation of what makes a workflow a real Digital Research Product.

The live DRP-Hub documentation defines the ladder as an **auto-computed card maturity signal**: the card gets the highest level for which all required fields are satisfied. `maturityOverride` can pin or cap the computed level.

For paper/presentation explanations, sharpen this into **cumulative evidence gates** — each level includes the obligations of previous levels, and later levels add specific evidence rather than vague quality labels:

- **L0 — Seed / Bookmark**
  - Minimum: URL/bookmark or note, title, short description, optional tags.
  - Live-card fields: at least `title`, `description`.
  - Interpretation: discoverable seed; **no repository, workflow, citation, or execution claim is required**.
  - Purpose: preserve potentially useful research products before they disappear.
- **L1 — Runnable Entry Point**
  - Adds repository or structured material, README, one documented command, sample input or minimal example, and representative output/screenshot.
  - Live-card fields: `gitUrl` and `entryCommand`, or a detected `reana.yaml`; `gitBranch` recommended.
  - Interpretation: a beginner or domain peer can understand the product and run one path.
  - Avoid overloading L1 with publication-grade metadata or backend-specific workflow validation.
- **L2 — Citable and Portable Package**
  - Adds `LICENSE`, `CITATION.cff`, authorship metadata, stable release tag/pinned commit, and dependency/environment or container specification including image digest where possible.
  - Live-card fields: `license`, `citationCffUrl`, `releaseTag`; encouraged `envImage`, `authorsOrcid`.
  - Interpretation: citable, legally reusable, and technically portable.
  - Draft `reana.yaml` or CI files may exist here, but **L2 does not claim successful validation**.
- **L3 — Validated Computational Product**
  - Adds a declared validation scope, workflow file (`reana.yaml`, `Snakefile`, `nextflow.config`, etc.), successful run identifier or CI run, expected-output checks, logs, and provenance binding commit/data/image/run ID.
  - Live-card fields: `workflowFile`, `lastRunId`, `validationScope`; optional `provenanceUrl`.
  - Interpretation: execution evidence exists for the stated scope; validation can be a smoke test and does not have to be a full catalogue rebuild if the scope is explicit.
  - **L3 is the first level where execution evidence is required.**
- **L4 — FAIR Publication Object**
  - Adds archival release/DOI, rich community metadata (DataCite/RO-Crate-aligned where useful), public DRP-Hub landing card, OAI-PMH/harvesting exposure when enabled, and human review/publication gate.
  - Live-card fields: `doi`, `archiveUrl`; optional `harvestEndpoint`.
  - Interpretation: the citable and validated L3 state is persistent, discoverable, harvestable, and ready for long-term reuse.
  - **L4 publishes and preserves validated evidence; it should not add unvalidated workflow claims.**

Useful presentation framing: **L0 preserves the seed → L1 makes it runnable → L2 makes it reusable/citable → L3 proves the declared run → L4 makes the validated evidence durable and discoverable.**

### Reproducibility depth is orthogonal to maturity
When explaining DRP-Hub to researchers, explicitly separate **maturity level** from **depth of reproduction**. A product can be L3-validated for a shallow/tutorial scope or a deep/full-production scope; the card must state the scope honestly.

Use this practical depth ladder:
- **D0 Inspect** — paper/card/metadata/files are listed and understandable.
- **D1 Plot replay** — a reader can regenerate published figures or tutorial plots from released tables/subsets.
- **D2 Workflow replay** — the declared workflow runs on sample or public data.
- **D3 Validation replay** — logs, provenance, expected-output checks, image digest, data identifiers, and run ID are recorded.
- **D4 Full production** — large-scale/raw-data reprocessing, only when feasible and scientifically justified.

Key user-facing principle: **if a paper publishes data and code, an ordinary reader should be able to reproduce at least the key plots/figures**. Full raw-data reprocessing should not be the default requirement for L3/L4 because it may require collaboration-scale compute, privileged calibration data, or weeks of runtime. Instead, DRP-Hub should publish the claim, scope, evidence, and exclusions.

Examples:
- **LHC-CMS open data tutorials**: tutorial-depth reproduction is often appropriate — NanoAOD reading, object selection, and a known histogram/plot; not full CMS detector reconstruction.
- **Gaia DR3 / SHBoost24-style astronomy**: a natural first DRP depth is regenerating diagnostic plots or one-label MLflow artifacts on public/sample data; full 217M-source catalogue rebuilding is a deeper optional scope, not the baseline claim.

Detailed notes from the corrected slide/paper workflow are in `references/corrected-maturity-and-conzept-integration.md`. Reproducibility-depth guidance for DRP-Hub presentations is in `references/reproducibility-depth-for-dpr-presentations.md`. For conference/CERN-style narrative framing that connects AI agents, DRP-Hub, REANA, trust, and the “publish the path back to the result” message, see `references/drp-hub-cern-opening-and-deck-narrative.md`.
When explaining how DRP-Hub fits into PUNCH4NFDI, use this layered view:

- **PUNCH-AAI** — identity, authentication, and group-based authorization
- **Compute4PUNCH** — federated execution resources across heterogeneous schedulers/sites
- **Storage4PUNCH** — federated data access and storage layer
- **REANA** — workflow execution, replay, and provenance capture
- **DRP-Hub** — registry/discovery/collaboration layer on top of executable workflows

This ordering is especially useful in slides: infrastructure first, workflow layer second, registry/maturity layer third.

Live-site note: the deployed `drphub-p4n.aip.de` frontend advertises FAIR/reproducible workflows, exposes an OAI-PMH link, and its current JS bundle references registry views, bookmarking, sharing, and active REANA configuration handling. That makes the hub materially richer than a static landing page; see `references/live-site-notes.md`.

## Notable DRPs (examples)
- **Learn with LHC-CMS Open Data** — 3 levels teaching CMS analysis (NanoAOD reading, muon reconstruction, Z boson analysis)
- **ttbar workflow with ATLAS open data** — top quark analysis using HTCondor
- **Cosmology data analysis** — slice rendering from EDSM project
- **REANA Environments** — pre-built Docker images with scientific libraries for REANA workflows

## Related Infrastructure
- **REANA** (Reproducible Workflows) — https://reanahub.io/
- **PUNCH4NFDI** — National Research Data Infrastructure for particle/astro/nuclear physics (~9,000 scientists)
- **NFDI** — German National Research Data Infrastructure

## When to Use
- User mentions "DRP", "Digital Research Product", "reproducible science framework", or "research product hub"
- User needs reproducible research workflows for particle physics/astrophysics
- User wants to share/share a reproducible analysis (containerized + data + code)
- User mentions "PUNCH4NFDI" or research infrastructure
- User needs REANA environments or containerized scientific computing

## Video / Outreach Explainers
When the user asks for a short video, social clip, or visual explainer about DRP-Hub, prefer a key-free OpenMontage/Remotion motion-graphics treatment unless they explicitly request AI-generated footage. Use the concise content beats and QA checklist in `references/openmontage-zero-key-drphub-video.md`; always verify the rendered MP4 with `ffprobe` and sample frames for legibility/cropping before delivery. If OpenMontage/Remotion is unavailable or the fastest reliable path is a local scripted render, use the creative fallback `creative-visuals-umbrella` reference `references/pure-python-docs-screenshot-video.md`: capture live DRP-Hub routes with Chromium, extract docs text from dumped DOM, render annotated screenshot scenes plus clean explanatory slides with PIL, narrate with local/no-key TTS, encode with ffmpeg, and QA sampled frames.

If the user says a click-through/webpage demo is not enough, switch to a docs-driven scenario: scrape docs routes such as `/docs`, `/docs/maturity`, `/docs/reana/workflows`, `/docs/cards/history`, `/docs/activity`, and `/docs/oai-pmh`; write a narrative from the documentation; mix real docs screenshots with simplified explanatory slides; and prioritize legibility over animated overlays. The useful DRP-Hub scenario framing is: **scientific claim → reusable research product → maturity ladder → DRP card anatomy → REANA execution → trust/discovery layer**. Detailed reusable workflow is in `creative-visuals-umbrella` reference `references/openmontage-docs-driven-scenario-video.md`.

## DRP Hub vs REANA Backend (Critical Distinction)
The DRP Hub (`https://reana-p4n.aip.de`) is a **Keycloak-SSO frontend** that wraps the raw REANA backend.

- **REANA worker tokens** (in `~/.reana/config.yaml`) authenticate against the REANA backend API, NOT the DRP Hub.
- The DRP Hub uses **Keycloak SSO** via `https://aipoidc.aip.de/realms/punchaai`.
- The `reana-client` CLI talks to the REANA backend directly — do not point it at the DRP Hub URL.
- To check workflow status on the DRP Hub, either:
  1. Use the **web UI** (https://reana-p4n.aip.de) with Keycloak login, or
  2. Authenticate via **Keycloak OAuth2 flow** to obtain a DRP Hub API token, or
  3. Point `reana-client` at the **underlying REANA backend** (not the DRP Hub frontend).

## API Discovery & Debugging
When the DRP Hub web UI loads but API calls fail:
1. The DRP Hub serves a SPA — API paths are discoverable from the JS bundle:
   ```bash
   curl -s https://reana-p4n.aip.de/static/js/main.fbfee2f8.js | grep -oP '"(/api/[^"]*)"' | sort -u
   ```
2. Use the `scripts/discover_api.py` helper to extract and test endpoints.
3. Remember: `/api/status` returns 401 without auth, `/api/config` is public.
4. Auth tokens in `~/.reana/config.yaml` are REANA worker tokens — they do NOT work against the DRP Hub API.

## Related Scripts
- `scripts/discover_api.py` — Auto-discovers and tests DRP Hub API endpoints

## Session Notes / References
- `references/live-site-notes.md` — grounded notes from the live `drphub-p4n.aip.de` deployment: homepage metadata, OAI-PMH exposure, and frontend signals for registry/bookmark/share/REANA-aware behaviour
- `references/openmontage-zero-key-drphub-video.md` — compact OpenMontage/Remotion pattern for producing a no-API-key DRP-Hub explainer video with local Piper narration and visual QA checks

## Quick Reference
```
What is DRP? → Digital Research Product for Reproducible Science
Where? → https://drphub-p4n.aip.de
Who runs it? → PUNCH4NFDI consortium, operated by AIP Potsdam
Powered by? → REANA for reproducibility
Concept? → Containerized, reproducible research workflows
Auth? → Keycloak SSO (https://aipoidc.aip.de/realms/punchaai)
Worker tokens? → Work on REANA backend ONLY, not DRP Hub API
```