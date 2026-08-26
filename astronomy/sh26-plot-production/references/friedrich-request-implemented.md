# Friedrich request — IMPLEMENTED (2026-08-21)

Supersedes `references/ruwe-shoutflag-plan.md` status (that file says
"awaiting go-ahead"). User said GO; all items built + run on full 402M and
delivered. Commits: `6050d97` (flags + P67 fix + P95–P99), `e519909` (RC doc).

## What shipped (measured n_points, full 402M, pyarrow-direct)

- `src/sh26/flags.py`:
  - `sh_outflag(pdf)` — 4-digit Anders+2022 EDR3 flag, NaN-safe; non-converged
    rows → "" (blank). Digits: (1) nummodels ≥30='0'/≥10='1'/<10='2';
    (2) AV95>0='0' else '1'; (3) large-unc all-six-pass='0'; (4) small-unc
    all-six-pass='0'. Computed on float64 copies; NaN inputs → '?' per digit.
  - `ruwe_flag(pdf)` — `ruwe > SF.query_RUWE(SkyCoord(l,b,frame='galactic'),
    crowding=True)`, chunked in 5M-row blocks (peak-mem bounded). NaN where
    ruwe/l/b missing.
- Both registered in `lazy_catalog.DERIVED_DEPS` and computed in `_derive` →
  every plot can filter/pushdown. `SH_OUTFLAG` deps = 16 cols (nummodels,
  AV95, dist16/50/84, AV16/84, teff16/84, logg16/84, met16/84, mass16/50/84);
  `ruweflag` deps = ruwe,l,b.
- **P67 re-cut** to canonical RC (4500<Teff<5000, −0.6<met<0.4, 2.35<logg<2.55)
  → n=**9,346,217** (old cut was 30.9M). P36/P77/P81/P83 still use the OLD RC
  def — intentionally untouched (own methodology); user may ask to align.
- **P95** RC X–Y full sample (Friedrich's exact plot: xlim [−15,5], ylim
  [−10,10], gridsize 150, vmax 300, cmap OrRd): n=9,346,217.
- **P96** RC XYZ (512, extent X[−15,5] Y[−10,10] Z[−6,6]): n=9,346,217.
- **P97** bulge box X–Y (|Z|<3,|Y|<3.5,|X|<5, 512): n=**26,130,225**.
- **P98** Mollweide ruweflag fraction (nbins 512, min_n 50, Reds):
  n=327,477,457.
- **P99** SH_OUTFLAG 4 per-digit sky maps + overall per-digit rates in
  suptitle (incl. digit-1 <10 tier): n=327,477,457.

## Pitfalls hit

- **Plot SPEC `columns=[]` fails when make() reads l/b/... that only come in
  via derived deps** — derived deps are READ but NOT kept in the frame. P97/98/
  99 all hit `KeyError: ['l','b']`. Put `l`,`b` (and any raw col make() reads)
  in `columns=` explicitly.
- **String flag digit extraction**: `flags[:, i]` on a 1-D object/string array
  → `IndexError: too many indices`. Build per-position arrays:
  `digits = [np.array([s[i] for s in flags], dtype=object) for i in range(4)]`.
- **gaiaunlimited** first call downloads 133 MB `dict_SL_ruwe.pkl` (cached in
  `~/.gaiaunlimited`) — on BOTH host and <compute-node> sh25 env. P98/P99 need it
  installed locally for the 200k smoke test.
- P99 suptitle carries the overall digit rates; keep the 4-panel manual
  `fig.add_axes` layout (not subplots) so each Mollweide keeps its own
  colorbar.

## Still BLOCKED

- **Kinematics (vphi, vz, Lz, axisymmetric potential; Queiroz+2023 /
  Nepal+2025 code)**: PM join is in (0 nulls verified) so data is ready, but
  the SH21 repo (`gitlab.aip.de:<user>/SH21`) is NOT cloneable from the
  agent host (permission denied). Needs user: repo access or the code file.
