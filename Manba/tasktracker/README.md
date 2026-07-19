# Normalized TaskTracker Data

Day la ban TaskTracker da convert sang schema hanh vi chung cua project.

Nguon raw:

```text
data/raw/tasktracker/extracted/data_google_drive_anonymized (SIGSCE 2020)/
```

## Noi dung

```text
tasktracker/
|-- normalized/
|   |-- labels.csv
|   `-- <session_id>.json
|-- label_review.csv
`-- skipped_files.csv
```

## File dung de train

Input chuan cua cac model la:

```text
data/normalized/tasktracker/
```

Du an hien van chap nhan `tasktracker/normalized/` nhu legacy fallback cho Mamba.

Trong do:

- Moi file JSON la mot session lap trinh.
- `labels.csv` noi `session_id` voi label.
- `label_review.csv` giup team kiem tra lai weak labels.

## Schema event

Moi JSON co dang:

```json
{
  "session_id": "...",
  "source": "tasktracker_sigcse2021",
  "metadata": {
    "language": "python",
    "task": "pies",
    "weak_label": 0
  },
  "events": [
    {
      "t": 0.0,
      "type": "type",
      "text": "...",
      "paste_source": null
    }
  ]
}
```

## Cach convert

TaskTracker khong co cung format voi PasteTrace, nhung co thong tin tuong duong:

- code snapshots theo thoi gian,
- IDE actions nhu paste, copy, run, debug, delete,
- timestamp,
- test/task status.

Quy tac convert:

- `t`: timestamp tuong doi tinh bang giay.
- `type`: text chen nho tu diff giua 2 snapshot.
- `paste`: action paste ro rang hoac block chen lon/multiline.
- `cut`: text bi xoa trong diff hoac delete/cut action.
- `other`: run/debug/copy/compile actions.
- `paste_source`: TaskTracker khong co nguon paste nen gan `unknown`.

`IdeState Active` bi bo qua vi no la heartbeat moi giay, neu giu lai se lam
`event_count` phinh gia va khong tuong dong voi PasteTrace.

## Y nghia label

TaskTracker khong co nhan cheating that. Label trong folder nay la weak
behavioral-risk label:

- `0`: normal-like trace.
- `1`: risky/paste-like trace.

Khong nen viet trong paper la confirmed cheating. Nen viet la behavioral risk
annotation hoac weak/manual risk label.

## Lenh tai tao output

Trich feature cho IF + XGBoost + SHAP:

```powershell
.\.venv\Scripts\python.exe src\pastetrace_if_xgb_shap.py `
  --data data\normalized\tasktracker `
  --subset all `
  --out outputs\tasktracker_features `
  --features-only
```

Build sequence va shared split cho Mamba (TaskTracker-only):

```powershell
.\venv\Scripts\python.exe -m src.data.build_sequences `
  --input-dir tasktracker `
  --min-events 1
.\venv\Scripts\python.exe -m src.data.make_splits  # chi validate split co dinh
```
