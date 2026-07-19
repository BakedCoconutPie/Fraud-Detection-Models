"""Build Mamba sequences from the normalized TaskTracker dataset only.

Canonical input is ``data/normalized/tasktracker``.  The legacy
``tasktracker/normalized`` layout is accepted so existing data need not be
copied.  Dataset splitting happens later and is shared through CSV files.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
from pathlib import Path


DATA_ROOT = Path("data") / "normalized" / "tasktracker"
LEGACY_DATA_ROOT = Path("tasktracker")
MAMBA_DATA_DIR = Path("data") / "mamba"
SEQUENCE_DIR = MAMBA_DATA_DIR / "sequences"
INDEX_PATH = MAMBA_DATA_DIR / "index.csv"

FEATURE_NAMES = [
    "is_type",
    "is_paste",
    "is_cut",
    "log_len",
    "paste_log_len",
    "is_large_paste",
    "log_delta_time",
]


def _normalized_dir(data_root: str | os.PathLike[str]) -> Path:
    """Return the directory that directly contains labels.csv and JSON files."""
    root = Path(data_root)
    nested = root / "normalized"
    if (nested / "labels.csv").is_file():
        return nested
    if (root / "labels.csv").is_file():
        return root
    raise FileNotFoundError(
        f"Khong tim thay labels.csv trong '{root}' hoac '{nested}'."
    )


def _load_labels(normalized_dir: Path, subset: str = "all") -> dict[str, int]:
    labels: dict[str, int] = {}
    with (normalized_dir / "labels.csv").open(
        encoding="utf8", errors="ignore", newline=""
    ) as handle:
        for row in csv.DictReader(handle):
            session_id = (row.get("session_id") or "").strip()
            raw_label = (row.get("label") or "").strip()
            if not session_id or raw_label not in {"0", "1"}:
                continue
            if subset == "original16" and (
                row.get("in_original_16") or ""
            ).strip().lower() != "yes":
                continue
            labels[session_id] = int(raw_label)
    return labels


def _load_sessions(normalized_dir: Path) -> dict[str, tuple[Path, dict]]:
    sessions: dict[str, tuple[Path, dict]] = {}
    for path in sorted(normalized_dir.glob("*.json")):
        try:
            with path.open(encoding="utf8", errors="ignore") as handle:
                record = json.load(handle)
        except (OSError, json.JSONDecodeError):
            continue
        session_id = str(record.get("session_id") or "").strip()
        if session_id:
            sessions[session_id] = (path, record)
    return sessions


def extract_normalized_sequence(record: dict) -> tuple[list[list[float]], bool]:
    """Convert one normalized session record into seven cross-source features.

    The optional ``label`` field in a JSON record is deliberately ignored. Labels
    are loaded separately from labels.csv by ``build_dataset_sequences``.
    """
    sequence: list[list[float]] = []
    previous_time: float | None = None
    time_available = False

    events = record.get("events")
    if not isinstance(events, list):
        return sequence, time_available

    for event in events:
        if not isinstance(event, dict):
            continue
        event_type = str(event.get("type") or "").strip().lower()
        if event_type not in {"type", "paste", "cut"}:
            continue

        text = event.get("text")
        if not isinstance(text, str):
            text = "" if text is None else str(text)

        try:
            current_time = float(event.get("t"))
            if not math.isfinite(current_time):
                current_time = None
        except (TypeError, ValueError):
            current_time = None

        delta_time = 0.0
        if current_time is not None and previous_time is not None:
            delta_time = max(0.0, current_time - previous_time)
            time_available = True
        if current_time is not None:
            previous_time = current_time

        sequence.append(
            [
                float(event_type == "type"),
                float(event_type == "paste"),
                float(event_type == "cut"),
                math.log1p(len(text)),
                math.log1p(len(text)) if event_type == "paste" else 0.0,
                float(event_type == "paste" and len(text) >= 128),
                math.log1p(delta_time),
            ]
        )

    return sequence, time_available


def summarize_normalized_events(record: dict) -> dict[str, int | float]:
    """Return human-readable aggregates; these are not model input features."""
    summary: dict[str, int | float] = {
        "type_events": 0,
        "paste_events": 0,
        "cut_events": 0,
        "external_paste_events": 0,
        "own_paste_events": 0,
        "same_machine_paste_events": 0,
        "unknown_paste_events": 0,
        "external_pasted_chars": 0,
        "max_external_paste_chars": 0,
        "max_paste_chars": 0,
        "typed_chars": 0,
        "pasted_chars": 0,
        "cut_chars": 0,
        "duration_sec": 0.0,
    }
    timestamps: list[float] = []
    events = record.get("events")
    if not isinstance(events, list):
        return summary

    for event in events:
        if not isinstance(event, dict):
            continue
        event_type = str(event.get("type") or "").strip().lower()
        if event_type not in {"type", "paste", "cut"}:
            continue
        text = event.get("text")
        text_len = len(text) if isinstance(text, str) else 0
        summary[f"{event_type}_events"] += 1
        char_key = {"type": "typed_chars", "paste": "pasted_chars", "cut": "cut_chars"}[event_type]
        summary[char_key] += text_len

        if event_type == "paste":
            summary["max_paste_chars"] = max(summary["max_paste_chars"], text_len)
            source = str(event.get("paste_source") or "").strip().lower()
            source_key = {
                "external": "external_paste_events",
                "own": "own_paste_events",
                "same_machine": "same_machine_paste_events",
            }.get(source, "unknown_paste_events")
            summary[source_key] += 1
            if source == "external":
                summary["external_pasted_chars"] += text_len
                summary["max_external_paste_chars"] = max(
                    summary["max_external_paste_chars"], text_len
                )

        try:
            timestamp = float(event.get("t"))
            if math.isfinite(timestamp):
                timestamps.append(timestamp)
        except (TypeError, ValueError):
            pass

    if timestamps:
        summary["duration_sec"] = max(0.0, max(timestamps) - min(timestamps))
    return summary


def infer_group_id(session_id: str, record: dict) -> str:
    """Return the anonymized participant identity used for grouped splitting.

    TaskTracker session ids repeat ``language`` and ``task`` before the
    participant-specific suffix. The suffix is stable across tasks for the
    same participant in the supplied normalized dataset.
    """
    metadata = record.get("metadata") if isinstance(record.get("metadata"), dict) else {}
    language = str(metadata.get("language") or "").strip()
    task = str(metadata.get("task") or "").strip()
    prefix = f"tasktracker_{language}_{task}_{task}_"
    if language and task and session_id.startswith(prefix):
        suffix = session_id[len(prefix) :]
        if suffix:
            return suffix
    # Safe fallback: a unique group prevents accidental merging of participants.
    return session_id


def build_dataset_sequences(
    data_root: str | os.PathLike[str],
    output_dir: str | os.PathLike[str],
    index_path: str | os.PathLike[str],
    dataset_name: str,
    min_events: int = 1,
    subset: str = "all",
) -> list[dict]:
    """Build one dataset and return its index rows."""
    normalized_dir = _normalized_dir(data_root)
    labels = _load_labels(normalized_dir, subset=subset)
    sessions = _load_sessions(normalized_dir)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    skipped: list[str] = []
    current_files: set[str] = set()

    for session_id, label in sorted(labels.items()):
        loaded = sessions.get(session_id)
        if loaded is None:
            skipped.append(f"{session_id}: khong tim thay JSON")
            continue
        source_path, record = loaded
        sequence, time_available = extract_normalized_sequence(record)
        if len(sequence) < min_events:
            skipped.append(
                f"{session_id}: chi co {len(sequence)} event (< {min_events})"
            )
            continue

        sample_id = session_id
        group_id = infer_group_id(session_id, record)
        output_path = out_dir / f"{sample_id}.json"
        output_record = {
            "id": sample_id,
            "session_id": session_id,
            "dataset": dataset_name,
            "source": record.get("source", dataset_name),
            "group_id": group_id,
            "label": label,
            "n_events": len(sequence),
            "time_available": time_available,
            "feature_names": FEATURE_NAMES,
            "behavior_summary": summarize_normalized_events(record),
            "seq": sequence,
        }
        with output_path.open("w", encoding="utf8") as handle:
            json.dump(output_record, handle, ensure_ascii=False)
        current_files.add(output_path.name)
        rows.append(
            {
                "id": sample_id,
                "session_id": session_id,
                "dataset": dataset_name,
                "group_id": group_id,
                "label": label,
                "n_events": len(sequence),
                "time_available": time_available,
                "path": output_path.as_posix(),
            }
        )

    # Dedicated generated directories are safe to clean after a successful build.
    for old_path in out_dir.glob("*.json"):
        if old_path.name not in current_files:
            old_path.unlink()

    index = Path(index_path)
    index.parent.mkdir(parents=True, exist_ok=True)
    with index.open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "id",
                "session_id",
                "dataset",
                "group_id",
                "label",
                "n_events",
                "time_available",
                "path",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    n_risk = sum(row["label"] == 1 for row in rows)
    n_normal = sum(row["label"] == 0 for row in rows)
    lengths = sorted(row["n_events"] for row in rows)
    print(f"\n[{dataset_name}] {len(rows)} sequences -> {out_dir}")
    print(f"  Weak labels: risk=1: {n_risk}, normal=0: {n_normal}")
    if lengths:
        print(
            f"  Events: min={lengths[0]}, median={lengths[len(lengths) // 2]}, "
            f"max={lengths[-1]}"
        )
    if skipped:
        print(f"  Skipped: {len(skipped)}")
        for reason in skipped[:20]:
            print(f"    - {reason}")
        if len(skipped) > 20:
            print(f"    ... va {len(skipped) - 20} session khac")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build Mamba sequences from normalized TaskTracker"
    )
    parser.add_argument("--input-dir", default=str(DATA_ROOT))
    parser.add_argument("--output-root", default=str(MAMBA_DATA_DIR))
    parser.add_argument("--min-events", type=int, default=1)
    args = parser.parse_args()

    input_root = Path(args.input_dir)
    canonical_ready = (input_root / "labels.csv").is_file() or (
        input_root / "normalized" / "labels.csv"
    ).is_file()
    if args.input_dir == str(DATA_ROOT) and not canonical_ready and LEGACY_DATA_ROOT.exists():
        input_root = LEGACY_DATA_ROOT
        print(f"Canonical input not found; using legacy layout: {input_root / 'normalized'}")

    output_root = Path(args.output_root)
    rows = build_dataset_sequences(
        input_root,
        output_root / "sequences",
        output_root / "index.csv",
        dataset_name="tasktracker",
        min_events=args.min_events,
    )

    if not rows:
        raise SystemExit("[ERROR] TaskTracker khong co sequence hop le de train.")
    print(f"\nPrepared {len(rows)} TaskTracker sessions for shared train/validation/test splits.")


if __name__ == "__main__":
    main()
