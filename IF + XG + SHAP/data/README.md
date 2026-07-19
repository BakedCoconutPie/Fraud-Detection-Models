# Data Directory

Do not commit raw private data to GitHub.

Recommended local layout:

```text
data/
├── raw/                 # downloaded/reconstructed public data, ignored by git
├── fpt/                 # private FPT IDE logs, ignored by git
├── private/             # sensitive intermediate files, ignored by git
└── sample/              # tiny synthetic examples safe to commit, optional
```

The model code expects a normalized dataset folder:

```text
PasteTrace_Normalized/
└── normalized/
    ├── labels.csv
    ├── 111_A.json
    └── ...
```

`labels.csv` columns:

- `session_id`
- `label`
- `in_original_16`

Each JSON file contains one session with `events`.
