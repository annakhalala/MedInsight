import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import streamlit as st

from styles import SHARED_CSS
from utils import (
    apply_blended_background, restore_session_from_token,
    create_session_token, _image_to_base64,
)
from auth_db import init_db, create_user, verify_user

LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "logo.jpeg"
BG_PATH = Path(__file__).resolve().parent.parent / "assets" / "ai_bg.jpeg"

st.set_page_config(
    page_title="MedInsight AI · Sign In",
    page_icon="⚕",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(SHARED_CSS, unsafe_allow_html=True)
apply_blended_background(BG_PATH)
init_db()

restore_session_from_token()

# ── Already logged in → bounce to Home ───────────────────────────────────────
if st.session_state.get("logged_in"):
    st.switch_page("Home.py")

st.markdown(
    """
    <style>
    #MainMenu, footer, header, [data-testid="stToolbar"] { visibility: hidden; }
    [data-testid="stSidebarNav"] { display: none; }
    .block-container { max-width: 460px !important; padding-top: 8vh !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

logo_b64 = _image_to_base64(str(LOGO_PATH))
logo_html = f'<img src="data:image/jpeg;base64,{logo_b64}" style="width:100%;height:100%;object-fit:cover;border-radius:12px;" />' if logo_b64 else "⚕"

st.markdown(
    f"""
    <div style="text-align:center;margin-bottom:28px;">
        <div style="width:56px;height:56px;margin:0 auto 14px;border-radius:14px;
             background:linear-gradient(135deg,#1d4ed8,#0ea5e9);display:flex;
             align-items:center;justify-content:center;font-size:26px;
             box-shadow:0 4px 18px rgba(29,78,216,0.45);overflow:hidden;">{logo_html}</div>
        <div style="font-weight:800;font-size:1.3rem;color:#e6edf3;">MedInsight <em style="font-style:normal;
             background:linear-gradient(135deg,#60a5fa,#38bdf8);-webkit-background-clip:text;
             -webkit-text-fill-color:transparent;">AI</em></div>
        <div style="font-size:0.82rem;color:#8b949e;margin-top:4px;">
            Sign in to get personalised drug recommendations
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
tab_login, tab_signup = st.tabs(["Sign In", "Create Account"])

with tab_login:
    with st.form("login_form", clear_on_submit=False):
        identifier = st.text_input("Username or email", placeholder="e.g. M8888 or you@example.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Sign In", use_container_width=True)

    if submitted:
        if not identifier or not password:
            st.error("Please enter both your username/email and password.")
        else:
            user = verify_user(identifier, password)
            if user is None:
                st.error("Incorrect username/email or password.")
            else:
                token = create_session_token(user)
                st.session_state.logged_in = True
                st.session_state.user_info = user
                st.session_state._auth_token = token
                st.query_params["t"] = token
                st.success(f"Welcome back, {user['username']}!")
                st.switch_page("Home.py")

with tab_signup:
    with st.form("signup_form", clear_on_submit=False):
        new_username = st.text_input("Choose a username", placeholder="e.g. Anna_K")
        new_email = st.text_input("Email", placeholder="you@example.com")
        new_password = st.text_input("Password", type="password", placeholder="At least 8 characters")
        confirm_password = st.text_input("Confirm password", type="password", placeholder="Repeat your password")
        agree = st.checkbox("I understand MedInsight AI is for research/educational purposes only, not medical advice.")
        signup_submitted = st.form_submit_button("Create Account", use_container_width=True)

    if signup_submitted:
        if not agree:
            st.error("Please confirm you understand this tool is not medical advice.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        else:
            ok, message = create_user(new_username, new_email, new_password)
            if ok:
                st.success(f"{message} You can now sign in from the Sign In tab.")
            else:
                st.error(message)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div style="text-align:center;margin-top:18px;font-size:0.72rem;color:#484f58;">
        MedInsight AI · Limkokwing University of Creative Technology · Lesotho<br>
        For educational and research purposes only. Not a substitute for professional medical advice.
    </div>
    """,
    unsafe_allow_html=True,
)
