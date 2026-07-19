"""CodeBERT fine-tuned classifier for cheating detection.

With only 18 labeled samples, full leave-one-out fine-tuning (18 separate
fine-tunes of a 125M-param transformer) is impractical on CPU, so this
script reports a single stratified-ish hold-out split for a sanity check
and then fine-tunes the final model on the full dataset for serving.
"""
import os

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments

DATASET_PATH = os.path.join("data", "dataset.csv")
MODEL_DIR = os.path.join("models", "codebert")
MODEL_NAME = "microsoft/codebert-base"
MAX_LEN = 256


class CodeDataset(Dataset):
    def __init__(self, codes, labels, tokenizer):
        enc = tokenizer(codes, truncation=True, padding="max_length", max_length=MAX_LEN, return_tensors="pt")
        self.input_ids = enc["input_ids"]
        self.attention_mask = enc["attention_mask"]
        self.labels = torch.tensor(labels, dtype=torch.long)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return {
            "input_ids": self.input_ids[idx],
            "attention_mask": self.attention_mask[idx],
            "labels": self.labels[idx],
        }


def main():
    df = pd.read_csv(DATASET_PATH)
    codes = df["code"].tolist()
    labels = df["label"].tolist()

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    # Quick hold-out sanity check (n=18 is too small for a robust train/test
    # split, this is illustrative only -- see README caveats).
    n_test = 4
    rng = np.random.RandomState(42)
    idx = rng.permutation(len(codes))
    test_idx, train_idx = idx[:n_test], idx[n_test:]

    train_ds = CodeDataset([codes[i] for i in train_idx], [labels[i] for i in train_idx], tokenizer)
    test_ds = CodeDataset([codes[i] for i in test_idx], [labels[i] for i in test_idx], tokenizer)

    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)
    args = TrainingArguments(
        output_dir=os.path.join(MODEL_DIR, "_checkpoints"),
        num_train_epochs=5,
        per_device_train_batch_size=2,
        logging_steps=5,
        save_strategy="no",
        report_to=[],
    )
    trainer = Trainer(model=model, args=args, train_dataset=train_ds)
    trainer.train()

    preds = trainer.predict(test_ds).predictions.argmax(axis=1)
    acc = (preds == np.array([labels[i] for i in test_idx])).mean()
    print(f"Hold-out accuracy on {n_test} samples: {acc:.3f} (sanity check only, n too small to trust)")

    # Fine-tune final model on the full dataset for serving.
    full_ds = CodeDataset(codes, labels, tokenizer)
    final_model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)
    final_args = TrainingArguments(
        output_dir=os.path.join(MODEL_DIR, "_checkpoints"),
        num_train_epochs=5,
        per_device_train_batch_size=2,
        logging_steps=5,
        save_strategy="no",
        report_to=[],
    )
    final_trainer = Trainer(model=final_model, args=final_args, train_dataset=full_ds)
    final_trainer.train()

    os.makedirs(MODEL_DIR, exist_ok=True)
    final_model.save_pretrained(MODEL_DIR)
    tokenizer.save_pretrained(MODEL_DIR)
    print(f"Saved final model to {MODEL_DIR}")


if __name__ == "__main__":
    main()
