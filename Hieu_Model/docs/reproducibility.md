# Reproducibility Guide

## 1. Prepare Environment

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 2. Prepare Data

The pipeline expects the normalized schema described in `docs/data_schema.md`.

Example local path:

```text
D:\Desktop\PasteTrace_Normalized\PasteTrace_Normalized
```

This folder should contain:

```text
normalized/
├── labels.csv
├── 111_A.json
└── ...
```

## 3. Run IF + XGBoost + SHAP

Original 16 PasteTrace sessions:

```powershell
.\scripts\run_if_xgb_shap.ps1 `
  -DataDir "D:\Desktop\PasteTrace_Normalized\PasteTrace_Normalized" `
  -Subset original16 `
  -OutDir "outputs\pastetrace_original16"
```

All 19 normalized PasteTrace sessions:

```powershell
.\scripts\run_if_xgb_shap.ps1 `
  -DataDir "D:\Desktop\PasteTrace_Normalized\PasteTrace_Normalized" `
  -Subset all `
  -OutDir "outputs\pastetrace_all19"
```

## 4. Output Files

- `features.csv`: extracted session-level features.
- `predictions.csv`: label, predicted probability, prediction, IF anomaly score.
- `metrics.json`: Precision, Recall, F1, AUC, confusion matrix.
- `shap_values.csv`: per-session SHAP values.
- `shap_importance.csv`: global feature importance by mean absolute SHAP.
- `shap_importance.png`: SHAP importance chart.

## 5. Important Caveat

PasteTrace is small and imbalanced. Treat its results as a case study, not as the main evidence for generalization.
