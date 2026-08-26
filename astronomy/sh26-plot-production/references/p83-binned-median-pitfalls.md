# P83 RC sky maps — spec + binned-median pitfalls (2026-08-17)

P83 `rc_sky_systematics`: red-clump l-b sky maps, extinction-law
systematics diagnostic (reference: Schlafly+ 2017 Fig D.1 style).
Module: `src/sh26/plots/p83_rc_sky_systematics.py`.

## Spec

- Sample: RC (P81 selection: teff50 4500–6200, logg50 2–3.5, G≤17.5) →
  50M: 3,484,138 RC; region 0<l<250°, |b|<20° → 1,772,998 in region.
- Bins 0.5°, min 3 stars/px → 39,076 filled pixels.
- 3 stacked panels: log10 count (gray), median teff50 (cividis),
  median met50 (RdYlGn). l axis REVERSED 250→0 (reference layout).
- 50M verified: teff50 4508–6008 K, met50 −1.55…+0.32, non-white 0.40.
- `ctx.save(..., extra={...})` keyword is `extra`, NOT `extras`.

## Binned-median pitfalls (both real, both caught by isolated test)

**Rule: any binned-stat helper is validated in ISOLATION against
`np.median` on a synthetic sample (50 random bins, tol 1e-9) BEFORE a
50M run.** The per-pixel Python loop (`np.median` per bin) also
OOM-killed a Dask worker on 50M — the loop is the memory killer, not
the data.

1. **`np.argpartition` returns INDICES, not values.**
   `med[kk] = part[-1]` after `part = np.argpartition(seg, kth)[:kth+1]`
   stored a segment index — medians came back as 0.5–1805 "K" inside a
   4500–6200 K selection. Correct: `seg[np.argpartition(seg, kth)[kth]]`
   (odd n); even n: `a = np.argpartition(seg, kth+1)[:kth+2]; a.sort();
   0.5*(seg[a[0]]+seg[a[1]])`.
2. **Orientation:** with `key = ib*n_l + il`, arrays reshape to
   `(n_b, n_l)` (rows = b), NOT `(n_l, n_b)`; and a REVERSED l extent
   (x runs l_hi→l_lo) requires `np.fliplr` on EVERY panel array (counts
   AND both median maps) or the map is mirrored.

Verified working helper: `p83_rc_sky_systematics.py::_bin_median`
(stable-sort by key once, per-bin partial sort only on bins ≥ min_n).
