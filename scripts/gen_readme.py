#!/usr/bin/env python3
"""Regenerate the repository README.md from on-disk SKILL.md frontmatter.

Run after adding, moving, or editing skills so the README inventory never
drifts from the tree:

    python3 scripts/gen_readme.py

What it does:
  * scans every `*/**/SKILL.md` (excluding `outdated-skills/`) and takes each
    skill's `description:` from its YAML frontmatter — the SKILL.md is the
    single source of truth; to change an inventory row, edit the skill,
  * rebuilds the layout table, categories overview, and skills inventory,
  * lists `outdated-skills/` contents in the "Superseded skills" section,
    pointing at the supersession map in `outdated-skills/README.md`.

Directory blurbs are curated in BLURBS below — add an entry when a new
top-level category directory appears (unknown directories fall back to a
generic blurb).

Requires: pyyaml.
"""
import collections
import pathlib
import re

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent

BLURBS = {  # curated per-directory descriptions; keep in sync with new categories
    "agents": "AstroAgent concepts and configuration",
    "astronomy": "AIP-developed survey archives, TAP/ADQL and REST queries, stellar catalogs, and astronomy-specific plots/animations. See [`astronomy/README.md`](astronomy/README.md) for the grouped astronomy routing guide.",
    "creative": "AIP-developed educational animations, Manim, visual explainers, and media workflows",
    "data-science": "AIP-developed scientific visualization and dense-data plotting workflows",
    "devops": "AIP-developed operations, containers, deployment, service exposure, and runtime troubleshooting",
    "infrastructure": "AIP-developed Hermes/OpenWebUI/API-server/MCP infrastructure, workspace backup, and integration workflows",
    "leisure": "AIP-developed nearby places and leisure search workflows",
    "media": "AIP-developed audio/video generation and media post-processing workflows",
    "mlops": "AIP-developed local LLM serving, quantization, and inference workflows (vLLM, Ollama, GGUF)",
    "productivity": "AIP-developed calendars, contacts, image-description, and document workflows",
    "python": "AIP-developed Python data engineering, caching, plotting, symbolic math, and reusable scientific-programming workflows",
    "reana-workflows": "AIP-developed REANA operations, client configuration, templates, execution recipes, monitoring, and workflow best practices",
    "research": "AIP-developed academic research, literature, arXiv access, LaTeX manuscripts, DRP, Bayesian imaging (J-UBIK/NIFTy), and paper improvement workflows",
    "science": "AIP-developed dt4acc digital twin, accelerator-science runbooks, EPICS/Tango, and host smoke tests",
    "software-development": "AIP-developed coding workflows, docs-first development, and application-specific implementation guides",
}
FALLBACK_BLURB = "AIP-developed skills"


def frontmatter(path: pathlib.Path) -> dict:
    text = path.read_text(errors="replace")
    match = re.search(r"^---\s*\n(.*?)\n---", text, re.S)
    if not match:
        return {}
    try:
        return yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return {}


def clip(s: str, n: int = 210) -> str:
    s = " ".join((s or "").split())
    return s if len(s) <= n else s[: n - 3].rstrip() + "..."


def main() -> None:
    skills = collections.defaultdict(list)  # top_dir -> [(rel_dir, description)]
    for sk in sorted(ROOT.glob("*/**/SKILL.md")):
        rel = sk.relative_to(ROOT)
        top = rel.parts[0]
        if top in ("outdated-skills", "scripts"):
            continue
        fm = frontmatter(sk)
        skills[top].append((str(rel.parent) + "/", clip(fm.get("description", ""))))

    outdated = sorted(
        str(p.relative_to(ROOT).parent).removeprefix("outdated-skills/")
        for p in (ROOT / "outdated-skills").glob("**/SKILL.md")
    )

    total = sum(len(v) for v in skills.values())
    cats = sorted(skills)

    out = []
    out.append("# AstroAgent Skills Repository\n")
    out.append(
        "Custom Hermes Agent skills developed by the AIP AstroAgent team. This repository "
        "intentionally keeps only project-specific/AIP-developed skills; stock Hermes skills "
        "and third-party vendor skills are excluded.\n"
    )
    out.append(
        f"Total: **{total}** custom skills across **{len(cats)}** categories, plus "
        f"**{len(outdated)}** superseded skills retained in "
        f"[`outdated-skills/`](outdated-skills/README.md).\n"
    )
    out.append(
        "> The inventory below is generated — run `python3 scripts/gen_readme.py` after "
        "changing skills instead of editing this file by hand.\n"
    )

    out.append("## Repository layout\n")
    out.append("| Directory | Description | Skills |")
    out.append("|---|---|---|")
    for c in cats:
        out.append(f"| `{c}/` | {BLURBS.get(c, FALLBACK_BLURB)} | {len(skills[c])} |")
    out.append(
        "| `outdated-skills/` | Superseded skills kept for provenance — see the "
        "[supersession map](outdated-skills/README.md). Not intended for new use. "
        f"| {len(outdated)} |"
    )
    out.append("")

    out.append("## Categories overview\n")
    for c in cats:
        title = c.replace("-", " ").title()
        blurb = BLURBS.get(c, FALLBACK_BLURB).split(". See ")[0].rstrip(".")
        out.append(f"**{title} ({len(skills[c])})** — {blurb}\n")

    out.append("## Skills inventory\n")
    out.append("| Skill | Description |")
    out.append("|---|---|")
    for c in cats:
        for rel, desc in sorted(skills[c]):
            out.append(f"| `{rel}` | {desc} |")
    out.append("")

    out.append("## Superseded skills (`outdated-skills/`)\n")
    out.append(
        "The 2026-07 skill sync from the production Hermes deployment at AIP "
        "([PR #4](https://github.com/arm2arm/AstroAgentAssistant/pull/4)) replaced these with "
        "curated successors. They are kept (not deleted) for provenance and easy restore; the "
        "per-skill supersession map lives in "
        "[`outdated-skills/README.md`](outdated-skills/README.md).\n"
    )
    for name in outdated:
        out.append(f"- `{name}`")
    out.append("")

    (ROOT / "README.md").write_text("\n".join(out))
    print(
        f"README.md regenerated: {total} skills, {len(cats)} categories, "
        f"{len(outdated)} in outdated-skills/"
    )


if __name__ == "__main__":
    main()
