from __future__ import annotations

import argparse
import json
import math
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd


TEXT_LIKE_TYPES = {"type", "paste", "cut"}


def text_len(value: object) -> int:
    if not isinstance(value, str):
        return 0
    return len(value)


def safe_div(num: float, den: float) -> float:
    return float(num / den) if den else 0.0


def summarize_session(path: Path, label_row: dict[str, object]) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    events = payload.get("events", [])
    event_count = len(events)
    times = [float(e.get("t", 0.0) or 0.0) for e in events]
    duration = max(times) - min(times) if times else 0.0
    gaps = np.diff(times) if len(times) > 1 else np.array([], dtype=float)

    by_type = {"type": [], "paste": [], "cut": [], "other": []}
    for event in events:
        by_type.setdefault(event.get("type", "other"), []).append(event)

    type_chars = sum(text_len(e.get("text")) for e in by_type.get("type", []))
    paste_events = by_type.get("paste", [])
    paste_chars = sum(text_len(e.get("text")) for e in paste_events)
    cut_chars = sum(text_len(e.get("text")) for e in by_type.get("cut", []))
    total_text_chars = type_chars + paste_chars

    paste_lens = np.array([text_len(e.get("text")) for e in paste_events], dtype=float)
    type_lens = np.array([text_len(e.get("text")) for e in by_type.get("type", [])], dtype=float)
    cut_lens = np.array([text_len(e.get("text")) for e in by_type.get("cut", [])], dtype=float)

    paste_source_counts = {
        "own": 0,
        "external": 0,
        "same_machine": 0,
        "unknown": 0,
    }
    paste_source_chars = {
        "own": 0,
        "external": 0,
        "same_machine": 0,
        "unknown": 0,
    }
    for event in paste_events:
        source = event.get("paste_source") or "unknown"
        if source not in paste_source_counts:
            source = "unknown"
        paste_source_counts[source] += 1
        paste_source_chars[source] += text_len(event.get("text"))

    row: dict[str, object] = {
        "session_id": payload.get("session_id", path.stem.replace("_", "/")),
        "source": payload.get("source", ""),
        "label": int(label_row["label"]),
        "in_original_16": label_row.get("in_original_16", ""),
        "event_count": event_count,
        "duration_sec": duration,
        "type_event_count": len(by_type.get("type", [])),
        "paste_event_count": len(paste_events),
        "cut_event_count": len(by_type.get("cut", [])),
        "other_event_count": len(by_type.get("other", [])),
        "type_chars": type_chars,
        "paste_chars": paste_chars,
        "cut_chars": cut_chars,
        "total_text_chars": total_text_chars,
        "paste_char_ratio": safe_div(paste_chars, total_text_chars),
        "cut_char_ratio": safe_div(cut_chars, total_text_chars + cut_chars),
        "events_per_min": safe_div(event_count, duration / 60.0),
        "typed_chars_per_min": safe_div(type_chars, duration / 60.0),
        "pasted_chars_per_min": safe_div(paste_chars, duration / 60.0),
        "paste_events_per_min": safe_div(len(paste_events), duration / 60.0),
        "max_paste_chars": float(paste_lens.max()) if paste_lens.size else 0.0,
        "mean_paste_chars": float(paste_lens.mean()) if paste_lens.size else 0.0,
        "median_paste_chars": float(np.median(paste_lens)) if paste_lens.size else 0.0,
        "max_type_chars": float(type_lens.max()) if type_lens.size else 0.0,
        "mean_type_chars": float(type_lens.mean()) if type_lens.size else 0.0,
        "max_cut_chars": float(cut_lens.max()) if cut_lens.size else 0.0,
        "mean_gap_sec": float(gaps.mean()) if gaps.size else 0.0,
        "median_gap_sec": float(np.median(gaps)) if gaps.size else 0.0,
        "max_gap_sec": float(gaps.max()) if gaps.size else 0.0,
        "long_gap_count_30s": int((gaps >= 30).sum()) if gaps.size else 0,
        "long_gap_count_120s": int((gaps >= 120).sum()) if gaps.size else 0,
    }

    for source in paste_source_counts:
        count = paste_source_counts[source]
        chars = paste_source_chars[source]
        row[f"paste_{source}_count"] = count
        row[f"paste_{source}_chars"] = chars
        row[f"paste_{source}_char_ratio"] = safe_div(chars, paste_chars)

    return row


def load_features(data_dir: Path, subset: str) -> pd.DataFrame:
    normalized_dir = data_dir / "normalized"
    labels_path = normalized_dir / "labels.csv"
    if not labels_path.exists():
        raise FileNotFoundError(f"Missing labels file: {labels_path}")

    labels = pd.read_csv(labels_path)
    if subset == "original16":
        labels = labels[labels["in_original_16"].astype(str).str.lower() == "yes"]
    elif subset != "all":
        raise ValueError("--subset must be original16 or all")

    rows = []
    for label_row in labels.to_dict(orient="records"):
        session_id = str(label_row["session_id"])
        file_name = session_id.replace("/", "_") + ".json"
        session_path = normalized_dir / file_name
        if not session_path.exists():
            raise FileNotFoundError(f"Missing session JSON for {session_id}: {session_path}")
        rows.append(summarize_session(session_path, label_row))

    return pd.DataFrame(rows).sort_values("session_id").reset_index(drop=True)


def require_model_dependencies(out_dir: Path) -> tuple[object, object, object, object]:
    os.environ.setdefault("MPLCONFIGDIR", str(out_dir / ".matplotlib"))
    missing = []
    try:
        from sklearn.ensemble import IsolationForest
        from sklearn.metrics import (
            balanced_accuracy_score,
            confusion_matrix,
            f1_score,
            precision_score,
            recall_score,
            roc_auc_score,
        )
        from sklearn.model_selection import LeaveOneOut
        from sklearn.preprocessing import StandardScaler
    except ModuleNotFoundError:
        missing.append("scikit-learn")
    try:
        from xgboost import XGBClassifier
    except ModuleNotFoundError:
        missing.append("xgboost")
    try:
        import shap
    except ModuleNotFoundError:
        missing.append("shap")

    if missing:
        raise RuntimeError(
            "Missing dependencies: "
            + ", ".join(missing)
            + ". Install them with: pip install -r requirements.txt"
        )

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return (
        {
            "IsolationForest": IsolationForest,
            "LeaveOneOut": LeaveOneOut,
            "StandardScaler": StandardScaler,
            "precision_score": precision_score,
            "recall_score": recall_score,
            "f1_score": f1_score,
            "roc_auc_score": roc_auc_score,
            "confusion_matrix": confusion_matrix,
            "balanced_accuracy_score": balanced_accuracy_score,
        },
        XGBClassifier,
        shap,
        plt,
    )


def balance_training_frame(
    X_train: pd.DataFrame, y_train: np.ndarray, random_state: int
) -> tuple[pd.DataFrame, np.ndarray]:
    rng = np.random.default_rng(random_state)
    classes, counts = np.unique(y_train, return_counts=True)
    if len(classes) < 2:
        return X_train, y_train

    target = int(counts.max())
    sampled_indices = []
    for cls in classes:
        cls_indices = np.where(y_train == cls)[0]
        replace = len(cls_indices) < target
        sampled = rng.choice(cls_indices, size=target, replace=replace)
        sampled_indices.extend(sampled.tolist())

    rng.shuffle(sampled_indices)
    return X_train.iloc[sampled_indices].reset_index(drop=True), y_train[sampled_indices]


def run_loo_pipeline(features: pd.DataFrame, out_dir: Path, random_state: int, threshold: float) -> None:
    sk, XGBClassifier, shap, plt = require_model_dependencies(out_dir)

    meta_cols = ["session_id", "source", "label", "in_original_16"]
    feature_cols = [c for c in features.columns if c not in meta_cols]
    X_raw = features[feature_cols].astype(float)
    y = features["label"].astype(int).to_numpy()

    predictions = []
    shap_rows = []
    start = time.perf_counter()

    loo = sk["LeaveOneOut"]()
    for fold, (train_idx, test_idx) in enumerate(loo.split(X_raw), start=1):
        X_train_raw = X_raw.iloc[train_idx]
        X_test_raw = X_raw.iloc[test_idx]
        y_train = y[train_idx]

        scaler = sk["StandardScaler"]()
        X_train_scaled = scaler.fit_transform(X_train_raw)
        X_test_scaled = scaler.transform(X_test_raw)

        contamination = min(0.45, max(0.05, float(y_train.mean())))
        iso = sk["IsolationForest"](
            n_estimators=300,
            contamination=contamination,
            random_state=random_state + fold,
        )
        iso.fit(X_train_scaled)
        train_if_score = -iso.score_samples(X_train_scaled)
        test_if_score = -iso.score_samples(X_test_scaled)

        X_train_model = X_train_raw.copy()
        X_test_model = X_test_raw.copy()
        X_train_model["if_anomaly_score"] = train_if_score
        X_test_model["if_anomaly_score"] = test_if_score

        X_train_balanced, y_train_balanced = balance_training_frame(
            X_train_model, y_train, random_state + fold
        )
        model = XGBClassifier(
            n_estimators=250,
            max_depth=2,
            learning_rate=0.08,
            subsample=0.9,
            colsample_bytree=0.9,
            min_child_weight=0,
            gamma=0,
            reg_lambda=2.0,
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=random_state + fold,
        )
        model.fit(X_train_balanced, y_train_balanced)
        probability = float(model.predict_proba(X_test_model)[0, 1])

        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_test_model)
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
        shap_row = {"session_id": features.iloc[test_idx[0]]["session_id"]}
        shap_row.update({col: float(value) for col, value in zip(X_test_model.columns, shap_values[0])})
        shap_rows.append(shap_row)

        predictions.append(
            {
                "session_id": features.iloc[test_idx[0]]["session_id"],
                "label": int(y[test_idx[0]]),
                "prob_cheat": probability,
                "pred_label": int(probability >= threshold),
                "if_anomaly_score": float(test_if_score[0]),
            }
        )

    elapsed = time.perf_counter() - start
    pred_df = pd.DataFrame(predictions)
    shap_df = pd.DataFrame(shap_rows)

    y_true = pred_df["label"].to_numpy()
    y_pred = pred_df["pred_label"].to_numpy()
    y_prob = pred_df["prob_cheat"].to_numpy()
    tn, fp, fn, tp = sk["confusion_matrix"](y_true, y_pred, labels=[0, 1]).ravel()

    metrics = {
        "n_sessions": int(len(pred_df)),
        "positive_labels": int(y_true.sum()),
        "negative_labels": int((y_true == 0).sum()),
        "threshold": float(threshold),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "precision": float(sk["precision_score"](y_true, y_pred, zero_division=0)),
        "recall": float(sk["recall_score"](y_true, y_pred, zero_division=0)),
        "f1": float(sk["f1_score"](y_true, y_pred, zero_division=0)),
        "specificity": safe_div(tn, tn + fp),
        "balanced_accuracy": float(sk["balanced_accuracy_score"](y_true, y_pred)),
        "auc": float(sk["roc_auc_score"](y_true, y_prob)) if len(set(y_true)) == 2 else math.nan,
        "confusion_matrix": [[int(tn), int(fp)], [int(fn), int(tp)]],
        "runtime_sec": elapsed,
    }

    importance = (
        shap_df.drop(columns=["session_id"])
        .abs()
        .mean()
        .sort_values(ascending=False)
        .rename_axis("feature")
        .reset_index(name="mean_abs_shap")
    )

    pred_df.to_csv(out_dir / "predictions.csv", index=False)
    shap_df.to_csv(out_dir / "shap_values.csv", index=False)
    importance.to_csv(out_dir / "shap_importance.csv", index=False)
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    top = importance.head(12).iloc[::-1]
    plt.figure(figsize=(8, 5))
    plt.barh(top["feature"], top["mean_abs_shap"])
    plt.xlabel("Mean |SHAP value|")
    plt.tight_layout()
    plt.savefig(out_dir / "shap_importance.png", dpi=200)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run IF + XGBoost + SHAP on normalized PasteTrace data.")
    parser.add_argument("--data", required=True, help="Path to PasteTrace_Normalized folder.")
    parser.add_argument("--subset", choices=["original16", "all"], default="original16")
    parser.add_argument("--out", default="outputs/pastetrace_original16")
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--features-only", action="store_true")
    args = parser.parse_args()

    data_dir = Path(args.data)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    features = load_features(data_dir, args.subset)
    features.to_csv(out_dir / "features.csv", index=False)
    print(f"Wrote {out_dir / 'features.csv'} ({len(features)} sessions)")

    if not args.features_only:
        run_loo_pipeline(features, out_dir, args.random_state, args.threshold)
        print(f"Wrote model outputs to {out_dir}")


if __name__ == "__main__":
    main()
