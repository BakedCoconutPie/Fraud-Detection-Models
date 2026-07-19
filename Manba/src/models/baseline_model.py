"""Majority-class baseline — always predict the dominant label (cheat=1)."""
import os

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

DATASET_PATH = os.path.join("data", "dataset.csv")


def compute_majority_metrics(y: list) -> dict:
    majority = 1 if sum(y) >= len(y) / 2 else 0
    y_pred   = [majority] * len(y)
    return {
        "accuracy":       accuracy_score(y, y_pred),
        "precision":      precision_score(y, y_pred, zero_division=0),
        "recall_cheat":   recall_score(y, y_pred, zero_division=0),
        "recall_normal":  recall_score(y, y_pred, pos_label=0, zero_division=0),
        "f1":             f1_score(y, y_pred, zero_division=0),
        "n":              len(y),
        "majority_class": majority,
    }


def main():
    df = pd.read_csv(DATASET_PATH)
    y  = df["label"].tolist()
    m  = compute_majority_metrics(y)
    print(f"\n[Majority Baseline (always predict {m['majority_class']})] n={m['n']}")
    print(f"  Accuracy      : {m['accuracy']:.3f}")
    print(f"  Precision     : {m['precision']:.3f}")
    print(f"  Recall(cheat) : {m['recall_cheat']:.3f}")
    print(f"  Recall(normal): {m['recall_normal']:.3f}")
    print(f"  F1            : {m['f1']:.3f}")


if __name__ == "__main__":
    main()
