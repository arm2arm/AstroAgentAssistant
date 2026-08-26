Summary of agentic LLM / agent workflows for astronomy

Purpose
- Capture session learnings about agentic large-language-model (LLM) usage in astronomy, cosmology, and galaxy-science workflows.

Contents
1) Session signal
- Recent arXiv papers (examples) are exploring agentic LLM systems for discovery, database querying (text-to-SQL), semantic search over galaxy images, decision-aware follow-up, and model-discovery in cosmology.

2) Key patterns and recommended practices
- Treat LLMs as proposal generators, not final arbiters: require downstream numerical/physical verification (unit tests, statistical validation, priors).
- Use retrieval-augmented generation (RAG) with pinned, versioned knowledge sources for provenance.
- Wrap any LLM→SQL or LLM→code output with schema checks, static analysis, and a dry-run safety layer before execution.
- For VLM-generated captions or semantic search: validate with measured features (e.g., concentration, Sersic fits) for scientific decisions.
- For agentic pipelines that write and execute code: require explicit test harnesses, deterministic seeds, and reproducibility metadata (env, packages, commit SHAs).
- For judge/evaluator LLMs: use a Judge Datasheet (psychometric protocol) to measure "dark current", bias, and calibration; prefer calibration against human annotations on a held-out set.
- In time-domain follow-up and scheduling: treat the system as a sequential decision problem (POMDP-like); cost models must be explicit and validated.

3) Minimal reproducibility checklist (apply to agentic LLM papers)
- public data / sample data subset URL
- code repository + instructions to run the agent (entrypoint + minimal config)
- exact model checkpoints (or API provider + prompt templates) and RAG indices with versions
- deterministic seeds, container/requirements, and an example end-to-end run with outputs
- unit tests / numeric checks that verify physical consistency

4) Pitfalls (session-specific)
- Hallucinated SQL or code causing accidental data exposure or destructive commands — enforce read-only and sandbox dry-run.
- Over-reliance on LLM scoring without psychometric calibration (judge dark current).
- VLM captions lacking fine-grained physical labels: rely on measured feature cross-checks.
- Agentic autonomy without explicit fail-safes: always require a verification gate for publication claims.

5) Quick templates and pointers (where to look next)
- Text-to-SQL: schema-grounding + parse-then-validate pattern.
- Semantic search: VLM captions → embedding index → contrastive retrieval → measurement-based verify step.
- Model discovery: LLM propose → symbolic regression / SR engine → physical-constraint filter → numeric fit & validation.

6) References (session-selected)
- ALeRCE text-to-SQL system (arXiv:2606.18108)
- Semantic search for 100M+ galaxy images (arXiv:2512.11982)
- Beyond AI as Assistants: Toward Autonomous Discovery in Cosmology (arXiv:2605.14791)
- DeepInflation, DarkAgents, VESTA, judge-datasheet, decision-aware LSST paper, and related arXiv entries found in session.

Usage
- This file is a concise reference intended for the astronomy-research-umbrella skill. When an agentic-LLM task arises, link this file into the SKILL.md and copy the reproducibility checklist into PR templates or reviewer checklists.
