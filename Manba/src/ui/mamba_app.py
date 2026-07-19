"""Streamlit dashboard for the TaskTracker-only Mamba pipeline."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INDEX_PATH = PROJECT_ROOT / "data" / "mamba" / "index.csv"
SPLIT_DIR = PROJECT_ROOT / "data" / "splits" / "tasktracker"
MODEL_DIR = PROJECT_ROOT / "models" / "mamba"
RESULTS_DIR = PROJECT_ROOT / "results" / "mamba"
CANONICAL_INPUT = PROJECT_ROOT / "data" / "normalized" / "tasktracker"
LEGACY_INPUT = PROJECT_ROOT / "tasktracker"

st.set_page_config(page_title="Mamba Risk Detection", page_icon="🧬", layout="wide")
st.title("🧬 Mamba Behavioral-Risk Classifier")
st.caption("TaskTracker only | shared grouped train/validation/test splits | weak labels")


def run_command(arguments: list[str]) -> tuple[str, int]:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(PROJECT_ROOT)
    result = subprocess.run(
        [sys.executable, *arguments],
        cwd=PROJECT_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return (result.stdout + result.stderr).strip(), result.returncode


def load_json(path: Path) -> dict:
    try:
        with path.open(encoding="utf8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}


with st.sidebar:
    st.header("Pipeline status")
    status = {
        "TaskTracker sequences": INDEX_PATH.is_file(),
        "Fixed group split CSVs": all(
            (SPLIT_DIR / f"{name}.csv").is_file()
            for name in ("train", "validation", "test")
        ),
        "Mamba checkpoint": (MODEL_DIR / "mamba.pt").is_file(),
        "Test predictions": (RESULTS_DIR / "predictions.csv").is_file(),
        "Test metrics": (RESULTS_DIR / "metrics.json").is_file(),
    }
    for label, available in status.items():
        st.write(f"{'✅' if available else '⬜'} {label}")
    try:
        import torch

        st.write(f"{'✅' if torch.cuda.is_available() else '⚠️'} CUDA GPU")
    except ImportError:
        st.write("⚠️ PyTorch unavailable")


data_tab, train_tab, test_tab, predict_tab = st.tabs(
    ["1. Prepare data", "2. Train + validation", "3. Held-out test", "4. Predict one"]
)

with data_tab:
    st.subheader("Build TaskTracker event sequences")
    st.info(
        "Canonical input: data/normalized/tasktracker. The legacy "
        "tasktracker/normalized folder is also supported. PasteTrace is not used."
    )
    default_input = CANONICAL_INPUT if CANONICAL_INPUT.exists() else LEGACY_INPUT
    input_dir = st.text_input("Normalized TaskTracker folder", str(default_input))
    min_events = st.number_input("Minimum events", min_value=1, value=1, step=1)
    if st.button("Build TaskTracker sequences", type="primary"):
        output, code = run_command(
            [
                "-m",
                "src.data.build_sequences",
                "--input-dir",
                input_dir,
                "--min-events",
                str(int(min_events)),
            ]
        )
        st.code(output, language="text")
        st.success("Sequences built.") if code == 0 else st.error("Build failed.")

    if INDEX_PATH.is_file():
        frame = pd.read_csv(INDEX_PATH)
        c1, c2, c3 = st.columns(3)
        c1.metric("Sessions", len(frame))
        c2.metric("Participants/groups", frame["group_id"].nunique())
        c3.metric("Risk label=1", int((frame["label"] == 1).sum()))
        if st.button("Validate fixed group split CSVs"):
            output, code = run_command(["-m", "src.data.make_splits"])
            st.code(output, language="text")
            st.success("Fixed splits are valid; no file changed.") if code == 0 else st.error("Fixed split validation failed.")

with train_tab:
    st.subheader("Train on train split; select checkpoint and threshold on validation")
    st.warning("The held-out test CSV is verified but its samples are not loaded during training.")
    c1, c2, c3 = st.columns(3)
    d_model = c1.selectbox("d_model", [32, 64, 128], index=1)
    n_layers = c2.selectbox("layers", [1, 2, 3, 4], index=1)
    dropout = c3.slider("dropout", 0.0, 0.5, 0.2, 0.05)
    c4, c5, c6 = st.columns(3)
    epochs = c4.number_input("epochs", 1, 500, 80)
    batch_size = c5.selectbox("batch size", [4, 8, 16, 32], index=1)
    patience = c6.number_input("early-stop patience", 1, 50, 10)
    if st.button("Train Mamba", type="primary"):
        output, code = run_command(
            [
                "-m",
                "src.models.mamba_model",
                "train",
                "--d-model",
                str(d_model),
                "--n-layers",
                str(n_layers),
                "--dropout",
                str(dropout),
                "--epochs",
                str(int(epochs)),
                "--batch-size",
                str(batch_size),
                "--patience",
                str(int(patience)),
                "--seed",
                "42",
            ]
        )
        st.code(output, language="text")
        st.success("Best validation checkpoint saved.") if code == 0 else st.error("Training failed.")
    config = load_json(MODEL_DIR / "config.json")
    if config:
        st.json(config)

with test_tab:
    st.subheader("Evaluate the frozen model on the held-out TaskTracker test split")
    st.caption("Weights and threshold are frozen before this command reads test sessions.")
    if st.button("Run held-out test", type="primary"):
        output, code = run_command(["-m", "src.models.mamba_model", "test"])
        st.code(output, language="text")
        st.success("Test completed.") if code == 0 else st.error("Test failed.")
    metrics = load_json(RESULTS_DIR / "metrics.json")
    if metrics:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Precision", f"{metrics.get('precision', 0):.3f}")
        c2.metric("Recall", f"{metrics.get('recall', 0):.3f}")
        c3.metric("F1", f"{metrics.get('f1', 0):.3f}")
        c4.metric("Balanced accuracy", f"{metrics.get('balanced_accuracy', 0):.3f}")
        st.json(metrics)
    predictions_path = RESULTS_DIR / "predictions.csv"
    if predictions_path.is_file():
        st.dataframe(pd.read_csv(predictions_path), use_container_width=True)

with predict_tab:
    st.subheader("Predict one unlabeled normalized TaskTracker JSON")
    normalized_dir = default_input / "normalized" if (default_input / "normalized").is_dir() else default_input
    examples = sorted(normalized_dir.glob("*.json"))
    default_json = examples[0] if examples else normalized_dir / "session.json"
    input_path = st.text_input("Normalized JSON", str(default_json))
    if st.button("Predict"):
        output, code = run_command(["-m", "src.models.mamba_model", "predict", input_path])
        st.code(output, language="json")
        if code != 0:
            st.error("Prediction failed.")
