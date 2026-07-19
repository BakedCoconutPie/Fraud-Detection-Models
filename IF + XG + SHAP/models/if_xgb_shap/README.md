# IF + XGBoost + SHAP Model

Implementation:

```text
src/pastetrace_if_xgb_shap.py
```

Pipeline:

1. Extract session-level behavioral features.
2. Fit Isolation Forest on the training fold.
3. Add the Isolation Forest anomaly score as a feature.
4. Train XGBoost on the supervised labels.
5. Explain predictions with SHAP.

Why this combination:

- Isolation Forest captures unusual behavior without relying only on labels.
- XGBoost works well on small tabular datasets and nonlinear feature interactions.
- SHAP provides local and global explanations for instructor review.

This branch is the explainable classical-machine-learning baseline for the paper.

## Model Files

Thư mục này **không chứa file model pre-trained** vì script sử dụng **Leave-One-Out
cross-validation** — model (Isolation Forest, XGBoost, StandardScaler) được **huấn
luyện lại mỗi lần chạy**.

Kết quả đầu ra (predictions, SHAP values, metrics) được lưu vào thư mục `outputs/`.
