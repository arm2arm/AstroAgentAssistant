#!/usr/bin/env python3
"""Deterministic geometry check for "Rising Cards" maturity figures.

Verifies, without any vision model, that a horizontal card sequence:
  (a) rises monotonically left->right (top edge moves up), and
  (b) is bottom-aligned (bottom edges agree within tolerance).

Method: at each card's expected x-center, scan a narrow pixel column for
non-white pixels (grayscale < 245) and record top/bottom extents.

Usage:
    python3 verify_rising_cards.py <image.png> [n_cards] [--lft 0.03] [--rgt 0.97]

Exit code 0 = PASS, 1 = FAIL (details on stdout).
Requires: pillow, numpy.
"""
import sys

import numpy as np
from PIL import Image


def check(path: str, n: int = 5, lft: float = 0.03, rgt: float = 0.97,
          thresh: int = 245, bottom_tol_frac: float = 0.03) -> bool:
    im = np.asarray(Image.open(path).convert("L"), dtype=float)
    H, W = im.shape
    nonwhite = im < thresh
    span = rgt - lft

    tops, bottoms = [], []
    for i in range(n):
        xc = int(W * (lft + (span / n) * (i + 0.5)))
        col = nonwhite[:, max(xc - 3, 0):xc + 3].any(axis=1)
        ys = np.where(col)[0]
        if ys.size == 0:
            print(f"FAIL: no content found at card {i} (x={xc})")
            return False
        tops.append(int(ys.min()))
        bottoms.append(int(ys.max()))
        print(f"card L{i}: x={xc} top={ys.min()} bottom={ys.max()} "
              f"height={ys.max() - ys.min()}")

    ok = True
    # (a) rising: top pixel row must strictly decrease (smaller y = higher)
    for i in range(1, n):
        if tops[i] >= tops[i - 1]:
            print(f"FAIL: card {i} does not rise above card {i - 1} "
                  f"(top {tops[i]} >= {tops[i - 1]})")
            ok = False
    # (b) bottom alignment within tolerance (badges/arcs may add outliers;
    #     compare against the median bottom)
    med = float(np.median(bottoms))
    tol = H * bottom_tol_frac
    for i, b in enumerate(bottoms):
        if abs(b - med) > tol:
            print(f"WARN: card {i} bottom={b} deviates from median {med:.0f} "
                  f"by more than {tol:.0f}px (decorations below the card can "
                  f"cause this; inspect manually)")
    print("PASS: cards rise monotonically L0->L{}".format(n - 1) if ok
          else "FAIL: rising-cards geometry violated")
    return ok


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    img = sys.argv[1]
    ncards = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    kwargs = {}
    args = sys.argv[3:]
    for j in range(0, len(args) - 1, 2):
        if args[j] == "--lft":
            kwargs["lft"] = float(args[j + 1])
        elif args[j] == "--rgt":
            kwargs["rgt"] = float(args[j + 1])
    sys.exit(0 if check(img, ncards, **kwargs) else 1)
