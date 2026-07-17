"""Mamba classifier using shared TaskTracker train/validation/test splits.

Commands::

    python -m src.models.mamba_model train
    python -m src.models.mamba_model test
    python -m src.models.mamba_model predict data/normalized/tasktracker/session.json

All labels are weak behavioral-risk labels: 0=normal-like, 1=risky. The test
split is never used for fitting, checkpoint selection, or threshold selection.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import random
import shutil
import time
from importlib.metadata import PackageNotFoundError, version as package_version
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
    roc_auc_score,
)
from torch.utils.data import DataLoader


MAMBA_DATA_DIR = Path("data") / "mamba"
SEQUENCE_DIR = MAMBA_DATA_DIR / "sequences"
INDEX_PATH = MAMBA_DATA_DIR / "index.csv"
SPLIT_DIR = Path("data") / "splits" / "tasktracker"
MODEL_DIR = Path("models") / "mamba"
RESULTS_DIR = Path("results") / "mamba"

D_MODEL = 64
N_LAYERS = 2
DROPOUT = 0.2
EPOCHS = 80
LR = 3e-4
WEIGHT_DECAY = 0.01
PATIENCE = 10
BATCH_SIZE = 8
MAX_LEN = 1000
D_STATE = 16
D_CONV = 4
EXPAND = 2
EXPECTED_SPLIT_SHAPES = {
    "train": {"sessions": 333, "groups": 191},
    "validation": {"sessions": 68, "groups": 37},
    "test": {"sessions": 69, "groups": 43},
}
EXPECTED_TEST_SESSIONS = EXPECTED_SPLIT_SHAPES["test"]["sessions"]
EXPECTED_TEST_RISK = 15
EXPECTED_TEST_NORMAL = 54


def _set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def _version(distribution: str) -> str | None:
    try:
        return package_version(distribution)
    except PackageNotFoundError:
        return None


def _software_versions() -> dict[str, str | None]:
    return {
        "python": platform.python_version(),
        "torch": torch.__version__,
        "mamba_ssm": _version("mamba-ssm"),
        "causal_conv1d": _version("causal-conv1d"),
        "numpy": np.__version__,
        "scikit_learn": _version("scikit-learn"),
    }


def _device_info(device: torch.device) -> dict[str, str | bool | None]:
    return {
        "device_type": device.type,
        "device_name": (
            torch.cuda.get_device_name(device) if device.type == "cuda" else platform.processor()
        ),
        "cuda_available": torch.cuda.is_available(),
        "cuda_version": torch.version.cuda,
    }


def _import_mamba():
    try:
        from mamba_ssm import Mamba

        return Mamba
    except (ImportError, OSError) as exc:
        raise RuntimeError(
            "Khong import duoc mamba-ssm. Hay dung GPU NVIDIA/CUDA va cai "
            "requirements-mamba.txt."
        ) from exc


class MambaBlock(nn.Module):
    def __init__(self, d_model: int):
        super().__init__()
        mamba_class = _import_mamba()
        self.norm = nn.LayerNorm(d_model)
        self.mamba = mamba_class(
            d_model=d_model,
            d_state=D_STATE,
            d_conv=D_CONV,
            expand=EXPAND,
        )

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return inputs + self.mamba(self.norm(inputs))


class MambaClassifier(nn.Module):
    def __init__(
        self,
        n_features: int,
        d_model: int = D_MODEL,
        n_layers: int = N_LAYERS,
        dropout: float = DROPOUT,
    ):
        super().__init__()
        self.input_proj = nn.Linear(n_features, d_model)
        self.blocks = nn.Sequential(*[MambaBlock(d_model) for _ in range(n_layers)])
        self.dropout = nn.Dropout(dropout)
        self.head = nn.Linear(d_model * 2, 1)

    def forward(self, inputs: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        hidden = self.blocks(self.input_proj(inputs))
        mask_float = mask.unsqueeze(-1).float()
        mean_pooled = (hidden * mask_float).sum(dim=1) / mask_float.sum(dim=1).clamp(min=1)
        masked_hidden = hidden.masked_fill(~mask.unsqueeze(-1), float("-inf"))
        max_pooled = masked_hidden.max(dim=1).values
        pooled = torch.cat([mean_pooled, max_pooled], dim=-1)
        return self.head(self.dropout(pooled)).squeeze(-1)


def _run_epoch(
    model: nn.Module,
    loader: DataLoader,
    device: torch.device,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
) -> tuple[float, list[int], list[float], list[str]]:
    training = optimizer is not None
    model.train(training)
    total_loss = 0.0
    y_true: list[int] = []
    y_prob: list[float] = []
    sample_ids: list[str] = []

    with torch.set_grad_enabled(training):
        for padded, _lengths, mask, ids, labels in loader:
            padded = padded.to(device)
            mask = mask.to(device)
            labels = labels.to(device)
            logits = model(padded, mask)
            if not torch.isfinite(logits).all():
                raise FloatingPointError("Model logits became NaN/Inf")
            loss = criterion(logits, labels)
            if not torch.isfinite(loss):
                raise FloatingPointError("Loss became NaN/Inf")

            if optimizer is not None:
                optimizer.zero_grad()
                loss.backward()
                grad_norm = nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                if not torch.isfinite(grad_norm):
                    raise FloatingPointError("Gradient norm became NaN/Inf")
                optimizer.step()

            total_loss += float(loss.item()) * len(labels)
            probabilities = torch.sigmoid(logits).detach().cpu().numpy()
            y_true.extend(labels.detach().cpu().numpy().astype(int).tolist())
            y_prob.extend(probabilities.astype(float).tolist())
            sample_ids.extend(ids)

    return total_loss / max(len(loader.dataset), 1), y_true, y_prob, sample_ids


def _metrics(y_true: list[int], y_prob: list[float], threshold: float) -> dict:
    scores = np.asarray(y_prob, dtype=float)
    if not np.all(np.isfinite(scores)):
        raise ValueError("Prediction scores contain NaN/Inf; retrain the model.")
    y_pred = (scores >= threshold).astype(int)
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=[0, 1], zero_division=0
    )
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    specificity = float(tn / (tn + fp)) if (tn + fp) else 0.0
    return {
        "precision": float(precision[1]),
        "recall": float(recall[1]),
        "f1": float(f1[1]),
        "auc": float(roc_auc_score(y_true, scores)) if len(set(y_true)) == 2 else None,
        "pr_auc": (
            float(average_precision_score(y_true, scores))
            if len(set(y_true)) == 2
            else None
        ),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "specificity": specificity,
        "tp": int(tp),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "normal_precision": float(precision[0]),
        "normal_recall": float(recall[0]),
        "normal_f1": float(f1[0]),
        "normal_support": int(support[0]),
        "risk_precision": float(precision[1]),
        "risk_recall": float(recall[1]),
        "risk_f1": float(f1[1]),
        "risk_support": int(support[1]),
    }


def _select_threshold(y_true: list[int], y_prob: list[float]) -> tuple[float, dict]:
    """Choose the validation threshold that maximizes positive-class F1."""
    candidates = np.unique(np.concatenate([np.asarray(y_prob, dtype=float), [0.5]]))
    best_threshold = 0.5
    best_metrics = _metrics(y_true, y_prob, best_threshold)
    best_key = (
        best_metrics["f1"],
        best_metrics["balanced_accuracy"],
        -abs(best_threshold - 0.5),
    )
    for threshold in candidates:
        metrics = _metrics(y_true, y_prob, float(threshold))
        key = (metrics["f1"], metrics["balanced_accuracy"], -abs(float(threshold) - 0.5))
        if key > best_key:
            best_threshold = float(threshold)
            best_metrics = metrics
            best_key = key
    return best_threshold, best_metrics


def _read_index() -> dict[str, dict[str, str]]:
    with INDEX_PATH.open(encoding="utf8", newline="") as handle:
        return {row["session_id"]: row for row in csv.DictReader(handle)}


def _read_split(path: Path) -> list[str]:
    with path.open(encoding="utf8", newline="") as handle:
        return [row["session_id"] for row in csv.DictReader(handle) if row.get("session_id")]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _required_inputs(
    validate_test_labels: bool,
) -> tuple[dict[str, list[str]], dict[str, dict[str, str]], dict]:
    paths = {
        "index": INDEX_PATH,
        "train": SPLIT_DIR / "train.csv",
        "validation": SPLIT_DIR / "validation.csv",
        "test": SPLIT_DIR / "test.csv",
    }
    for path in paths.values():
        if not path.is_file():
            raise SystemExit(
                f"[ERROR] Missing {path}; build sequences and place the team's fixed split CSVs."
            )
    index = _read_index()
    splits = {name: _read_split(paths[name]) for name in ("train", "validation", "test")}

    split_sets = {name: set(values) for name, values in splits.items()}
    if any(len(values) != len(split_sets[name]) for name, values in splits.items()):
        raise SystemExit("[ERROR] Duplicate session_id found inside split CSV.")
    overlap = (
        (split_sets["train"] & split_sets["validation"])
        | (split_sets["train"] & split_sets["test"])
        | (split_sets["validation"] & split_sets["test"])
    )
    if overlap:
        raise SystemExit("[ERROR] Session leakage found across split CSV files.")
    union = set().union(*split_sets.values())
    if union != set(index):
        raise SystemExit("[ERROR] Split CSV union does not exactly match TaskTracker index.")
    group_sets = {
        name: {index[session]["group_id"] for session in sessions}
        for name, sessions in splits.items()
    }
    group_overlap = (
        (group_sets["train"] & group_sets["validation"])
        | (group_sets["train"] & group_sets["test"])
        | (group_sets["validation"] & group_sets["test"])
    )
    if group_overlap:
        raise SystemExit("[ERROR] Participant/group leakage found across splits.")
    counts = {}
    for name, sessions in splits.items():
        labels = (
            [int(index[session]["label"]) for session in sessions]
            if name != "test" or validate_test_labels
            else []
        )
        counts[name] = {
            "sessions": len(sessions),
            "risk_1": labels.count(1) if labels else None,
            "normal_0": labels.count(0) if labels else None,
            "groups": len(group_sets[name]),
        }
    for name, expected in EXPECTED_SPLIT_SHAPES.items():
        actual = {key: counts[name][key] for key in expected}
        if actual != expected:
            raise SystemExit(
                f"[ERROR] Official {name} split mismatch: expected {expected}, "
                f"found {actual}. Replace all three CSV files in {SPLIT_DIR} "
                "with the fixed files supplied by the group; do not regenerate them."
            )
    if validate_test_labels:
        test_risk = counts["test"]["risk_1"]
        test_normal = counts["test"]["normal_0"]
        if test_risk != EXPECTED_TEST_RISK or test_normal != EXPECTED_TEST_NORMAL:
            raise SystemExit(
                "[ERROR] Official test label mismatch: expected risk=1: 15 and "
                f"normal=0: 54; found risk=1: {test_risk}, normal=0: {test_normal}."
            )
    manifest = {
        "dataset": "tasktracker",
        "label_type": "weak_behavioral_risk",
        "source": "fixed_group_csv_files",
        "counts": counts,
        "participant_overlap_count": 0,
        "total_sessions": sum(len(values) for values in splits.values()),
        "split_sha256": {
            name: _sha256(paths[name]) for name in ("train", "validation", "test")
        },
    }
    return splits, index, manifest


def _copy_split_inputs(manifest: dict) -> dict[str, dict[str, str | int]]:
    """Archive byte-for-byte copies of the split CSVs used for evaluation."""
    destination = RESULTS_DIR / "splits"
    destination.mkdir(parents=True, exist_ok=True)
    copies: dict[str, dict[str, str | int]] = {}
    for name in ("train", "validation", "test"):
        source = SPLIT_DIR / f"{name}.csv"
        saved_copy = destination / f"{name}.csv"
        shutil.copy2(source, saved_copy)
        copied_hash = _sha256(saved_copy)
        expected_hash = manifest["split_sha256"][name]
        if copied_hash != expected_hash:
            raise SystemExit(f"[ERROR] Split copy hash mismatch for {name}.csv")
        copies[name] = {
            "source": str(source),
            "saved_copy": str(saved_copy),
            "sha256": copied_hash,
            "sessions": int(manifest["counts"][name]["sessions"]),
            "groups": int(manifest["counts"][name]["groups"]),
        }
    return copies


def _verify_checkpoint_split_manifest(config: dict, current_manifest: dict) -> None:
    """Prevent evaluating a checkpoint trained with different split files."""
    trained_manifest = config.get("split_manifest")
    if not isinstance(trained_manifest, dict):
        raise SystemExit(
            "[ERROR] Model config has no training split manifest; retrain Mamba with "
            "the official fixed split files."
        )
    trained_hashes = trained_manifest.get("split_sha256")
    current_hashes = current_manifest.get("split_sha256")
    if trained_hashes != current_hashes:
        raise SystemExit(
            "[ERROR] The checkpoint was trained with different split CSV files. "
            "Replace the CSVs with the official group files, then rerun train and test. "
            f"Training hashes={trained_hashes}; current hashes={current_hashes}."
        )


def _make_loader(dataset, batch_size: int, shuffle: bool):
    from src.models.mamba_dataset import collate_fn

    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, collate_fn=collate_fn)


def _write_prediction_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _prediction_rows(
    ordered_ids: list[str],
    y_true: list[int],
    y_prob: list[float],
    threshold: float,
    max_len: int,
) -> list[dict]:
    rows: list[dict] = []
    for session_id, truth, score in zip(ordered_ids, y_true, y_prob):
        with (SEQUENCE_DIR / f"{session_id}.json").open(encoding="utf8") as handle:
            record = json.load(handle)
        pred = int(score >= threshold)
        summary = record.get("behavior_summary", {})
        n_events = int(record.get("n_events", 0))
        rows.append(
            {
                # Required common comparison schema (keep these four first).
                "session_id": session_id,
                "true_label": truth,
                "risk_score": score,
                "pred_label": pred,
                # Mamba-specific audit fields.
                "threshold": threshold,
                "correct": int(truth == pred),
                "n_events": n_events,
                "n_events_used": min(n_events, max_len),
                "sequence_truncated": int(n_events > max_len),
                "evidence_status": (
                    "INSUFFICIENT_EVENTS" if n_events < 3 else "OK"
                ),
                "type_events": summary.get("type_events", 0),
                "paste_events": summary.get("paste_events", 0),
                "cut_events": summary.get("cut_events", 0),
                "typed_chars": summary.get("typed_chars", 0),
                "pasted_chars": summary.get("pasted_chars", 0),
                "cut_chars": summary.get("cut_chars", 0),
                "max_paste_chars": summary.get("max_paste_chars", 0),
                "duration_sec": summary.get("duration_sec", 0.0),
            }
        )
    return rows


def cmd_train(args: argparse.Namespace) -> None:
    from src.data.build_sequences import FEATURE_NAMES
    from src.models.mamba_dataset import SequenceDataset, build_scaler_from_ids

    _set_seed(args.seed)
    splits, _index, manifest = _required_inputs(validate_test_labels=False)
    train_ids = splits["train"]
    validation_ids = splits["validation"]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    print(
        f"TaskTracker: train={len(train_ids)}, validation={len(validation_ids)}, "
        f"held-out test={len(splits['test'])}"
    )
    print("Held-out test event sequences are not used for training or threshold selection.")

    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)
    started = time.perf_counter()
    scaler = build_scaler_from_ids(train_ids, str(SEQUENCE_DIR), max_len=args.max_len)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    scaler.save(str(MODEL_DIR / "scaler.json"))
    train_dataset = SequenceDataset(train_ids, str(SEQUENCE_DIR), scaler, args.max_len)
    validation_dataset = SequenceDataset(
        validation_ids, str(SEQUENCE_DIR), scaler, args.max_len
    )
    train_loader = _make_loader(train_dataset, args.batch_size, True)
    validation_loader = _make_loader(validation_dataset, args.batch_size, False)

    labels = np.array([int(item["label"].item()) for item in train_dataset])
    positives = int(labels.sum())
    negatives = int(len(labels) - positives)
    pos_weight = torch.tensor([negatives / max(positives, 1)], device=device)
    n_features = int(train_dataset[0]["seq"].shape[1])
    try:
        model = MambaClassifier(n_features, args.d_model, args.n_layers, args.dropout).to(device)
    except RuntimeError as exc:
        raise SystemExit(f"[ERROR] {exc}") from exc
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=args.lr, weight_decay=args.weight_decay
    )

    model_path = MODEL_DIR / "mamba.pt"
    best_f1 = -1.0
    best_loss = float("inf")
    best_epoch = 0
    best_threshold = 0.5
    stale_epochs = 0
    stopped_reason = "completed"
    history: list[dict] = []
    print(f"{'Epoch':>5} {'TrainLoss':>10} {'ValLoss':>10} {'ValF1':>8} {'Threshold':>10}")

    for epoch in range(1, args.epochs + 1):
        try:
            train_loss, *_ = _run_epoch(model, train_loader, device, criterion, optimizer)
            val_loss, val_true, val_prob, _ = _run_epoch(
                model, validation_loader, device, criterion
            )
        except FloatingPointError as exc:
            stopped_reason = f"non_finite: {exc}"
            print(f"[STOP] {stopped_reason}")
            break
        threshold, val_metrics = _select_threshold(val_true, val_prob)
        val_f1 = float(val_metrics["f1"])
        print(f"{epoch:5d} {train_loss:10.4f} {val_loss:10.4f} {val_f1:8.4f} {threshold:10.4f}")
        history.append(
            {
                "epoch": epoch,
                "train_loss": train_loss,
                "validation_loss": val_loss,
                "validation_f1": val_f1,
                "validation_balanced_accuracy": val_metrics["balanced_accuracy"],
                "validation_threshold": threshold,
                "learning_rate": float(optimizer.param_groups[0]["lr"]),
            }
        )
        improved = val_f1 > best_f1 + 1e-8 or (
            abs(val_f1 - best_f1) <= 1e-8 and val_loss < best_loss
        )
        if improved:
            torch.save(model.state_dict(), model_path)
            best_f1 = val_f1
            best_loss = val_loss
            best_epoch = epoch
            best_threshold = threshold
            stale_epochs = 0
        else:
            stale_epochs += 1
            if stale_epochs >= args.patience:
                stopped_reason = "early_stopping"
                print(f"Early stopping at epoch {epoch}.")
                break

    if best_epoch == 0:
        raise SystemExit("[ERROR] No finite validation checkpoint was saved.")
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    train_runtime = time.perf_counter() - started
    train_peak_memory_mb = (
        float(torch.cuda.max_memory_allocated(device) / (1024**2))
        if device.type == "cuda"
        else None
    )
    n_parameters = int(sum(parameter.numel() for parameter in model.parameters()))
    n_trainable_parameters = int(
        sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)
    )

    history_path = RESULTS_DIR / "training_history.csv"
    _write_prediction_csv(history_path, history)
    config = {
        "dataset": "tasktracker",
        "label_type": "weak_behavioral_risk",
        "training_seed": args.seed,
        "random_state": args.seed,
        "software_versions": _software_versions(),
        "device": _device_info(device),
        "n_features": n_features,
        "feature_names": FEATURE_NAMES,
        "d_model": args.d_model,
        "input_projection": (
            f"torch.nn.Linear(in_features={n_features}, out_features={args.d_model}, "
            "bias=True), applied independently to every event"
        ),
        "n_layers": args.n_layers,
        "d_state": D_STATE,
        "d_conv": D_CONV,
        "expand": EXPAND,
        "dropout": args.dropout,
        "max_len": args.max_len,
        "padding": "right padding with zero vectors to the longest sequence in each batch",
        "masking": "boolean valid-token mask; padding excluded from mean and max pooling",
        "truncation": "keep the first max_len events in chronological order",
        "empty_session_policy": "reject zero-event sessions; accept 1-2 events with INSUFFICIENT_EVENTS audit flag",
        "best_epoch": best_epoch,
        "best_validation_f1": best_f1,
        "best_validation_loss": best_loss,
        "decision_threshold": best_threshold,
        "threshold_selection": "maximize_positive_f1_on_validation",
        "epochs_requested": args.epochs,
        "epochs_completed": len(history),
        "stopped_reason": stopped_reason,
        "pooling": "masked_mean_plus_max",
        "block_normalization": (
            "pre-norm residual in every block: x = x + Mamba(LayerNorm(x)); "
            "each block has its own torch.nn.LayerNorm(d_model); no additional "
            "LayerNorm after the block stack"
        ),
        "classification_head": "concat(masked_mean, masked_max) -> dropout -> Linear(2*d_model, 1)",
        "optimizer": "AdamW",
        "learning_rate": args.lr,
        "weight_decay": args.weight_decay,
        "batch_size": args.batch_size,
        "max_epochs": args.epochs,
        "loss_function": "BCEWithLogitsLoss",
        "class_imbalance": {
            "method": "positive class weight from train split only",
            "formula": "pos_weight = n_train_label_0 / n_train_label_1",
            "pos_weight": float(negatives / max(positives, 1)),
        },
        "early_stopping_patience": args.patience,
        "checkpoint_selection": "highest positive-class F1 on validation; validation loss breaks ties",
        "feature_encoding": {
            "is_type": "1[event_type == type], otherwise 0; not standardized",
            "is_paste": "1[event_type == paste], otherwise 0; not standardized",
            "is_cut": "1[event_type == cut], otherwise 0; not standardized",
            "log_len": "raw=log(1+text_length); z=(raw-train_mean)/train_std",
            "paste_log_len": "log(1+text_length) for paste, otherwise 0; not standardized",
            "is_large_paste": "1[paste and text_length >= 128], otherwise 0; not standardized",
            "log_delta_time": "raw=log(1+max(0,t_i-t_(i-1))); z=(raw-train_mean)/train_std",
        },
        "scaler": {
            "fit_split": "train",
            "continuous_feature_indices": [3, 6],
            "mean": scaler.mean_.tolist(),
            "std": scaler.std_.tolist(),
        },
        "n_parameters": n_parameters,
        "n_trainable_parameters": n_trainable_parameters,
        "train_peak_memory_mb": train_peak_memory_mb,
        "model_size_mb": float(model_path.stat().st_size / (1024**2)),
        "n_train_sessions": len(train_ids),
        "n_validation_sessions": len(validation_ids),
        "n_test_sessions_held_out": len(splits["test"]),
        "train_runtime_sec": train_runtime,
        "runtime_comparison_note": (
            "Runtime is descriptive for the recorded hardware only; do not compare "
            "speed directly with a model measured on different hardware."
        ),
        "split_manifest": manifest,
    }
    with (MODEL_DIR / "config.json").open("w", encoding="utf8") as handle:
        json.dump(config, handle, indent=2, ensure_ascii=False, allow_nan=False)

    # Save validation predictions from the selected checkpoint for threshold audit.
    state = torch.load(model_path, map_location=device)
    model.load_state_dict(state)
    model.eval()
    _, val_true, val_prob, val_ids = _run_epoch(model, validation_loader, device, criterion)
    validation_rows = _prediction_rows(
        val_ids, val_true, val_prob, best_threshold, args.max_len
    )
    _write_prediction_csv(RESULTS_DIR / "validation_predictions.csv", validation_rows)
    print(f"Best checkpoint: epoch={best_epoch}, validation_f1={best_f1:.4f}")
    print(f"Validation-selected threshold: {best_threshold:.6f}")
    print(f"Train runtime: {train_runtime:.2f} sec")
    print(f"Parameters: {n_parameters:,}")
    print(f"Peak train GPU memory: {train_peak_memory_mb} MB")


def _load_model_and_scaler(device: torch.device):
    from src.models.mamba_dataset import SequenceScaler

    paths = {
        "model": MODEL_DIR / "mamba.pt",
        "config": MODEL_DIR / "config.json",
        "scaler": MODEL_DIR / "scaler.json",
    }
    for path in paths.values():
        if not path.is_file():
            raise SystemExit(f"[ERROR] Missing {path}; train Mamba first.")
    with paths["config"].open(encoding="utf8") as handle:
        config = json.load(handle)
    if config.get("dataset") != "tasktracker":
        raise SystemExit("[ERROR] Saved model is not a TaskTracker-only model.")
    scaler = SequenceScaler.load(str(paths["scaler"]))
    try:
        model = MambaClassifier(
            config["n_features"], config["d_model"], config["n_layers"], config["dropout"]
        )
    except RuntimeError as exc:
        raise SystemExit(f"[ERROR] {exc}") from exc
    state = torch.load(paths["model"], map_location=device)
    invalid = [
        name
        for name, tensor in state.items()
        if torch.is_tensor(tensor) and not torch.isfinite(tensor).all()
    ]
    if invalid:
        raise SystemExit(f"[ERROR] Saved model contains NaN/Inf: {', '.join(invalid[:5])}")
    model.load_state_dict(state)
    model.to(device).eval()
    return model, scaler, config


def cmd_test(args: argparse.Namespace) -> None:
    from src.models.mamba_dataset import SequenceDataset

    splits, _index, manifest = _required_inputs(validate_test_labels=True)
    test_ids = splits["test"]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, scaler, config = _load_model_and_scaler(device)
    _verify_checkpoint_split_manifest(config, manifest)
    test_dataset = SequenceDataset(test_ids, str(SEQUENCE_DIR), scaler, int(config["max_len"]))
    test_loader = _make_loader(test_dataset, args.batch_size, False)
    criterion = nn.BCEWithLogitsLoss()
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)
        torch.cuda.synchronize()
    started = time.perf_counter()
    test_loss, y_true, y_prob, ordered_ids = _run_epoch(model, test_loader, device, criterion)
    if device.type == "cuda":
        torch.cuda.synchronize()
    inference_runtime = time.perf_counter() - started
    inference_peak_memory_mb = (
        float(torch.cuda.max_memory_allocated(device) / (1024**2))
        if device.type == "cuda"
        else None
    )

    threshold = float(config["decision_threshold"])
    common_metrics = _metrics(y_true, y_prob, threshold)
    metrics = {
        # Required shared comparison fields.
        "n_test_sessions": len(y_true),
        "threshold": threshold,
        "precision": common_metrics["precision"],
        "recall": common_metrics["recall"],
        "f1": common_metrics["f1"],
        "auc": common_metrics["auc"],
        "pr_auc": common_metrics["pr_auc"],
        "balanced_accuracy": common_metrics["balanced_accuracy"],
        "specificity": common_metrics["specificity"],
        "tp": common_metrics["tp"],
        "tn": common_metrics["tn"],
        "fp": common_metrics["fp"],
        "fn": common_metrics["fn"],
        "train_runtime_sec": float(config["train_runtime_sec"]),
        "inference_runtime_sec": inference_runtime,
        "model_size_mb": float((MODEL_DIR / "mamba.pt").stat().st_size / (1024**2)),
        "random_state": int(config["random_state"]),
        "mamba_package": "mamba-ssm",
        "mamba_package_version": config["software_versions"]["mamba_ssm"],
        # Mamba-specific reproducibility and diagnostic fields.
        "model": "mamba",
        "dataset": "tasktracker",
        "split": "test",
        "label_type": "weak_behavioral_risk",
        "threshold_selection": config["threshold_selection"],
        "accuracy": common_metrics["accuracy"],
        "macro_f1": common_metrics["macro_f1"],
        "normal_precision": common_metrics["normal_precision"],
        "normal_recall": common_metrics["normal_recall"],
        "normal_f1": common_metrics["normal_f1"],
        "normal_support": common_metrics["normal_support"],
        "risk_support": common_metrics["risk_support"],
        "test_loss": test_loss,
        "best_epoch": config["best_epoch"],
        "best_validation_f1": config["best_validation_f1"],
        "input_features": config["feature_names"],
        "max_len": config["max_len"],
        "d_model": config["d_model"],
        "n_layers": config["n_layers"],
        "pooling": config["pooling"],
        "n_parameters": config["n_parameters"],
        "n_trainable_parameters": config["n_trainable_parameters"],
        "train_peak_memory_mb": config["train_peak_memory_mb"],
        "inference_peak_memory_mb": inference_peak_memory_mb,
        "software_versions": config["software_versions"],
        "training_device": config["device"],
        "inference_device": _device_info(device),
        "mamba_method": {
            "event_encoding": config["feature_encoding"],
            "scaler": config["scaler"],
            "max_len": config["max_len"],
            "padding": config["padding"],
            "masking": config["masking"],
            "truncation": config["truncation"],
            "empty_session_policy": config["empty_session_policy"],
            "d_model": config["d_model"],
            "input_projection": config["input_projection"],
            "n_layers": config["n_layers"],
            "d_state": config["d_state"],
            "d_conv": config["d_conv"],
            "expand": config["expand"],
            "dropout": config["dropout"],
            "block_normalization": config["block_normalization"],
            "pooling": config["pooling"],
            "classification_head": config["classification_head"],
            "optimizer": config["optimizer"],
            "learning_rate": config["learning_rate"],
            "weight_decay": config["weight_decay"],
            "batch_size": config["batch_size"],
            "max_epochs": config["max_epochs"],
            "loss_function": config["loss_function"],
            "class_imbalance": config["class_imbalance"],
            "early_stopping_patience": config["early_stopping_patience"],
            "checkpoint_selection": config["checkpoint_selection"],
            "threshold_selection": config["threshold_selection"],
        },
        "score_definition": "risk_score = sigmoid(model_logit), in [0,1], not calibrated probability",
        "label_note": "Weak behavioral-risk label; not confirmed evidence of cheating.",
        "runtime_comparison_note": config["runtime_comparison_note"],
        "split_manifest": manifest,
    }
    rows = _prediction_rows(
        ordered_ids, y_true, y_prob, threshold, int(config["max_len"])
    )
    if len(rows) != EXPECTED_TEST_SESSIONS or ordered_ids != test_ids:
        raise SystemExit(
            "[ERROR] Prediction output does not exactly match the ordered official test.csv."
        )
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    split_files_used = _copy_split_inputs(manifest)
    metrics["split_files_used"] = split_files_used
    predictions_path = RESULTS_DIR / "predictions.csv"
    metrics_path = RESULTS_DIR / "metrics.json"
    method_path = RESULTS_DIR / "method.json"
    _write_prediction_csv(predictions_path, rows)
    with metrics_path.open("w", encoding="utf8") as handle:
        json.dump(metrics, handle, indent=2, ensure_ascii=False, allow_nan=False)
    method_report = {
        "model": "Mamba behavioral-risk classifier",
        "package": metrics["mamba_package"],
        "package_version": metrics["mamba_package_version"],
        "software_versions": metrics["software_versions"],
        "training_device": metrics["training_device"],
        "inference_device": metrics["inference_device"],
        "n_parameters": metrics["n_parameters"],
        "n_trainable_parameters": metrics["n_trainable_parameters"],
        "model_size_mb": metrics["model_size_mb"],
        "train_peak_memory_mb": metrics["train_peak_memory_mb"],
        "inference_peak_memory_mb": metrics["inference_peak_memory_mb"],
        "runtime_comparison_note": metrics["runtime_comparison_note"],
        "split_manifest": metrics["split_manifest"],
        "split_files_used": split_files_used,
        **metrics["mamba_method"],
    }
    with method_path.open("w", encoding="utf8") as handle:
        json.dump(method_report, handle, indent=2, ensure_ascii=False, allow_nan=False)

    print(f"TaskTracker held-out test: {len(y_true)} sessions")
    print(f"Threshold         : {threshold:.6f} (selected on validation)")
    print(f"Precision         : {metrics['precision']:.4f}")
    print(f"Recall            : {metrics['recall']:.4f}")
    print(f"F1                : {metrics['f1']:.4f}")
    print(f"AUC               : {metrics['auc']:.4f}")
    print(f"PR-AUC            : {metrics['pr_auc']:.4f}")
    print(f"Balanced accuracy : {metrics['balanced_accuracy']:.4f}")
    print(f"Specificity       : {metrics['specificity']:.4f}")
    print(f"Confusion          : TP={metrics['tp']} TN={metrics['tn']} FP={metrics['fp']} FN={metrics['fn']}")
    print(f"Predictions        : {predictions_path}")
    print(f"Metrics            : {metrics_path}")
    print(f"Method             : {method_path}")
    print(f"Split copies       : {RESULTS_DIR / 'splits'}")


def cmd_predict(args: argparse.Namespace) -> dict:
    from src.data.build_sequences import extract_normalized_sequence

    input_path = Path(args.input)
    if not input_path.is_file() or input_path.suffix.lower() != ".json":
        raise SystemExit("[ERROR] predict requires one normalized JSON file.")
    with input_path.open(encoding="utf8", errors="ignore") as handle:
        record = json.load(handle)
    sequence, _ = extract_normalized_sequence(record)
    if not sequence:
        raise SystemExit("[ERROR] JSON has no valid type/paste/cut events.")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, scaler, config = _load_model_and_scaler(device)
    scaled = scaler.transform(sequence[: int(config["max_len"])])
    tensor = torch.tensor(scaled, dtype=torch.float32).unsqueeze(0).to(device)
    mask = torch.ones(1, tensor.shape[1], dtype=torch.bool, device=device)
    with torch.no_grad():
        score = float(torch.sigmoid(model(tensor, mask)).item())
    threshold = float(config["decision_threshold"])
    pred_label = int(score >= threshold)
    result = {
        "session_id": record.get("session_id", input_path.stem),
        "risk_score": score,
        "pred_label": pred_label,
        "threshold": threshold,
        "n_events": len(scaled),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="TaskTracker-only Mamba risk classifier")
    subparsers = parser.add_subparsers(dest="command", required=True)
    train_parser = subparsers.add_parser("train", help="Train and select threshold on validation")
    train_parser.add_argument("--d-model", type=int, default=D_MODEL)
    train_parser.add_argument("--n-layers", type=int, default=N_LAYERS)
    train_parser.add_argument("--dropout", type=float, default=DROPOUT)
    train_parser.add_argument("--epochs", type=int, default=EPOCHS)
    train_parser.add_argument("--lr", type=float, default=LR)
    train_parser.add_argument("--weight-decay", type=float, default=WEIGHT_DECAY)
    train_parser.add_argument("--patience", type=int, default=PATIENCE)
    train_parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    train_parser.add_argument("--max-len", type=int, default=MAX_LEN)
    train_parser.add_argument("--seed", type=int, default=42)
    test_parser = subparsers.add_parser("test", help="Evaluate once on held-out TaskTracker test")
    test_parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    predict_parser = subparsers.add_parser("predict", help="Predict one unlabeled normalized JSON")
    predict_parser.add_argument("input")

    args = parser.parse_args()
    if args.command == "train":
        cmd_train(args)
    elif args.command == "test":
        cmd_test(args)
    else:
        cmd_predict(args)


if __name__ == "__main__":
    main()
