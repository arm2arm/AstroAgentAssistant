---
name: astro-llm-research
title: Searching and curating astronomy papers about LLMs, agents, and AI-driven analysis
description: Procedures, queries, pitfalls, and reproducible recipes for finding, verifying, and harvesting papers on large language models and agentic/LLM-based data analysis applied to galaxy formation, cosmology, and related astronomical subfields.
authors:
  - Hermes Agent (automated skill update)
tags:
  - astronomy
  - arXiv
  - LLM
  - agents
  - literature-search
---

Purpose

This skill collects best-practice steps, example search queries, verification checks, and reproducible fallback methods for locating and curating literature where large language models (LLMs), retrieval-augmented methods (RAG), or agentic workflows are applied to astronomy — specifically galaxy formation, astrophysics of galaxies, and cosmology.

When to use

- You need the most recent arXiv preprints or published papers about LLMs/agents in astronomy.
- You are assembling a reading list, writing a related methods section, or preparing a literature review.

High-level workflow (robust)

1. Start with targeted arXiv search queries (examples in references/search_queries.md).
2. Prefer astro-ph.GA and astro-ph.CO categories, but include astro-ph.IM, cs.CL, cs.LG when instrumentation/methods or multimodal models are relevant.
3. Use site:arxiv.org operator + quoted phrases for broad web search if arXiv search UI or API is rate-limited.
4. Fetch the abstract page (https://arxiv.org/abs/<id>) and verify categories, submission date, comments, and pdf link (https://arxiv.org/pdf/<id>.pdf).
5. For large lists, automate with web_extract or scripted curl/wget; but always verify each pdf link and capture DOI/Zenodo links in metadata.
6. Save a curated record per paper: arXiv id, title, authors, categories, abstract (first 300 words), pdf URL, abs URL, submission date, comments/DOI, and recommended review note.

Quick verification checklist

- Does abstract/title mention LLM, language model, agent, agentic, RAG, retrieval-augmented, Mephisto, AstroLLaMA, AstroSage, Pathfinder, cosmosage, etc.?
- Is the paper in an astronomy category (astro-ph.GA/CO/IM) or CS category (cs.CL/cs.LG) with astronomy applications?
- Is there a DOI, data/Zenodo link, or code repository (GitHub/HF) to verify artifacts?
- Is the PDF accessible (HTTP 200)? If not, try the abs page or publisher link.

Pitfalls & notes

- web_extract and automated scrapers can hit service limits (credit or rate limits). Have a fallback: manual browser search, saving search result HTML, or using arXiv API/rsync mirror.
- Keywords alone miss domain-specific names (Mephisto, AstroLLaMA, AstroSage, AstroMLab, Pathfinder, TransientVerse, radio-llava, Mephisto). Include proper nouns when refining.
- Many early-stage or education-focused papers discuss LLM use (class experiments, ethical notes). Decide whether to include pedagogy papers.
- When a paper claims an "agentic" pipeline, inspect the methods: does it actually run iterative tool-using agents, or is it a scripted pipeline labelled as an "agent"? Record evidence.

Reproducible example (manual)

1) Search: site:arxiv.org "large language model" astronomy order:-announced_date_first
2) From results, open abs pages and copy pdf links (https://arxiv.org/pdf/XXXX.XXXXX.pdf).
3) Verify with curl -I <pdf_url> or check via browser; save metadata.

References

- references/search_queries.md — concrete queries, regex patterns, and session-specific examples (added alongside this skill).
- references/agentbench-installation.md — AgentBench FC installation pattern, Docker setup, and running benchmarks (discovered July 2026).

Subsections

- arXiv agentic harvesting: see references/arxiv-agentic-session-notes.md for the session-proven arXiv API usage, backoff patterns, and export scripts originally captured in the 'arxiv-agentic-workflow' skill. This subsection consolidates arXiv-specific commands and the small helper scripts used to fetch and verify PDFs.

Maintenance

- Update the references file with newly discovered model names or dataset handles.
- Add templates/scripts for automated harvesting (scripts/harvest_arxiv.py) if harvesting patterns stabilize and pass review.
- Add session-specific notes about agentic "sidekicks" (personal researcher assistants) and best-practice provenance capture when agents materially modify artifacts. See references/agentic-sidekicks.md for a concise recipe and integration notes.

Agentic sidekicks and Hermes integration

Support files added for VO & data‑publishing and session notes: references/vo-data-publishing.md, references/session_notes.md

A new support file 'references/drp_runnability.md' was added. It provides a concise, actionable recipe and CI checklist for converting DRPs into runnable research objects, and includes the provenance rule for assistant-generated modifications.



- Trigger: when harvesting literature or assisting researchers in astronomy, consider agentic sidekicks (per-user assistant agents) as part of the workflow support strategy.
- Short summary: agentic sidekicks are lightweight, per-researcher assistants that help scaffold DRP-style packaging (README, CITATION.cff, reana.yaml, container specs), surface maturity gaps (L0->L4), and produce patchable artifacts rather than ephemeral chat outputs.
- Provenance rule: any assistant-generated or assistant-modified artifact must be recorded in provenance.yaml with timestamp, assistant identifier, and a brief description of the change so the artifact remains auditable.
- Integration hint: pair sidekicks with registries like DRP-Hub and execution platforms like REANA so assistant actions become reviewable workflow artifacts rather than opaque suggestions.
- Collaboration note: research and examples referenced in-session included collaborations such as BMFTR, PhysicsLLM, and PUNCH4NFDI / DFG projects — include these names in session references when relevant.

