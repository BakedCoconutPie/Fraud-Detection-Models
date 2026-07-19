"""FastAPI backend serving the three cheating-detection models.

Run with: uvicorn src.api.main:app --reload
"""
import json
import os
from collections import defaultdict
from typing import List

import joblib
import torch
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from src.models.bilstm_model import BiLSTMClassifier, encode
from src.models.explain import Explainer

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SVM_DIR = os.path.join(ROOT, "models", "svm")
BILSTM_DIR = os.path.join(ROOT, "models", "bilstm")
CODEBERT_DIR = os.path.join(ROOT, "models", "codebert")

app = FastAPI(title="PasteTrace Cheating Detector")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class CodeRequest(BaseModel):
    code: str


class PredictionResult(BaseModel):
    label: int
    label_name: str
    cheating_probability: float
    explanation: str


class BatchPredictionResult(PredictionResult):
    case: str
    student: str
    group: str


_state = {}


@app.on_event("startup")
def load_models():
    _state["svm_model"] = joblib.load(os.path.join(SVM_DIR, "svm.pkl"))
    _state["svm_vectorizer"] = joblib.load(os.path.join(SVM_DIR, "vectorizer.pkl"))

    with open(os.path.join(BILSTM_DIR, "config.json"), encoding="utf8") as f:
        cfg = json.load(f)
    with open(os.path.join(BILSTM_DIR, "vocab.json"), encoding="utf8") as f:
        vocab = json.load(f)
    bilstm = BiLSTMClassifier(cfg["vocab_size"], cfg["embed_dim"], cfg["hidden_dim"])
    bilstm.load_state_dict(torch.load(os.path.join(BILSTM_DIR, "bilstm.pt"), map_location="cpu"))
    bilstm.eval()
    _state["bilstm_model"] = bilstm
    _state["bilstm_vocab"] = vocab
    _state["bilstm_max_len"] = cfg["max_len"]

    _state["codebert_tokenizer"] = AutoTokenizer.from_pretrained(CODEBERT_DIR)
    codebert = AutoModelForSequenceClassification.from_pretrained(CODEBERT_DIR)
    codebert.eval()
    _state["codebert_model"] = codebert

    _state["explainer"] = Explainer()


def _result(label: int, prob: float, explanation: str) -> PredictionResult:
    return PredictionResult(
        label=label,
        label_name="Cheating" if label else "Normal",
        cheating_probability=float(prob),
        explanation=explanation,
    )


def predict_svm(code: str) -> PredictionResult:
    vec = _state["svm_vectorizer"].transform([code])
    prob = _state["svm_model"].predict_proba(vec)[0][1]
    label = int(prob >= 0.5)
    explanation = _state["explainer"].build_reason(
        code, label, svm_model=_state["svm_model"], svm_vectorizer=_state["svm_vectorizer"]
    )
    return _result(label, prob, explanation)


def predict_bilstm(code: str) -> PredictionResult:
    ids = encode(code, _state["bilstm_vocab"], _state["bilstm_max_len"]).unsqueeze(0)
    with torch.no_grad():
        prob = torch.sigmoid(_state["bilstm_model"](ids)).item()
    label = int(prob >= 0.5)
    explanation = _state["explainer"].build_reason(code, label)
    return _result(label, prob, explanation)


def predict_codebert(code: str) -> PredictionResult:
    tokenizer = _state["codebert_tokenizer"]
    enc = tokenizer(code, truncation=True, padding="max_length", max_length=256, return_tensors="pt")
    with torch.no_grad():
        logits = _state["codebert_model"](**enc).logits
        prob = torch.softmax(logits, dim=1)[0][1].item()
    label = int(prob >= 0.5)
    explanation = _state["explainer"].build_reason(code, label)
    return _result(label, prob, explanation)


PREDICTORS = {"svm": predict_svm, "bilstm": predict_bilstm, "codebert": predict_codebert}


@app.post("/predict/{model_name}", response_model=PredictionResult)
def predict(model_name: str, request: CodeRequest):
    if model_name not in PREDICTORS:
        return {"error": f"unknown model '{model_name}', choose one of {list(PREDICTORS)}"}
    return PREDICTORS[model_name](request.code)


@app.post("/predict-file/{model_name}", response_model=PredictionResult)
async def predict_file(model_name: str, file: UploadFile = File(...)):
    raw = await file.read()
    code = raw.decode("utf8", errors="ignore")
    return PREDICTORS[model_name](code)


def _group_key(relative_path: str):
    """Group an uploaded file's relative path into (case, student).

    Browsers report folder uploads as "<picked-folder>/<...>/<file>" via
    webkitRelativePath. When the user picks a case-study folder like "111"
    directly, parts[0] is "111" and parts[1] is the student letter -- the
    submission may still be nested deeper (e.g. extra-credit subfolders),
    so everything past parts[1] is treated as part of the same student.
    """
    parts = [p for p in relative_path.replace("\\", "/").split("/") if p]
    if len(parts) >= 2:
        return parts[0], parts[1]
    return parts[0] if parts else "unknown", ""


@app.post("/predict-folder/{model_name}", response_model=List[BatchPredictionResult])
async def predict_folder(model_name: str, files: List[UploadFile] = File(...)):
    if model_name not in PREDICTORS:
        return []

    groups = defaultdict(list)
    for f in files:
        if not f.filename.lower().endswith(".pde"):
            continue
        case, student = _group_key(f.filename)
        raw = await f.read()
        groups[(case, student)].append(raw.decode("utf8", errors="ignore"))

    results = []
    for (case, student), chunks in sorted(groups.items()):
        if not student:
            continue
        code = "\n\n".join(chunks)
        if not code.strip():
            continue
        pred = PREDICTORS[model_name](code)
        results.append(
            BatchPredictionResult(case=case, student=student, group=f"{case}/{student}", **pred.model_dump())
        )
    return results


@app.get("/health")
def health():
    return {"status": "ok", "models": list(PREDICTORS)}


static_dir = os.path.join(ROOT, "src", "ui")
if os.path.isdir(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="ui")
