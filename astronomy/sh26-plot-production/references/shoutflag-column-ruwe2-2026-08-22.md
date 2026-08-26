# SH_OUTFLAG becomes a real catalog column + ruwe2 flag (2026-08-22)

Status: **DONE, committed + pushed** (`b2ef248` SH_OUTFLAG, `70d168a` ruwe2).
Supersedes `ruwe-shoutflag-plan.md` (that doc's "awaiting go-ahead / not yet
built" + "derived column, blank digit on non-converged" shape is stale).

## Current full-catalog final = v220826

`/lustre/<user>/ipython/SH2025/reana/final/combined/sh26_final_joined_v220826/`
— 402,121,784 rows, 3032 parts, **133 cols**. = v190826 (132 cols) + `SH_OUTFLAG`
as the LAST column, `large_string`, 4-char on **ALL rows** (NaN → digit `'1'`,
NOT blank — FA21 `fSH_OUTFLAG` verbatim, see the 4-digit definition in
`ruwe-shoutflag-plan.md`). Built by `scripts/sh26_add_shoutflag.py` (one-part-in /
one-part-out, 48 dask workers on <compute-node>, 2.1 min for the whole catalog). The
numpy→pyarrow string-trap that this build hit is fully documented in
`memory-bounded-parquet-analysis` → `shoutflag_string_build_corruption_2026-08.md`.

Old catalogs still present, untouched: `sh26_final_joined_v190826` (132 cols, no
SH_OUTFLAG), `sh26_final_joined` (129 cols, 4094 parts, no PM). **v220826 is the
default full-catalog dataset for new full-402M work** — update the served-table
`--data` default and any hardcoded path that still points at v190826.

## Reusable loader pattern: promote a derived col to a stored col

`SH_OUTFLAG` was originally a per-frame derived column (`flags.sh_outflag`,
computed in `LazyCatalog._derive`, returned `""` on non-converged rows). It is now
a REAL parquet column. The loader supports BOTH without breaking old datasets:
in `LazyCatalog.get()`, before `_resolve`, promote any name that is requested as
derived but already exists in the schema to a raw pushed-down column and drop it
from the derive list:

```python
schema = self._ensure_schema()
derived, raw_cols = list(spec.derived), list(spec.columns)
if "SH_OUTFLAG" in derived and "SH_OUTFLAG" in schema:
    derived.remove("SH_OUTFLAG"); raw_cols.append("SH_OUTFLAG")
requested = _resolve(raw_cols, derived, self.quality_cuts)
...
pdf = _derive(pdf, derived)   # NOTE: pass the LOCAL `derived`, not spec.derived
```

Pitfall hit: the first version called `_derive(pdf, spec.derived)` and still
derived SH_OUTFLAG (and crashed on the new data, which has no `nummodels` in the
pushed set for the plot). Pass the local `derived` list. On 214,444 converged
test rows the real column and `flags.sh_outflag` were **100% identical**, so P99
output is unchanged either way; P99's `flags != ""` guard still works because the
global `MISSING==False` cut already removed non-converged rows.

## ruwe2 flag (binarity-only, crowding=False)

- `ruwe2` = `ruwe > SF.query_RUWE(l, b, crowding=False)` — the sky-varying
  threshold where excess RUWE is attributed to **binarity only** (floor
  ~1.08–1.27 across the sky), per the gaiaunlimited DR3-unresolved-binaries
  notebook (Castro-Ginard+2024). The existing `ruweflag` uses `crowding=True`
  (floor ~1.15–1.36). `ruwe2` is a **strict superset** of `ruweflag`.
- Impl: `flags.ruwe_flag2()` + `ruwe_threshold(..., crowding=True|False)` kwarg
  (chunked SkyCoord, ~7M rows/s — negligible even at 402M). Registered in
  `DERIVED_DEPS` (`"ruwe2": ["ruwe","l","b"]`) + `_derive`.
- **P100** `mollweide_ruwe2_flag`: Mollweide fraction map mirroring P98. Run
  with `--no-cuts` — the default `ruwe<=1.4` QC cut removes exactly the rows
  this flag is meant to capture.
- Verify superset with `scripts/check_ruwe2.py <dir_with_part.parquet> [n]`
  (asserts 0 `ruweflag`-only rows). Test sample: ruweflag 8.27% → ruwe2 10.80%.
- `ruwe2` is DERIVED (needs per-row SkyCoord lookup), NOT a stored column —
  computed in `_derive` on the fly, like `ruweflag`.

## Figures from test-sample runs are NOT committed

P99 (SH_OUTFLAG digits) and P100 (ruwe2) figure files left untracked: they were
rendered from a 2-part / 214k-row sample, not a representative full-sky render.
Regenerate on the full 402M (served table or pyarrow-direct) before committing
if a canonical version is wanted.
