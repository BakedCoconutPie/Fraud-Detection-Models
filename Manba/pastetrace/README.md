# PasteTrace Normalized Dataset

Day la ban PasteTrace da chuan hoa, dung truc tiep cho pipeline IF + XGBoost + SHAP
va exporter sequence cho Mamba.

## Folder nay co gi?

```text
pastetrace/
|-- README.md
|-- SCHEMA.md
|-- inventory.xlsx
`-- normalized/
    |-- labels.csv
    |-- 111_A.json
    |-- 111_B.json
    |-- ...
    `-- 211_Q.json
```

Trong do:

- `normalized/*.json`: moi file la mot programming session da dua ve event schema chung.
- `normalized/labels.csv`: nhan cua tung session.
- `SCHEMA.md`: mo ta format JSON va labels.
- `inventory.xlsx`: ghi chu cac session goc, session nao dung duoc, session nao bi loai va ly do.

## 16 hay 19 sessions?

Dataset nay co 19 session normalized.

- `original16`: 16 session goc, loc bang cot `in_original_16 == yes` trong `labels.csv`.
- `all`: toan bo 19 session normalized.

Khi viet paper hoac bao cao ket qua, phai noi ro dang dung `original16` hay `all`.
Hai setting nay co the cho ket qua khac nhau.

## Vi sao chuan hoa nhu vay?

PasteTrace goc co nhieu file va tien xu ly rieng cua tool. Pipeline model can mot
format gon hon:

- moi bai lam = mot session,
- moi session co chuoi event theo thoi gian,
- moi event co `t`, `type`, `text`, `paste_source`,
- nhan tach rieng trong `labels.csv`.

Cach nay giup cung mot model co the doc PasteTrace, TaskTracker va du lieu nop bai
tu tool cua nhom sau nay.

## Cach chay nhanh

IF + XGBoost + SHAP, dung toan bo 19 session:

```powershell
.\.venv\Scripts\python.exe src\pastetrace_if_xgb_shap.py `
  --data data\normalized\pastetrace `
  --subset all `
  --out outputs\pastetrace_all19
```

Chi trich feature cho 16 session goc:

```powershell
.\.venv\Scripts\python.exe src\pastetrace_if_xgb_shap.py `
  --data data\normalized\pastetrace `
  --subset original16 `
  --out outputs\pastetrace_original16_features `
  --features-only
```

Build sequence cho Mamba (TaskTracker train/validation, PasteTrace external test):

```powershell
.\venv\Scripts\python.exe -m src.data.build_sequences `
  --train-dir tasktracker `
  --test-dir pastetrace `
  --min-events 1
```

## Luu y label

`paste_source == "same_machine"` duoc giu rieng. Khong nen tu dong gop vao `own`
hay `external`, vi day la nhom mo ho va can duoc bao cao rieng khi giai thich ket
qua.
