# Normalized Behavioral Data Schema

Each programming session is stored as one JSON file:

```json
{
  "session_id": "111/A",
  "source": "pastetrace_sp2023",
  "events": [
    {
      "t": 0.0,
      "type": "paste",
      "text": "float x = 0;",
      "paste_source": "external"
    }
  ]
}
```

Fields:

- `session_id`: stable session identifier.
- `source`: data source, e.g. `pastetrace_sp2023` or `fpt_ide_2026`.
- `events`: ordered event list.

Event fields:

- `t`: relative timestamp in seconds.
- `type`: one of `type`, `paste`, `cut`, `other`.
- `text`: raw event text.
- `paste_source`: only for paste events; one of `own`, `external`, `same_machine`, `unknown`, or `null`.

Labels are stored separately in `normalized/labels.csv` to reduce accidental label leakage.

```csv
session_id,label,in_original_16
111/A,1,yes
111/E,0,yes
```

Label convention:

- `1`: cheated/risky according to the study label.
- `0`: normal/honest according to the study label.

The final source code should not be used as input for the IF + XGBoost + SHAP pipeline.
