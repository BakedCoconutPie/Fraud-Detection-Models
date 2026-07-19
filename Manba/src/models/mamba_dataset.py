"""Dataset utilities for TaskTracker Mamba event sequences.

The scaler is fit only on the shared TaskTracker training split. Validation,
test, and new sessions use that frozen scaler.
"""
import json
import os
from typing import Optional

import numpy as np
import torch
from torch.utils.data import Dataset

SCALER_PATH = os.path.join("models", "mamba", "scaler.json")
# Dense continuous features that need scaling (log_len=3, log_delta_time=6).
# Sparse paste_log_len stays in its bounded log1p scale to avoid huge z-scores.
CONTINUOUS_IDXS = [3, 6]


class SequenceScaler:
    """StandardScaler for selected feature columns, fit on train only."""

    def __init__(self):
        self.mean_: Optional[np.ndarray] = None
        self.std_: Optional[np.ndarray] = None

    def fit(self, seqs: list[list[list[float]]]) -> "SequenceScaler":
        vals = {i: [] for i in CONTINUOUS_IDXS}
        for seq in seqs:
            for vec in seq:
                for i in CONTINUOUS_IDXS:
                    vals[i].append(vec[i])
        self.mean_ = np.zeros(len(CONTINUOUS_IDXS))
        self.std_ = np.ones(len(CONTINUOUS_IDXS))
        for k, i in enumerate(CONTINUOUS_IDXS):
            arr = np.array(vals[i], dtype=np.float32)
            self.mean_[k] = arr.mean()
            s = arr.std()
            self.std_[k] = s if s > 1e-8 else 1.0
        return self

    def transform(self, seq: list[list[float]]) -> list[list[float]]:
        out = []
        for vec in seq:
            v = list(vec)
            for k, i in enumerate(CONTINUOUS_IDXS):
                v[i] = (v[i] - float(self.mean_[k])) / float(self.std_[k])
            out.append(v)
        return out

    def save(self, path: str = SCALER_PATH):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf8") as f:
            json.dump({
                "continuous_idxs": CONTINUOUS_IDXS,
                "mean": self.mean_.tolist(),
                "std": self.std_.tolist(),
            }, f)

    @classmethod
    def load(cls, path: str = SCALER_PATH) -> "SequenceScaler":
        with open(path, encoding="utf8") as f:
            d = json.load(f)
        sc = cls()
        sc.mean_ = np.array(d["mean"], dtype=np.float32)
        sc.std_ = np.array(d["std"], dtype=np.float32)
        return sc


class SequenceDataset(Dataset):
    """Load generated behavioral sequences by sample id."""

    def __init__(
        self,
        ids: list[str],
        seq_dir: str = os.path.join("data", "mamba", "sequences"),
        scaler: Optional[SequenceScaler] = None,
        max_len: int = 1000,
    ):
        self.seq_dir = seq_dir
        self.scaler = scaler
        self.max_len = max_len

        self.records = []
        for sid in ids:
            path = os.path.join(seq_dir, f"{sid}.json")
            with open(path, encoding="utf8") as f:
                rec = json.load(f)
            seq = rec["seq"][:max_len]
            if scaler is not None:
                seq = scaler.transform(seq)
            self.records.append({
                "id": sid,
                "seq": torch.tensor(seq, dtype=torch.float32),
                "label": torch.tensor(rec["label"], dtype=torch.float32),
            })

    def __len__(self):
        return len(self.records)

    def __getitem__(self, idx):
        return self.records[idx]


def build_scaler_from_ids(
    train_ids: list[str],
    seq_dir: str = os.path.join("data", "mamba", "sequences"),
    max_len: int | None = None,
) -> SequenceScaler:
    """Fit scaler on raw (unscaled) train sequences only."""
    seqs = []
    for sid in train_ids:
        path = os.path.join(seq_dir, f"{sid}.json")
        with open(path, encoding="utf8") as f:
            rec = json.load(f)
        seqs.append(rec["seq"] if max_len is None else rec["seq"][:max_len])
    sc = SequenceScaler()
    sc.fit(seqs)
    return sc


def collate_fn(batch: list[dict]) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, list[str]]:
    """Pad sequences to max length in batch. Returns (padded_seqs, lengths, mask, ids, labels)."""
    seqs = [item["seq"] for item in batch]
    labels = torch.stack([item["label"] for item in batch])
    ids = [item["id"] for item in batch]

    lengths = torch.tensor([s.shape[0] for s in seqs], dtype=torch.long)
    max_len = int(lengths.max().item())
    n_feat = seqs[0].shape[1]

    padded = torch.zeros(len(seqs), max_len, n_feat)
    mask = torch.zeros(len(seqs), max_len, dtype=torch.bool)
    for i, s in enumerate(seqs):
        L = s.shape[0]
        padded[i, :L, :] = s
        mask[i, :L] = True

    return padded, lengths, mask, ids, labels
