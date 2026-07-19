# Mamba Sequence Model

> **Trạng thái: Đang được phát triển.** Thư mục này chưa có model file hoặc script
> huấn luyện. Hướng dẫn chạy mô hình Mamba sẽ được bổ sung khi hoàn thành.

This directory is reserved for the deep sequence model branch.

Expected future contents:

```text
models/mamba/
├── README.md
├── train.py
├── dataset.py
├── config.yaml
└── checkpoints/      # ignored by git if large
```

Planned input:

- Event sequence from the same normalized JSON files.
- Each event encoded by type, timestamp gap, text length, and paste source.

Planned evaluation:

- Use the same folds as IF + XGBoost + SHAP.
- Report Precision, Recall, F1, AUC, runtime, and model size.

This directory is intentionally a placeholder until the Mamba branch is implemented.
