#!/usr/bin/env python3
"""Deterministic text-clipping QA for matplotlib card/diagram figures.

Usage:  python3 qa_figure_text.py <figures_module.py>
where <figures_module.py> exposes builders as module-level callables:
    BUILDERS = {'figure_name': callable_returning_fig, ...}
(or a flat script whose top-level names end in common builder patterns —
 pass names explicitly:  python3 qa_figure_text.py mod.py name1 name2 ...)

Exit code 0 = all text fits its containing box and the canvas; 1 = any
overflow (printed per-figure). This is EXACT geometry from matplotlib's own
renderer — no pixel heuristics, no vision model.

Discovered 2026-08-23 (drp-paper): caught 9 real label overflows in a
5-card ladder + 7-box workflow diagram that the vision endpoint (timing out)
never saw, and that PIL edge checks would miss (clipping happens *inside*
the figure, at the card border, not the canvas border).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

TOL_PX = 2.0  # rounding tolerance


def qa(name: str, fig) -> list[str]:
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    problems: list[str] = []
    for ax in fig.axes:
        fw, fh = fig.get_size_inches() * fig.dpi
        for t in ax.texts:
            if not t.get_text().strip():
                continue
            ext = t.get_window_extent(renderer=rend)
            # canvas bounds
            if (ext.x0 < -TOL_PX or ext.x1 > fw + TOL_PX
                    or ext.y0 < -TOL_PX or ext.y1 > fh + TOL_PX):
                problems.append(f"{name}: text {t.get_text()!r} outside canvas")
            # smallest containing patch (the card the label belongs to)
            cx, cy = (ext.x0 + ext.x1) / 2, (ext.y0 + ext.y1) / 2
            best, best_area = None, None
            for p in ax.patches:
                if not isinstance(p, (FancyBboxPatch, Rectangle)):
                    continue
                bb = p.get_window_extent(renderer=rend)
                if bb.contains(cx, cy):
                    a = bb.width * bb.height
                    if best_area is None or a < best_area:
                        best, best_area = bb, a
            if best is not None and (
                    ext.x0 < best.x0 - TOL_PX or ext.x1 > best.x1 + TOL_PX
                    or ext.y0 < best.y0 - TOL_PX or ext.y1 > best.y1 + TOL_PX):
                problems.append(
                    f"{name}: text {t.get_text()!r} overflows box by "
                    f"L{max(0.0, best.x0 - ext.x0):.1f} "
                    f"R{max(0.0, ext.x1 - best.x1):.1f} "
                    f"B{max(0.0, best.y0 - ext.y0):.1f} "
                    f"T{max(0.0, ext.y1 - best.y1):.1f}px"
                )
    return problems


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: qa_figure_text.py <figures_module.py> [builder_name ...]")
    path = Path(sys.argv[1])
    spec = importlib.util.spec_from_file_location("figs_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # module-level __main__ guard blocks generation

    wanted = set(sys.argv[2:])
    builders = getattr(mod, "BUILDERS", None)
    if builders is None:
        # flat script: treat all public callables as builders
        builders = {n: getattr(mod, n) for n in dir(mod)
                    if n.isidentifier() and callable(getattr(mod, n))
                    and not n.startswith("_")}
    all_problems: list[str] = []
    checked = 0
    for name, builder in builders.items():
        if wanted and name not in wanted:
            continue
        checked += 1
        all_problems += qa(name, builder())
        plt.close("all")
    if all_problems:
        print("figure text-fit QA FAILED:")
        for p in all_problems:
            print(" -", p)
        raise SystemExit(1)
    if checked == 0:
        raise SystemExit("no builders found in module (expected BUILDERS dict or public callables)")
    print(f"figure text-fit QA passed ({checked} figures)")


if __name__ == "__main__":
    main()
