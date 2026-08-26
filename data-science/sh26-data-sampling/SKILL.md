---
name: sh26-data-sampling
title: SH26 5M-row sample from Newton joined catalog
description: Use when sampling or refreshing the ~5M row SH26 dataset.
tags:
  - sh26
  - data-sampling
  - dask
---

# Sample and transfer SH26 full joined catalog

Source on Newton (141.33.4.144): `/lustre/<user>/ipython/SH2025/reana/final/combined/sh26_final_joined/` — 4094 parts, ~402M rows. Script: `scripts/sample_parquet.py`.

## Commands

```bash
# Sample on Newton
ssh arm2arm@141.33.4.144 \
  "cd /lustre/<user>/ipython/SH2025/reana && python3 scripts/sample_parquet.py \
    --input final/combined/sh26_final_joined/ \
    --output sampled/sh26_5m_sample.parq/"

# SCP 8 splits locally
DEST=/home/hermes/projects/SH26/data/sh26_joined_5m.parq/
mkdir -p "$DEST"
for i in {0..7}; do
  scp arm2arm@141.33.4.144:".../splits/part.${i}.parquet" "$DEST/"
done

# Run plots
cd /home/hermes/projects/SH26 && PYTHONPATH=src python -m sh26 plots --all --no-cuts \
  --data data/sh26_joined_5m.parq --threads 16 --memory 4GB
```

**PITFALL:** Never use `sh26_phase1_dedup/` — missing enriched SH21/Weiler/BJ columns. Use only `sh26_final_joined/`.
