# Silent data corruption when building flag strings with `'' += np.where(...)` (SH26 SH_OUTFLAG, 2026-08-22)

## The trap

Faithfully porting FA21-style `fSH_OUTFLAG` (pandas, `df['SH_OUTFLAG']=str('')`, `df.loc[sel, col]+='0'`) to vectorized numpy with a plain Python string seed:

```python
flag = ''                                   # str
flag += np.where(sel1, '0', np.where(sel2, '1', '2'))   # now ndarray <U2 (2 chars/row!)
flag += np.where(sel, '0', '1')
...
pa.array(np.asarray(flag, dtype=object))    # np.asarray(<U2 ndarray) -> 2D (N,2) char matrix
# pyarrow takes column 0 -> 1-char flags, written "successfully"
```

Two distinct corruptions stack:

1. `'' + np.array(['0','2'], dtype='<U1')` promotes to `<U2` **per-row 2-char fields**, so each subsequent `+= np.where(..., '0', '1')` overwrites into the padded second char position instead of appending a digit.
2. `np.asarray(<U2 ndarray, dtype=object)` yields a **2D** `(N, 2)` object array; `pa.array(..., type=pa.large_string())` silently takes column 0.

Output looks plausible (valid-looking flags, right row count, clean write) and a naive spot check of the first values passes. Detection came from an **independent full-column recomputation** that flagged 100% mismatch.

## The fix (FA21 semantics)

Seed with an object-dtype pandas Series — exactly what FA21's `df.loc[sel, col] += 'digit'` does under the hood:

```python
flag = pd.Series('', index=df.index, dtype=object)
flag += pd.Series(np.where(sel1, '0', np.where(sel2, '1', '2')), index=df.index, dtype=object)
flag += pd.Series(np.where(sel, '0', '1'), index=df.index, dtype=object)
# then: pa.array(np.asarray(flag, dtype=object), type=pa.large_string())  # flag is object Series -> 1D
```

Note: a manual sanity test that used `pd.Series` from the start produced correct 4-char values and *hid* the bug from the direct (non-dask) repro — the corruption was in the numpy path, not dask. Always verify the exact code path that will run.

## Dask 2025.10 LocalCluster kwarg

`spill_directory` and `worker_process_spill_dir` both rejected on dask 2025.10.0 (both raise `Server.__init__() got an unexpected keyword argument` → "Nanny failed to start"). For part-sized I/O with ample RAM, omit spill config entirely. If spill is genuinely needed, inspect `LocalCluster.__init__` signature on the target env first — the name has moved across releases.

## Per-part map pattern (verified, 402M rows in 2.1 min)

For "add a derived column to every part" jobs on a big RAM node (<compute-node>: 96c/770GB), one-part-in-one-part-out beats a served Dask table:

```python
cluster = LocalCluster(n_workers=48, threads_per_worker=2, memory_limit='15GB',
                       dashboard_address='127.0.0.1:8790')
with Client(cluster):
    import dask.bag as db
    total = db.from_sequence(list(zip(in_parts, out_parts))).starmap(process_file).compute()
```

- Keep part names/order identical in the output dir → trivially diff-able, no metadata rewrite needed.
- Worker-side print of intermediate values (with `file=sys.stderr, flush=True`) is how the truncated flags were caught in the dask path.
- Run with `--max-parts 2` test first; verify on the test parts; then full run to a NEW tagged dir (`sh26_final_joined_v220826`), never in place.

## Verification checklist that caught it

1. Schema: new col is LAST, name/type as intended, 0 float64 cols.
2. Row count (dataset `count_rows`) + part count match input exactly.
3. Per-part schema-drift scan across all output parts.
4. **Independent recomputation** of the derived column in a separately written script, full equality on sample parts (first/middle/last), plus full-column equality of all pre-existing columns (NaN-aware: `(a==b) | (a.isna() & b.isna())`).
5. Derived-value sanity: flag-length uniqueness (`str.len().nunique()==1`), value_counts distribution checked against physical expectation.

## Ops notes (<compute-node> via Newton)

- Script transfer to <compute-node>: `ssh newton "ssh <compute-node> 'cat > /tmp/x.py'" < localfile`, then md5-verify both hops. (scp hung on approval timeout; cat-redirect works.)
- Long jobs: launch on <compute-node> with `nohup ... > /tmp/x.log 2>&1 < /dev/null &`, poll the log; nested-SSH foreground calls time out at ~7 min and heredocs nested two levels deep mangle easily — write verify scripts to local files and ship them the same cat way.
- After killing dask, `pkill -f dask` on the node cleared stray schedulers; no stale state left for the re-run.
