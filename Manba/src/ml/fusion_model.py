"""Phase 7 — Fusion Model

Combines CodeBERT embeddings (768 dims) with behavioral keystroke features
(10 dims) → 778-dim input vector for a lightweight classifier.

Architecture
------------
    embeddings.npy  [n, 768]          (from codebert_embed.py)
         +
    features.csv    [n, 10 features]  (from features.py)
         =
    fused vector    [n, 778]
         |
    XGBoost / SVM / MLP  (LOO evaluation)

The fusion head is intentionally tiny — CodeBERT already carries the heavy
representation; behavioral features add interpretable complementary signal.

Usage
-----
    # Run full pipeline (requires embeddings.npy and features.csv to exist):
    python -m src.ml.fusion_model

    # Generate embeddings first if needed:
    python -m src.ml.codebert_embed
    python -m src.ml.features
"""

import os
import warnings

import joblib
import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import LeaveOneOut
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

warnings.filterwarnings("ignore", category=ConvergenceWarning)

EMBED_PATH       = os.path.join("data", "embeddings.npy")
INDEX_PATH       = os.path.join("data", "embeddings_index.csv")
FEAT_PATH        = os.path.join("data", "features.csv")
MODEL_SAVE_PATH  = os.path.join("models", "fusion_xgb.pkl")

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

RISK_THRESHOLDS = {
    "ext_char_frac":    (0.3,  "≥30 % of code came from external paste"),
    "pasted_char_frac": (0.6,  "≥60 % of code was inserted by paste"),
    "external_paste":   (1,    "external paste event(s) detected"),
    "paste_ratio":      (0.05, "paste events > 5 % of all keystrokes"),
    "max_paste_length": (200,  "single paste ≥ 200 characters"),
}


# -----------------------------------------------------------------------
# Metrics helpers
# -----------------------------------------------------------------------

def _metrics(y_true, y_pred) -> dict:
    return {
        "accuracy":      accuracy_score(y_true, y_pred),
        "precision":     precision_score(y_true, y_pred, zero_division=0),
        "recall_cheat":  recall_score(y_true, y_pred, zero_division=0),
        "recall_normal": recall_score(y_true, y_pred, pos_label=0, zero_division=0),
        "f1":            f1_score(y_true, y_pred, zero_division=0),
        "n":             len(y_true),
    }


def _print_metrics(name: str, m: dict):
    print(f"\n  [{name}]")
    print(f"    Accuracy      : {m['accuracy']:.3f}")
    print(f"    Precision     : {m['precision']:.3f}")
    print(f"    Recall(cheat) : {m['recall_cheat']:.3f}")
    print(f"    Recall(normal): {m['recall_normal']:.3f}")
    print(f"    F1            : {m['f1']:.3f}")


# -----------------------------------------------------------------------
# LOO evaluators
# -----------------------------------------------------------------------

def _loo_xgb(X: np.ndarray, y: np.ndarray) -> dict:
    try:
        from xgboost import XGBClassifier
    except ImportError:
        print("    [XGBoost] not installed — pip install xgboost")
        return {}

    loo = LeaveOneOut()
    y_true, y_pred = [], []
    for train_idx, test_idx in loo.split(X):
        scaler = StandardScaler()
        X_tr = scaler.fit_transform(X[train_idx])
        X_te = scaler.transform(X[test_idx])

        y_tr = y[train_idx]
        # Per-fold sample weights: upweight the minority class (normal=0)
        n_pos_f = int(y_tr.sum())
        n_neg_f = len(y_tr) - n_pos_f
        sw = np.where(y_tr == 1, 1.0, float(n_pos_f) / max(n_neg_f, 1))

        try:
            clf = XGBClassifier(
                n_estimators=50,
                max_depth=2,
                learning_rate=0.1,
                eval_metric="logloss",
                verbosity=0,
                random_state=42,
            )
            clf.fit(X_tr, y_tr, sample_weight=sw)
        except Exception as e:
            print(f"    [XGBoost] fold error: {e}")
            continue

        y_true.append(y[test_idx][0])
        y_pred.append(int(clf.predict(X_te)[0]))

    if not y_true:
        print("    [XGBoost] all folds failed — check XGBoost version")
        return {}
    return _metrics(y_true, y_pred)


def _loo_svm(X: np.ndarray, y: np.ndarray) -> dict:
    loo = LeaveOneOut()
    y_true, y_pred = [], []
    for train_idx, test_idx in loo.split(X):
        scaler = StandardScaler()
        X_tr = scaler.fit_transform(X[train_idx])
        X_te = scaler.transform(X[test_idx])
        clf = SVC(kernel="rbf", class_weight="balanced", probability=True, random_state=42)
        clf.fit(X_tr, y[train_idx])
        y_true.append(y[test_idx][0])
        y_pred.append(int(clf.predict(X_te)[0]))
    return _metrics(y_true, y_pred)


def _loo_mlp(X: np.ndarray, y: np.ndarray) -> dict:
    loo = LeaveOneOut()
    y_true, y_pred = [], []
    for train_idx, test_idx in loo.split(X):
        scaler = StandardScaler()
        X_tr = scaler.fit_transform(X[train_idx])
        X_te = scaler.transform(X[test_idx])
        clf = MLPClassifier(
            hidden_layer_sizes=(256, 64),
            max_iter=500,
            random_state=42,
            early_stopping=False,
        )
        clf.fit(X_tr, y[train_idx])
        y_true.append(y[test_idx][0])
        y_pred.append(int(clf.predict(X_te)[0]))
    return _metrics(y_true, y_pred)


# -----------------------------------------------------------------------
# Student risk report
# -----------------------------------------------------------------------

def _build_reasons(feat_row: pd.Series, score: float) -> list[str]:
    """Return a list of human-readable risk reasons for one student."""
    reasons = []
    for col, (threshold, description) in RISK_THRESHOLDS.items():
        if col in feat_row and feat_row[col] >= threshold:
            val = feat_row[col]
            if isinstance(val, float):
                reasons.append(f"- {description}  ({col}={val:.2f})")
            else:
                reasons.append(f"- {description}  ({col}={int(val)})")
    if not reasons:
        reasons.append("- no strong behavioral signals detected")
    return reasons


def print_student_risk_report(
    index_df: pd.DataFrame,
    feat_df: pd.DataFrame,
    scores: np.ndarray,
    preds: np.ndarray,
    show_labels: bool = True,
):
    """Print a sorted risk table for all students."""
    order = np.argsort(scores)[::-1]

    bar_width = 20
    print("\n" + "=" * 60)
    print("  STUDENT RISK REPORT  (sorted by score, high -> low)")
    print("=" * 60)

    for rank, i in enumerate(order, 1):
        row   = index_df.iloc[i]
        sid   = f"{row['case']}/{row['student']}"
        label = int(row["label"])
        score = float(scores[i])
        pred  = int(preds[i])

        filled = int(round(score * bar_width))
        bar    = "#" * filled + "-" * (bar_width - filled)
        risk_label = "HIGH" if score >= 0.6 else ("MEDIUM" if score >= 0.35 else "LOW")

        print(f"\n  #{rank:02d}  {sid}")
        print(f"  Risk: [{bar}] {score*100:.0f}%  [{risk_label}]")
        if show_labels and label != -1:
            gt_tag = " <- TRUE: CHEAT" if label == 1 else " <- TRUE: normal"
            print(f"  Prediction: {'CHEAT' if pred == 1 else 'normal'}{gt_tag}")
        else:
            print(f"  Prediction: {'CHEAT' if pred == 1 else 'normal'}")

        frow = feat_df[
            (feat_df["case"] == str(row["case"])) &
            (feat_df["student"] == str(row["student"]))
        ]
        if not frow.empty:
            reasons = _build_reasons(frow.iloc[0], score)
            print("  Reasons:")
            for r in reasons:
                print(f"    {r}")

    print("\n" + "=" * 60)


# -----------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------

def load_data() -> tuple[np.ndarray, np.ndarray, pd.DataFrame, pd.DataFrame]:
    """Load embeddings, features, align by (case, student), return fused X and y."""
    embeddings = np.load(EMBED_PATH)                     # [n, 768]
    index_df   = pd.read_csv(INDEX_PATH)                 # case, student, label
    feat_df    = pd.read_csv(FEAT_PATH)                  # case, student, label, features...

    # Align feature rows to the same order as embeddings_index.csv
    merged = index_df.merge(
        feat_df[["case", "student"] + FEATURE_COLS],
        on=["case", "student"],
        how="left",
    )
    feat_matrix = merged[FEATURE_COLS].fillna(0).values.astype(np.float32)

    X_fused = np.concatenate([embeddings, feat_matrix], axis=1)  # [n, 768+10]
    y = index_df["label"].values.astype(int)
    return X_fused, y, index_df, feat_df


def _train_and_save(X: np.ndarray, y: np.ndarray) -> tuple:
    """Train XGBoost on ALL labeled data, save to disk, return (clf, scaler, scores, preds)."""
    from xgboost import XGBClassifier

    n_pos = int(y.sum())
    n_neg = len(y) - n_pos
    sw_all = np.where(y == 1, 1.0, float(n_pos) / max(n_neg, 1))

    scaler = StandardScaler()
    X_sc   = scaler.fit_transform(X)

    clf = XGBClassifier(
        n_estimators=50, max_depth=2, learning_rate=0.1,
        eval_metric="logloss", verbosity=0, random_state=42,
    )
    clf.fit(X_sc, y, sample_weight=sw_all)

    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
    joblib.dump({"clf": clf, "scaler": scaler}, MODEL_SAVE_PATH)
    print(f"Model saved: {MODEL_SAVE_PATH}")

    return clf, scaler, clf.predict_proba(X_sc)[:, 1], clf.predict(X_sc)


def _load_and_predict(X: np.ndarray) -> tuple | None:
    """Load saved model and predict on new (unlabeled) data."""
    if not os.path.exists(MODEL_SAVE_PATH):
        return None
    saved  = joblib.load(MODEL_SAVE_PATH)
    X_sc   = saved["scaler"].transform(X)
    scores = saved["clf"].predict_proba(X_sc)[:, 1]
    preds  = saved["clf"].predict(X_sc)
    return scores, preds


def main():
    if not os.path.exists(EMBED_PATH):
        print(f"embeddings.npy not found at {EMBED_PATH}")
        print("Run first:  python -m src.ml.codebert_embed")
        return
    if not os.path.exists(FEAT_PATH):
        print(f"features.csv not found at {FEAT_PATH}")
        print("Run first:  python -m src.ml.features")
        return

    X, y, index_df, feat_df = load_data()
    inference_mode = (y == -1).any()

    n_labeled = int((y >= 0).sum())
    print(f"Fused input: {X.shape}  (labeled={n_labeled}, unlabeled={(y==-1).sum()})")
    print(f"  CodeBERT dims : 768  |  Behavioral: {len(FEATURE_COLS)}  |  Total: {X.shape[1]}")
    print(f"  Mode: {'INFERENCE — using saved model' if inference_mode else 'TRAIN — LOO + save'}")

    if inference_mode:
        # ── Inference mode: no labels → load saved model ──────────────
        result = _load_and_predict(X)
        if result is None:
            print(f"\nNo saved model found at {MODEL_SAVE_PATH}")
            print("Run the pipeline on labeled data first to train and save the model.")
            return
        scores, preds = result
        print_student_risk_report(index_df, feat_df, scores, preds, show_labels=False)
        return

    # ── Training mode: LOO evaluation then save ────────────────────────
    X_labeled = X[y >= 0]
    y_labeled  = y[y >= 0]

    print("\n--- LOO Evaluation (labeled samples only) ---")

    xgb_m = _loo_xgb(X_labeled, y_labeled)
    if xgb_m:
        _print_metrics("XGBoost (fused)", xgb_m)

    svm_m = _loo_svm(X_labeled, y_labeled)
    _print_metrics("SVM-RBF (fused)", svm_m)

    mlp_m = _loo_mlp(X_labeled, y_labeled)
    _print_metrics("MLP (fused)", mlp_m)

    # Train final model on ALL labeled data and save
    try:
        clf, scaler, scores, preds = _train_and_save(X_labeled, y_labeled)
    except ImportError:
        print("XGBoost not available — falling back to SVM (model NOT saved)")
        scaler = StandardScaler()
        X_sc   = scaler.fit_transform(X_labeled)
        clf    = SVC(kernel="rbf", class_weight="balanced", probability=True, random_state=42)
        clf.fit(X_sc, y_labeled)
        scores = clf.predict_proba(X_sc)[:, 1]
        preds  = clf.predict(X_sc)

    # Build index/feat subsets for labeled rows only
    labeled_mask  = y >= 0
    index_labeled = index_df[labeled_mask].reset_index(drop=True)
    print_student_risk_report(index_labeled, feat_df, scores, preds, show_labels=True)


if __name__ == "__main__":
    main()
