import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import streamlit as st
import pandas as pd

from styles import SHARED_CSS
from utils import (
    load_assets, get_drug_stats, render_header, apply_blended_background,
    CONDITION_COLORS, CONDITION_ICONS, restore_session_from_token, clean_text,
    top_drugs_for_condition,
)
from logs_db import log_prediction

LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "logo.jpeg"
BG_PATH = Path(__file__).resolve().parent.parent / "assets" / "ai_bg.jpeg"

st.set_page_config(
    page_title="MedInsight AI · Predict",
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
drug_stats = get_drug_stats(df)

render_header(LOGO_PATH, "predict")

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="section-heading">Condition Classifier</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Predict a Condition from a Drug Review</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div style="color:#8b949e;font-size:0.875rem;line-height:1.8;margin-bottom:16px;">
        Paste or describe a patient review below. The model predicts the most likely
        condition: <strong style="color:#e6edf3;">Depression</strong>,
        <strong style="color:#e6edf3;">High Blood Pressure</strong>, or
        <strong style="color:#e6edf3;">Type 2 Diabetes</strong>. It also suggests
        top-rated drugs for that condition based on real patient reviews.
    </div>
    """,
    unsafe_allow_html=True,
)

example = (
    "I've been taking this medication for a few weeks now and my mood has "
    "improved significantly, with far fewer side effects than my last prescription."
)
review_text = st.text_area(
    "Patient review text",
    placeholder=example,
    height=140,
    label_visibility="collapsed",
)

col_a, col_b = st.columns([1, 5])
with col_a:
    run = st.button("Predict Condition", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

if run:
    if not review_text or not review_text.strip():
        st.warning("Please enter some review text first.")
    else:
        cleaned = clean_text(review_text)
        X = vectorizer.transform([cleaned])
        proba = model.predict_proba(X)[0]
        classes = model.classes_
        results = sorted(zip(classes, proba), key=lambda x: x[1], reverse=True)
        predicted_condition, top_prob = results[0]

        MIN_CONFIDENCE = 0.60
        if top_prob < MIN_CONFIDENCE:
            st.warning("Low confidence prediction. Please enter a more specific review describing symptoms related to Depression, High Blood Pressure, or Type 2 Diabetes.")
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<div style="font-size:0.8rem;color:#8b949e;font-weight:700;margin-bottom:8px;">CONFIDENCE BY CONDITION</div>', unsafe_allow_html=True)
            for cond, prob in results:
                c = CONDITION_COLORS.get(cond, "#1d4ed8")
                st.markdown(
                    f"""
                    <div style="margin-bottom:10px;">
                        <div style="display:flex;justify-content:space-between;font-size:0.82rem;
                             color:#e6edf3;margin-bottom:4px;">
                            <span>{cond}</span><span>{prob * 100:.1f}%</span>
                        </div>
                        <div style="height:8px;background:rgba(255,255,255,0.06);border-radius:6px;overflow:hidden;">
                            <div style="height:100%;width:{prob * 100:.1f}%;background:{c};"></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            st.markdown('</div>', unsafe_allow_html=True)
            st.stop()

        log_prediction(
            st.session_state.user_info["username"],
            review_text,
            predicted_condition,
            {c: float(p) for c, p in results},
        )

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-heading">Result</div>', unsafe_allow_html=True)

        icon = CONDITION_ICONS.get(predicted_condition, "⚕")
        color = CONDITION_COLORS.get(predicted_condition, "#1d4ed8")
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:16px;padding:18px 20px;
                 background:rgba(255,255,255,0.02);border:1px solid {color}55;
                 border-radius:14px;margin-bottom:18px;">
                <div style="font-size:2.2rem;">{icon}</div>
                <div>
                    <div style="font-size:0.7rem;color:#8b949e;text-transform:uppercase;
                         letter-spacing:0.08em;font-weight:700;">Predicted Condition</div>
                    <div style="font-size:1.4rem;font-weight:800;color:{color};">{predicted_condition}</div>
                    <div style="font-size:0.8rem;color:#8b949e;margin-top:2px;">
                        Confidence: {top_prob * 100:.1f}%
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div style="font-size:0.8rem;color:#8b949e;font-weight:700;margin-bottom:8px;">CONFIDENCE BY CONDITION</div>', unsafe_allow_html=True)
        for cond, prob in results:
            c = CONDITION_COLORS.get(cond, "#1d4ed8")
            st.markdown(
                f"""
                <div style="margin-bottom:10px;">
                    <div style="display:flex;justify-content:space-between;font-size:0.82rem;
                         color:#e6edf3;margin-bottom:4px;">
                        <span>{cond}</span><span>{prob * 100:.1f}%</span>
                    </div>
                    <div style="height:8px;background:rgba(255,255,255,0.06);border-radius:6px;overflow:hidden;">
                        <div style="height:100%;width:{prob * 100:.1f}%;background:{c};"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Drug recommendations ──────────────────────────────────────────
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-heading">Recommended</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">Top-Rated Drugs for {predicted_condition}</div>', unsafe_allow_html=True)

        top = top_drugs_for_condition(drug_stats, predicted_condition, n=5)
        if top.empty:
            st.info("No drug statistics available for this condition yet.")
        else:
            cols = st.columns(len(top))
            for col, (_, row) in zip(cols, top.iterrows()):
                col.markdown(
                    f"""
                    <div class="metric-tile" style="border-top-color:{color};text-align:left;">
                        <div style="font-weight:700;font-size:0.92rem;color:#e6edf3;">{row['drugName']}</div>
                        <div style="font-size:0.72rem;color:#8b949e;margin-top:6px;">
                            ⭐ {row['avg_rating']:.1f}/10 avg rating<br>
                            👍 {row['avg_useful']:.0f} avg useful votes<br>
                            📝 {int(row['review_count'])} reviews
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        st.markdown('</div>', unsafe_allow_html=True)

# ── Prediction history ────────────────────────────────────────────────────────
from logs_db import get_user_logs

history = get_user_logs(st.session_state.user_info["username"], limit=10)
if history:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">History</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Your Recent Predictions</div>', unsafe_allow_html=True)
    hist_df = pd.DataFrame(history)[["created_at", "predicted_condition", "review_text"]]
    hist_df.columns = ["When", "Predicted Condition", "Review (excerpt)"]
    hist_df["Review (excerpt)"] = hist_df["Review (excerpt)"].str.slice(0, 90) + "…"
    st.dataframe(hist_df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)
