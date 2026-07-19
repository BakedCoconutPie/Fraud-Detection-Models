"""Validate that the Mamba notebook uses the current dataset roles.

The notebook is maintained directly. This helper remains only as a quick
guard against accidentally restoring the legacy data flow.
"""

import json
from pathlib import Path


NOTEBOOK = Path("notebooks") / "mamba_colab.ipynb"


with NOTEBOOK.open(encoding="utf8") as handle:
    notebook = json.load(handle)

source = "\n".join(
    "".join(cell.get("source", [])) for cell in notebook.get("cells", [])
)
required = ["tasktracker", "pastetrace", "src.models.mamba_model test"]

missing = [token for token in required if token not in source]
if missing:
    raise SystemExit(f"Notebook validation failed: missing={missing}")

print("Notebook OK: TaskTracker=train, PasteTrace=external test.")
