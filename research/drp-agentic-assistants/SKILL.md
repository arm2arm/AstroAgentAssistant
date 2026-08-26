---
name: drp-agentic-assistants
description: Integrate agentic assistants into DRP / reproducibility papers, slides, and architecture with grounded, non-hype framing; especially Hermes + DRP-Hub + REANA style workflows.
---

# DRP Agentic Assistants

## When to use
Use this skill when the user wants to:
- add or revise paper/slides/notes about agentic assistants in a reproducibility ecosystem
- explain how assistants fit into DRP-Hub, REANA, FAIR metadata, CI, and workflow publication
- choose a concrete framework (for example Hermes Agent) and justify why it fits DRP-style workflows
- describe per-user isolated assistants that guide researchers from partially reproducible projects toward publication-grade DRPs

## Core framing
The robust framing is:
- assistants are **maturity accelerators**, not autonomous scientific authorities
- assistants should produce **explicit artifacts**, not opaque conversational output
- assistants do **not** replace:
  - human scientific judgment
  - executable validation / CI
  - provenance capture and version control
  - FAIR metadata or registry publication

Anchor the argument around the L0→L4 maturity path:
- L0/L1: identify missing README, workflow description, example outputs, usage notes
- L2: generate citation/license/environment assets
- L3: strengthen validation, CI, provenance summaries, test artifacts
- L4: improve FAIR metadata, archival readiness, registry packaging, discovery-facing fields

## Recommended architecture language
When the user wants a concrete DRP-Hub integration model, prefer this structure:
1. **One user, one isolated assistant profile**
   - separate memory, tools, sessions, optional skills, and credentials
   - avoid cross-project leakage and enforce data privacy boundaries
2. **Assistant outputs are patchable artifacts**
   - `reana.yaml` (utilizing a default 32GB memory layout and referencing official templates from PUNCH GitLab `https://gitlab-p4n.aip.de/punch_public/reana/environments`)
   - Snakemake boilerplate
   - container recipes (Apptainer/Singularity, Docker)
   - `README.md`
   - `LICENSE`
   - `CITATION.cff`
   - FAIR metadata drafts
   - CI templates
   - validation/provenance summaries
3. **Assistant activity should be auditable**
   - version-controlled patches and human-in-the-loop review
   - workflow-native outputs
   - provenance-bearing summaries/logs
4. **DRP-Hub becomes a guided reproducibility surface**
   - not only a registry of finished objects
   - also an entry point for improving incomplete projects toward higher maturity (L0 -> L4 transition)
5. **Accelerating L0 -> L4 Transition via Automated Sandbox Debugging Loops**
   - **L0 (Minimal)** -> **L1 (Documented)**: Assistant identifies missing documentation and automatically scaffolds a robust `README.md` and basic pipeline configs.
   - **L1 (Documented)** -> **L2 (Citable)**: Assistant generates structural metadata assets like `CITATION.cff`, container manifests, and license files.
   - **L2 (Citable)** -> **L3 (Validated)**: Assistant implements a "compile-sandbox" loop on the execution engine (REANA). It deploys the workflow, parses output/error logs, automatically generates git patches to fix code/environment bugs (such as syntax errors, missing packages, or path mismatches), and redeploys iteratively until execution is fully validated and reproducible.
   - **L3 (Validated)** -> **L4 (FAIR Product)**: Assistant compiles provenance-bearing summaries, registers DOI metadata, and publishes to the DRP-Hub.

## If the chosen framework is Hermes Agent
Ground claims in official Hermes docs / README, not in generic agent discourse.

Safe, grounded points from project docs:
- Hermes is an **open-source autonomous AI agent framework** developed by **Nous Research**.
- Hermes is described as **self-improving** via reusable skills / learning loop.
- Hermes supports **persistent memory / cross-session recall**.
- Hermes uses tools and can operate through multiple interfaces/platforms.
- Hermes supports **profiles / isolation**, which maps well to per-user assistant deployment.

Do **not** oversell. State assumptions explicitly:
- Hermes is a suitable substrate for researcher guidance **if** outputs remain explicit, reviewable, and tied to reproducibility infrastructure.
- The framework helps close packaging/documentation/validation gaps; it does not by itself guarantee scientific correctness.

User preference: concise, practical, audit-first style
- The user (Arman Khalatyan) prefers concise, direct, and practical edits: keep paragraphs short, start with the core idea, and make assumptions explicit.
- When revising papers or patches for this user, prefer audit-first framing: "what artifact was produced", "which skill/version produced it", "where to find CI artifacts / logs".
- Visual style preference: dark background palette (document notes only), but avoid embedding style details into academic text. Keep this as a skill-level note so future sessions keep terse output and audit traces.


A reliable section sequence is:
1. recent scientific-agent literature relevant to DRPs
2. why a concrete framework is needed
3. why Hermes fits DRP requirements
4. how Hermes should integrate with DRPs
5. Hermes as a user-facing assistant inside DRP-Hub
6. recommendations for provenance, CI coupling, and patchable outputs

Useful table pattern:
- column 1: Hermes capability
- column 2: operational meaning
- column 3: DRP relevance

Good capability rows:
- persistent memory and session recall
- reusable skills / self-improvement loop
- tool-using architecture
- profiles and isolation boundaries
- multi-platform / remote execution

## Recommended slide pattern
For slides, a stable 3-frame sequence works well:
1. **Why choose Hermes for DRP assistance?**
   - open-source, self-improving, persistent memory, isolated profiles
2. **How Hermes should integrate with DRPs**
   - explicit artifacts in, explicit artifacts out; what it should do vs not replace
3. **Hermes inside DRP-Hub can improve reproducibility**
   - one user / one assistant, concrete support, reproducibility impact

Keep slides practical and non-hype:
- emphasize outputs and workflow support
- emphasize provenance and reviewability
- connect benefits directly to L0→L4 progression

## Bibliography / citation pattern
When a specific framework is adopted:
- cite the official project repository/docs rather than stale third-party summaries
- replace superseded framework references in the bibliography when the paper direction changes
- keep claims aligned with what the project documentation explicitly says

## Verification steps
After revising paper/slides:
1. rebuild paper with full LaTeX + BibTeX cycle
2. rebuild slides with at least two LaTeX passes
3. check page count and confirm no fatal errors
4. tolerate minor `Underfull \hbox` warnings unless the layout is visibly degraded
5. ensure paper/slides use the same assistant framing and terminology

## Pitfalls
- Do not frame the assistant as replacing REANA, FAIR metadata, CI, or scientific review.
- Do not leave assistant discussion as generic hype disconnected from concrete DRP artifacts.
- Do not mix old framework branding into the bibliography after the user changes direction.
- Do not describe chat convenience as the main value; the main value is artifact production and guided maturation.

## References
- See `references/hermes-drp-framing.md` for grounded wording, capability mapping, and integration points used in a successful paper+slides revision.
