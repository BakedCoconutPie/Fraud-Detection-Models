# PasteTrace – Fraud Detection System: Source Code Guide

Hệ thống phân tích gian lận học thuật sử dụng dữ liệu keystroke từ môi trường lập trình PasteTrace.

---

## Hai chế độ hoạt động

Đây là điểm quan trọng nhất để hiểu hệ thống:

```
CHEER MODE — có nhãn giảng viên (agrigation.csv)
  Folder mới          Code (.pde) + History (meta.json) + Nhãn (X / "")
        ↓                                  ↓
  build_dataset.py → dataset.csv (label = 0 hoặc 1)
        ↓
  features.py + codebert_embed.py   (extract features + embeddings)
        ↓
  fusion_model.py → LOO evaluation → LƯU model vào models/fusion_xgb.pkl


PREDICT MODE — sinh viên mới, KHÔNG cần nhãn
  Folder mới          Code (.pde) + History (meta.json)   ← CHỈ CẦN 2 thứ này
        ↓
  build_dataset.py → dataset.csv (label = -1, unknown)
        ↓
  features.py + codebert_embed.py   (extract giống hệt trên)
        ↓
  fusion_model.py → TẢI model từ models/fusion_xgb.pkl → Dự đoán % gian lận
```

**agrigation.csv chỉ dùng cho chế độ TRAIN** — khi muốn xây dựng hoặc cải thiện model. Khi kiểm tra sinh viên mới, KHÔNG cần nhãn. Model đã học từ dữ liệu lịch sử sẽ tự đưa ra dự đoán.

---

## Kiến trúc tổng quan

```
PasteTrace data (meta.json + .pde code)
         │
         ├─── NHÁNH CODE-TEXT ──────────────────────────────┐
         │     build_dataset.py  → data/dataset.csv          │
         │     svm_model.py      (TF-IDF + SVM, LOO)         │
         │     codebert_embed.py → data/embeddings.npy       │
         │                                                    │
         └─── NHÁNH BEHAVIORAL ─────────────────────────────┤
               features.py        → data/features.csv        │
               behavioral_model.py (LR, DT, Rule, LOO)       │
                                                              │
               FUSION: embeddings.npy [768] + features [10]  │
               fusion_model.py → XGBoost → models/fusion_xgb.pkl
                                                              │
         streamlit_app.py  (Dashboard) ◄──────────────────────┘
```

- **17 sinh viên lịch sử** (15 cheat / 2 normal) làm training data.
- Tất cả đánh giá LOO dùng Leave-One-Out vì dataset nhỏ.
- Nhãn từ `agrigation.csv`: `X`→1 (cheat), `""`→0 (normal), `?`/`*`→bỏ.

---

## Dữ liệu PasteTrace

### Cấu trúc thư mục

```
pre-processed/
  111/
    agrigation.csv        ← nhãn giảng viên (chỉ cần khi TRAIN)
    A/
      meta.json           ← keystroke history
      sketch_A/code.pde   ← source code Processing
    B/  (không có meta.json → bị loại)
  211/
    agrigation.csv
    O/
      BouncingBall/meta.json            ← student O có 2 project
      Student_Fractal_Assignment/meta.json
```

**Folder mới (PREDICT mode) — không cần agrigation.csv:**
```
new_semester/
  101/                    ← case folder (không cần agrigation.csv)
    StudentA/
      meta.json
      sketch/code.pde
    StudentB/
      meta.json
      sketch/code.pde
```

### meta.json – History events

| Field | Ý nghĩa |
|-------|---------|
| `L="T"` | Typed — gõ bàn phím |
| `L="P"` | Pasted — Ctrl+V |
| `L="C"` | Copied — Ctrl+C |
| `E` | Nội dung text |
| `N` | (chỉ paste) nguồn gốc |

**External paste** = `L="P"` mà `N` KHÔNG chứa `"paste from project"` → code từ ngoài hệ thống (web, ChatGPT) → tín hiệu gian lận mạnh nhất.

---

## src/data/build_dataset.py

Đọc folder data, tạo `data/dataset.csv`.

**Hai chế độ tự động:**
- Nếu tìm thấy `agrigation.csv` → TRAIN mode, label = 0/1
- Nếu KHÔNG có `agrigation.csv` → PREDICT mode, label = -1 (unknown)

```python
# Auto-detect: có label → TRAIN, không có → PREDICT
labeled_cases = [d for d in subdirs if "agrigation.csv" in case_dir/d]
cases  = labeled_cases if labeled_cases else all_subdirs
# Không có nhãn:
labels = scan_students(case_dir)  # → {student: -1}
```

**Hàm chính:**
- `load_labels(case_dir)` — đọc agrigation.csv → {student: 0/1}
- `scan_students(case_dir)` — scan tất cả subdir → {student: -1}
- `collect_code(student_dir)` — os.walk tìm .pde files
- `find_meta_jsons(student_dir)` — os.walk tìm meta.json
- `extract_behavioral_features(meta_paths)` — 7 chỉ số từ events

**CLI:**
```bash
python -m src.data.build_dataset
python -m src.data.build_dataset --root /path/to/new_semester
```

---

## src/ml/features.py

Extract **10 behavioral features** từ meta.json → `data/features.csv`.

| Feature | Ý nghĩa |
|---------|---------|
| `total_events` | Tổng số events |
| `type_count` | Số keystroke |
| `paste_count` | Số lần paste |
| `paste_ratio` | paste / total |
| `max_paste_length` | Paste lớn nhất (ký tự) |
| `external_paste` | Số external paste |
| `ext_paste_ratio` | external / total paste |
| `pasted_char_frac` | Ký tự paste / tổng |
| `ext_char_frac` | Ký tự ngoài / tổng **(signal mạnh nhất)** |
| `typed_chars` | Tổng ký tự gõ |

**CLI:**
```bash
python -m src.ml.features
python -m src.ml.features --root /path/to/new_semester
```

---

## src/ml/codebert_embed.py

Mã hóa code Processing (.pde) thành vector 768 chiều — **frozen** (không fine-tune).

### Tại sao frozen?
- 17 mẫu quá ít để fine-tune → overfitting
- CodeBERT đã pre-train trên code GitHub bao gồm Java (Processing-based)
- Dùng như feature extractor: code → vector 768 dims

### Xử lý code dài (> 512 tokens)
```
Tokens: [t1..t800]
Window 1: [CLS] t1..t510 [SEP]  → CLS vec 1
Window 2: [CLS] t255..t765 [SEP] → CLS vec 2  (stride=256)
Window 3: [CLS] t511..t800 [SEP] → CLS vec 3
Final = mean(CLS vec 1, 2, 3)  → [768]
```

**Output:** `data/embeddings.npy` [n, 768] + `data/embeddings_index.csv`

**CLI:**
```bash
python -m src.ml.codebert_embed
# Lần đầu tải ~500MB từ HuggingFace | CPU: 5-15 phút
```

---

## src/ml/fusion_model.py

Kết hợp CodeBERT [768] + behavioral [10] = **778 chiều** → XGBoost.

### Hai chế độ trong main()

```python
inference_mode = (y == -1).any()  # label=-1 → không có nhãn

if inference_mode:
    # Tải model đã lưu, chỉ predict
    saved = joblib.load("models/fusion_xgb.pkl")
    scores = saved["clf"].predict_proba(X_sc)[:, 1]
else:
    # LOO evaluation + train + lưu model
    _loo_xgb(X, y)  # LOO metrics
    _train_and_save(X, y)  # → models/fusion_xgb.pkl
```

### LOO Evaluation (chỉ khi có nhãn)
- 3 model: XGBoost (chính), SVM-RBF, MLP
- XGBoost dùng `sample_weight` để cân bằng class imbalance (15:2)
- StandardScaler fit lại từng fold (tránh data leakage)

### Lưu/tải model
```
models/fusion_xgb.pkl  ←  {"clf": XGBClassifier, "scaler": StandardScaler}
```
Model chỉ được lưu sau khi train trên dữ liệu có nhãn. Khi predict trên dữ liệu mới, file này được tải lại mà không cần train lại.

**CLI:**
```bash
python -m src.ml.fusion_model
# Tự phát hiện TRAIN hoặc PREDICT mode dựa trên dataset.csv
```

---

## src/models/svm_model.py

TF-IDF + SVM baseline cho nhánh code-text.

```
code (str) → TfidfVectorizer(5000 features) → SVC(kernel="linear", balanced)
```

LOO results điển hình: recall_normal = 0 (= majority baseline). TF-IDF không đủ signal với 17 mẫu và class imbalance 15:2.

**Output:** `models/svm/svm.pkl` + `models/svm/vectorizer.pkl`

---

## src/models/behavioral_model.py

3 phương pháp LOO trên 10 behavioral features:

| Model | Đặc điểm |
|-------|---------|
| Logistic Regression | `class_weight="balanced"` + StandardScaler |
| Decision Tree | `max_depth=3` tránh overfit |
| Threshold Rule | Tìm ngưỡng tốt nhất trên `ext_char_frac` mỗi fold |

LR thường cho `recall_normal > 0` — tốt hơn SVM baseline.

---

## src/models/baseline_model.py

Luôn dự đoán nhãn đa số (cheat=1). Kết quả: accuracy=0.882, recall_normal=0.

Đây là ngưỡng tối thiểu — model hữu ích phải vượt qua AND có `recall_normal > 0`.

---

## src/ui/streamlit_app.py

Dashboard giáo viên, hỗ trợ cả TRAIN và PREDICT mode.

### Chạy
```bash
streamlit run src/ui/streamlit_app.py
```

### Sidebar – Chọn folder

**Nút "📁 Chọn folder"** mở hộp thoại native (tkinter) để chọn thư mục — không cần nhập tay đường dẫn.

Sau khi chọn, hệ thống tự nhận diện:
- **TRAIN** (có agrigation.csv) → hiển thị màu xanh
- **PREDICT** (không có nhãn) → hiển thị màu cam, cần model đã lưu

### Pipeline Steps

| Bước | Module | Output |
|------|--------|--------|
| 1 · Build Dataset | `src.data.build_dataset` | `data/dataset.csv` |
| 2 · Extract Features | `src.ml.features` | `data/features.csv` |
| 3 · CodeBERT Embeddings | `src.ml.codebert_embed` | `data/embeddings.npy` |
| 4 · Fusion (XGBoost) | `src.ml.fusion_model` | `models/fusion_xgb.pkl` (train) hoặc Risk Report (predict) |

### Tab Risk Report

- Chế độ TRAIN: Dùng XGBoost train tươi trên data hiện tại
- Chế độ PREDICT: Tải `models/fusion_xgb.pkl` → predict → không cần nhãn
- Màu card: **Đỏ** = dự đoán CHEAT, **Xanh** = dự đoán normal
- Hiển thị nhãn thực (✓/✗) chỉ khi có agrigation.csv

---

## Quy trình chạy

### Lần đầu — Train model trên 17 students lịch sử
```bash
# Bước 1-4: chọn folder pre-processed trong UI và chạy từng bước
python -m src.data.build_dataset    # TRAIN mode
python -m src.ml.features
python -m src.ml.codebert_embed     # ~500MB download lần đầu
python -m src.ml.fusion_model       # → lưu models/fusion_xgb.pkl
```

### Khoá học mới — Predict KHÔNG cần nhãn
```bash
# Folder new_semester/ chỉ cần: case/student/meta.json + case/student/sketch/code.pde
# KHÔNG cần agrigation.csv
python -m src.data.build_dataset --root /path/to/new_semester  # PREDICT mode, label=-1
python -m src.ml.features         --root /path/to/new_semester
python -m src.ml.codebert_embed   # embed code mới
python -m src.ml.fusion_model     # load model → dự đoán
```

Hoặc dùng UI: chọn folder mới → hệ thống nhận diện PREDICT mode → chạy bước 1→4.

### Mamba data flow

Mamba chỉ dùng 470 session TaskTracker. Input chuẩn là
`data/normalized/tasktracker/` (có legacy fallback `tasktracker/normalized/`).
Các session được build vào `data/mamba/sequences/`, sau đó chia theo participant
group thành 70% train, 15% validation và 15% held-out test. Scaler chỉ fit train;
checkpoint và threshold chỉ chọn trên validation.

```bash
python -m src.data.build_sequences --min-events 1
python -m src.data.make_splits  # validate fixed group CSVs; khong tao split moi
python -m src.models.mamba_model train --epochs 80 --patience 10 --seed 42
python -m src.models.mamba_model test
```

Output so sánh chuẩn nằm tại `results/mamba/predictions.csv` và
`results/mamba/metrics.json`. Nhãn TaskTracker là weak behavioral-risk label,
không phải bằng chứng gian lận đã xác nhận.

---

## So sánh models (LOO, n=17 labeled students)

| Model | Branch | Recall(cheat) | Recall(normal) | F1 |
|-------|--------|---------------|----------------|----|
| Majority Baseline | — | 1.000 | 0.000 | 0.938 |
| SVM (TF-IDF) | Code-text | 1.000 | 0.000 | 0.938 |
| LR (behavioral) | Behavioral | ~1.000 | ~0.500 | ~0.960 |
| XGBoost Fusion | Both | 0.867 | 0.000 | 0.867 |

`recall_normal` là chỉ số khó nhất — chỉ 2 mẫu normal trong 17. XGBoost fusion cho điểm risk tốt hơn (93% cho cheat, 7% cho normal khi train full) dù LOO recall_normal vẫn 0 do quá ít mẫu.

---

## FAQ

**Q: Để dùng inference mode, tôi làm gì?**
A: Xóa agrigation.csv khỏi thư mục dữ liệu (hoặc dùng folder không có file đó). Pipeline tự nhận PREDICT mode và load model từ `models/fusion_xgb.pkl`.

**Q: Tại sao 111/B bị loại?**
A: Không có meta.json → không extract được behavioral features → loại để đảm bảo cả 2 nhánh so sánh trên 17 mẫu giống nhau.

**Q: CodeBERT có hiểu Processing code không?**
A: Processing là Java-based. CodeBERT được train trên Java. Dùng frozen (không fine-tune) là đủ vì chúng ta chỉ cần feature extraction, không cần domain adaptation.

**Q: External paste vs internal paste?**
A: Internal (N chứa "paste from project") = copy từ project trong PasteTrace, ít nghi ngờ. External (N không chứa chuỗi đó) = code từ web/ChatGPT/file ngoài → tín hiệu gian lận chính.

**Q: Tại sao dùng sample_weight thay vì scale_pos_weight?**
A: `scale_pos_weight` là fixed global weight. `sample_weight` cho phép tính weight khác nhau mỗi LOO fold (16 samples mỗi fold, tỉ lệ class thay đổi). Tránh trường hợp XGBoost cho kết quả 0.000 do parameter incompatibility với XGBoost 2.x.
