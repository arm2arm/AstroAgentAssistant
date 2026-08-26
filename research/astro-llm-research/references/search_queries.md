Concrete arXiv search queries and patterns for LLMs/agents in astronomy

Start with these search queries in the arXiv web UI (set "all" and sort by "announced_date_first"):

- "large language model" astronomy
- "large language models" astronomy
- "language model" astro-ph.GA
- "LLM" astro-ph.IM OR astro-ph.GA OR astro-ph.CO
- "agent" "astronomy" "language model"
- "Mephisto" OR "AstroLLaMA" OR "AstroSage" OR "AstroMLab" OR "Pathfinder" OR "cosmosage"
- "retrieval-augmented" astronomy
- "RAG" astro-ph.IM

Fallback google/site queries (when scraping arXiv search page hits limits):

- site:arxiv.org "large language model" astronomy
- site:arxiv.org "Mephisto" OR "AstroLLaMA" OR "AstroSage" OR "Pathfinder" OR "cosmosage"

Regex patterns for identifying arXiv IDs in HTML or text:

- r"arxiv.org/abs/([0-9]{4}\\.[0-9]{4,5}(v\\d+)?)"
- r"arxiv.org/pdf/([0-9]{4}\\.[0-9]{4,5}(v\\d+)?)\\.pdf"

Notes

- Expand model name list as new specialized models are released.
- When using web_extract, batch queries into groups of 3-5 abs URLs to avoid rate limits.
