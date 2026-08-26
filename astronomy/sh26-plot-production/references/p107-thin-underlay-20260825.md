# P107 v2 — "thin" full underlay + PDF delivery (2026-08-25)

Companion to `p107-<compute-node>-ops-2026-08-25.md` (P107 v1 + <compute-node> ops).

User request "put thin in full plots pdf" = make the full-distribution
hexbin underlay in the 4 dual-hexbin panels (XY, XZ, CMD, Kiel) THINNER
(sparse cells faint, lighter grey) under the cleaned viridis overlay, and
deliver a PDF. `ctx.save` already writes PNG + PDF + JSON sidecar — just
pull the `.pdf` over nested SSH with `cat` (same as the PNG), verify
`%PDF-1.4` header + `%%EOF`.

## matplotlib `hexbin` pitfall: `bins="log"` and `norm=` are mutually exclusive

Passing both warns `Only one of 'bins' and 'norm' arguments can be
supplied, ignoring bins='log'` and the **norm wins**. So a "log + floor"
underlay must use an EXPLICIT `LogNorm(vmin=1, vmax=...)` with NO
`bins`/`mincnt` args. (Pyright flags tuple-unpacking like
`*p["full_norm"]` in hexbin calls as "not iterable" — false positive.)

## Thin-underlay recipe

Full layer (thin):
```python
ax.hexbin(xf, yf, gridsize=gs, cmap="Greys",
          norm=LogNorm(vmin=1, vmax=max(len(xf), 2)),
          extent=ext, linewidths=0, alpha=0.45, rasterized=True)
```
The `vmin=1` floor is what makes sparse cells very light grey; the
densest cell hits the Greys top. Cleaned layer on top keeps
`bins="log", mincnt=1, alpha=0.95` (viridis). Same gridsize/extent for
both layers so the underlay aligns with the overlay.

## Verify a visual thinning change without vision

(vision_analyze timed out 4× this session.) Same panel pixel-crop
before/after; classify grey = `|r−g|<12 & |g−b|<12` & not >245-white.
Here grey coverage 0.370→0.230 of the crop and mean brightness
230→233 → underlay thinner + lighter, change confirmed deterministically.

## Nested-SSH src-tree redeploy (simplest verified form)

```
tar cf - src | ssh N "timeout 90 ssh NN 'rm -rf <job>/src && tar xf - -C <job> && md5sum <job>/src/<file>.py'"
```
Stdin passes THROUGH both ssh layers to the inner `tar` (verified working
2026-08-25; simpler than stage-on-Newton). md5-verify the key file
local-vs-remote. CAVEAT: a `< file` redirect written INSIDE the inner
command is evaluated on the INNER host — staged-file redirects there
silently 404 (hit both forms this session).

## Run numbers (v2, <compute-node> pyarrow-direct, tmux)

read 402,121,784 rows 98 s → converged 327,477,457 → make() 356.4 s →
total 625.7 s. PDF 1.37 MB (collections rasterized → fast in Acrobat).
Committed `4d98ebe` (module + PNG + PDF) → origin/main in sync.
