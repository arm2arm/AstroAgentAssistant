# Join re-run v190826: PM columns + float32 storage — 2026-08-19

Supersedes the output-name / overwrite notes in
`join-on-<compute-node>-papermill.md` (read that first for the full setup: two-root
paths, local cluster, run commands, the .ipynb-via-patch pitfall).

State of `notebooks/sh2026_join_papermill.ipynb` at commit `30b8d3c`:

## PM columns (resolves the "402M PM join" open question)

The PM source IS the Gaia float32 table — no separate PM parquet needed.
Verified present in `GaiaSource.float32.parq/part.0.parquet` (69 cols total):
`pmra`, `pmra_error`, `pmdec`, `pmdec_error` (plus a bare `pm`).

- `gaia_cols` now lists all 4 after `ag_gspphot` (13 Gaia cols pulled).
- Verification cell's `required_exact` list extended with the same 4.
- Consequence: P82/P90–P93 can run at full 402M scale; drop the "50M"
  paper labels once the v190826 catalog is built.

## New output name (non-destructive)

User rule: re-runs must not clobber existing catalogs.

- `out_path2 = workdir + "/final/combined/sh26_final_joined_v190826"`
- Checkpoints: `sh26_final_joined_v190826.__tmp_{base,dups,enriched}`
- June artifacts `sh26_phase2` + `__tmp_*` and the 210 GB
  `sh26_final_joined/` are untouched. New catalog = **133 cols**
  (old 129 + 4 PM).
- Convention: tag re-run outputs with a date suffix (`vDDMMYY`) rather
  than overwriting; mention in the plan doc.

## float32 storage convention (user rule: "all processes")

Every pipeline write stores float32, never float64:

```python
# setup cell:
def _f32(ddf):
    casts = {c: "float32" for c in ddf.columns
             if str(ddf.dtypes.get(c, "")) == "float64"}
    if casts:
        ddf = ddf.astype(casts)
    return ddf

# every write becomes:  _f32(ddf).to_parquet(...)
```

Applied to all 4 writes (base, dups, enriched stage1, final). Dask dtypes
resolve lazily, so the astyle cast is a cheap projection, not an extra
read. Verification cell ends with a hard assert: zero float64 columns in
the final output (prints the offenders if any).

Side benefit: served-table memory drops to the ~35 GB float32 budget
(plan previously said "60–70 GB float64 *or* ~35 GB float32" — now
guaranteed).

## Technique: JSON-safe notebook editing (recurring)

Same lesson as the parent reference — re-stating because it fired AGAIN
this session: build/modify the papermill wrapper programmatically
(`json.load` → mutate `cells[i]['source']` as a list of `\n`-terminated
lines → `json.dump(indent=1)` → re-load → `compile()` every code cell).
Helper script pattern kept in `/tmp/build_join_nb.py` during the session.
Never `patch`/sed a `.ipynb`.

## Doc sync

`doc/full_catalog_plan.md` updated in the same commit: PM open question
marked RESOLVED, cost-class note for P82/P90–P93, float32 convention
under the served-table architecture section. Keep plan doc and notebooks
in lockstep (commit together).
