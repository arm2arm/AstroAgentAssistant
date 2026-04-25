---
name: reana-sin-plot-workflow
description: |
  Minimal REANA workflow that plots a sine curve in green using pandas and matplotlib.
  Includes `reana.yaml`, `plot_sin.py` (and optional `requirements.txt`).
contributors:
  - Hermes
---

## Files

### reana.yaml
```yaml
name: sin-plot
description: Plot a sine curve in green using pandas and matplotlib.
environment:
  # Choose an appropriate REANA environment that already includes pandas, matplotlib, numpy.
  # Example (replace with the exact tag you need):
  image: gitlab-p4n.aip.de/punch_public/reana/environments:latest
commands:
  - python plot_sin.py
```

### plot_sin.py
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Generate x values
x = np.linspace(0, 2 * np.pi, 200)
# Compute sine
y = np.sin(x)

# Build a pandas DataFrame
df = pd.DataFrame({"x": x, "sin(x)": y})

# Plot using pandas (which internally uses matplotlib)
ax = df.plot(x="x", y="sin(x)", color="green", legend=False)
ax.set_xlabel('x')
ax.set_ylabel('sin(x)')
ax.set_title('Sine wave (green)')

plt.tight_layout()
plt.savefig('sin_plot.png')
plt.close()
```

### (Optional) requirements.txt
```
pandas
matplotlib
numpy
```

## Usage
1. Create a directory and place the above files inside.
2. Upload and start the workflow with REANA client:
   ```bash
   reana-client upload -w sin-plot .
   reana-client start -w sin-plot
   ```
3. Retrieve the output image after completion:
   ```bash
   reana-client getoutput -w sin-plot sin_plot.png .
   ```
