"""Phase 8 — Teacher Dashboard

Streamlit UI để import data, chạy ML pipeline và xem kết quả phân tích gian lận.

Chạy:
    streamlit run src/ui/streamlit_app.py

Hai chế độ hoạt động:
  TRAIN  — thư mục có agrigation.csv (nhãn giảng viên) → train + lưu model
  PREDICT — thư mục KHÔNG có nhãn (code + meta.json thuần) → load model đã lưu → dự đoán
"""

import os
import subprocess
import sys

import numpy as np
import pandas as pd
import streamlit as st

# ── Paths ──────────────────────────────────────────────────────────────
_HERE        = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

DATA_DIR          = os.path.join(PROJECT_ROOT, "data")
DATASET_PATH      = os.path.join(DATA_DIR, "dataset.csv")
FEAT_PATH         = os.path.join(DATA_DIR, "features.csv")
EMBED_PATH        = os.path.join(DATA_DIR, "embeddings.npy")
INDEX_PATH        = os.path.join(DATA_DIR, "embeddings_index.csv")
MODEL_SAVE_PATH   = os.path.join(PROJECT_ROOT, "models", "fusion_xgb.pkl")

_DEFAULT_PREPROC = os.path.join(
    PROJECT_ROOT, "PasteTrace-release", "PasteTrace-release",
    "case studies", "sp2023", "pre-processed",
)

FEATURE_COLS = [
    "total_events", "type_count", "paste_count", "paste_ratio",
    "max_paste_length", "external_paste", "ext_paste_ratio",
    "pasted_char_frac", "ext_char_frac", "typed_chars",
]

RISK_RULES = [
    ("ext_char_frac",    0.30, "≥ 30% code từ external paste"),
    ("pasted_char_frac", 0.60, "≥ 60% code được insert bằng paste"),
    ("external_paste",   1,    "Phát hiện external paste event"),
    ("paste_ratio",      0.05, "Paste chiếm > 5% tổng keystroke"),
    ("max_paste_length", 200,  "Cú paste lớn ≥ 200 ký tự"),
]

# ── Page config ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PasteTrace – Cheating Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  .card-cheat  { border-left:5px solid #e53935; background:#fff5f5; padding:14px 18px;
                 border-radius:6px; margin-bottom:12px; }
  .card-normal { border-left:5px solid #43a047; background:#f4fff4; padding:14px 18px;
                 border-radius:6px; margin-bottom:12px; }
  .card-unknown{ border-left:5px solid #888; background:#f8f8f8; padding:14px 18px;
                 border-radius:6px; margin-bottom:12px; }
  .sid         { font-size:1.1em; font-weight:700; }
  .badge-cheat { background:#e53935; color:#fff; font-size:0.75em;
                 padding:2px 8px; border-radius:12px; font-weight:700; }
  .badge-norm  { background:#43a047; color:#fff; font-size:0.75em;
                 padding:2px 8px; border-radius:12px; font-weight:700; }
  .badge-risk  { background:#555; color:#fff; font-size:0.72em;
                 padding:2px 7px; border-radius:10px; }
  .mode-train  { background:#1565c0; color:#fff; font-size:0.8em;
                 padding:3px 10px; border-radius:12px; font-weight:700; }
  .mode-pred   { background:#e65100; color:#fff; font-size:0.8em;
                 padding:3px 10px; border-radius:12px; font-weight:700; }
  .ok  { color:#43a047; font-weight:700; }
  .bad { color:#e53935; font-weight:700; }
  .bar { font-family:monospace; font-size:1.15em; letter-spacing:1px; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════

def _exists(path: str) -> bool:
    return path is not None and os.path.exists(path)


def _get_root() -> str:
    base    = st.session_state.get("data_root", _DEFAULT_PREPROC)
    use_raw = st.session_state.get("use_raw", False)
    return os.path.join(base, "RawData") if use_raw else base


def _detect_mode(root: str) -> str:
    """Return 'train', 'predict', or 'unknown' based on whether labels exist."""
    if not os.path.isdir(root):
        return "unknown"
    for d in os.listdir(root):
        if os.path.isdir(os.path.join(root, d)):
            if os.path.isfile(os.path.join(root, d, "agrigation.csv")):
                return "train"
    return "predict"


def _run(module: str, extra_args: list | None = None) -> tuple[bool, str]:
    cmd = [sys.executable, "-m", module] + (extra_args or [])
    proc = subprocess.run(
        cmd, cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=600,
    )
    out = proc.stdout
    if proc.stderr.strip():
        out += "\n[stderr]\n" + proc.stderr
    return proc.returncode == 0, out


def _feature_score(row: pd.Series) -> float:
    s  = 0.40 * min(float(row.get("ext_char_frac",    0)), 1.0)
    s += 0.25 * min(float(row.get("pasted_char_frac", 0)), 1.0)
    s += 0.20 * min(float(row.get("external_paste",   0)) / 5, 1.0)
    s += 0.15 * min(float(row.get("paste_ratio",      0)) * 10, 1.0)
    return round(s, 4)


def _reasons(row: pd.Series) -> list[str]:
    out = []
    for col, thresh, desc in RISK_RULES:
        if col in row and float(row[col]) >= thresh:
            v = row[col]
            disp = f"{v:.3f}" if isinstance(v, float) else str(int(v))
            out.append(f"{desc}  <small>({col} = {disp})</small>")
    return out or ["Không phát hiện tín hiệu bất thường"]


def _bar(score: float, color: str, width: int = 20) -> str:
    f = int(round(score * width))
    return (
        f'<span class="bar"><span style="color:{color}">{"█"*f}</span>'
        f'{"░"*(width-f)}</span>'
    )


def _open_folder_dialog() -> str | None:
    """Open native folder picker via tkinter. Returns selected path or None."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        tk_root = tk.Tk()
        tk_root.withdraw()
        tk_root.wm_attributes("-topmost", 1)
        folder = filedialog.askdirectory(
            title="Chọn thư mục dữ liệu PasteTrace",
            initialdir=st.session_state.get("data_root", os.path.expanduser("~")),
        )
        tk_root.destroy()
        return os.path.normpath(folder) if folder else None
    except Exception as e:
        st.error(f"Không mở được folder picker: {e}")
        return None


# ══════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.title("🔍 PasteTrace")

    # ── 1. DATA SOURCE ────────────────────────────────────────────────
    st.subheader("📁 Nguồn dữ liệu")

    if "data_root" not in st.session_state:
        st.session_state["data_root"] = _DEFAULT_PREPROC
    if "use_raw" not in st.session_state:
        st.session_state["use_raw"] = False

    # --- Folder browser button ---
    col_browse, col_raw = st.columns([1, 1])
    if col_browse.button("📁 Chọn folder", use_container_width=True):
        picked = _open_folder_dialog()
        if picked:
            st.session_state["data_root"] = picked
            st.rerun()

    use_raw = col_raw.checkbox("RawData", value=st.session_state["use_raw"])
    if use_raw != st.session_state["use_raw"]:
        st.session_state["use_raw"] = use_raw
        st.rerun()

    # Show current path (read-only display)
    effective_root = (
        os.path.join(st.session_state["data_root"], "RawData")
        if use_raw else st.session_state["data_root"]
    )
    st.caption("Thư mục đang dùng:")
    st.code(effective_root, language=None)

    # --- Mode detection & status ---
    root_ok = os.path.isdir(effective_root)
    mode    = _detect_mode(effective_root) if root_ok else "unknown"

    if root_ok:
        cases_found = sorted(
            d for d in os.listdir(effective_root)
            if os.path.isdir(os.path.join(effective_root, d)) and d not in ("RawData",)
        )
        if mode == "train":
            st.success(
                f"**Chế độ TRAIN** · {len(cases_found)} case(s): "
                f"{', '.join(cases_found)}\n\n"
                "Có `agrigation.csv` → pipeline sẽ **train + lưu model**."
            )
        elif mode == "predict":
            st.warning(
                f"**Chế độ PREDICT** · {len(cases_found)} case(s): "
                f"{', '.join(cases_found)}\n\n"
                "Không có nhãn → pipeline sẽ **load model đã train** để dự đoán."
            )
            if not _exists(MODEL_SAVE_PATH):
                st.error("⚠️ Chưa có model đã train! Hãy chạy pipeline TRAIN trước.")
    else:
        st.error("❌ Thư mục không tồn tại")

    with st.expander("ℹ️ Pre-processed vs RawData"):
        st.markdown(
            "**Pre-processed** (khuyên dùng): meta.json đã decode, "
            "History events đọc được ngay.\n\n"
            "**RawData**: bản gốc thô — tích checkbox để dùng subfolder `RawData/` bên trong."
        )

    st.divider()

    # ── 2. PIPELINE STEPS ─────────────────────────────────────────────
    st.subheader("🔧 Pipeline")

    if mode == "predict":
        st.caption("Chế độ PREDICT: bước 4 sẽ dùng model đã lưu")
    else:
        st.caption("Chạy từng bước theo thứ tự ↓")

    STEPS = [
        ("1 · Build Dataset",       "src.data.build_dataset", DATASET_PATH, False, True),
        ("2 · Extract Features",    "src.ml.features",        FEAT_PATH,    False, True),
        ("3 · CodeBERT Embeddings", "src.ml.codebert_embed",  EMBED_PATH,   True,  False),
        ("4 · Fusion (XGBoost)",    "src.ml.fusion_model",    None,         False, False),
    ]

    for label, module, outfile, heavy, needs_root in STEPS:
        done = _exists(outfile)
        icon = "✅" if done else "⬜"
        col1, col2 = st.columns([4, 1])
        col1.markdown(f"{icon} **{label}**")
        if col2.button("▶", key=f"btn_{module}"):
            if heavy:
                st.warning("⚠️ Tải model ~500 MB lần đầu — cần internet & vài phút.")
            extra = ["--root", effective_root] if needs_root and root_ok else []
            with st.spinner("Running …"):
                ok, out = _run(module, extra)
            st.toast("✅ Xong!" if ok else "❌ Lỗi!", icon="✅" if ok else "❌")
            with st.expander("Output"):
                st.code((out[-3000:] if len(out) > 3000 else out) or "(no output)")
            if ok:
                st.rerun()

    st.divider()
    st.caption("Train code-text models (LOO) — chỉ chế độ TRAIN")

    col_s, col_b = st.columns(2)
    if col_s.button("SVM"):
        with st.spinner("Training SVM …"):
            ok, out = _run("src.models.svm_model")
        st.toast("✅ SVM" if ok else "❌ SVM", icon="✅" if ok else "❌")
        with st.expander("SVM"):
            st.code(out[-2000:])

    if col_b.button("BiLSTM"):
        with st.spinner("Training BiLSTM (slow) …"):
            ok, out = _run("src.models.bilstm_model")
        st.toast("✅ BiLSTM" if ok else "❌ BiLSTM", icon="✅" if ok else "❌")
        with st.expander("BiLSTM"):
            st.code(out[-2000:])

    if st.button("Behavioral (LR/DT/Rule)"):
        with st.spinner("Running behavioral models …"):
            ok, out = _run("src.models.behavioral_model")
        st.toast("✅ Done" if ok else "❌ Failed", icon="✅" if ok else "❌")
        with st.expander("Behavioral output"):
            st.code(out[-2000:])

    st.divider()
    if st.button("🔄 Refresh"):
        st.rerun()


# ══════════════════════════════════════════════════════════════════════
# MAIN — 4 Tabs
# ══════════════════════════════════════════════════════════════════════

tab_ds, tab_feat, tab_emb, tab_risk = st.tabs([
    "📊 Dataset",
    "🔬 Behavioral Features",
    "🧠 CodeBERT Embeddings",
    "⚠️  Risk Report",
])

# ──────────────────────────────────────────────────────────────────────
# TAB 1 · DATASET
# ──────────────────────────────────────────────────────────────────────
with tab_ds:
    st.subheader("Dataset Overview")

    if not _exists(DATASET_PATH):
        st.info("dataset.csv chưa tồn tại → Chạy **Step 1** ở sidebar.")
        st.stop()

    df = pd.read_csv(DATASET_PATH, usecols=["case", "student", "label"])
    has_labels_in_data = (df["label"] >= 0).all()

    n_total  = len(df)
    n_cheat  = int((df["label"] == 1).sum())
    n_normal = int((df["label"] == 0).sum())
    n_unknown= int((df["label"] == -1).sum())

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Tổng sinh viên",     n_total)
    m2.metric("🔴 Gian lận (1)",    n_cheat)
    m3.metric("🟢 Bình thường (0)", n_normal)
    m4.metric("❓ Chưa có nhãn",   n_unknown)

    if n_unknown > 0:
        st.info(
            "Chế độ **PREDICT**: dataset không có nhãn. "
            "Cột label = -1 (unknown). Chạy bước 3→4 để dự đoán.",
            icon="⚡",
        )

    if has_labels_in_data and n_cheat + n_normal > 0:
        try:
            import plotly.express as px
            fig_pie = px.pie(
                values=[n_cheat, n_normal], names=["Cheat", "Normal"],
                color_discrete_sequence=["#e53935", "#43a047"],
                title="Phân bố nhãn", hole=0.35,
            )
            fig_pie.update_traces(textinfo="percent+label")
            fig_pie.update_layout(height=280, showlegend=False)
            st.plotly_chart(fig_pie, use_container_width=True)
        except ImportError:
            pass

    disp = df.copy()
    disp["label"] = disp["label"].map({1: "🔴 CHEAT", 0: "🟢 normal", -1: "❓ unknown"})
    disp.columns = ["Case", "Student", "Label"]
    st.dataframe(disp, use_container_width=True, hide_index=True)


# ──────────────────────────────────────────────────────────────────────
# TAB 2 · BEHAVIORAL FEATURES
# ──────────────────────────────────────────────────────────────────────
with tab_feat:
    st.subheader("Behavioral Features  (meta.json → History events)")

    if not _exists(FEAT_PATH):
        st.info("features.csv chưa tồn tại → Chạy **Step 2** ở sidebar.")
        st.stop()

    feat_df = pd.read_csv(FEAT_PATH)
    feat_df["student_id"] = (
        feat_df["case"].astype(str) + "/" + feat_df["student"].astype(str)
    )
    avail = [c for c in FEATURE_COLS if c in feat_df.columns]

    try:
        import plotly.express as px

        norm = feat_df[avail].copy()
        for col in avail:
            mx = norm[col].max()
            if mx > 0:
                norm[col] = norm[col] / mx
        norm.index = feat_df["student_id"]

        fig_heat = px.imshow(
            norm,
            color_continuous_scale="Reds",
            title="Heatmap features  (chuẩn hoá 0–1 theo cột)",
            labels={"color": ""},
            aspect="auto",
        )
        fig_heat.update_layout(height=420, margin=dict(l=60, r=20, t=50, b=20))
        st.plotly_chart(fig_heat, use_container_width=True)
    except ImportError:
        st.dataframe(feat_df[["student_id"] + avail], use_container_width=True)

    st.subheader("Drilldown — một sinh viên")
    chosen = st.selectbox("Chọn sinh viên", feat_df["student_id"].tolist())
    row = feat_df[feat_df["student_id"] == chosen].iloc[0]
    cols = st.columns(5)
    for i, col_name in enumerate(avail):
        v = float(row[col_name])
        cols[i % 5].metric(col_name, f"{v:.4f}" if v < 10 else f"{int(v)}")

    with st.expander("Bảng đầy đủ tất cả sinh viên"):
        d2 = feat_df[["student_id", "label"] + avail].copy()
        d2["label"] = d2["label"].map({1: "CHEAT", 0: "normal", -1: "unknown"})
        st.dataframe(d2, use_container_width=True, hide_index=True)


# ──────────────────────────────────────────────────────────────────────
# TAB 3 · CODEBERT EMBEDDINGS
# ──────────────────────────────────────────────────────────────────────
with tab_emb:
    st.subheader("CodeBERT Embeddings  (768 dims → 2D)")

    if not _exists(EMBED_PATH) or not _exists(INDEX_PATH):
        st.info("embeddings.npy chưa tồn tại → Chạy **Step 3** ở sidebar.")
        st.markdown("""
        **Khi chạy Step 3:**
        - Tải `microsoft/codebert-base` lần đầu ≈ 500 MB (cần internet)
        - Model **không bị fine-tune** — chỉ dùng như feature extractor đông lạnh
        - Code mỗi sinh viên → tokenize → CLS token 768 chiều
        - Code > 512 token: sliding window stride 256, lấy mean các CLS vector

        ⏱️ CPU: 5–15 phút  |  GPU: 1–2 phút
        """)
        st.stop()

    embeddings = np.load(EMBED_PATH)
    idx_df     = pd.read_csv(INDEX_PATH)
    idx_df["student_id"] = idx_df["case"].astype(str) + "/" + idx_df["student"].astype(str)
    idx_df["label_name"] = idx_df["label"].map({1: "Cheat", 0: "Normal", -1: "Unknown"})

    st.metric("Embedding shape", f"{embeddings.shape[0]} × {embeddings.shape[1]}")

    try:
        import plotly.express as px
        from sklearn.decomposition import PCA
        from sklearn.manifold import TSNE

        method = st.radio("Reduction method", ["PCA", "t-SNE"], horizontal=True)
        if method == "PCA":
            red = PCA(n_components=2, random_state=42)
            xy  = red.fit_transform(embeddings)
            ev  = red.explained_variance_ratio_
            sub = f"PC1 {ev[0]*100:.1f}% + PC2 {ev[1]*100:.1f}%"
        else:
            perp = min(5, len(embeddings) - 1)
            red  = TSNE(n_components=2, perplexity=perp, random_state=42, n_iter=1000)
            xy   = red.fit_transform(embeddings)
            sub  = f"perplexity={perp}"

        plot_df = pd.DataFrame({
            "x": xy[:, 0], "y": xy[:, 1],
            "label": idx_df["label_name"],
            "student": idx_df["student_id"],
        })
        fig_sc = px.scatter(
            plot_df, x="x", y="y",
            color="label", text="student",
            color_discrete_map={"Cheat": "#e53935", "Normal": "#43a047", "Unknown": "#888"},
            title=f"CodeBERT Embedding Space — {method}  ({sub})",
        )
        fig_sc.update_traces(
            textposition="top center",
            marker=dict(size=11, line=dict(width=1, color="white")),
        )
        fig_sc.update_layout(height=480)
        st.plotly_chart(fig_sc, use_container_width=True)

        with st.expander("Cosine Similarity Matrix"):
            norms  = np.linalg.norm(embeddings, axis=1, keepdims=True)
            normed = embeddings / np.maximum(norms, 1e-9)
            sim    = normed @ normed.T
            labels = idx_df["student_id"].tolist()
            fig_sim = px.imshow(
                sim, x=labels, y=labels,
                color_continuous_scale="Blues",
                title="Cosine similarity giữa các sinh viên",
                zmin=0, zmax=1,
            )
            fig_sim.update_layout(height=520)
            st.plotly_chart(fig_sim, use_container_width=True)

    except ImportError:
        st.info("Cài plotly & scikit-learn để xem visualisation.")
        st.write(f"Embedding loaded OK — shape: {embeddings.shape}")


# ──────────────────────────────────────────────────────────────────────
# TAB 4 · RISK REPORT
# ──────────────────────────────────────────────────────────────────────
with tab_risk:
    st.subheader("⚠️  Student Risk Report")
    st.caption("🔴 Đỏ = dự đoán CHEAT  ·  🟢 Xanh = dự đoán normal")

    if not _exists(FEAT_PATH) and not _exists(DATASET_PATH):
        st.info("Chạy ít nhất **Step 1** + **Step 2** để xem Risk Report.")
        st.stop()

    if _exists(FEAT_PATH):
        feat_df = pd.read_csv(FEAT_PATH)
    else:
        feat_df = pd.read_csv(DATASET_PATH, usecols=["case", "student", "label"])
        for c in FEATURE_COLS:
            feat_df[c] = 0

    feat_df["student_id"] = feat_df["case"].astype(str) + "/" + feat_df["student"].astype(str)
    avail = [c for c in FEATURE_COLS if c in feat_df.columns]

    # Detect data mode
    data_has_labels = _exists(DATASET_PATH) and (
        pd.read_csv(DATASET_PATH, usecols=["label"])["label"].ge(0).all()
    )

    score_source = "behavioral features only (fallback)"

    # ── Try XGBoost fusion ──────────────────────────────────────────
    if _exists(EMBED_PATH) and _exists(INDEX_PATH):
        try:
            import joblib
            from sklearn.preprocessing import StandardScaler
            from xgboost import XGBClassifier

            embeddings = np.load(EMBED_PATH)
            idx_df     = pd.read_csv(INDEX_PATH)

            aligned  = idx_df.merge(
                feat_df[["case", "student"] + avail],
                on=["case", "student"], how="left",
            )
            feat_mat = aligned[avail].fillna(0).values.astype(np.float32)
            X = np.concatenate([embeddings, feat_mat], axis=1)
            y = idx_df["label"].values

            if not data_has_labels and _exists(MODEL_SAVE_PATH):
                # ── PREDICT mode: load saved model ──────────────────
                saved  = joblib.load(MODEL_SAVE_PATH)
                X_sc   = saved["scaler"].transform(X)
                proba  = saved["clf"].predict_proba(X_sc)[:, 1]
                clspred= saved["clf"].predict(X_sc)
                score_source = "XGBoost saved model (trained on labeled data)"
            else:
                # ── TRAIN mode: fit fresh on this data ──────────────
                n_pos = int((y == 1).sum())
                n_neg = int((y == 0).sum())
                sw    = np.where(y == 1, 1.0, float(n_pos) / max(n_neg, 1))
                scaler = StandardScaler()
                X_sc   = scaler.fit_transform(X)
                clf    = XGBClassifier(
                    n_estimators=50, max_depth=2, learning_rate=0.1,
                    eval_metric="logloss", verbosity=0, random_state=42,
                )
                clf.fit(X_sc, y, sample_weight=sw)
                proba  = clf.predict_proba(X_sc)[:, 1]
                clspred= clf.predict(X_sc)
                score_source = "XGBoost fusion (CodeBERT 768 + behavioral 10)"

            prob_map = {
                f"{r['case']}/{r['student']}": float(proba[i])
                for i, r in idx_df.iterrows()
            }
            pred_map = {
                f"{r['case']}/{r['student']}": int(clspred[i])
                for i, r in idx_df.iterrows()
            }
            feat_df["_score"] = feat_df["student_id"].map(prob_map).fillna(0)
            feat_df["_pred"]  = feat_df["student_id"].map(pred_map).fillna(0).astype(int)

        except Exception as e:
            feat_df["_score"] = feat_df.apply(_feature_score, axis=1)
            feat_df["_pred"]  = (feat_df["_score"] >= 0.40).astype(int)
            score_source = f"behavioral only (error: {e})"
    else:
        feat_df["_score"] = feat_df.apply(_feature_score, axis=1)
        feat_df["_pred"]  = (feat_df["_score"] >= 0.40).astype(int)

    feat_df = feat_df.sort_values("_score", ascending=False).reset_index(drop=True)

    # ── Summary metrics ──────────────────────────────────────────────
    n_flagged = int((feat_df["_pred"] == 1).sum())
    n_total   = len(feat_df)

    c1, c2, c3 = st.columns(3)
    c1.metric("Tổng sinh viên",  n_total)
    c2.metric("🔴 Dự đoán CHEAT",  n_flagged)
    c3.metric("🟢 Dự đoán normal", n_total - n_flagged)

    if data_has_labels:
        n_correct = int((feat_df["_pred"] == feat_df["label"]).sum())
        st.caption(f"Đúng nhãn thực: **{n_correct}/{n_total}**   |   📌 {score_source}")
    else:
        st.caption(f"📌 {score_source}  ·  Không có nhãn để so sánh")

    if not data_has_labels and not _exists(MODEL_SAVE_PATH):
        st.error(
            "Chưa có model đã train. Hãy:\n"
            "1. Chọn folder có `agrigation.csv` (labeled data)\n"
            "2. Chạy Step 1→4 để train và lưu model\n"
            "3. Sau đó quay lại với folder sinh viên mới"
        )
        st.stop()

    st.divider()

    # ── Filter & sort ────────────────────────────────────────────────
    col_f1, col_f2 = st.columns([1, 2])
    filter_pred = col_f1.selectbox("Lọc", ["Tất cả", "CHEAT", "normal"])
    sort_by     = col_f2.radio("Sắp xếp", ["Score ↓", "Student ID"], horizontal=True)

    show_df = feat_df.copy()
    if filter_pred == "CHEAT":
        show_df = show_df[show_df["_pred"] == 1]
    elif filter_pred == "normal":
        show_df = show_df[show_df["_pred"] == 0]
    if sort_by == "Student ID":
        show_df = show_df.sort_values("student_id")

    # ── Student cards ────────────────────────────────────────────────
    for _, row in show_df.iterrows():
        score = float(row["_score"])
        pred  = int(row["_pred"])
        label = int(row.get("label", -1))
        sid   = str(row["student_id"])

        card_class = "card-cheat" if pred == 1 else "card-normal"
        bar_color  = "#e53935"    if pred == 1 else "#43a047"
        pred_badge = (
            '<span class="badge-cheat">CHEAT</span>' if pred == 1
            else '<span class="badge-norm">normal</span>'
        )
        rlevel       = "HIGH" if score >= 0.6 else ("MED" if score >= 0.3 else "LOW")
        reasons      = _reasons(row)
        reasons_html = "".join(f"<li style='margin:3px 0'>{r}</li>" for r in reasons)
        bar_html     = _bar(score, bar_color)

        # True label row (only when labeled)
        if label == 1:
            label_line = (
                f'Nhãn thực: <span class="badge-cheat">CHEAT</span> '
                f'<span class="ok">✓</span>' if pred == 1 else
                f'Nhãn thực: <span class="badge-cheat">CHEAT</span> '
                f'<span class="bad">✗</span>'
            )
        elif label == 0:
            label_line = (
                f'Nhãn thực: <span class="badge-norm">normal</span> '
                f'<span class="ok">✓</span>' if pred == 0 else
                f'Nhãn thực: <span class="badge-norm">normal</span> '
                f'<span class="bad">✗</span>'
            )
        else:
            label_line = ""

        st.markdown(f"""
        <div class="{card_class}">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px">
            <span class="sid">{sid}</span>
            <span style="display:flex; gap:6px; align-items:center">
              {pred_badge}
              <span class="badge-risk">{rlevel}</span>
            </span>
          </div>
          {bar_html} &nbsp;<b>{score*100:.0f}%</b>
          {"<div style='font-size:0.85em; margin-top:4px; color:#555'>"+label_line+"</div>" if label_line else ""}
          <ul style="margin:6px 0 0 14px; padding:0; font-size:0.83em; color:#555; list-style:disc">
            {reasons_html}
          </ul>
        </div>
        """, unsafe_allow_html=True)
