---
name: reana-workflow-sin-plot
version: "1.0"
description: Automates creation, submission, monitoring, and retrieval of a REANA workflow that plots a green sine curve using pandas and matplotlib.
author: Hermes
---

## Overview
This skill automates the full REANA workflow lifecycle for generating a green sine‑wave plot using pandas and matplotlib.

## Prerequisites
- REANA server URL (default `https://reana.cern.ch`).
- REANA access token with `workflow-create`, `workflow-start`, `workflow-getoutput`, and `workflow-status` scopes.
- Python 3 on the host machine.

## Steps
1. **(Optional) Isolate the REANA client**
   ```bash
   python3 -m venv ~/reana_venv
   source ~/reana_venv/bin/activate
   pip install --upgrade pip
   pip install reana-client
   ```
2. **Create workflow directory**
   ```bash
   mkdir -p ~/reana_sin_workflow && cd ~/reana_sin_workflow
   ```
3. **Write `reana.yaml`**
   ```yaml
   name: sin-plot
   description: Plot a sine curve in green using pandas & matplotlib.
   environment:
     image: gitlab-p4n.aip.de:5005/p4nreana/reana-env:py311-astro.9845
   commands:
     - python plot_sin.py
   ```
4. **Write `plot_sin.py`**
   ```python
   import numpy as np, pandas as pd, matplotlib.pyplot as plt
   x = np.linspace(0, 2*np.pi, 200)
   y = np.sin(x)
   df = pd.DataFrame({'x': x, 'sin(x)': y})
   ax = df.plot(x='x', y='sin(x)', color='green', legend=False)
   ax.set_xlabel('x')
   ax.set_ylabel('sin(x)')
   ax.set_title('Sine wave (green)')
   plt.tight_layout()
   plt.savefig('sin_plot.png')
   plt.close()
   ```
5. **(Optional) `requirements.txt`** – needed only when building a custom image.
   ```text
   pandas
   matplotlib
   numpy
   ```
6. **Upload workflow**
   ```bash
   reana-client upload -w sin-plot .
   ```
7. **Start workflow**
   ```bash
   reana-client start -w sin-plot
   ```
8. **Monitor until finished**
   ```bash
   while true; do
       status=$(reana-client status -w sin-plot | grep -i status | awk '{print $2}')
       echo "Current status: $status"
       [[ "$status" =~ ^(finished|failed)$ ]] && break
       sleep 5
   done
   ```
9. **Retrieve the image**
   ```bash
   reana-client getoutput -w sin-plot sin_plot.png .
   ```
   The file `sin_plot.png` will appear in the current directory.

## Pitfalls & Tips
- Export token and server before any command:
  ```bash
  export REANA_SERVER_URL=https://reana.cern.ch   # or your dev URL
  export REANA_ACCESS_TOKEN=YOUR_TOKEN_HERE
  ```
- Verify the environment image contains the required libraries; otherwise build a custom Docker image and reference it.
- Pre‑pull the Docker image if your network blocks on‑the‑fly pulls.
- Use the virtual environment to avoid system‑wide package conflicts.

## Verification
After step 9 you should have a `sin_plot.png` showing a smooth green sine wave with axis labels and a title.
