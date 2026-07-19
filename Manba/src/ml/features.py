"""Phase 5 — Feature Engineering

Extract behavioral keystroke features from meta.json History events for
every student in the dataset.  Output is a wide-format CSV (one row per
student) ready for the fusion model, plus a human-readable per-student
long-format table on stdout.

Usage:
    python -m src.ml.features

Input:
    dataset.csv  (needs columns: case, student, label)
    PasteTrace meta.json files found next to each student's submission

Output:
    data/features.csv  — ML-ready wide format
"""

import csv
import json
import os

import pandas as pd

DATASET_PATH = os.path.join("data", "dataset.csv")
OUTPUT_PATH = os.path.join("data", "features.csv")

CASE_STUDY_ROOT = os.path.join(
    "PasteTrace-release", "PasteTrace-release", "case studies", "sp2023", "pre-processed"
)

FEATURE_COLS = [
    "total_events",
    "type_count",
    "paste_count",
    "paste_ratio",
    "max_paste_length",
    "external_paste",
    "ext_paste_ratio",
    "pasted_char_frac",
    "ext_char_frac",
    "typed_chars",
]


def find_meta_jsons(student_dir: str) -> list[str]:
    """Return all meta.json paths found recursively under a student directory."""
    paths = []
    for root, _dirs, files in os.walk(student_dir):
        for name in files:
            if name == "meta.json":
                paths.append(os.path.join(root, name))
    return paths


def extract_features(meta_paths: list[str]) -> dict:
    """Compute 10 behavioral features from one or more meta.json History arrays.

    External paste = paste event whose N note does not mention
    'paste from project', meaning the content came from outside the
    PasteTrace-tracked ecosystem (web, ChatGPT, another IDE, etc.).
    Multiple meta.json files (e.g. student 211/O) are pooled together.

    Feature reference
    -----------------
    total_events      : total History events of any type
    type_count        : events where L="T"  (keyboard strokes / backspaces)
    paste_count       : events where L="P"  (Ctrl-V pastes)
    paste_ratio       : paste_count / total_events
    max_paste_length  : char length of the single largest paste (0 if none)
    external_paste    : paste events with N missing or N has no 'paste from project'
    ext_paste_ratio   : external_paste / max(paste_count, 1)
    pasted_char_frac  : pasted chars / total chars  (how much code came from paste)
    ext_char_frac     : external-pasted chars / total chars  (strongest single signal)
    typed_chars       : total chars typed (raw len of T event E strings)
    """
    all_events: list[dict] = []
    for path in meta_paths:
        try:
            with open(path, encoding="utf8", errors="ignore") as f:
                data = json.load(f)
            all_events.extend(data.get("History", []))
        except Exception:
            pass

    type_events  = [e for e in all_events if e.get("L") == "T"]
    paste_events = [e for e in all_events if e.get("L") == "P"]

    typed_chars   = sum(len(e.get("E", "")) for e in type_events)
    paste_sizes   = [len(e.get("E", "")) for e in paste_events]
    pasted_chars  = sum(paste_sizes)
    total_chars   = max(typed_chars + pasted_chars, 1)
    total_events  = len(all_events)
    paste_count   = len(paste_events)

    def _is_external(event: dict) -> bool:
        n = (event.get("N") or "").lower()
        return "paste from project" not in n

    ext_events = [e for e in paste_events if _is_external(e)]
    ext_chars  = sum(len(e.get("E", "")) for e in ext_events)

    return {
        "total_events":     total_events,
        "type_count":       len(type_events),
        "paste_count":      paste_count,
        "paste_ratio":      round(paste_count / max(total_events, 1), 6),
        "max_paste_length": max(paste_sizes) if paste_sizes else 0,
        "external_paste":   len(ext_events),
        "ext_paste_ratio":  round(len(ext_events) / max(paste_count, 1), 6),
        "pasted_char_frac": round(pasted_chars / total_chars, 6),
        "ext_char_frac":    round(ext_chars / total_chars, 6),
        "typed_chars":      typed_chars,
    }


def _long_format(student_id: str, label: int, feats: dict) -> str:
    """Return a per-student long-format display block."""
    lines = [
        f"\n  Student: {student_id}  |  label: {'CHEAT' if label == 1 else 'normal'}",
        f"  {'feature':<22} {'value':>12}",
        f"  {'-'*36}",
    ]
    for col in FEATURE_COLS:
        v = feats[col]
        lines.append(f"  {col:<22} {v:>12}")
    return "\n".join(lines)


def build_features(df: pd.DataFrame, data_root: str = CASE_STUDY_ROOT) -> pd.DataFrame:
    """Return wide-format feature DataFrame aligned with df rows."""
    records = []
    for _, row in df.iterrows():
        case, student = str(row["case"]), str(row["student"])
        student_dir = os.path.join(data_root, case, student)
        meta_paths = find_meta_jsons(student_dir)
        feats = extract_features(meta_paths) if meta_paths else {c: 0 for c in FEATURE_COLS}
        records.append({"case": case, "student": student, "label": int(row["label"]), **feats})
    return pd.DataFrame(records)


def main():
    import argparse
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--root",   default=None, help="Path to pre-processed case study root")
    parser.add_argument("--output", default=None, help="Output path for features.csv")
    known, _ = parser.parse_known_args()

    data_root   = known.root   or CASE_STUDY_ROOT
    output_path = known.output or OUTPUT_PATH

    df = pd.read_csv(DATASET_PATH, usecols=["case", "student", "label"])
    feat_df = build_features(df, data_root=data_root)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    feat_df.to_csv(output_path, index=False)
    print(f"Saved {len(feat_df)} rows to {output_path}")

    print("\n" + "=" * 50)
    print("  Per-student feature report")
    print("=" * 50)
    for _, row in feat_df.iterrows():
        sid = f"{row['case']}/{row['student']}"
        feats = {c: row[c] for c in FEATURE_COLS}
        print(_long_format(sid, int(row["label"]), feats))


if __name__ == "__main__":
    main()
