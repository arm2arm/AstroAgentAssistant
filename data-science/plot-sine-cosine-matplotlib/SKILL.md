---
name: plot-sine-cosine-matplotlib
description: Generate a PNG plot of sin(x) in red and cos(x) in green using matplotlib, handling missing dependencies in a managed Python environment.
author: Hermi (sorgenfresser)
---

## Goal
Create a 512×512 PNG image that visualises the functions:
- `sin(x)` plotted in **red**
- `cos(x)` plotted in **green**

The image should be saved to a path you can deliver (e.g., `~/sin_cos_plot.png`).

## Prerequisites & Constraints
- The environment may be *externally managed* (PEP 668), meaning `pip install` without `--break-system-packages` will fail.
- Preferred method: install the system package `python3-matplotlib` via `apt-get`. If you lack sudo, fall back to a virtual environment using `python3 -m venv` and install matplotlib inside it.
- Ensure the script runs with Python 3.12 (the default).
- Do **not** overwrite existing files unintentionally; use a unique filename or ask the user for a path if uncertain.

## Procedure
1. **Check for matplotlib**
   ```bash
   python3 -c "import matplotlib" && echo OK || echo MISSING"
   ```
2. **If missing**, attempt system install (requires sudo). If sudo is unavailable, create a venv:
   ```bash
   python3 -m venv /tmp/plotvenv
   source /tmp/plotvenv/bin/activate
   pip install matplotlib
   ```
3. **Write the plotting script** (can be inline in a `python3 - <<'PY'` heredoc):
   ```python
   import numpy as np
   import matplotlib.pyplot as plt
   x = np.linspace(0, 2*np.pi, 400)
   plt.figure(figsize=(6,6), dpi=150)
   plt.plot(x, np.sin(x), color='red', label='sin(x)')
   plt.plot(x, np.cos(x), color='green', label='cos(x)')
   plt.xlabel('x')
   plt.ylabel('y')
   plt.title('Sine (red) vs Cosine (green)')
   plt.legend()
   out_path = '/home/hermes/sin_cos_plot.png'
   plt.savefig(out_path, bbox_inches='tight')
   print(out_path)
   ```
4. **Run the script** using the appropriate Python (system or venv).
5. **Verify** the file exists:
   ```bash
   ls -l /home/hermes/sin_cos_plot.png
   ```
6. **Deliver** the image to the user by including `MEDIA:/home/hermes/sin_cos_plot.png` in your reply.

## Pitfalls & Fixes
- *ModuleNotFoundError*: Indicates matplotlib isn’t installed – follow step 2.
- *Permission denied* on `/usr/bin/apt`: You don’t have sudo. Use the virtual‑env fallback.
- *File not found after script*: Ensure the script printed the correct path and that the directory is writable.
- *Large image*: Adjust `figsize` or `dpi` if the file is too big for the platform.

## Example Commands
```bash
# Quick check
python3 -c "import matplotlib" || echo missing

# System install (if you have sudo)
sudo apt-get update && sudo apt-get install -y python3-matplotlib

# Virtual‑env fallback
python3 -m venv ~/plotenv
source ~/plotenv/bin/activate
pip install matplotlib
```

## Verification
After running, you should see a PNG file at `/home/hermes/sin_cos_plot.png` that shows two curves, red for sine and green for cosine, with axes labeled and a legend.

---
