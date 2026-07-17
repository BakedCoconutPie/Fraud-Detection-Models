"""Behavioral branch — LOO evaluation for LR, Decision Tree, and threshold rule.

Input: data/features.csv (10 features from meta.json, same 17 students).
Uses identical LOO folds as the code-text branch for a fair comparison.
"""
import os

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import LeaveOneOut
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

FEAT_PATH = os.path.join("data", "features.csv")

FEATURE_COLS = [
    "total_events", "type_count", "paste_count", "paste_ratio",
    "max_paste_length", "external_paste", "ext_paste_ratio",
    "pasted_char_frac", "ext_char_frac", "typed_chars",
]

THRESHOLD_FEATURE = "ext_char_frac"


def _metrics(y_true, y_pred):
    return {
        "accuracy":      accuracy_score(y_true, y_pred),
        "precision":     precision_score(y_true, y_pred, zero_division=0),
        "recall_cheat":  recall_score(y_true, y_pred, zero_division=0),
        "recall_normal": recall_score(y_true, y_pred, pos_label=0, zero_division=0),
        "f1":            f1_score(y_true, y_pred, zero_division=0),
        "n":             len(y_true),
    }


def print_metrics(name, m):
    print(f"\n[{name}] LOO results (n={m['n']}):")
    print(f"  Accuracy      : {m['accuracy']:.3f}")
    print(f"  Precision     : {m['precision']:.3f}")
    print(f"  Recall(cheat) : {m['recall_cheat']:.3f}")
    print(f"  Recall(normal): {m['recall_normal']:.3f}")
    print(f"  F1            : {m['f1']:.3f}")


def evaluate_loo_lr(X, y):
    loo = LeaveOneOut()
    y_true, y_pred = [], []
    for train_idx, test_idx in loo.split(X):
        scaler  = StandardScaler()
        X_tr    = scaler.fit_transform(X[train_idx])
        X_te    = scaler.transform(X[test_idx])
        clf     = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)
        clf.fit(X_tr, y[train_idx])
        y_true.append(y[test_idx][0])
        y_pred.append(int(clf.predict(X_te)[0]))
    return _metrics(y_true, y_pred)


def evaluate_loo_dt(X, y):
    loo = LeaveOneOut()
    y_true, y_pred = [], []
    for train_idx, test_idx in loo.split(X):
        clf = DecisionTreeClassifier(class_weight="balanced", max_depth=3, random_state=42)
        clf.fit(X[train_idx], y[train_idx])
        y_true.append(y[test_idx][0])
        y_pred.append(int(clf.predict(X[test_idx])[0]))
    return _metrics(y_true, y_pred)


def evaluate_loo_threshold(X_df, y_list):
    """Threshold rule on ext_char_frac — threshold picked per fold to maximise F1."""
    y_true, y_pred = [], []
    vals = X_df[THRESHOLD_FEATURE].values
    for i in range(len(y_list)):
        train_mask = [j for j in range(len(y_list)) if j != i]
        x_tr = vals[train_mask]
        y_tr = np.array(y_list)[train_mask]

        best_thresh, best_f1 = -0.01, -1.0
        for t in [-0.01] + sorted(np.unique(x_tr).tolist()):
            preds = (x_tr > t).astype(int)
            f = f1_score(y_tr, preds, zero_division=0)
            if f > best_f1:
                best_f1, best_thresh = f, t

        y_true.append(y_list[i])
        y_pred.append(1 if vals[i] > best_thresh else 0)
    return _metrics(y_true, y_pred)


def main():
    df   = pd.read_csv(FEAT_PATH)
    avail = [c for c in FEATURE_COLS if c in df.columns]
    X    = df[avail].values
    y    = df["label"].values

    print_metrics("Logistic Regression (behavioral)", evaluate_loo_lr(X, y))
    print_metrics("Decision Tree (behavioral)",       evaluate_loo_dt(X, y))
    print_metrics(f"Threshold Rule ({THRESHOLD_FEATURE})",
                  evaluate_loo_threshold(df[avail], df["label"].tolist()))


if __name__ == "__main__":
    main()
