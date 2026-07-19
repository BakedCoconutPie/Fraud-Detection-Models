"""Validate the team's fixed TaskTracker split CSVs without modifying them.

The module name is kept for CLI compatibility. It no longer creates or rewrites
splits because the official session lists are supplied by the research group.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


INDEX_PATH = Path("data") / "mamba" / "index.csv"
SPLIT_DIR = Path("data") / "splits" / "tasktracker"
EXPECTED_SPLITS = {
    "train": {"sessions": 333, "groups": 191},
    "validation": {"sessions": 68, "groups": 37},
    "test": {"sessions": 69, "groups": 43, "risk_1": 15, "normal_0": 54},
}


def _read_rows(path: Path, key: str) -> list[str]:
    with path.open(encoding="utf8", newline="") as handle:
        return [row[key] for row in csv.DictReader(handle) if row.get(key)]


def validate_fixed_splits(index_path: Path, split_dir: Path) -> dict:
    paths = {name: split_dir / f"{name}.csv" for name in ("train", "validation", "test")}
    for path in (index_path, *paths.values()):
        if not path.is_file():
            raise ValueError(f"Missing required file: {path}")

    with index_path.open(encoding="utf8", newline="") as handle:
        index = {row["session_id"]: row for row in csv.DictReader(handle)}
    splits = {name: _read_rows(path, "session_id") for name, path in paths.items()}
    sets = {name: set(values) for name, values in splits.items()}
    if any(len(values) != len(sets[name]) for name, values in splits.items()):
        raise ValueError("Duplicate session_id found inside a split CSV")
    overlap = (
        (sets["train"] & sets["validation"])
        | (sets["train"] & sets["test"])
        | (sets["validation"] & sets["test"])
    )
    if overlap:
        raise ValueError(f"Session leakage across splits: {len(overlap)} session(s)")
    if set().union(*sets.values()) != set(index):
        raise ValueError("Split union must contain every indexed TaskTracker session exactly once")

    group_sets = {
        name: {index[session]["group_id"] for session in sessions}
        for name, sessions in splits.items()
    }
    group_overlap = (
        (group_sets["train"] & group_sets["validation"])
        | (group_sets["train"] & group_sets["test"])
        | (group_sets["validation"] & group_sets["test"])
    )
    if group_overlap:
        raise ValueError(f"Participant/group leakage: {len(group_overlap)} group(s)")

    counts = {}
    for name, sessions in splits.items():
        labels = [int(index[session]["label"]) for session in sessions]
        counts[name] = {
            "sessions": len(sessions),
            "risk_1": labels.count(1),
            "normal_0": labels.count(0),
            "groups": len(group_sets[name]),
        }
    for name, expected in EXPECTED_SPLITS.items():
        actual = {key: counts[name][key] for key in expected}
        if actual != expected:
            raise ValueError(
                f"Official {name} split must be {expected}; found {actual}. "
                "Replace all three CSV files with the files supplied by the group; "
                "do not regenerate them."
            )
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate fixed TaskTracker split CSVs")
    parser.add_argument("--index", default=str(INDEX_PATH))
    parser.add_argument("--split-dir", default=str(SPLIT_DIR))
    args = parser.parse_args()
    try:
        counts = validate_fixed_splits(Path(args.index), Path(args.split_dir))
    except (KeyError, ValueError) as exc:
        raise SystemExit(f"[ERROR] {exc}") from exc
    print(f"Fixed split validation passed: {counts}")
    print("No split file was created or modified.")


if __name__ == "__main__":
    main()
