import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix,
)

from styles import SHARED_CSS
from utils import (
    load_assets, render_header, apply_blended_background,
    CONDITION_COLORS, MPL_BG, MPL_GRID, MPL_TEXT, MPL_LABEL, mpl_defaults,
    restore_session_from_token,
)

LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "logo.jpeg"
BG_PATH = Path(__file__).resolve().parent.parent / "assets" / "ai_bg.jpeg"

st.set_page_config(
    page_title="MedInsight AI · Analytics",
    page_icon="⚕",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(SHARED_CSS, unsafe_allow_html=True)
apply_blended_background(BG_PATH)

restore_session_from_token()

if not st.session_state.get("logged_in"):
    st.switch_page("pages/Login.py")

st.markdown(
    """<style>[data-testid="stSidebarNav"] { display: none; }</style>""",
    unsafe_allow_html=True,
)

model, vectorizer, df = load_assets()
render_header(LOGO_PATH, "analytics")

# ── Dataset overview ──────────────────────────────────────────────────────────
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="section-heading">Dataset</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Condition &amp; Rating Distribution</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    counts = df["condition"].value_counts()
    fig, ax = plt.subplots(figsize=(5, 4))
    mpl_defaults(fig, ax)
    colors = [CONDITION_COLORS.get(c, "#1d4ed8") for c in counts.index]
    ax.bar(counts.index, counts.values, color=colors)
    ax.set_title("Reviews per Condition", color=MPL_TEXT, fontsize=12, fontweight="bold")
    ax.set_ylabel("Number of Reviews")
    plt.xticks(rotation=15, ha="right")
    st.pyplot(fig, use_container_width=True)

with col2:
    fig, ax = plt.subplots(figsize=(5, 4))
    mpl_defaults(fig, ax)
    ax.hist(df["rating"], bins=10, color="#38bdf8", edgecolor=MPL_BG)
    ax.set_title("Rating Distribution", color=MPL_TEXT, fontsize=12, fontweight="bold")
    ax.set_xlabel("Rating (1–10)")
    ax.set_ylabel("Number of Reviews")
    st.pyplot(fig, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── Useful count by condition ─────────────────────────────────────────────────
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="section-heading">Engagement</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Average Rating by Condition</div>', unsafe_allow_html=True)

avg_rating = df.groupby("condition")["rating"].mean().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(9, 3.6))
mpl_defaults(fig, ax)
colors = [CONDITION_COLORS.get(c, "#1d4ed8") for c in avg_rating.index]
ax.barh(avg_rating.index, avg_rating.values, color=colors)
ax.set_xlabel("Average Rating (1–10)")
ax.set_xlim(0, 10)
for i, v in enumerate(avg_rating.values):
    ax.text(v + 0.1, i, f"{v:.2f}", color=MPL_TEXT, va="center", fontsize=9)
st.pyplot(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Model performance ──────────────────────────────────────────────────────────
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="section-heading">Model</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Logistic Regression Performance</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div style="color:#8b949e;font-size:0.82rem;line-height:1.7;margin-bottom:16px;">
        Recomputed on a fresh 80/20 stratified split of the cleaned dataset using the
        same TF-IDF vectoriser and trained model shipped with this app.
    </div>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def _evaluate(_df):
    from utils import clean_text

    texts = _df["review"].apply(clean_text)
    X = vectorizer.transform(texts)
    y = _df["condition"]
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    preds = model.predict(X_test)
    metrics = {
        "Accuracy": accuracy_score(y_test, preds),
        "Precision": precision_score(y_test, preds, average="weighted", zero_division=0),
        "Recall": recall_score(y_test, preds, average="weighted", zero_division=0),
        "F1-Score": f1_score(y_test, preds, average="weighted", zero_division=0),
    }
    cm = confusion_matrix(y_test, preds, labels=model.classes_)
    return metrics, cm


with st.spinner("Scoring model on a held-out split…"):
    metrics, cm = _evaluate(df)

m_cols = st.columns(4)
for col, (label, value) in zip(m_cols, metrics.items()):
    col.markdown(
        f'<div class="metric-tile"><div class="metric-value">{value * 100:.1f}%</div>'
        f'<div class="metric-label">{label}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("<div style='margin:20px 0 8px;font-size:0.8rem;color:#8b949e;font-weight:700;'>CONFUSION MATRIX</div>", unsafe_allow_html=True)
fig, ax = plt.subplots(figsize=(5.5, 4.5))
mpl_defaults(fig, ax)
im = ax.imshow(cm, cmap="Blues")
labels = model.classes_
ax.set_xticks(range(len(labels)))
ax.set_yticks(range(len(labels)))
ax.set_xticklabels(labels, rotation=25, ha="right", color=MPL_LABEL)
ax.set_yticklabels(labels, color=MPL_LABEL)
ax.set_xlabel("Predicted")
ax.set_ylabel("Actual")
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                 color="white" if cm[i, j] > cm.max() / 2 else MPL_TEXT, fontsize=10)
st.pyplot(fig, use_container_width=False)
st.markdown('</div>', unsafe_allow_html=True)
