"""BiLSTM classifier for cheating detection, implemented in PyTorch
(shares the torch dependency already needed for CodeBERT instead of
pulling in TensorFlow as a second deep-learning framework)."""
import json
import os
import re

import pandas as pd
import torch
import torch.nn as nn
from torch.nn.utils.rnn import pad_sequence

DATASET_PATH = os.path.join("data", "dataset.csv")
MODEL_DIR = os.path.join("models", "bilstm")
VOCAB_SIZE = 10000
MAX_LEN = 300
EMBED_DIM = 128
HIDDEN_DIM = 64
EPOCHS = 30


def tokenize(text):
    return re.findall(r"\w+|[^\w\s]", text.lower())


def build_vocab(texts, vocab_size):
    counts = {}
    for text in texts:
        for tok in tokenize(text):
            counts[tok] = counts.get(tok, 0) + 1
    most_common = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[: vocab_size - 2]
    vocab = {"<pad>": 0, "<unk>": 1}
    for tok, _ in most_common:
        vocab[tok] = len(vocab)
    return vocab


def encode(text, vocab, max_len):
    ids = [vocab.get(tok, 1) for tok in tokenize(text)][:max_len]
    return torch.tensor(ids, dtype=torch.long)


class BiLSTMClassifier(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, bidirectional=True, batch_first=True)
        self.fc = nn.Linear(hidden_dim * 2, 1)

    def forward(self, x):
        emb = self.embedding(x)
        _, (h_n, _) = self.lstm(emb)
        h = torch.cat([h_n[0], h_n[1]], dim=1)
        return self.fc(h).squeeze(1)


def train_model(X_ids, y, vocab_size, epochs=EPOCHS):
    model = BiLSTMClassifier(vocab_size, EMBED_DIM, HIDDEN_DIM)
    padded = pad_sequence(X_ids, batch_first=True, padding_value=0)
    labels = torch.tensor(y, dtype=torch.float32)

    n_pos = labels.sum().item()
    n_neg = len(labels) - n_pos
    pos_weight = torch.tensor(n_neg / max(n_pos, 1))
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    model.train()
    for _ in range(epochs):
        optimizer.zero_grad()
        logits = model(padded)
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()
    return model


def evaluate_loo(texts, labels):
    """Leave-one-out CV, retraining vocab+model each fold to avoid leakage."""
    correct = 0
    for i in range(len(texts)):
        train_idx = [j for j in range(len(texts)) if j != i]
        vocab = build_vocab([texts[j] for j in train_idx], VOCAB_SIZE)
        X_train = [encode(texts[j], vocab, MAX_LEN) for j in train_idx]
        y_train = [labels[j] for j in train_idx]
        model = train_model(X_train, y_train, len(vocab))

        model.eval()
        with torch.no_grad():
            x_test = encode(texts[i], vocab, MAX_LEN).unsqueeze(0)
            prob = torch.sigmoid(model(x_test)).item()
        pred = 1 if prob >= 0.5 else 0
        correct += int(pred == labels[i])
    return correct / len(texts)


def main():
    df = pd.read_csv(DATASET_PATH)
    texts = df["code"].tolist()
    labels = df["label"].tolist()

    acc = evaluate_loo(texts, labels)
    print(f"Leave-one-out accuracy: {acc:.3f} (n={len(df)})")

    vocab = build_vocab(texts, VOCAB_SIZE)
    X = [encode(t, vocab, MAX_LEN) for t in texts]
    model = train_model(X, labels, len(vocab))

    os.makedirs(MODEL_DIR, exist_ok=True)
    torch.save(model.state_dict(), os.path.join(MODEL_DIR, "bilstm.pt"))
    with open(os.path.join(MODEL_DIR, "vocab.json"), "w", encoding="utf8") as f:
        json.dump(vocab, f)
    with open(os.path.join(MODEL_DIR, "config.json"), "w", encoding="utf8") as f:
        json.dump(
            {"vocab_size": len(vocab), "embed_dim": EMBED_DIM, "hidden_dim": HIDDEN_DIM, "max_len": MAX_LEN},
            f,
        )
    print(f"Saved final model to {MODEL_DIR}")


if __name__ == "__main__":
    main()
