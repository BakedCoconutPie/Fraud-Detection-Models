# PasteTrace – Fraud Detection System

He thong phat hien gian lan hoc thuat tu du lieu keystroke cua moi truong lap trinh **PasteTrace**.
Ket hop hai nhanh: phan tich **code text** (CodeBERT) va phan tich **hanh vi go phim** (behavioral features) → XGBoost Fusion.

---

## Mamba: TaskTracker-only, fixed group split

Nhanh Mamba chi dung 470 session TaskTracker. PasteTrace khong con la input train,
validation hay test cua Mamba. Input chuan la `data/normalized/tasktracker/`;
`tasktracker/normalized/` cu van duoc ho tro de tranh phai copy du lieu.

- `data/splits/tasktracker/train.csv`: fit scaler va train weights.
- `data/splits/tasktracker/validation.csv`: chon checkpoint va threshold.
- `data/splits/tasktracker/test.csv`: danh gia cuoi cung mot lan.
- Cac session co cung participant/group id luon nam trong cung mot split.
- Hop dong bat buoc: train `333 sessions/191 groups`, validation
  `68 sessions/37 groups`, test `69 sessions/43 groups`; test gom 15 risk va
  54 normal.
- Nhan TaskTracker la weak behavioral-risk label, khong phai bang chung cheating.

Chay CLI:

```bash
python -m src.data.build_sequences --min-events 1
python -m src.data.make_splits  # chi validate 3 CSV co dinh, khong tao split
python -m src.models.mamba_model train --epochs 80 --patience 10 --lr 3e-4 --batch-size 8 --seed 42
python -m src.models.mamba_model test
```

Model input chi gom 7 feature co o ca hai dataset: `is_type`, `is_paste`,
`is_cut`, `log_len`, `paste_log_len`, `is_large_paste`, `log_delta_time`.
Model dung masked mean+max pooling de khong lam mat cac cu paste lon, hiem.
`risk_score` la sigmoid decision score trong [0,1], khong duoc mo ta la xac suat
cheating da calibration. Threshold duoc chon bang validation de toi da positive F1,
sau do dong bang khi test.

Output:

```text
data/mamba/sequences/                          # 470 TaskTracker sequences
data/mamba/index.csv                           # session/label/group index
data/splits/tasktracker/train.csv              # shared split
data/splits/tasktracker/validation.csv
data/splits/tasktracker/test.csv
models/mamba/mamba.pt
models/mamba/config.json                       # threshold + architecture
results/mamba/predictions.csv                  # common comparison schema
results/mamba/metrics.json                     # common comparison metrics
results/mamba/validation_predictions.csv       # Mamba threshold audit
results/mamba/training_history.csv              # loss/F1 per epoch
results/mamba/method.json                       # package + methodology + hardware
results/mamba/splits/train.csv                  # exact split copies actually read
results/mamba/splits/validation.csv
results/mamba/splits/test.csv
```

Dashboard rieng cho Mamba:

```bash
streamlit run src/ui/mamba_app.py
```

Notebook GPU: `notebooks/mamba_colab.ipynb`.

Bon cot dau cua `predictions.csv` la `session_id,true_label,risk_score,pred_label`.
`metrics.json` co cac field so sanh chung: precision, recall, f1, auc, pr_auc,
balanced_accuracy, specificity, TP/TN/FP/FN, runtime va model size. Cac field Mamba
bo sung duoc mo ta day du trong `MAMBA_IO.md`.

---

## Yeu cau he thong

| | |
|---|---|
| Python | **3.10** (khuyen nghi, da test) |
| RAM | Toi thieu 8 GB (CodeBERT can ~2 GB khi chay) |
| Disk | ~3 GB (model CodeBERT ~500 MB + venv) |
| Internet | Chi can mot lan dau de tai CodeBERT |
| OS | Windows 10/11, macOS, Linux |

---

## Cai dat sau khi clone tu GitHub

### Buoc 1 — Clone repo

```bash
git clone https://github.com/<your-username>/FraudDetection3Model.git
cd FraudDetection3Model
```

### Buoc 2 — Tao virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Buoc 3 — Cai dependencies

```bash
pip install -r requirements.txt
```

> **Luu y:** PyTorch CPU-only (~250 MB). Neu co GPU NVIDIA, thay dong dau trong `requirements.txt`:
> ```
> --extra-index-url https://download.pytorch.org/whl/cu121
> ```

### Buoc 4 — Cau hinh Streamlit (chi lam 1 lan)

```bash
# Windows
mkdir %USERPROFILE%\.streamlit
echo [general] > %USERPROFILE%\.streamlit\credentials.toml
echo email = "" >> %USERPROFILE%\.streamlit\credentials.toml

# macOS / Linux
mkdir -p ~/.streamlit
printf '[general]\nemail = ""\n' > ~/.streamlit/credentials.toml
```

### Buoc 5 — Dat du lieu PasteTrace

Dam bao thu muc `PasteTrace-release/` co cau truc:

```
PasteTrace-release/
  PasteTrace-release/
    case studies/
      sp2023/
        pre-processed/
          111/
            agrigation.csv
            A/ B/ C/ ...
          211/
            agrigation.csv
            A/ B/ C/ ...
```

---

## Chay ung dung

### Cach 1 — Dashboard UI (khuyen nghi)

```bash
streamlit run src/ui/streamlit_app.py
```

Mo trinh duyet tai **http://localhost:8501**

Trong UI:
1. Nhan **Chon folder** → chon thu muc `pre-processed`
2. Chay lan luot cac buoc **1 → 2 → 3 → 4** o sidebar

### Cach 2 — CLI

```bash
python -m src.data.build_dataset
python -m src.ml.features
python -m src.ml.codebert_embed
python -m src.ml.fusion_model
```

---

## Thu tu chay cho tung truong hop

### Lan dau tien (train model)

Chay du 4 buoc. Buoc 3 se tai ~500 MB CodeBERT model (chi mot lan).

```
Buoc 1  →  Buoc 2  →  Buoc 3 (tai 500 MB)  →  Buoc 4
                                                    ↓
                                         Luu model: models/fusion_xgb.pkl
```

### Hom sau — co folder sinh vien moi

> Cau hoi thuong gap: "Co can chay lai buoc 3 khong? Co ton them 500 MB khong?"

**Tra loi: Can chay lai buoc 3, NHUNG KHONG tai lai 500 MB.**

- Model CodeBERT da duoc luu vao cache may tinh sau lan dau
- Lan sau buoc 3 chi doc tu cache (khong can internet) va embed code moi
- Thoi gian buoc 3 lan sau: ~1–3 phut tuy so luong sinh vien

```
Folder sinh vien moi
  |
  Buoc 1  →  dataset.csv moi (code + meta.json moi)
  Buoc 2  →  features.csv moi
  Buoc 3  →  embeddings.npy moi  <-- PHAI CHAY, nhung load tu cache, KHONG tai 500 MB
  Buoc 4  →  Doc embeddings.npy moi → predict → Risk Report
```

**Tai sao phai chay buoc 3?**
Buoc 3 doc file `data/dataset.csv` (vua duoc tao o buoc 1 voi sinh vien moi) va tao ra
`data/embeddings.npy` chua vector dai dien code cua TUNG sinh vien moi do.
Neu bo qua buoc 3, buoc 4 se doc embeddings.npy cu cua cohort truoc → ket qua sai.

**Tom tat: Can chay ca 4 buoc cho moi cohort moi. Chi co buoc 3 LAN DAU la ton 500 MB.**

---

## Giai thich Pipeline — 4 buoc

### Buoc 1 · Build Dataset

```
Folder PasteTrace  →  data/dataset.csv
```

Doc toan bo sinh vien trong folder, voi moi sinh vien:
- Lay **nhan** tu `agrigation.csv` (X=gian lan, ""=binh thuong)
- Doc toan bo file `.pde` (source code Processing)
- Doc `meta.json` de lay behavioral features

**Tu dong nhan biet che do:**

| Truong hop | Mode | Ghi chu |
|------------|------|---------|
| Folder co `agrigation.csv` | **TRAIN** | Co nhan giao vien → train + luu model |
| Folder KHONG co `agrigation.csv` | **PREDICT** | Sinh vien moi → load model → du doan |

---

### Buoc 2 · Extract Features

```
meta.json  →  data/features.csv  (10 behavioral features)
```

| Feature | Y nghia |
|---------|---------|
| `ext_char_frac` | **Tin hieu manh nhat** — % ky tu tu paste ben ngoai (web, ChatGPT...) |
| `pasted_char_frac` | % ky tu duoc paste (ke ca paste noi bo) |
| `external_paste` | So lan paste tu nguon ngoai |
| `paste_ratio` | Paste / tong keystroke |
| `max_paste_length` | Do dai cu paste lon nhat |

**External paste** = Ctrl+V ma ghi chu N KHONG chua "paste from project"
→ code den tu ngoai he thong PasteTrace (web, ChatGPT, file ngoai...).

---

### Buoc 3 · CodeBERT Embeddings

```
code (.pde)  →  data/embeddings.npy  [n_students × 768]
```

#### Tai sao lan dau tai 500 MB?

`microsoft/codebert-base` la mo hinh AI lon (125 trieu tham so) duoc Microsoft
pre-train tren hang trieu dong code GitHub.

**File duoc luu vao cache sau khi tai:**
```
Windows:   C:\Users\<ten>\\.cache\huggingface\hub\models--microsoft--codebert-base\
macOS/Linux: ~/.cache/huggingface/hub/models--microsoft--codebert-base/
```

**Cac lan sau: Load tu cache, khong can internet, mat 30 giay - 2 phut.**

#### Model dung nhu the nao?

Model duoc dung **dong lanh (frozen)** — KHONG fine-tune, chi trich xuat dac trung:

```
Code Processing → Token IDs → CodeBERT (frozen) → Vector 768 chieu
```

Tai sao khong fine-tune? Chi co 17 mau → fine-tune se bi overfitting.

**Code dai hon 512 token** (gioi han cua CodeBERT):
```
[t1..t800] → Window 1: [CLS] t1..t510 [SEP]  → vec 1
           → Window 2: [CLS] t255..t765 [SEP] → vec 2  (overlap 50%)
           → Window 3: [CLS] t511..t800 [SEP] → vec 3
           → Final = trung binh(vec1, vec2, vec3)  [768 dims]
```

**Khi nao chay lai buoc 3?**

| Tinh huong | Can chay lai? | Tai lai 500 MB? |
|------------|--------------|-----------------|
| Lan dau tien | Co | Co (mot lan duy nhat) |
| Cohort moi (sinh vien moi) | Co | Khong (load cache) |
| Chi thay doi model/features | Khong | Khong |
| Cung cohort, khong co gi thay doi | Khong | Khong |

---

### Buoc 4 · Fusion Model (XGBoost)

```
embeddings.npy [n×768]  +  features.csv [n×10]
       =  fused vector [n×778]
              ↓
         XGBoost Classifier
```

#### Tai sao ket hop 2 nguon?

| Nguon | Thong tin |
|-------|-----------|
| CodeBERT [768] | Ngu nghia code — code nay "trong giong" code gian lan khong? |
| Behavioral [10] | Hanh vi — sinh vien nay co paste nhieu tu ngoai khong? |

Ket hop ca hai cho ket qua toan dien hon: code co the bi chinh sua nhe de qua kiem tra,
nhung hanh vi keystroke kho gia mao hon.

#### Hai che do buoc 4:

**TRAIN mode** (folder co `agrigation.csv`):
```
1. LOO Evaluation (17 folds, train 16, test 1)
   → In metrics: accuracy, precision, recall(cheat), recall(normal), F1
2. Train final model tren TOAN BO data
3. LUU model → models/fusion_xgb.pkl
4. In Risk Report
```

**PREDICT mode** (folder KHONG co `agrigation.csv`):
```
1. TAI model tu models/fusion_xgb.pkl
2. Du doan xac suat gian lan cho tung sinh vien moi
3. In Risk Report — % gian lan, ly do
   (khong co nhan thuc de so sanh)
```

---

## Cau truc thu muc

```
FraudDetection3Model/
├── src/
│   ├── data/
│   │   └── build_dataset.py     # Buoc 1
│   ├── ml/
│   │   ├── features.py          # Buoc 2
│   │   ├── codebert_embed.py    # Buoc 3
│   │   └── fusion_model.py      # Buoc 4
│   ├── models/
│   │   ├── baseline_model.py
│   │   ├── svm_model.py
│   │   └── behavioral_model.py
│   └── ui/
│       └── streamlit_app.py     # Dashboard
├── data/                        # Output (auto-generated)
│   ├── dataset.csv
│   ├── features.csv
│   ├── embeddings.npy
│   └── embeddings_index.csv
├── models/                      # Trained models (auto-generated)
│   ├── fusion_xgb.pkl           # XGBoost saved model
│   └── svm/
├── tasktracker/                 # Legacy normalized TaskTracker layout
├── data/splits/tasktracker/     # Shared Mamba train/validation/test IDs
├── requirements.txt
├── guide.md                     # Giai thich chi tiet source code
└── README.md
```

---

## Xu ly loi thuong gap

### `No module named 'xgboost'`
```bash
pip install xgboost
```

### Streamlit hoi email
```bash
mkdir %USERPROFILE%\.streamlit
echo [general] > %USERPROFILE%\.streamlit\credentials.toml
echo email = "" >> %USERPROFILE%\.streamlit\credentials.toml
```

### `No saved model found` khi chay PREDICT mode
Phai train model truoc tren du lieu co nhan:
```bash
python -m src.data.build_dataset    # folder co agrigation.csv
python -m src.ml.features
python -m src.ml.codebert_embed
python -m src.ml.fusion_model       # → tao models/fusion_xgb.pkl
```

### CodeBERT chay cham
```bash
# Kiem tra GPU
python -c "import torch; print(torch.cuda.is_available())"
# True → tu dong dung GPU | False → CPU (cham hon ~5-10x)
```

---

## Thong tin ky thuat

| Component | Chi tiet |
|-----------|---------|
| Python | 3.10+ |
| PyTorch | 2.x (CPU build) |
| Transformers | 5.x (HuggingFace) |
| XGBoost | 3.x |
| Streamlit | 1.58+ |
| CodeBERT | microsoft/codebert-base (RoBERTa-based, 125M params) |
| Dataset | 17 students, 15 cheat / 2 normal, LOO evaluation |
| Feature vector | 778 dims (768 CodeBERT + 10 behavioral) |
