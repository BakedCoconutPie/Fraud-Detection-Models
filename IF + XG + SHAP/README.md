# Behavioral Programming Exam Cheating Detection

This repository contains reproducibility code for a research project on detecting cheating risk in programming exams using behavioral signals from IDE logs.

The project currently includes:

- A normalized behavioral data schema compatible with reconstructed PasteTrace data and future FPT IDE logs.
- A classical explainable pipeline: Isolation Forest + XGBoost + SHAP.
- Placeholders for the sequence model branch: Mamba.
- Scripts and notes for reproducing the PasteTrace case-study results.

For a Vietnamese walkthrough of the data conversion, model flow, outputs, and
metrics, see `docs/learning_guide_vi.md`.

## Repository Layout

```text
.
|-- data/
|   |-- normalized/          # 19 session JSONs + labels.csv (PasteTrace)
|   `-- README.md
|-- docs/
|   |-- data_schema.md
|   |-- learning_guide_vi.md
|   `-- reproducibility.md
|-- models/
|   |-- if_xgb_shap/
|   |   `-- README.md        # Model được train lại khi chạy (LOO CV)
|   `-- mamba/
|       `-- README.md        # Placeholder – đang phát triển
|-- outputs/
|   |-- pastetrace_original16/
|   `-- pastetrace_all19/
|-- scripts/
|   |-- run_all_experiments.ps1
|   `-- run_if_xgb_shap.ps1
|-- src/
|   `-- pastetrace_if_xgb_shap.py
|-- paper_updated_if_xgb_shap.tex
|-- paper_update_notes.md
|-- requirements.txt
`-- README.md
```

## Models

| Model | Thư mục | Trạng thái | Ghi chú |
|---|---|---|---|
| Isolation Forest + XGBoost + SHAP | `models/if_xgb_shap/` | ✅ Sẵn sàng | Model được huấn luyện lại mỗi lần chạy script (LOO CV). Không cần file model pre-trained. |
| Mamba (Sequence Model) | `models/mamba/` | 🚧 Đang phát triển | Chưa có script hoặc checkpoint. Hướng dẫn sẽ được bổ sung. |

## Quick Start

Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Run the IF + XGBoost + SHAP pipeline (sử dụng dữ liệu trong repo):

```powershell
.\scripts\run_if_xgb_shap.ps1 `
  -DataDir "data" `
  -Subset original16 `
  -OutDir "outputs\pastetrace_original16"
```

Run both PasteTrace settings:

```powershell
.\scripts\run_all_experiments.ps1 `
  -DataDir "data"
```

> **Lưu ý:** Script `src/pastetrace_if_xgb_shap.py` nhận tham số `--data` trỏ tới
> thư mục cha chứa `normalized/`. Model (Isolation Forest, XGBoost, StandardScaler)
> sẽ được **huấn luyện lại** mỗi lần chạy bằng Leave-One-Out cross-validation —
> không cần load model có sẵn.

> **Mamba:** Hướng dẫn chạy mô hình Mamba đang được phát triển. Xem
> `models/mamba/README.md` để biết kế hoạch triển khai.

## Data

Raw or private data should not be committed directly. Put local datasets under:

- `data/raw/` for downloaded or reconstructed public data.
- `data/fpt/` for private FPT collection data.
- `data/private/` for sensitive intermediate files.
- `data/normalized/` for normalized PasteTrace sessions (included in this repo).

The pipeline expects a normalized folder with:

```text
normalized/
|-- <session_id>.json
`-- labels.csv
```

See `docs/data_schema.md`.

## Current PasteTrace Results

| Dataset | Sessions | Precision | Recall | F1 | AUC |
|---|---:|---:|---:|---:|---:|
| PasteTrace original16 | 16 | 0.867 | 0.929 | 0.897 | 0.714 |
| PasteTrace all19 | 19 | 0.875 | 0.875 | 0.875 | 0.833 |

These results are a small case study only. PasteTrace is highly imbalanced, so the main paper conclusions should rely on the larger FPT dataset and the direct comparison with Mamba.

## Citation

Citation information will be added after the paper title, author list, and venue are finalized.
