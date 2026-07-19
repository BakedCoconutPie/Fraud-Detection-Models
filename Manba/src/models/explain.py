"""Model-agnostic explanations for a cheating prediction.

Since the underlying dataset is tiny (18 labeled students), the most
reliable explanation is not "what did the neural net attend to" but
"which already-graded submission does this code resemble, and how
strongly" -- the same logic a human grader uses when reading a MOSS
report. SVM additionally gets a token-level explanation since its
linear decision boundary makes that cheap and exact.
"""
import os

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATASET_PATH = os.path.join("data", "dataset.csv")
SIMILARITY_THRESHOLD = 0.3


class Explainer:
    def __init__(self):
        df = pd.read_csv(DATASET_PATH)
        self.cases = df["case"].tolist()
        self.students = df["student"].tolist()
        self.labels = df["label"].tolist()
        self.codes = df["code"].tolist()
        self.vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
        self.matrix = self.vectorizer.fit_transform(self.codes)

    def nearest_neighbors(self, code, top_k=3):
        vec = self.vectorizer.transform([code])
        sims = cosine_similarity(vec, self.matrix)[0]
        order = np.argsort(sims)[::-1][:top_k]
        return [
            {
                "case": self.cases[i],
                "student": self.students[i],
                "label": int(self.labels[i]),
                "similarity": float(sims[i]),
            }
            for i in order
        ]

    @staticmethod
    def svm_top_tokens(code, svm_model, svm_vectorizer, top_k=5):
        vec = svm_vectorizer.transform([code])
        coef = svm_model.coef_
        coef = coef.toarray().ravel() if hasattr(coef, "toarray") else np.asarray(coef).ravel()
        contrib = vec.toarray().ravel() * coef
        feature_names = svm_vectorizer.get_feature_names_out()
        order = np.argsort(contrib)[::-1][:top_k]
        return [
            {"token": feature_names[i], "weight": float(contrib[i])}
            for i in order
            if contrib[i] > 0
        ]

    def build_reason(self, code, label, svm_model=None, svm_vectorizer=None):
        parts = []
        neighbors = self.nearest_neighbors(code)
        best = neighbors[0]

        if best["similarity"] >= SIMILARITY_THRESHOLD:
            verdict = "đã ghi nhận là gian lận" if best["label"] == 1 else "đã ghi nhận là bình thường"
            parts.append(
                f"Code giống {best['similarity'] * 100:.0f}% với bài case {best['case']}/"
                f"sinh viên {best['student']} ({verdict})."
            )
            others = [n for n in neighbors[1:] if n["similarity"] >= SIMILARITY_THRESHOLD]
            if others:
                other_str = "; ".join(
                    f"{n['case']}/{n['student']} ({n['similarity'] * 100:.0f}%, "
                    f"{'gian lận' if n['label'] == 1 else 'bình thường'})"
                    for n in others
                )
                parts.append(f"Các bài tương tự khác: {other_str}.")
        else:
            parts.append("Không có bài nộp nào trong dữ liệu huấn luyện đủ giống để so khớp trực tiếp.")

        if svm_model is not None and svm_vectorizer is not None:
            tokens = self.svm_top_tokens(code, svm_model, svm_vectorizer)
            if tokens:
                token_str = ", ".join(f"'{t['token']}'" for t in tokens)
                parts.append(f"Token/đoạn mã đóng góp nhiều nhất vào điểm gian lận: {token_str}.")

        prefix = "Bị đánh dấu nghi vấn gian lận vì: " if label == 1 else "Được đánh giá là bình thường vì: "
        return prefix + " ".join(parts)
