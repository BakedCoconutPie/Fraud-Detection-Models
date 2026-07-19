"""Build a labeled dataset.csv from PasteTrace ground-truth aggregation files.

Ground truth comes from `agrigation.csv` (the "Cheated" column, filled in by
a human grader), NOT from whether a submission appears under the `MOSS/`
folder -- MOSS only records *detected matches*, many of which are annotated
as false flags in the aggregation notes.

Each row contains: case, student, label, code, plus 7 behavioral features
extracted from meta.json History events. Students without a meta.json
(e.g., 111/B) are excluded so both model branches compare on the same 17
samples. Student 211/O has two project subfolders -- their events are pooled.
"""
import csv
import json
import os

CASE_STUDY_ROOT = os.path.join(
    "PasteTrace-release", "PasteTrace-release", "case studies", "sp2023", "pre-processed"
)
OUTPUT_PATH = os.path.join("data", "dataset.csv")

CASES = ["111", "211"]

BEHAVIORAL_COLS = [
    "paste_to_type_events",
    "pasted_char_frac",
    "ext_char_frac",
    "largest_paste",
    "paste_external",
    "n_paste",
    "typed_chars",
]


def load_labels(case_dir):
    """Return {student: 0/1} from agrigation.csv, dropping ambiguous '?'/'*' rows."""
    agg_path = os.path.join(case_dir, "agrigation.csv")
    labels = {}
    with open(agg_path, encoding="utf8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            student = row.get("Student", "").strip()
            if not student:
                continue
            cheated = (row.get("Cheated") or "").strip()
            if cheated == "X":
                labels[student] = 1
            elif cheated == "":
                labels[student] = 0
            # '?' and '*' are ambiguous -> excluded entirely
    return labels


def scan_students(case_dir):
    """Return {student: -1} for all sub-dirs — used in inference mode (no labels)."""
    return {
        d: -1
        for d in sorted(os.listdir(case_dir))
        if os.path.isdir(os.path.join(case_dir, d))
    }


def collect_code(student_dir):
    """Concatenate all .pde files found recursively under a student folder.

    211/O has two subfolders (BouncingBall, Student_Fractal_Assignment); os.walk
    picks them up without special-casing.
    """
    chunks = []
    for root, _dirs, files in os.walk(student_dir):
        for name in sorted(files):
            if name.lower().endswith(".pde"):
                path = os.path.join(root, name)
                with open(path, encoding="utf8", errors="ignore") as f:
                    chunks.append(f.read())
    return "\n\n".join(chunks)


def find_meta_jsons(student_dir):
    """Return all meta.json paths found recursively under a student directory.

    Most students have a single meta.json at the top level; 211/O has one in
    each of its two project subfolders.
    """
    paths = []
    for root, _dirs, files in os.walk(student_dir):
        for name in files:
            if name == "meta.json":
                paths.append(os.path.join(root, name))
    return paths


def extract_behavioral_features(meta_paths):
    """Compute 7 behavioral features from one or more meta.json History arrays.

    Events with L="T" are typed; L="P" are pasted. External paste = paste
    event whose N note does not mention 'paste from project', meaning the
    content came from outside the PasteTrace-tracked ecosystem (web, ChatGPT,
    external file, etc.).  Multiple meta.json files (211/O) are pooled.
    """
    all_events = []
    for path in meta_paths:
        try:
            with open(path, encoding="utf8", errors="ignore") as f:
                data = json.load(f)
            all_events.extend(data.get("History", []))
        except Exception:
            pass

    type_events = [e for e in all_events if e.get("L") == "T"]
    paste_events = [e for e in all_events if e.get("L") == "P"]

    typed_chars = sum(len(e.get("E", "")) for e in type_events)
    paste_sizes = [len(e.get("E", "")) for e in paste_events]
    pasted_chars = sum(paste_sizes)
    total_chars = max(typed_chars + pasted_chars, 1)

    def is_external(event):
        n = (event.get("N") or "").lower()
        return "paste from project" not in n

    ext_paste_events = [e for e in paste_events if is_external(e)]
    ext_chars = sum(len(e.get("E", "")) for e in ext_paste_events)

    n_type = len(type_events)
    n_paste = len(paste_events)

    return {
        "paste_to_type_events": round(n_paste / max(n_type, 1), 6),
        "pasted_char_frac": round(pasted_chars / total_chars, 6),
        "ext_char_frac": round(ext_chars / total_chars, 6),
        "largest_paste": max(paste_sizes) if paste_sizes else 0,
        "paste_external": len(ext_paste_events),
        "n_paste": n_paste,
        "typed_chars": typed_chars,
    }


def main(root: str | None = None, output: str | None = None):
    """
    Parameters
    ----------
    root   : override CASE_STUDY_ROOT  (path to the pre-processed folder)
    output : override OUTPUT_PATH
    """
    import argparse
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--root",   default=None)
    parser.add_argument("--output", default=None)
    known, _ = parser.parse_known_args()

    data_root   = root   or known.root   or CASE_STUDY_ROOT
    output_path = output or known.output or OUTPUT_PATH

    rows = []
    skipped = []

    # Auto-discover case folders (any non-special subdir of data_root)
    all_subdirs = sorted(
        d for d in os.listdir(data_root)
        if os.path.isdir(os.path.join(data_root, d)) and d not in ("RawData",)
    )
    labeled_cases = [
        d for d in all_subdirs
        if os.path.isfile(os.path.join(data_root, d, "agrigation.csv"))
    ]
    cases = labeled_cases if labeled_cases else (all_subdirs or CASES)
    inference_mode = not bool(labeled_cases)

    mode_str = "INFERENCE (no labels, label=-1)" if inference_mode else "TRAIN (labeled)"
    print(f"Mode  : {mode_str}")
    print(f"Cases : {cases}")

    for case in cases:
        case_dir = os.path.join(data_root, case)
        if os.path.isfile(os.path.join(case_dir, "agrigation.csv")):
            labels = load_labels(case_dir)
        else:
            labels = scan_students(case_dir)

        for student, label in sorted(labels.items()):
            student_dir = os.path.join(case_dir, student)
            if not os.path.isdir(student_dir):
                skipped.append(f"{case}/{student}: directory not found")
                continue

            meta_paths = find_meta_jsons(student_dir)
            if not meta_paths:
                skipped.append(f"{case}/{student}: no meta.json (excluded to keep both branches on same 17 samples)")
                continue

            code = collect_code(student_dir)
            if not code.strip():
                skipped.append(f"{case}/{student}: no .pde code found")
                continue

            behavioral = extract_behavioral_features(meta_paths)
            rows.append({
                "case": case,
                "student": student,
                "label": label,
                "code": code,
                **behavioral,
            })

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fieldnames = ["case", "student", "label", "code"] + BEHAVIORAL_COLS
    with open(output_path, "w", encoding="utf8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    n_pos     = sum(1 for r in rows if r["label"] == 1)
    n_neg     = sum(1 for r in rows if r["label"] == 0)
    n_unknown = sum(1 for r in rows if r["label"] == -1)
    if n_unknown > 0:
        print(f"Wrote {len(rows)} samples to {output_path}  ({n_unknown} unlabeled, PREDICT mode)")
    else:
        print(f"Wrote {len(rows)} samples to {output_path}  ({n_pos} cheating, {n_neg} normal)")

    if skipped:
        print("\nSkipped:")
        for s in skipped:
            print(f"  {s}")

    print("\nPer-sample behavioral snapshot:")
    header = f"  {'case/student':<14} {'label':<6} {'ext_frac':<10} {'pasted_frac':<12} {'n_paste':<8} {'ext_pastes'}"
    print(header)
    print("  " + "-" * (len(header) - 2))
    for r in rows:
        print(
            f"  {r['case']}/{r['student']:<12} {r['label']:<6} "
            f"{r['ext_char_frac']:<10.3f} {r['pasted_char_frac']:<12.3f} "
            f"{r['n_paste']:<8} {r['paste_external']}"
        )


if __name__ == "__main__":
    main()
