# Corrected DRP maturity model + Conzept integration notes

Session context: generated a 16-slide presentation from a DRP-Hub paper PDF plus Conzept context. The user explicitly said the paper/previous slides' L0–L4 ideas were "a little bit off" and asked to fix the relationships and deepen the concepts.

## Corrected L0–L4 semantics

Treat L0–L4 as **cumulative evidence gates**:

1. **L0 — Seed / Bookmark**
   - Purpose: preserve potentially useful material before it disappears.
   - Minimum: URL/bookmark or note, title, short description, optional tags.
   - No repository, workflow, citation, or execution claim.

2. **L1 — Runnable Entry Point**
   - Purpose: make a first run understandable to a beginner/domain peer.
   - Adds: repository or structured material, README, one documented command, sample input/minimal example, representative output/screenshot.
   - Do not require publication-grade metadata or backend-specific workflow execution.

3. **L2 — Citable and Portable Package**
   - Purpose: make reuse legal, attributable, versioned, and technically portable.
   - Adds: LICENSE, CITATION.cff, authorship metadata, stable release tag or pinned commit, dependency/environment/container spec; image digest where possible.
   - Draft `reana.yaml` or CI files may exist, but L2 does **not** claim successful validation.

4. **L3 — Validated Computational Product**
   - Purpose: record evidence that a declared workflow actually ran under a stated scope.
   - Adds: workflow file, successful run identifier or CI run, expected-output checks, logs, provenance binding commit/data/image/run ID, validation scope.
   - L3 is the first level where execution evidence is required.
   - Validation can be a smoke test or scoped test, not necessarily a full scientific/catalogue rebuild, if the scope is explicit.

5. **L4 — FAIR Publication Object**
   - Purpose: make the citable and validated product persistent, discoverable, harvestable, and reviewable.
   - Adds: archived release/DOI, rich metadata, public DRP-Hub landing card, OAI-PMH/harvesting exposure if enabled, human review/publication gate.
   - L4 should publish and preserve the validated L3 state; do not introduce unvalidated workflow claims at L4.

Compact presentation line: **L0 preserves the seed → L1 makes it runnable → L2 makes it reusable/citable → L3 proves the declared run → L4 makes the validated evidence durable and discoverable.**

## Conzept × DRP-Hub framing

Conzept is best framed as a semantic/topic exploration layer, while DRP-Hub is the product-evidence layer.

- Conzept answers: *What concepts, sources, entities, papers, datasets, instruments, and methods are connected to this topic?*
- DRP-Hub answers: *Which connected research products are runnable, citable, validated, and FAIR-ready?*

Useful integration diagram:

```text
Conzept semantic graph
  topic / paper / dataset / method / instrument
        ↓ mapping layer
  entity IDs · keywords/aliases · linked papers/data · candidate DRP cards
        ↓
DRP-Hub cards ranked/filterable by L0–L4 maturity, validation status, reuse actions
```

User-experience example: start from “Gaia DR3”, “stellar distances”, or “XGBoost photometric inference” in Conzept; land on DRP-Hub cards ranked by maturity, validation state, and reuse actions.

## Slide-generation lessons

- Reuse the paper's diagram style for DRP-Hub talks: white background, thin grey boxes, small accent strips, restrained arrows, service-layer diagrams.
- For long scientific titles in PowerPoint/PDF export, use a slightly smaller title font (~22–23 pt) with ~0.8 inch title box height and place subtitle below ~1.05 inch to avoid wrapping collisions.
- Render to PDF and inspect contact sheets; title collisions often appear only after LibreOffice export.
