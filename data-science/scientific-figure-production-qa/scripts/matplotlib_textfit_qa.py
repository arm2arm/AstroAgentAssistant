#!/usr/bin/env python3
"""Deterministic matplotlib text-fit QA.

Fails if any text element in a figure exceeds the smallest containing patch
(box) or the figure canvas. This is a hard, repeatable substitute / complement
to visual QA — use it whenever the vision endpoint is unavailable or to guard
a build/verify step. It caught real clipping (9 overflows) in a session where
the vision tool kept timing out, so it should be treated as a first-class gate,
not a fallback.

Usage:
    python3 matplotlib_textfit_qa.py <module.py> <builder1> [builder2 ...]

Each <builder> must be a zero-arg function in <module.py> that returns a
matplotlib Figure. The module is imported by path, so keep its top-level
import side-effects light (set Agg; build figures only inside the builders,
never at import time).

Exit 0 = all text fits, 1 = overflow(s) found, 2 = usage/import error.

Example (module figures/make_figs.py with def boundary():, def ladder():):
    python3 matplotlib_textfit_qa.py figures/make_figs.py boundary ladder
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

TOL_PX = 2.0  # rounding tolerance for the box/canvas comparison


def load_module(path: str):
    p = Path(path).resolve()
    spec = importlib.util.spec_from_file_location(p.stem, p)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot import {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[p.stem] = mod
    spec.loader.exec_module(mod)
    return mod


def qa(name: str, fig) -> list[str]:
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib.patches import FancyBboxPatch, Rectangle

    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    problems: list[str] = []
    fw, fh = fig.get_size_inches() * fig.dpi
    for ax in fig.axes:
        for t in ax.texts:
            if not t.get_text().strip():
                continue
            ext = t.get_window_extent(renderer=rend)
            cx, cy = (ext.x0 + ext.x1) / 2, (ext.y0 + ext.y1) / 2
            best, best_area = None, None
            for patch in ax.patches:
                if not isinstance(patch, (FancyBboxPatch, Rectangle)):
                    continue
                try:
                    bb = patch.get_window_extent(renderer=rend)
                except Exception:
                    continue
                if bb.contains(cx, cy):
                    a = bb.width * bb.height
                    if best_area is None or a < best_area:
                        best, best_area = bb, a
            if best is not None and (
                ext.x0 < best.x0 - TOL_PX or ext.x1 > best.x1 + TOL_PX
                or ext.y0 < best.y0 - TOL_PX or ext.y1 > best.y1 + TOL_PX
            ):
                problems.append(
                    f"{name}: text {t.get_text()!r} overflows box by "
                    f"L{max(0.0, best.x0 - ext.x0):.1f} "
                    f"R{max(0.0, ext.x1 - best.x1):.1f} "
                    f"B{max(0.0, best.y0 - ext.y0):.1f} "
                    f"T{max(0.0, ext.y1 - best.y1):.1f}px"
                )
            if ext.x0 < -TOL_PX or ext.x1 > fw + TOL_PX or ext.y0 < -TOL_PX or ext.y1 > fh + TOL_PX:
                problems.append(f"{name}: text {t.get_text()!r} outside canvas")
    import matplotlib.pyplot as plt
    plt.close(fig)
    return problems


def main() -> int:
    if len(sys.argv) < 3 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return 2
    mod_path = sys.argv[1]
    builders = sys.argv[2:]
    try:
        mod = load_module(mod_path)
    except Exception as e:  # noqa: BLE001
        print(f"import error: {e}")
        return 2
    all_problems: list[str] = []
    for name in builders:
        fn = getattr(mod, name, None)
        if fn is None:
            print(f"error: {mod_path} has no attribute {name!r}")
            return 2
        all_problems += qa(name, fn())
    if all_problems:
        print("figure text-fit QA FAILED:")
        for p in all_problems:
            print("  -", p)
        return 1
    print(f"figure text-fit QA passed ({len(builders)} figures)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
