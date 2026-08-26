Session SH26 plots summary

This file collects session-specific notes and example code snippets used during the June 12, 2026 'SH26' plotting session.

1) Created log-log 2D histogram for dist50 vs dist50_sh21 saved as /home/hermes/projects/SH26/img/dist50_vs_dist50_sh21_hist_logxy.png

Snippet (pcolormesh, LogNorm):

```python
H, xedges, yedges = np.histogram2d(x, y, bins=[xbins, ybins])
H_masked = ma.masked_where(H == 0, H)
pcm = ax.pcolormesh(xedges, yedges, H_masked.T, norm=LogNorm(vmin=H_masked.min(), vmax=H_masked.max()), cmap='viridis', shading='auto')
```

2) Hexbin + marginals for teff50 vs teff50_sh21 (linear scales) saved as /home/hermes/projects/SH26/img/teff50_vs_teff50_sh21_hex_marg_linear.png

Snippet (hexbin + marginals):

```python
fig = plt.figure(figsize=(8,7))
gs = gridspec.GridSpec(2,2,width_ratios=[4,1],height_ratios=[1,4],hspace=0.05,wspace=0.05)
ax_main = fig.add_subplot(gs[1,0])
ax_xhist = fig.add_subplot(gs[0,0], sharex=ax_main)
ax_yhist = fig.add_subplot(gs[1,1], sharey=ax_main)

hb = ax_main.hexbin(x, y, gridsize=200, cmap='viridis', mincnt=1)
ax_main.plot([mn, mx], [mn, mx], color='red', linestyle='--')
``` 

3) Notes & guardrails
- LOG_COLUMNS = ['log50','met50','av50'] should be treated as pre-logged; avoid log axes for them.
- Save images to /home/hermes/projects/SH26/img and print 'WROTE <path>' to mark completion.

