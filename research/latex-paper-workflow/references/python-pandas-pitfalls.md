# Python-Pandas Pitfalls in Data Science Workflows

Session reference: `bs-wawa-project-2026` — ML simulation workflow for HPC admission control.

## Boolean Series Index Alignment Error

**Error**: `pandas.errors.IndexingError: Unalignable boolean Series provided as indexer (index of the boolean Series and of the indexed object do not match)`

**Cause**: Creating a boolean mask from one DataFrame and applying it to a different DataFrame with a mismatched index:
```python
mask = df_a['col'] == value      # mask.index is df_a.index
subset = df_b[mask]               # ERROR: mask.index != df_b.index
```

**Fix**: Use `iloc[mask.values]` to bypass index alignment:
```python
subset = df_b.iloc[mask.values]   # works regardless of index mismatch
```

**Why this happens**: Pandas Series index-aligned indexing (`df[mask]`) requires the boolean Series index to match the DataFrame index exactly. `iloc` uses positional indexing and doesn't care about index alignment.

**Common scenarios**:
- Creating a mask from `test_data` but applying it to `simulation_results` (which has a different index)
- Filtering results from one model run with a mask derived from the data generation step
- Any case where you have two DataFrames with different row ordering or indexing

## Matplotlib Grid Mismatch Warning

**Warning**: `UserWarning: tight_layout not applied: number of columns in subplot specifications must be multiples of one another.`

**Cause**: Mixing subplot grids with different column counts (e.g., `2,4` grid mixed with `3,3` grid in the same figure).

**Fix**: Ensure all `add_subplot()` calls use a consistent grid (e.g., all `3,3` or all `2,3`).

## Installing Python Packages on Debian/Ubuntu

**Error**: `pip install xgboost torch` fails with "Note: if you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages."

**Fix**: Use `pip install --break-system-packages <package>` or create a virtual environment first:
```bash
python3 -m venv ~/myenv
source ~/myenv/bin/activate
pip install xgboost torch
```

## Feature Scaling for Neural Networks

When training ANN/MLP on tabular data, always standardize features before training:
```python
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
```

**Important**: Fit the scaler only on training data, transform both train and test separately.

## Mixed Grid Subplot Specs

When building multi-panel figures in matplotlib, be consistent with grid dimensions:
- `fig.add_subplot(3, 3, N)` expects 9 panels total
- `fig.add_subplot(2, 4, N)` expects 8 panels total
- Mixing them causes `tight_layout` to fail silently

---

## PyTorch/ANN-Specific Pitfalls

### Optimizer Must Reference the Trained Model Instance

**Error**: ANN predicts garbage (MAE >> baseline, R² < 0) despite correct training loop code.

**Cause**: Creating the optimizer from a *fresh* model instance instead of the one being trained:
```python
# BUG: optimizer trains a DIFFERENT model than ann_model!
ann_model = SimpleANN()
optimizer = torch.optim.Adam(SimpleANN().parameters(), lr=0.001)  # new instance
for epoch in range(200):
    optimizer.step()  # optimizes the FRESH model, not ann_model
pred = ann_model(X_test)  # ann_model was never trained
```

**Fix**: Create the optimizer on the actual model instance:
```python
ann_model = SimpleANN()
optimizer = torch.optim.Adam(ann_model.parameters(), lr=0.001)  # correct
for epoch in range(200):
    optimizer.zero_grad()
    loss = criterion(ann_model(X_train), y_train)
    loss.backward()
    optimizer.step()
```

**Detection**: If `MAE > 0.9 × mean(y_test)` and `R² < 0`, the model likely wasn't trained. A properly trained model on this task should have `R² > 0.85`.

### Learning Curve: Proper Train/Test Split with Synthetic Data

**Error**: `ValueError: Found array with 0 sample(s)` during StandardScaler fit in a learning curve loop.

**Cause**: Generating `max(n, 500)` samples and trying to split into `n_train = min(n, total-500)` and `tail(500)` fails when `n` is small — `n_train` becomes 0.

**Fix**: Generate a pool of `n + n_test` samples, then cleanly split:
```python
pool = generate_dataset(n + 500)    # generate enough for both splits
tmp_train = pool.head(n)            # first n → training
tmp_test = pool.tail(500)           # last 500 → evaluation
```

### Learning Curve: Proportional Epochs for Small Training Sets

Small training sets need proportionally more epochs to converge. Use dynamic epoch scaling:
```python
n_epochs = max(300, int(200 * n_train / 200))
for _ in range(n_epochs):
    # ... training loop
```
This ensures ANN has enough capacity to learn from limited data in early learning curve points.

---

## Scientific Visualization Patterns

### Multi-Model Grid Sizing

When plotting **N models** in a subplot grid, use at least N columns. A common mistake: trying to fit 4 models into a 3-column grid (indices 0,1,2,3 but only 3 columns available). Always use `plt.subplots(4, 4, ...)` for 4 models, not `plt.subplots(4, 3, ...)`.

### Explainable Multi-Model Comparison Layout

A proven pattern for comparing multiple ML models in a publication-quality figure:

| Row | Content | Purpose |
|-----|---------|---------|
| Row 1 | Predicted vs Actual scatter per model | Raw prediction accuracy |
| Row 2 | Error distribution (|actual−predicted|) per model | How errors are distributed |
| Row 3 | Simulation outcomes (success rate, cancellations, error matrix) | Operational impact |
| Row 4 | Deep analysis (model comparison, per-group breakdown, learning curve) | Deeper insights |

Each model gets its own column. Use a consistent color palette: Blue=RF, Yellow=GB, Green=XGB, Red/Orange=ANN.
