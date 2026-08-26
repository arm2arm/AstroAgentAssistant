# ML Model Comparison for HPC Runtime Prediction

Session reference: `bs-wawa-project-2026` — Master thesis on ML-based HPC admission control.

## Key Finding: Tree Ensembles vs ANN on Small Tabular Data

On a dataset with **3 features and 1500 training samples**, tree ensembles (RF, GB, XGBoost) significantly outperform a neural network (ANN/MLP) for runtime prediction:

| Model | MAE | R² | Cancellations | Success Rate |
|-------|-----|-----|---------------|-------------|
| Random Forest | 0.7821 | 0.9681 | 3 | 99.3% |
| Gradient Boosting | 0.7785 | 0.9702 | 4 | 99.1% |
| XGBoost | 0.7964 | 0.9665 | 5 | 98.9% |
| ANN (MLP) [3,32,64,32,1] | 1.9157 | 0.8594 | 11 | 97.6% |
| Baseline (user estimate) | — | — | 21 | 95.6% |

## Why Tree Ensembles Win

- **Low feature count (3)**: Tree ensembles naturally capture non-linear relationships without feature engineering.
- **Small dataset (1500 samples)**: ANN has 4,256 trainable parameters — severely underfitting on this scale.
- **Tabular data structure**: HPC job metadata is inherently tabular, which is the native strength of tree ensembles.
- **No hyperparameter tuning needed**: RF and GB work well with defaults; ANN requires careful tuning.

## Practical Recommendation

For HPC runtime prediction (and similar tabular prediction tasks with <10k samples and <20 features):
- **Use Random Forest or Gradient Boosting** as the primary models
- **Use XGBoost** as an optional third option (may underperform GB on small datasets due to regularization)
- **Always include all three tree models** in comparison — they typically produce similar results, confirming the improvement is model-agnostic
- **Avoid ANN** unless you have >10k samples and >10 features

## Simulation Evaluation Pattern

Each ML model is evaluated on two dimensions:
1. **Prediction accuracy**: MAE, RMSE, R² on the test set
2. **Admission control impact**: Cancellation count, success rate, throughput, and error classification (TP/FP/FN/TN)

The error classification decomposes each model's rejection decisions into:
- **TP**: Correctly rejected a doomed job (good)
- **FP**: Incorrectly rejected a good job (bad)
- **FN**: Accepted a doomed job that got cancelled (bad)
- **TN**: Correctly accepted a good job (good)

For admission control, low FP is critical — rejecting a good job is less costly than cancelling a doomed one.
