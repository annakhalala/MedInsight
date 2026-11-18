"""
Shared helpers used by Home.py and every page in pages/.

This module is added to sys.path by each entry-point script:
    sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
"""
from pathlib import Path
import base64
import pickle
import re
import secrets

import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT_DIR / "final_model.pkl"
VECTORIZER_PATH = ROOT_DIR / "tfidf_vectorizer.pkl"
DATA_PATH = ROOT_DIR / "cleaned_data.csv"

# ── Condition palette (kept in sync with the landing page in Home.py) ────────
CONDITION_COLORS = {
    "Depression": "#7c3aed",
    "High Blood Pressure": "#dc2626",
    "Type 2 Diabetes": "#059669",
}

CONDITION_ICONS = {
    "Depression": "🧠",
    "High Blood Pressure": "🫀",
    "Type 2 Diabetes": "🩸",
}

CONDITION_SLUG = {
    "Depression": "dep",
    "High Blood Pressure": "bp",
    "Type 2 Diabetes": "dia",
}

# ── Matplotlib dark-theme constants ──────────────────────────────────────────
MPL_BG = "#0d1117"
MPL_GRID = "#21262d"
MPL_TEXT = "#e6edf3"
MPL_LABEL = "#8b949e"


def mpl_defaults(fig=None, ax=None):
    """Apply the dark MedInsight theme to a matplotlib figure/axes pair.

    Usage:
        fig, ax = plt.subplots()
        ...
        mpl_defaults(fig, ax)
    """
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "figure.facecolor": MPL_BG,
        "axes.facecolor": MPL_BG,
        "savefig.facecolor": MPL_BG,
        "text.color": MPL_TEXT,
        "axes.labelcolor": MPL_LABEL,
        "xtick.color": MPL_LABEL,
        "ytick.color": MPL_LABEL,
        "axes.edgecolor": MPL_GRID,
        "grid.color": MPL_GRID,
        "font.family": "sans-serif",
    })

    if fig is not None:
        fig.patch.set_facecolor(MPL_BG)
    if ax is not None:
        ax.set_facecolor(MPL_BG)
        for spine in ax.spines.values():
            spine.set_color(MPL_GRID)
        ax.grid(color=MPL_GRID, linewidth=0.6, alpha=0.6)
        ax.tick_params(colors=MPL_LABEL)


# ── Asset loading ────────────────────────────────────────────────────────────
def _train_and_save_model() -> tuple[LogisticRegression, TfidfVectorizer, pd.DataFrame]:
    """Train a fresh model from the cleaned dataset and overwrite the shipped artifacts."""
    df = pd.read_csv(DATA_PATH)
    texts = df["review"].fillna("").apply(clean_text)

    vectorizer = TfidfVectorizer(
        max_features=5000,
        stop_words="english",
        ngram_range=(1, 2),
        sublinear_tf=True,
    )
    X = vectorizer.fit_transform(texts)
    y = df["condition"]

    model = LogisticRegression(
        max_iter=3000,
        class_weight="balanced",
        C=2.0,
        random_state=42,
        solver="liblinear",
    )
    model.fit(X, y)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    with open(VECTORIZER_PATH, "wb") as f:
        pickle.dump(vectorizer, f)

    return model, vectorizer, df


@st.cache_resource(show_spinner=False)
def load_assets():
    """Load the trained model, TF-IDF vectorizer, and cleaned dataset.

    If the saved artifact is stale or behaves poorly, retrain a fresh model from
    the cleaned data and overwrite the package artifacts.
    """
    if not MODEL_PATH.exists() or not VECTORIZER_PATH.exists():
        return _train_and_save_model()

    try:
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        with open(VECTORIZER_PATH, "rb") as f:
            vectorizer = pickle.load(f)
        df = pd.read_csv(DATA_PATH)

        if not hasattr(model, "predict") or not hasattr(model, "classes_"):
            raise ValueError("Model is missing prediction attributes.")

        X = vectorizer.transform(df["review"].fillna("").apply(clean_text))
        _, X_test, _, y_test = train_test_split(
            X, df["condition"], test_size=0.2, random_state=42, stratify=df["condition"]
        )
        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        f1 = f1_score(y_test, preds, average="weighted", zero_division=0)
        if acc < 0.65 or f1 < 0.60:
            raise ValueError(f"Saved model underperformed: acc={acc:.3f}, f1={f1:.3f}")
        return model, vectorizer, df
    except Exception:
        return _train_and_save_model()


@st.cache_data(show_spinner=False)
def get_drug_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate per-drug, per-condition stats used for recommendations.

    Returns a DataFrame indexed by (condition, drugName) with average
    rating, average usefulCount, and review count, sorted so the best
    drug for each condition comes first.
    """
    stats = (
        df.groupby(["condition", "drugName"])
        .agg(
            avg_rating=("rating", "mean"),
            avg_useful=("usefulCount", "mean"),
            review_count=("rating", "count"),
        )
        .reset_index()
    )
    # Require a minimum sample size so a single 10/10 review doesn't win
    stats = stats[stats["review_count"] >= 5]
    stats["score"] = stats["avg_rating"] * 0.7 + (
        stats["avg_useful"].clip(upper=50) / 50 * 10
    ) * 0.3
    stats = stats.sort_values(["condition", "score"], ascending=[True, False])
    return stats


def top_drugs_for_condition(drug_stats: pd.DataFrame, condition: str, n: int = 5) -> pd.DataFrame:
    return drug_stats[drug_stats["condition"] == condition].head(n)


# ── Text cleaning (mirrors src/data_cleaning.py from the ML pipeline) ────────
def clean_text(text: str) -> str:
    import re

    text = str(text).lower()
    text = re.sub(r"[^a-z\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ── Images ────────────────────────────────────────────────────────────────────
def _image_to_base64(path) -> str:
    """Return a base64-encoded string for an image, or '' if missing/unreadable."""
    try:
        p = Path(path)
        if not p.exists():
            return ""
        return base64.b64encode(p.read_bytes()).decode("utf-8")
    except Exception:
        return ""


def apply_blended_background(bg_path):
    """Apply a subtle, blended background image behind the authenticated app
    (as opposed to the brighter, full-bleed background used on the public
    landing page inside Home.py)."""
    bg_b64 = _image_to_base64(str(bg_path))
    if bg_b64:
        css = (
            f'linear-gradient(160deg,rgba(9,13,18,0.94),rgba(13,17,23,0.94)),'
            f'url("data:image/jpeg;base64,{bg_b64}") center/cover fixed no-repeat'
        )
    else:
        css = "#0d1117"
    st.markdown(
        f"""<style>.stApp {{ background: {css} !important; }}</style>""",
        unsafe_allow_html=True,
    )


# ── Header ────────────────────────────────────────────────────────────────────
def render_header(logo_path, active: str = "home"):
    """Render the shared top navigation header.

    active: one of "home", "predict", "analytics" — controls which nav
    link is highlighted.
    """
    logo_b64 = _image_to_base64(str(logo_path))
    logo_html = (
        f'<img src="data:image/jpeg;base64,{logo_b64}" />'
        if logo_b64 else "⚕"
    )

    token = st.session_state.get("_auth_token", "")
    qs = f"?t={token}" if token else ""

    def link(label, page, slug):
        cls = "mi-nav-link active" if active == slug else "mi-nav-link"
        return f'<a class="{cls}" href="/{page}{qs}" target="_self">{label}</a>'

    nav_links = (
        link("Home", "", "home")
        + link("Predict", "Predict", "predict")
        + link("Analytics", "Analytics", "analytics")
    )

    username = st.session_state.get("user_info", {}).get("username", "")

    st.markdown(
        f"""
        <div class="mi-header">
            <a href="/{qs}" target="_self" class="mi-logo" style="text-decoration:none;">
                <div class="mi-logo-icon">{logo_html}</div>
                <span class="mi-logo-name">MedInsight <em>AI</em></span>
            </a>
            <div class="mi-nav">{nav_links}</div>
            <div class="mi-nav-user">
                <span class="mi-nav-uname">👤 {username}</span>
                <a class="mi-nav-logout" href="/{qs}" target="_self" id="mi-logout">Log out</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # A real logout button (HTML links can't touch session_state directly).
    _, _, logout_col = st.columns([6, 1, 1])
    with logout_col:
        if st.button("Log out", key=f"logout_{active}", use_container_width=True):
            do_logout()
            st.rerun()


# ── Session token store (survives Streamlit's per-page session_state resets
#    that can occur when a multipage link is opened fresh) ───────────────────
# NOTE: this is an in-memory store, scoped to the running server process.
# It is intentionally simple — good enough for a small class/demo deployment.
_SESSION_STORE: dict[str, dict] = {}


def create_session_token(user_info: dict) -> str:
    token = secrets.token_urlsafe(24)
    _SESSION_STORE[token] = user_info
    return token


def restore_session_from_token():
    """If the current session isn't logged in but the URL carries a valid
    session token (?t=...), restore st.session_state from the token store."""
    if st.session_state.get("logged_in"):
        return

    token = st.query_params.get("t")
    if not token:
        return

    user_info = _SESSION_STORE.get(token)
    if user_info:
        st.session_state.logged_in = True
        st.session_state.user_info = user_info
        st.session_state._auth_token = token


def do_logout():
    token = st.session_state.get("_auth_token")
    if token:
        _SESSION_STORE.pop(token, None)
    for key in ("logged_in", "user_info", "_auth_token"):
        st.session_state.pop(key, None)
    st.query_params.clear()
