# Friedrich email work — SH_OUTFLAG, RUWE binary flag, bulge box, RC fix (2026-08-21)

Collaborator (Friedrich) request for the new DR3 StarHorse flagging. Status:
**plan presented, awaiting user go-ahead.** Verified facts below were measured
on <compute-node> against `sh26_final_joined_v190826` (do not re-probe).

## Verified facts (measured, not assumed)

- Catalog has **l, b — NO ra/dec** (132 schema cols). Everything needed is
  present: `ruwe`, `nummodels`, `dist16/50/84/95`, `AV16/84/95`, `teff16/84`,
  `logg16/84`, `met16/84`, `mass16/50/84`, PM cols, `MISSING`, `SHBOOST`.
- **gaiaunlimited** (pip-installed in sh25 env): `BinarySystemsSelectionFunction`
  from `gaiaunlimited.selectionfunctions import binaries`. `query_RUWE(coord,
  crowding=True)` accepts **galactic-frame SkyCoord directly**
  (`SkyCoord(l*u.deg, b*u.deg, frame="galactic")`) — no ra/dec conversion.
  Downloads a 133 MB `dict_SL_ruwe.pkl` on first use (cached in
  `~/.gaiaunlimited`). Timing: **0.4 s per 1M rows** → ~2 min for full 327M.
  Local thresholds ≈ 1.15–1.36 (median 1.23) vs the classic global 1.4 —
  coordinate dependence is real.
- ruwe stats (1.06M sample): median 1.015, min 0.46, max 87.8, 0 nulls;
  `ruwe>1.4`: 6.4%, `ruwe>2.0`: 3.4%.

## Required definitions (verbatim from Friedrich — do not paraphrase)

- `fSH_OUTFLAG` = Anders+2022 EDR3 flags, 4 digits: (1) nummodels ≥30='0' /
  ≥10='1' / else '2'; (2) AV95>0='0' else '1'; (3) large-unc: ALL six
  half-width tests pass = '0' else '1' (dist, AV, teff<1000, logg<1, met<1,
  mass<1 rel); (4) small-unc: ALL six lower-bound tests pass = '0' else '1'
  (dist>0.001 rel, AV>0.01, teff>20, logg>0.01, met>0.01, mass>0.01 rel).
- `ruweflag = df.ruwe > SF.query_RUWE(coord, crowding=True)` — per-source
  coordinate-dependent threshold (Castro-Ginard+2024 App A). Separate bool
  column preferred (Friedrich: "separate column or additional digit"; separate
  keeps digits 1:1 with EDR3).
- **Canonical RC definition (replaces our P67 cut)**: `4500<teff50<5000 &
  -0.6<met50<0.4 & 2.35<logg50<2.55`. Our P67 (4500<6200, 2<logg<3.5, no met)
  must be re-cut and re-run.
- **Bulge box** (Queiroz+2021 Fig 1, extended right): |ZGal|<3, |YGal|<3.5,
  |XGal|<5 kpc.

## Planned implementation (approved shape, not yet built)

1. One prep pass adds `SH_OUTFLAG` (str) + `ruweflag` (bool) as **derived
   columns in `lazy_catalog._derive`** so every plot can filter/pushdown on
   them. ~5 min total. NaN-safe: non-converged rows get blank digit (assumed —
   Anders+2022 flagged converged only; confirm intent).
2. Plots (full 402M, pyarrow-direct, 512-class grids): P95 RC X–Y full sample
   (Friedrich's exact cut, xlim [−15,5], ylim [−10,10]); P96 RC XYZ; P97 bulge
   box X–Y; P98 ruweflag Mollweide (fraction/flagged count per cell, nbins 512);
   P99 SH_OUTFLAG digit-by-digit rates.
3. P67 re-cut to canonical RC, re-run (expect ~15–20M vs 30.9M old).
4. **Kinematics (vphi, vz, Lz, axisymmetric potential; Queiroz+2023/Nepal+2025
   code) BLOCKED**: PM join is in (0 nulls verified) so data is ready, but the
   SH21 repo (gitlab.aip.de:<user>/SH21) is not cloneable from the agent
   host (permission denied). Needs user: repo access or the file.

## Open assumptions presented to user (defaults chosen)

1. SH_OUTFLAG on non-converged rows: blank digit.
2. ruweflag: separate bool column (not 5th digit).
3. P67 definition replaced outright (one canonical RC cut).
