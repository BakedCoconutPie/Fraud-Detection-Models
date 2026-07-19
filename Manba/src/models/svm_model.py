"""TF-IDF + SVM baseline for cheating detection on Processing (.pde) source code."""
import os

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import LeaveOneOut
from sklearn.svm import SVC

DATASET_PATH = os.path.join("data", "dataset.csv")
MODEL_DIR = os.path.join("models", "svm")


def _metrics(y_true, y_pred):
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall_cheat": recall_score(y_true, y_pred, zero_division=0),
        "recall_normal": recall_score(y_true, y_pred, pos_label=0, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "n": len(y_true),
    }


def print_metrics(name, m):
    print(f"\n[{name}] LOO results (n={m['n']}):")
    print(f"  Accuracy      : {m['accuracy']:.3f}")
    print(f"  Precision     : {m['precision']:.3f}")
    print(f"  Recall(cheat) : {m['recall_cheat']:.3f}")
    print(f"  Recall(normal): {m['recall_normal']:.3f}")
    print(f"  F1            : {m['f1']:.3f}")


def evaluate_loo(X, y):
    """Leave-one-out CV: with only 17 labeled samples, a single train/test
    split is not statistically meaningful, so every sample takes a turn as
    the held-out test point."""
    loo = LeaveOneOut()
    y_true, y_pred = [], []
    for train_idx, test_idx in loo.split(X):
        vectorizer = TfidfVectorizer(max_features=5000)
        X_train = vectorizer.fit_transform(X.iloc[train_idx])
        X_test = vectorizer.transform(X.iloc[test_idx])
        model = SVC(kernel="linear", class_weight="balanced", probability=True)
        model.fit(X_train, y.iloc[train_idx])
        y_true.append(y.iloc[test_idx].values[0])
        y_pred.append(model.predict(X_test)[0])
    return _metrics(y_true, y_pred)


def main():
    df = pd.read_csv(DATASET_PATH)
    X, y = df["code"], df["label"]

    m = evaluate_loo(X, y)
    print_metrics("SVM (TF-IDF)", m)

    vectorizer = TfidfVectorizer(max_features=5000)
    X_vec = vectorizer.fit_transform(X)
    model = SVC(kernel="linear", class_weight="balanced", probability=True)
    model.fit(X_vec, y)

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, os.path.join(MODEL_DIR, "svm.pkl"))
    joblib.dump(vectorizer, os.path.join(MODEL_DIR, "vectorizer.pkl"))
    print(f"\nSaved final model to {MODEL_DIR}")


if __name__ == "__main__":
    main()
