---
name: animate-sine-cosine-matplotlib
description: Generate an MP4 animation of sine (green) and cosine (red) curves using matplotlib for frame rendering and ffmpeg for encoding. The skill avoids privileged operations and destructive commands.
author: Hermi (sorgenfresser)
---

## Goal
Create a short (~2 seconds) MP4 animation showing the sine and cosine curves moving in phase. The output file is placed in a user‑writable location (e.g., `/home/hermes/sin_cos_anim.mp4`).

## Prerequisites & Constraints
- `matplotlib` must be importable in the current Python environment. If it is missing, the user should install it manually (e.g., `sudo apt-get install python3-matplotlib` outside of this skill).
- `ffmpeg` must be available on the system (it is pre‑installed on the default VM).
- Use a temporary directory such as `/tmp/anim_frames` for intermediate PNG frames. No privileged commands (`sudo`) are used.
- Avoid destructive operations; the skill does **not** automatically delete the temporary frames. The user can manually clean them up if desired.

## Procedure
1. **Verify dependencies** (run manually if needed):
   ```bash
   python3 -c "import matplotlib" && echo "matplotlib OK" || echo "matplotlib missing"
   ffmpeg -version >/dev/null && echo "ffmpeg OK" || echo "ffmpeg missing"
   ```
2. **Generate PNG frames**
   ```bash
   mkdir -p /tmp/anim_frames
   python3 - <<'PY'
   import numpy as np, matplotlib.pyplot as plt, os
   frames = 60  # 2 seconds at 30 fps
   out_dir = '/tmp/anim_frames'
   for i in range(frames):
       t = i / frames * 2 * np.pi
       x = np.linspace(0, 2*np.pi, 400)
       plt.figure(figsize=(6,4), dpi=100)
       plt.plot(x, np.sin(x + t), color='green', linewidth=3, label='sin(x)')
       plt.plot(x, np.cos(x + t), color='red', linewidth=3, label='cos(x)')
       plt.xlim(0, 2*np.pi)
       plt.ylim(-1.2, 1.2)
       plt.title('Animated Sine (green) & Cosine (red)')
       plt.xlabel('x')
       plt.ylabel('y')
       plt.legend()
       plt.grid(True)
       fname = os.path.join(out_dir, f'frame_{i:03d}.png')
       plt.savefig(fname, bbox_inches='tight')
       plt.close()
   print('frame generation complete')
   PY
   ```
3. **Encode the frames into MP4**
   ```bash
   ffmpeg -y -framerate 30 -i /tmp/anim_frames/frame_%03d.png \
          -c:v libx264 -pix_fmt yuv420p \
          -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" \
          /home/hermes/sin_cos_anim.mp4
   ```
   - `-y` overwrites any existing file.
   - The `pad` filter ensures the dimensions are even, which many codecs require.
4. **Check the result**
   ```bash
   ls -lh /home/hermes/sin_cos_anim.mp4
   ```
   The file should be a few tens of kilobytes and play smoothly.
5. **(Optional) Clean up** – the user can remove the temporary frames manually if desired:
   ```bash
   rm -r /tmp/anim_frames
   ```

## Pitfalls & Fixes
- *Missing matplotlib*: Install it via the system package manager or a virtual environment before running the skill.
- *ffmpeg not found*: Install `ffmpeg` (`sudo apt-get install ffmpeg`) outside of this skill.
- *Permission errors*: The paths used (`/tmp/anim_frames` and `/home/hermes`) are writable for the agent.
- *Large video*: Reduce `frames` or `dpi` in the Python script to shrink the output size.

## One‑liner (after dependencies are satisfied)
```bash
mkdir -p /tmp/anim_frames && python3 - <<'PY'
import numpy as np, matplotlib.pyplot as plt, os
frames=60; out='/tmp/anim_frames'
for i in range(frames):
    t=i/frames*2*np.pi; x=np.linspace(0,2*np.pi,400)
    plt.figure(figsize=(6,4),dpi=100)
    plt.plot(x, np.sin(x+t), 'g', linewidth=3)
    plt.plot(x, np.cos(x+t), 'r', linewidth=3)
    plt.xlim(0,2*np.pi); plt.ylim(-1.2,1.2); plt.grid(True)
    plt.savefig(f'{out}/frame_{i:03d}.png'); plt.close()
PY
ffmpeg -y -framerate 30 -i /tmp/anim_frames/frame_%03d.png -c:v libx264 -pix_fmt yuv420p -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" /home/hermes/sin_cos_anim.mp4
```

---
