---
name: shboost_cmd_plot_and_animation
title: ShBoost CMD Plot and Population Animation
description: Cache selected columns from the ShBoost 2024 S3 dataset, create a hexbin CMD with log-scaled density, add optimized non‑overlapping stellar‑population annotations, and generate both a high‑resolution PNG and an MP4 animation.
author: hermes
---

## Overview
Automates the workflow for visualising the ShBoost 2024 colour‑magnitude diagram (CMD) from a massive S3 dataset. Handles efficient caching, sampling, hexbin density plotting, colour‑coded annotations, legend creation, and animation generation.

## Prerequisites
- Python 3.12+ with packages: `dask[dataframe]`, `pandas`, `matplotlib`, `seaborn`.
- Access to the public S3 bucket `s3://shboost2024/shboost_08july2024_pub.parq/`.
- `ffmpeg` (optional; falls back to GIF via PillowWriter).

## Constants (adjust as needed)
```python
S3_ENDPOINT = "https://s3.data.aip.de:9000"
S3_PARQUET_GLOB = "s3://shboost2024/shboost_08july2024_pub.parq/*.parquet"
STORAGE_OPTS = {"use_ssl": True, "anon": True, "client_kwargs": {"endpoint_url": S3_ENDPOINT}}
CACHE_PATH = "shboost_full_cmd.parquet"   # local cache of selected columns
TARGET_ROWS = 10**12  # placeholder – full cache will be written regardless of size
PLOT_ROWS = 10_000_000  # rows used for the actual figure (adjust for RAM)
```

## 1. Load or Create Cache
```python
def load_or_fetch(force_refresh: bool) -> pd.DataFrame:
    if os.path.isfile(CACHE_PATH) and not force_refresh:
        print(f"🔄 Loading cached full data from {CACHE_PATH}")
        full_dd = dd.read_parquet(CACHE_PATH)
    else:
        print("⏬ Reading metadata from S3 …")
        full_dd = dd.read_parquet(S3_PARQUET_GLOB, storage_options=STORAGE_OPTS)
        full_dd = full_dd[["bprp0", "mg0"]]
        total_rows = full_dd.shape[0].compute()
        print(f"Dataset size: {total_rows:,} rows (full cache will be written)")
        full_dd.to_parquet(CACHE_PATH, write_index=False)
        print("Full cache saved.")
        full_dd = dd.read_parquet(CACHE_PATH)

    # Sample for plotting
    total_rows = full_dd.shape[0].compute()
    frac = min(PLOT_ROWS / total_rows, 1.0)
    print(f"Sampling fraction for plot: {frac:.6%} → ~{min(PLOT_ROWS, total_rows):,} rows")
    sample_dd = full_dd if frac >= 1.0 else full_dd.sample(frac=frac, random_state=42)
    pdf = sample_dd.compute()
    print(f"Sampled rows for plot: {len(pdf):,}")
    return pdf
```

## 2. Static CMD Plot (`plot_cmd`)
```python
def plot_cmd(df: pd.DataFrame, png_path: str = "shboost_cmd.png"):
    sns.set_style("whitegrid")
    plt.rcParams.update({
        "font.size": 12,
        "axes.titlesize": 14,
        "axes.labelsize": 13,
        "legend.fontsize": 11,
        "figure.figsize": (8, 6),
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
    })
    mesh = plt.hexbin(df["bprp0"], df["mg0"], gridsize=512, cmap="viridis",
                     mincnt=1, linewidths=0.2, norm=LogNorm())
    cb = plt.colorbar(mesh, label="Counts")
    cb.ax.set_ylabel("Counts", rotation=270, labelpad=15)
    cb.ax.set_yscale('log')

    # Colour map for population labels
    color_map = {
        "Main Sequence": "tab:blue",
        "Turn‑off / Subgiants": "tab:orange",
        "Red Giant Branch": "tab:red",
        "Red Clump": "tab:purple",
        "Horizontal Branch": "tab:brown",
        "AGB": "tab:pink",
        "White Dwarfs": "tab:gray",
        "Blue Stragglers": "tab:green",
    }
    def add_label(txt, xy, offset=(20,20)):
        plt.annotate(txt, xy=xy, xytext=offset, textcoords='offset points',
                     fontsize=9, color=color_map.get(txt, 'white'), ha='center', va='center',
                     bbox=dict(boxstyle='round,pad=0.2', fc='black', alpha=0.6),
                     arrowprops=dict(arrowstyle='->', color='black', lw=0.8))
    # Optimised placements (adjust if you change PLOT_ROWS)
    add_label('Main Sequence', xy=(1.5, 8), offset=(-60, -20))
    add_label('Turn‑off / Subgiants', xy=(0.8, 4), offset=(-60, -20))
    add_label('Red Giant Branch', xy=(1.9, 0), offset=(60, 40))
    add_label('Red Clump', xy=(1.2, 0.8), offset=(60, -40))
    add_label('Horizontal Branch', xy=(0.4, -1), offset=(-60, 30))
    add_label('AGB', xy=(2.3, -0.5), offset=(60, 30))
    add_label('White Dwarfs', xy=(-0.25, 13), offset=(-80, -30))
    add_label('Blue Stragglers', xy=(-0.2, 7), offset=(-80, 30))

    # Legend matching annotation colours
    from matplotlib.lines import Line2D
    pop_legend = [Line2D([0],[0],marker='o',color='w',label=name,
                         markerfacecolor=color_map[name],markersize=8) for name in color_map]
    plt.legend(handles=pop_legend, loc='upper right', fontsize=8, framealpha=0.7, title='Populations')

    plt.title(f"ShBoost 2024 Colour‑Magnitude Diagram ({len(df):,} stars)")
    plt.xlabel("bprp0")
    plt.ylabel("mg0")
    plt.xlim(-4, 8)
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(png_path, dpi=300)
    plt.close()
    print(f"✅ Saved PNG -> {png_path}")
```

## 3. Animation (`create_animation`)
```python
def create_animation(df, png_path="shboost_cmd.png"):
    import matplotlib.animation as animation
    from matplotlib.colors import LogNorm
    fig, ax = plt.subplots()
    sns.set_style("whitegrid")
    plt.rcParams.update({"font.size": 12, "axes.titlesize": 14, "axes.labelsize": 13,
                         "legend.fontsize": 11, "figure.figsize": (8, 6),
                         "savefig.dpi": 300, "savefig.bbox": "tight"})
    mesh = ax.hexbin(df["bprp0"], df["mg0"], gridsize=512, cmap="viridis",
                     mincnt=1, linewidths=0.2, norm=LogNorm())
    cb = fig.colorbar(mesh, label="Counts")
    cb.ax.set_ylabel("Counts", rotation=270, labelpad=15)
    cb.ax.set_yscale('log')
    ax.set_xlabel("bprp0")
    ax.set_ylabel("mg0")
    ax.set_xlim(-4, 8)
    ax.invert_yaxis()
    ax.set_title(f"ShBoost 2024 Colour‑Magnitude Diagram ({len(df):,} stars)")

    populations = [
        ("Main Sequence", (1.5, 8)),
        ("Turn‑off / Subgiants", (0.8, 4)),
        ("Red Giant Branch", (1.9, 0)),
        ("Red Clump", (1.2, 0.8)),
        ("Horizontal Branch", (0.4, -1)),
        ("AGB", (2.3, -0.5)),
        ("White Dwarfs", (-0.25, 13)),
        ("Blue Stragglers", (-0.2, 7)),
    ]
    color_map = {name: col for name, col in zip([p[0] for p in populations],
                     ["tab:blue","tab:orange","tab:red","tab:purple","tab:brown",
                      "tab:pink","tab:gray","tab:green"])}
    from matplotlib.lines import Line2D
    pop_legend = [Line2D([0],[0],marker='o',color='w',label=name,
                         markerfacecolor=color_map[name],markersize=8) for name in color_map]
    ax.legend(handles=pop_legend, loc='upper right', fontsize=8, framealpha=0.7, title='Populations')

    annotation = ax.annotate('', xy=(0,0), xytext=(0,0), textcoords='offset points',
                             bbox=dict(boxstyle='round,pad=0.3', fc='black', alpha=0.6),
                             arrowprops=dict(arrowstyle='->', color='red', lw=1))
    def init():
        annotation.set_visible(False)
        return (annotation,)
    def update(frame):
        name, xy = populations[frame]
        annotation.set_visible(True)
        annotation.set_text(name)
        annotation.xy = xy
        annotation.set_position((30, -30))
        annotation.set_fontsize(12)
        annotation.set_color(color_map.get(name, 'white'))
        return (annotation,)
    anim = animation.FuncAnimation(fig, update, frames=len(populations), init_func=init,
                                   interval=2000, blit=False, repeat=True, save_count=len(populations))
    out_path = os.path.join(os.path.dirname(png_path), 'shboost_population_animation.mp4')
    try:
        from matplotlib.animation import FFMpegWriter
        writer = FFMpegWriter(fps=0.5)
        anim.save(out_path, writer=writer)
    except Exception:
        out_path = os.path.join(os.path.dirname(png_path), 'shboost_population_animation.gif')
        from matplotlib.animation import PillowWriter
        anim.save(out_path, writer=PillowWriter(fps=0.5))
    plt.close(fig)
    print(f"✅ Saved animation -> {out_path}")
```

## 4. Execution
```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force-refresh", action="store_true",
                        help="Ignore existing cache and re‑download from S3.")
    args = parser.parse_args()
    df = load_or_fetch(force_refresh=args.force_refresh)
    plot_cmd(df)
    create_animation(df)
```

## Tips & Gotchas
- **Memory**: The full cache (~200 M rows) occupies several GB on disk but stays lazy thanks to Dask. Only `PLOT_ROWS` rows are materialised.
- **Adjust `PLOT_ROWS`** if you hit RAM limits.
- **Annotation offsets** may need tweaking for different sample sizes.
- **FFmpeg**: Install `ffmpeg` for MP4 output; otherwise the fallback GIF works everywhere.
- **Cache invalidation**: Use `--force-refresh` when the upstream dataset updates.

---

*Skill created by Hermes.*