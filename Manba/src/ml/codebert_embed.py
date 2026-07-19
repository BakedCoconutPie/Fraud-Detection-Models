"""Phase 6 — CodeBERT Embedding Extractor

Encodes each student's Processing (.pde) source code into a 768-dimensional
vector using microsoft/codebert-base as a **frozen** feature extractor.
No fine-tuning is performed — the pretrained model is used as-is.

Pipeline (matches the architecture diagram):

    code (.pde text)
          |
     tokenizer           (RobertaTokenizer, max 512 tokens per window)
          |
     CodeBERT            (microsoft/codebert-base, frozen, CPU or GPU)
          |
   embedding [768]       (CLS token of each window, averaged if code > 512 tokens)
          |
    embeddings.npy       (shape: [n_students, 768])

Long code handling
------------------
CodeBERT is limited to 512 tokens. For code that exceeds this limit
(common in Processing assignments), a sliding-window strategy is used:
- Window size : 512 tokens (full context)
- Stride      : 256 tokens (50 % overlap)
- Final vector: mean of all window CLS embeddings

Usage
-----
# Extract embeddings for all students in dataset.csv:
    python -m src.ml.codebert_embed

# Use the CodeBertEmbedder class directly in other scripts:
    from src.ml.codebert_embed import CodeBertEmbedder
    embedder = CodeBertEmbedder()
    vec = embedder.embed("void setup() { size(500,500); }")  # → np.array (768,)

Output files
------------
    data/embeddings.npy        shape [n, 768], float32
    data/embeddings_index.csv  columns: case, student, label
"""

import os

import numpy as np
import pandas as pd
import torch
from transformers import AutoModel, AutoTokenizer

DATASET_PATH = os.path.join("data", "dataset.csv")
EMBED_PATH   = os.path.join("data", "embeddings.npy")
INDEX_PATH   = os.path.join("data", "embeddings_index.csv")

MODEL_NAME   = "microsoft/codebert-base"
MAX_LEN      = 512   # CodeBERT hard limit
STRIDE       = 256   # overlap for sliding window


class CodeBertEmbedder:
    """Frozen CodeBERT used as a feature extractor (no gradient updates).

    Parameters
    ----------
    model_name : str
        HuggingFace model id, defaults to microsoft/codebert-base.
    device : str or None
        'cuda', 'cpu', or None (auto-detect).
    """

    def __init__(self, model_name: str = MODEL_NAME, device: str | None = None):
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = device

        print(f"Loading {model_name} on {device} ...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()
        self.model.to(self.device)

        # Freeze all parameters — we only extract features, not fine-tune.
        for param in self.model.parameters():
            param.requires_grad = False

        print("Model loaded. Parameters frozen.")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def embed(self, code: str) -> np.ndarray:
        """Return a 768-dim embedding for a single code string.

        If the tokenized code exceeds MAX_LEN tokens, a sliding window is
        used and the per-window CLS embeddings are averaged.

        Parameters
        ----------
        code : str
            Raw source code (any length).

        Returns
        -------
        np.ndarray  shape (768,), dtype float32
        """
        token_ids = self.tokenizer.encode(code, add_special_tokens=False)

        # Split into overlapping windows that fit within MAX_LEN.
        # Each window: [CLS] + up to 510 real tokens + [SEP]
        window_size = MAX_LEN - 2
        windows = self._sliding_windows(token_ids, window_size, STRIDE)

        cls_vectors = []
        for window in windows:
            input_ids = (
                [self.tokenizer.cls_token_id]
                + window
                + [self.tokenizer.sep_token_id]
            )
            input_tensor = torch.tensor([input_ids], dtype=torch.long).to(self.device)
            attention_mask = torch.ones_like(input_tensor)

            with torch.no_grad():
                outputs = self.model(
                    input_ids=input_tensor,
                    attention_mask=attention_mask,
                )
            # CLS token is position 0 of last_hidden_state
            cls_vec = outputs.last_hidden_state[0, 0, :].cpu().numpy()
            cls_vectors.append(cls_vec)

        # Average across windows (single window → just that CLS vector)
        return np.mean(cls_vectors, axis=0).astype(np.float32)

    def embed_batch(self, codes: list[str], verbose: bool = True) -> np.ndarray:
        """Embed a list of code strings.

        Parameters
        ----------
        codes   : list of str
        verbose : bool — print progress

        Returns
        -------
        np.ndarray  shape (len(codes), 768), dtype float32
        """
        embeddings = []
        for i, code in enumerate(codes):
            if verbose:
                print(f"  [{i+1}/{len(codes)}] embedding ({len(code)} chars) ...", end="\r")
            embeddings.append(self.embed(code))
        if verbose:
            print()
        return np.stack(embeddings, axis=0)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _sliding_windows(token_ids: list[int], window_size: int, stride: int) -> list[list[int]]:
        """Split token_ids into overlapping windows of at most window_size."""
        if len(token_ids) <= window_size:
            return [token_ids]
        windows = []
        start = 0
        while start < len(token_ids):
            end = min(start + window_size, len(token_ids))
            windows.append(token_ids[start:end])
            if end == len(token_ids):
                break
            start += stride
        return windows


# ----------------------------------------------------------------------
# Batch extraction script
# ----------------------------------------------------------------------

def main():
    df = pd.read_csv(DATASET_PATH, usecols=["case", "student", "label", "code"])
    print(f"Dataset: {len(df)} students  ({df['label'].sum()} cheat, {(df['label']==0).sum()} normal)")

    embedder = CodeBertEmbedder()

    print(f"\nExtracting embeddings ...")
    embeddings = embedder.embed_batch(df["code"].tolist(), verbose=True)

    os.makedirs("data", exist_ok=True)
    np.save(EMBED_PATH, embeddings)
    print(f"Saved embeddings: {EMBED_PATH}  shape={embeddings.shape}")

    index_df = df[["case", "student", "label"]].copy()
    index_df.to_csv(INDEX_PATH, index=False)
    print(f"Saved index    : {INDEX_PATH}")

    # Quick sanity check — cosine similarity between first two students
    if len(embeddings) >= 2:
        a, b = embeddings[0], embeddings[1]
        cos = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
        s0 = f"{df['case'].iloc[0]}/{df['student'].iloc[0]}"
        s1 = f"{df['case'].iloc[1]}/{df['student'].iloc[1]}"
        print(f"\nSanity check — cosine({s0}, {s1}) = {cos:.4f}")


if __name__ == "__main__":
    main()
