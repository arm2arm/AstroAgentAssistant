# Conference Paper → Refereed-Journal Paper Upgrade Checklist

Derived from the agentic-astronomy-paper journal upgrade (2026-07-02, commits
`c27da0c` + `f163262`). Use when the user asks to make a manuscript "a true
research paper that could be submitted to a refereed journal".

Core principle (matches this user's standards): **every claim added must be
backed by an artifact in the repo** — an executable script, machine-readable
results file, or verified reference. Prose-only upgrades are not upgrades.
Being explicit about what a pilot does NOT show earns reviewer trust; an
overclaim loses it.

## Work order that worked (7 steps, run as todo list)

1. **Verify references via CrossRef** (before touching prose):
   ```bash
   curl -s "https://api.crossref.org/works/<DOI>" | jq -r \
     '.message | [.DOI, .title[0], (.["container-title"][0] // "?"),
      (.volume // "?"), (.issue // "-"), (.page // "?"),
      (.issued["date-parts"][0][0]|tostring)] | join(" || ")'
   # author list:
   curl -s ".../works/<DOI>" | jq -r \
     '.message.author | map(.family + ", " + (.given // "")) | join(" and ")'
   ```
   Fix bare-URL `@misc` entries into proper `@article`/`@inproceedings` with
   DOI (e.g. Binder2018 → SciPy 2018 proceedings, pp. 113–120,
   10.25080/Majora-4af1f417-011). Also verify locally-installed tool versions
   cited in the text (`reana-client version`, `snakemake --version`).

2. **Formalize the model**: promote informal concepts to numbered
   Definitions (e.g. DRP as 7-tuple; maturity as
   `L(r) = max{k | ∧_{j≤k} ∧_{p∈P_j} p(r)}` — cumulative + decidable by
   construction). Keep definitions short; put predicates in a table.

3. **Ship a reference implementation** under `code/` in the paper repo:
   small, dependency-free, deterministic (e.g. scanner whose exit code = 
   detected level). The paper cites the file; the file must actually run.

4. **Run a real (even small) evaluation**: seeded synthetic testbed
   (`make_testbed.py`), scripted remediation, REAL execution gates (actual
   `snakemake` runs, not mocked). Write machine-readable outcomes to
   `results/*.json`. Timing pitfalls hit in session:
   - initialize per-step timers (`exec_t = 0.0`) before conditionals, or
     total-time accounting double-counts / crashes;
   - the re-scan after remediation belongs INSIDE the timed loop step;
   - verify the execution gate actually ran: query the results JSON
     (`jq '[.repos[].steps[] | select(.target==3) | .exec_ok]'`) — a
     suspiciously fast run means the gate silently failed (here: snakemake
     needed `-s workflows/Snakefile`, default lookup found nothing).

5. **Results figure/table generated ONLY from the results JSON** — never
   hand-typed numbers. One generator script (`figures/make_results_fig.py`).

6. **Rewrite prose around measurable claims**: central-claim paragraph,
   contributions list keyed to sections, related work split (infrastructure
   lineage vs agent systems) with an explicit positioning paragraph,
   limitations section that names what the pilot does not show, Data & Code
   Availability statement, AI-assistance disclosure. The paper should
   practice its own reproducibility policy.

7. **Full rebuild + commit**: clean aux → pdflatex → bibtex → pdflatex ×2;
   check `grep -c '^!' main.log`, undefined citations, overfull count;
   commit with an itemized message.

## webofc-specific pitfalls found in this pass

- **`amsthm` breaks `webofc.cls`**: `! LaTeX Error: Command \openbox already
  defined.` Fix: drop `amsthm`, use plain `\paragraph`-style or manual
  definition formatting for Definitions.
- **Circled numerals across figure + caption**: in matplotlib use Unicode
  ①–⑤ (`\u2460`–`\u2464`) inline in card titles; in the LaTeX caption use
  `\ding{192}`–`\ding{196}` (requires `\usepackage{pifont}`). Verify glyphs
  rendered: `pdffonts main.pdf | grep -i ding` (Dingbats embedded) and
  `pdftotext` shows ➀➁➂ correctly.

## Figure presentation upgrade pattern (linear pipeline → swim lanes)

When a figure shows a process crossing system/ownership boundaries, a flat
left-to-right box chain hides the architecture. Redesign as horizontal swim
lanes (one lane per owning system: repository / execution platform /
registry), with:
- artifact chips (monospace filenames) in the producer lane;
- numbered stage cards inside the executing lane;
- **labelled** lane-crossing arrows (the API calls / handoffs are the story);
- dashed feedback loop if the process is cyclic (e.g. CI re-validation);
- NO baked-in title — journal convention: the caption describes the figure,
  walking the lanes with the matching circled numerals.
Verify with the renderer-bbox collision check (see matplotlib-pitfalls skill,
"Renderer-Based Collision Detection") — it catches text overlaps PIL misses.
