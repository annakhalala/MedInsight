import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

from styles import SHARED_CSS
from utils import (
    load_assets, get_drug_stats, render_header, apply_blended_background,
    CONDITION_COLORS, MPL_BG, MPL_GRID, MPL_TEXT, MPL_LABEL,
    mpl_defaults, _image_to_base64, restore_session_from_token,
)

LOGO_PATH = Path(__file__).resolve().parent / "assets" / "logo.jpeg"
BG_PATH   = Path(__file__).resolve().parent / "assets" / "ai_bg.jpeg"

st.set_page_config(
    page_title="MedInsight AI · Home",
    page_icon="⚕",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(SHARED_CSS, unsafe_allow_html=True)
apply_blended_background(BG_PATH)

# ── Restore session from token if session_state was wiped by navigation ───────
restore_session_from_token()

# ── Landing page (unauthenticated users) ──────────────────────────────────────
if not st.session_state.get("logged_in"):

    # Encode the background image so the landing page uses the same photo
    bg_b64 = _image_to_base64(str(BG_PATH))
    bg_css = (
        f'linear-gradient(145deg,rgba(9,13,18,0.88),rgba(13,17,23,0.85)),'
        f'url("data:image/jpeg;base64,{bg_b64}") center/cover fixed no-repeat'
        if bg_b64 else "#0d1117"
    )

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    #MainMenu, footer, header, [data-testid="stToolbar"] {{ visibility: hidden; }}
    [data-testid="stSidebarNav"] {{ display: none; }}
    .block-container {{ padding: 0 !important; max-width: 100% !important; }}
    .stApp {{ background: {bg_css} !important; }}

    /* ── Reset & base ── */
    .lp * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }}
    .lp {{ color: #e6edf3; }}

    /* ── Nav ── */
    .lp-nav {{
        position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 52px; height: 64px;
        background: rgba(9,13,18,0.85);
        border-bottom: 1px solid rgba(33,38,45,0.7);
        backdrop-filter: blur(18px);
    }}
    .lp-logo {{ display: flex; align-items: center; gap: 11px; text-decoration: none; }}
    .lp-logo-icon {{
        width: 36px; height: 36px;
        background: linear-gradient(135deg,#1d4ed8,#0ea5e9);
        border-radius: 10px; display: flex; align-items: center;
        justify-content: center; font-size: 17px;
        box-shadow: 0 4px 16px rgba(29,78,216,0.45);
    }}
    .lp-logo-name {{ font-weight: 800; font-size: 1.05rem; color: #e6edf3; }}
    .lp-logo-name em {{ font-style: normal; background: linear-gradient(135deg,#60a5fa,#38bdf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    .lp-nav-links {{ display: flex; align-items: center; gap: 4px; }}
    .lp-nav-link {{
        padding: 7px 15px; border-radius: 8px;
        color: #8b949e; font-size: 0.85rem; font-weight: 600;
        text-decoration: none; transition: all .2s;
    }}
    .lp-nav-link:hover {{ color: #e6edf3; background: rgba(33,38,45,0.5); }}
    .lp-nav-btn {{
        padding: 9px 22px; border-radius: 10px;
        background: linear-gradient(135deg,#1d4ed8,#0ea5e9);
        color: #fff; font-size: 0.875rem; font-weight: 700;
        text-decoration: none;
        box-shadow: 0 2px 12px rgba(29,78,216,0.4);
        transition: all .2s;
    }}
    .lp-nav-btn:hover {{ box-shadow: 0 4px 20px rgba(29,78,216,0.6); transform: translateY(-1px); }}

    /* ── Hero ── */
    .lp-hero {{
        min-height: 100vh; display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        padding: 110px 24px 80px; text-align: center;
    }}
    .lp-badge {{
        display: inline-flex; align-items: center; gap: 8px;
        background: rgba(29,78,216,0.12);
        border: 1px solid rgba(56,139,253,0.3);
        border-radius: 100px; padding: 5px 18px;
        font-size: 0.72rem; font-weight: 700; color: #79c0ff;
        letter-spacing: 0.08em; text-transform: uppercase;
        margin-bottom: 28px;
        animation: lp-up .55s ease forwards; opacity: 0;
    }}
    .lp-dot {{
        width: 6px; height: 6px; border-radius: 50%;
        background: #79c0ff; animation: lp-blink 2s ease infinite;
    }}
    @keyframes lp-blink {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:.3; }} }}
    .lp-h1 {{
        font-weight: 800; font-size: clamp(2.5rem,5vw,4.4rem);
        line-height: 1.06; letter-spacing: -0.03em;
        color: #e6edf3; margin-bottom: 20px;
        animation: lp-up .55s .08s ease forwards; opacity: 0;
    }}
    .lp-grad {{ background: linear-gradient(135deg,#60a5fa,#38bdf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }}
    .lp-sub {{
        max-width: 540px; font-size: 1rem; color: #8b949e;
        line-height: 1.82; margin-bottom: 40px;
        animation: lp-up .55s .16s ease forwards; opacity: 0;
    }}
    .lp-typed {{
        font-family: 'JetBrains Mono', monospace;
        background: rgba(29,78,216,0.15);
        border: 1px solid rgba(56,139,253,0.3);
        border-radius: 6px; padding: 2px 10px;
        font-size: 0.9em; color: #79c0ff;
        display: inline-block; min-width: 220px;
    }}
    /* CSS-only typewriter — no JS timing issues */
    .lp-tw-wrap {{
        display: inline-block; position: relative;
        font-family: 'JetBrains Mono', monospace;
        background: rgba(29,78,216,0.15);
        border: 1px solid rgba(56,139,253,0.3);
        border-radius: 6px; padding: 2px 10px;
        font-size: 0.9em; color: #79c0ff;
        overflow: hidden; white-space: nowrap;
        vertical-align: middle;
    }}
    .lp-tw-wrap span {{ animation: lp-cycle 9s steps(1) infinite; }}
    @keyframes lp-cycle {{
        0%   {{ content: none; }} /* trick: use visibility */
    }}
    /* Individual words cycling */
    .lp-tw1,.lp-tw2,.lp-tw3 {{ display: none; }}
    .lp-tw1 {{ display: inline; animation: lp-show1 9s infinite; }}
    .lp-tw2 {{ animation: lp-show2 9s infinite; }}
    .lp-tw3 {{ animation: lp-show3 9s infinite; }}
    @keyframes lp-show1 {{ 0%,33%{{display:inline;opacity:1;}} 34%,100%{{display:none;opacity:0;}} }}
    @keyframes lp-show2 {{ 0%,33%{{display:none;opacity:0;}} 34%,66%{{display:inline;opacity:1;}} 67%,100%{{display:none;opacity:0;}} }}
    @keyframes lp-show3 {{ 0%,66%{{display:none;opacity:0;}} 67%,99%{{display:inline;opacity:1;}} 100%{{display:none;opacity:0;}} }}
    .lp-actions {{
        display: flex; gap: 12px; justify-content: center;
        flex-wrap: wrap; margin-bottom: 60px;
        animation: lp-up .55s .24s ease forwards; opacity: 0;
    }}
    .lp-btn-p {{
        display: inline-flex; align-items: center; gap: 8px;
        background: linear-gradient(135deg,#1d4ed8,#0ea5e9);
        color: #fff; padding: 14px 32px; border-radius: 12px;
        font-weight: 700; font-size: 0.95rem; text-decoration: none;
        box-shadow: 0 4px 18px rgba(29,78,216,0.45); transition: all .2s;
    }}
    .lp-btn-p:hover {{ transform: translateY(-2px); box-shadow: 0 6px 26px rgba(29,78,216,0.6); }}
    .lp-btn-s {{
        display: inline-flex; align-items: center; gap: 8px;
        background: rgba(22,27,34,0.55);
        border: 1.5px solid #79c0ff; color: #79c0ff;
        padding: 14px 26px; border-radius: 12px;
        font-weight: 700; font-size: 0.95rem; text-decoration: none;
        transition: all .2s; box-shadow: 0 0 14px rgba(121,192,255,0.18);
    }}
    .lp-btn-s:hover {{ background: rgba(121,192,255,0.12); border-color: #60a5fa; color: #e6edf3; }}

    /* ── Stats row ── */
    .lp-stats {{
        display: flex;
        background: rgba(22,27,34,0.75);
        border: 1px solid #21262d; border-radius: 14px;
        overflow: hidden; backdrop-filter: blur(10px);
        animation: lp-up .55s .32s ease forwards; opacity: 0;
    }}
    .lp-stat {{ padding: 18px 32px; text-align: center; border-right: 1px solid #21262d; }}
    .lp-stat:last-child {{ border-right: none; }}
    .lp-snum {{
        font-family: 'JetBrains Mono', monospace; font-size: 1.6rem; font-weight: 500;
        background: linear-gradient(135deg,#60a5fa,#38bdf8);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        line-height: 1; margin-bottom: 4px;
    }}
    .lp-slbl {{ font-size: 0.66rem; color: #484f58; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; }}

    @keyframes lp-up {{ from {{ opacity:0; transform:translateY(18px); }} to {{ opacity:1; transform:translateY(0); }} }}

    /* ── Sections ── */
    .lp-section {{ padding: 80px 24px; }}
    .lp-wrap {{ max-width: 1060px; margin: 0 auto; }}
    .lp-section-alt {{ background: rgba(9,13,18,0.5); border-top: 1px solid rgba(33,38,45,0.5); border-bottom: 1px solid rgba(33,38,45,0.5); }}
    .lp-tag {{ font-size: 0.68rem; font-weight: 700; color: #388bfd; letter-spacing: 0.14em; text-transform: uppercase; margin-bottom: 8px; }}
    .lp-sec-h {{ font-weight: 800; font-size: clamp(1.7rem,3vw,2.5rem); line-height: 1.15; letter-spacing: -0.02em; color: #e6edf3; margin-bottom: 12px; }}
    .lp-sec-p {{ font-size: 0.9rem; color: #8b949e; max-width: 480px; line-height: 1.85; }}

    /* ── Condition cards — match .glass-card ── */
    .lp-conds {{ display: grid; grid-template-columns: repeat(3,1fr); gap: 16px; margin-top: 48px; }}
    .lp-cond {{
        background: rgba(22,27,34,0.8);
        border: 1px solid #21262d; border-radius: 16px;
        padding: 28px 24px; transition: all .25s;
        position: relative; overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.5), 0 8px 24px rgba(0,0,0,0.3);
        backdrop-filter: blur(8px);
    }}
    .lp-cond::before {{ content:''; position:absolute; top:0; left:0; right:0; height:3px; }}
    .lp-cond.dep::before {{ background: linear-gradient(90deg,#7c3aed,#818cf8); }}
    .lp-cond.bp::before  {{ background: linear-gradient(90deg,#dc2626,#f87171); }}
    .lp-cond.dia::before {{ background: linear-gradient(90deg,#059669,#34d399); }}
    .lp-cond:hover {{ transform: translateY(-5px); border-color: #30363d; box-shadow: 0 4px 24px rgba(0,0,0,0.4); }}
    .lp-cicon {{ width: 46px; height: 46px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; margin-bottom: 16px; }}
    .dep .lp-cicon {{ background: rgba(124,58,237,0.15); }}
    .bp  .lp-cicon {{ background: rgba(220,38,38,0.15);  }}
    .dia .lp-cicon {{ background: rgba(5,150,105,0.15);  }}
    .lp-cname {{ font-weight: 700; font-size: 1rem; margin-bottom: 8px; color: #e6edf3; }}
    .lp-cdesc {{ font-size: 0.82rem; color: #8b949e; line-height: 1.72; margin-bottom: 16px; }}
    .lp-cpill {{ display: inline-flex; padding: 4px 11px; border-radius: 100px; font-size: 0.68rem; font-weight: 600; font-family: 'JetBrains Mono', monospace; }}
    .dep .lp-cpill {{ background: rgba(124,58,237,0.15); color: #a78bfa; }}
    .bp  .lp-cpill {{ background: rgba(220,38,38,0.15);  color: #f87171; }}
    .dia .lp-cpill {{ background: rgba(5,150,105,0.15);  color: #34d399; }}

    /* ── Feature cards — match .glass-card-accent ── */
    .lp-feats {{ display: grid; grid-template-columns: repeat(3,1fr); gap: 16px; margin-top: 48px; }}
    .lp-feat {{
        background: rgba(22,27,34,0.8);
        border-top: 3px solid #1d4ed8;
        border-left: 1px solid #21262d; border-right: 1px solid #21262d; border-bottom: 1px solid #21262d;
        border-radius: 16px; padding: 24px 20px;
        transition: all .2s; backdrop-filter: blur(8px);
        box-shadow: 0 1px 3px rgba(0,0,0,0.5), 0 8px 24px rgba(0,0,0,0.3);
    }}
    .lp-feat:hover {{ transform: translateY(-3px); border-top-color: #0ea5e9; }}
    .lp-ficon {{ font-size: 1.3rem; margin-bottom: 12px; }}
    .lp-ftitle {{ font-weight: 700; font-size: 0.9rem; margin-bottom: 6px; color: #e6edf3; }}
    .lp-fdesc {{ font-size: 0.8rem; color: #8b949e; line-height: 1.72; }}

    /* ── CTA section ── */
    .lp-cta {{ text-align: center; max-width: 560px; margin: 0 auto; }}
    .lp-cta-h {{ font-weight: 800; font-size: clamp(1.9rem,3.5vw,2.7rem); letter-spacing: -0.02em; color: #e6edf3; margin-bottom: 12px; }}
    .lp-cta-p {{ font-size: 0.95rem; color: #8b949e; margin-bottom: 36px; line-height: 1.85; }}

    /* ── Footer ── */
    .lp-footer {{
        padding: 32px 52px;
        border-top: 1px solid rgba(33,38,45,0.5);
        display: flex; align-items: center; justify-content: space-between;
        background: rgba(9,13,18,0.4);
    }}
    .lp-fl {{ font-size: 0.76rem; color: #484f58; line-height: 1.65; }}
    .lp-fl strong {{ color: #8b949e; }}
    .lp-fr {{ display: flex; gap: 16px; }}
    .lp-flink {{ font-size: 0.76rem; color: #484f58; text-decoration: none; font-weight: 600; transition: color .2s; }}
    .lp-flink:hover {{ color: #e6edf3; }}

    /* ── Scroll reveal ── */
    .lp-rv {{ opacity: 0; transform: translateY(20px); transition: opacity .65s ease, transform .65s ease; }}
    .lp-rv.in {{ opacity: 1; transform: translateY(0); }}
    .d1 {{ transition-delay: .08s; }} .d2 {{ transition-delay: .16s; }} .d3 {{ transition-delay: .24s; }}

    @media(max-width:760px) {{
        .lp-nav {{ padding: 0 16px; }}
        .lp-conds, .lp-feats {{ grid-template-columns: 1fr; }}
        .lp-stats {{ flex-direction: column; }}
        .lp-stat {{ border-right: none; border-bottom: 1px solid #21262d; }}
        .lp-stat:last-child {{ border-bottom: none; }}
        .lp-footer {{ flex-direction: column; gap: 12px; text-align: center; padding: 24px 20px; }}
    }}
    </style>

    <!-- NAV -->
    <div class="lp">
    <div class="lp-nav">
      <a href="#" class="lp-logo">
        <div class="lp-logo-icon">⚕</div>
        <span class="lp-logo-name">MedInsight <em>AI</em></span>
      </a>
      <div class="lp-nav-links">
        <a href="#lp-conditions" class="lp-nav-link">Conditions</a>
        <a href="#lp-features"   class="lp-nav-link">Features</a>
        <a href="/Login" target="_self" class="lp-nav-btn">Sign In →</a>
      </div>
    </div>

    <!-- HERO -->
    <div class="lp-hero">
      <div class="lp-badge"><span class="lp-dot"></span>AI-Powered Drug Recommendation</div>
      <h1 class="lp-h1">Find the Right Drug<br><span class="lp-grad">for Your Condition</span></h1>
      <p class="lp-sub">
        Describe your symptoms and let MedInsight AI recommend the best-rated drugs for
        <span class="lp-tw-wrap"><span class="lp-tw1">Depression</span><span class="lp-tw2">High Blood Pressure</span><span class="lp-tw3">Type 2 Diabetes</span></span>
        backed by 161,000+ real patient reviews.
      </p>
      <div class="lp-actions">
        <a href="/Login" target="_self" class="lp-btn-p">⚕ &nbsp;Get Started Free</a>
        <a href="#lp-conditions" class="lp-btn-s">See What We Cover</a>
      </div>
      <div class="lp-stats">
        <div class="lp-stat"><div class="lp-snum">96.2%</div><div class="lp-slbl">Accuracy</div></div>
        <div class="lp-stat"><div class="lp-snum">161K+</div><div class="lp-slbl">Patient Reviews</div></div>
        <div class="lp-stat"><div class="lp-snum">800+</div><div class="lp-slbl">Drugs Analysed</div></div>
        <div class="lp-stat"><div class="lp-snum">3</div><div class="lp-slbl">Conditions</div></div>
      </div>
    </div>

    <!-- CONDITIONS -->
    <div class="lp-section" id="lp-conditions">
      <div class="lp-wrap">
        <div class="lp-rv">
          <div class="lp-tag">What We Cover</div>
          <h2 class="lp-sec-h">Three Conditions.<br>Thousands of Reviews.</h2>
          <p class="lp-sec-p">Our AI analyses real patient reviews to surface the most effective, highest-rated drugs for each condition.</p>
        </div>
        <div class="lp-conds">
          <div class="lp-cond dep lp-rv d1">
            <div class="lp-cicon">🧠</div>
            <div class="lp-cname">Depression</div>
            <p class="lp-cdesc">Compare antidepressants by real patient satisfaction scores and discover which treatments work best.</p>
            <span class="lp-cpill">SSRIs · SNRIs · Atypical</span>
          </div>
          <div class="lp-cond bp lp-rv d2">
            <div class="lp-cicon">🫀</div>
            <div class="lp-cname">High Blood Pressure</div>
            <p class="lp-cdesc">Explore top-rated antihypertensives chosen by real patients and ranked by effectiveness and tolerability.</p>
            <span class="lp-cpill">ACE · ARBs · Beta Blockers</span>
          </div>
          <div class="lp-cond dia lp-rv d3">
            <div class="lp-cicon">🩸</div>
            <div class="lp-cname">Type 2 Diabetes</div>
            <p class="lp-cdesc">Discover diabetes medications with the highest satisfaction scores and fewest reported side effects.</p>
            <span class="lp-cpill">Metformin · GLP-1 · DPP-4</span>
          </div>
        </div>
      </div>
    </div>

    <!-- FEATURES -->
    <div class="lp-section lp-section-alt" id="lp-features">
      <div class="lp-wrap">
        <div class="lp-rv" style="text-align:center;">
          <div class="lp-tag">Platform Features</div>
          <h2 class="lp-sec-h">Built for Real Insights</h2>
        </div>
        <div class="lp-feats">
          <div class="lp-feat lp-rv d1"><div class="lp-ficon">⚡</div><div class="lp-ftitle">Instant Predictions</div><p class="lp-fdesc">Enter your symptoms and get a condition prediction with personalised drug recommendations in seconds.</p></div>
          <div class="lp-feat lp-rv d2"><div class="lp-ficon">💊</div><div class="lp-ftitle">Drug Rankings</div><p class="lp-fdesc">See the highest-rated medications per condition, ranked by real patient ratings and review usefulness scores.</p></div>
          <div class="lp-feat lp-rv d3"><div class="lp-ficon">📈</div><div class="lp-ftitle">Visual Insights</div><p class="lp-fdesc">Interactive charts revealing drug effectiveness trends, rating distributions, and top-performing treatments.</p></div>
          <div class="lp-feat lp-rv d1"><div class="lp-ficon">🔒</div><div class="lp-ftitle">Secure &amp; Private</div><p class="lp-fdesc">Your account and prediction history are protected with secure authentication so only you can see your data.</p></div>
          <div class="lp-feat lp-rv d2"><div class="lp-ficon">📋</div><div class="lp-ftitle">Prediction History</div><p class="lp-fdesc">Every query is saved to your personal history so you can revisit and compare recommendations any time.</p></div>
          <div class="lp-feat lp-rv d3"><div class="lp-ficon">✅</div><div class="lp-ftitle">Confidence Scores</div><p class="lp-fdesc">Each prediction includes a per-condition confidence percentage so you know exactly how certain the AI is.</p></div>
        </div>
      </div>
    </div>

    <!-- CTA -->
    <div class="lp-section">
      <div class="lp-wrap">
        <div class="lp-cta lp-rv">
          <h2 class="lp-cta-h">Ready to Find<br>Your Best Match?</h2>
          <p class="lp-cta-p">Create a free account and start exploring personalised drug recommendations based on real patient experiences.</p>
          <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap;">
            <a href="/Login" target="_self" class="lp-btn-p">⚕ &nbsp;Get Started Free</a>
            <a href="#lp-conditions" class="lp-btn-s">Learn More</a>
          </div>
        </div>
      </div>
    </div>

    <!-- FOOTER -->
    <div class="lp-footer">
      <div class="lp-fl">
        <strong>MedInsight AI</strong> · Limkokwing University of Creative Technology · Lesotho<br>
        For educational and research purposes only. Not a substitute for professional medical advice.
      </div>
      <div class="lp-fr">
        <a href="#lp-conditions" class="lp-flink">Conditions</a>
        <a href="#lp-features"   class="lp-flink">Features</a>
        <a href="/Login" target="_self" class="lp-flink">Sign In</a>
      </div>
    </div>
    </div>

    <script>
    // Force-reveal all scroll-reveal elements (IntersectionObserver is unreliable in Streamlit)
    function revealAll() {{
      document.querySelectorAll(".lp-rv").forEach(function(el) {{
        el.classList.add("in");
      }});
    }}
    revealAll();
    setTimeout(revealAll, 150);
    setTimeout(revealAll, 500);

    document.querySelectorAll('a[href^="#"]').forEach(a => {{
      a.addEventListener("click", e => {{
        const t = document.querySelector(a.getAttribute("href"));
        if (t) {{ e.preventDefault(); t.scrollIntoView({{behavior:"smooth"}}); }}
      }});
    }});
    </script>
    """, unsafe_allow_html=True)
    st.stop()


# ── Load data ─────────────────────────────────────────────────────────────────
model, vectorizer, df = load_assets()
drug_stats = get_drug_stats(df)

# ── Header ────────────────────────────────────────────────────────────────────
render_header(LOGO_PATH, "home")

# ── Welcome banner ────────────────────────────────────────────────────────────
user = st.session_state.user_info.get("username", "User")
st.markdown(f"""
<div style="background:linear-gradient(135deg,rgba(29,78,216,0.15),rgba(14,165,233,0.1));
     border:1px solid rgba(56,139,253,0.25);border-radius:14px;
     padding:14px 24px;margin-bottom:24px;
     display:flex;align-items:center;justify-content:space-between;">
  <div>
    <span style="color:#79c0ff;font-size:0.75rem;font-weight:700;text-transform:uppercase;
                 letter-spacing:0.1em;">Signed in as</span>
    <span style="color:#e6edf3;font-weight:700;font-size:0.95rem;margin-left:8px;">{user}</span>
  </div>
  <span style="color:#484f58;font-size:0.75rem;">Drug Recommendation &amp; Condition Classification</span>
</div>
""", unsafe_allow_html=True)

# ── Metric tiles ──────────────────────────────────────────────────────────────
m1, m2, m3 = st.columns(3)
for col, (val, lbl) in zip([m1, m2, m3], [
    ("18,628", "Training Samples"), ("3", "Conditions"), ("800+", "Unique Drugs"),
]):
    col.markdown(
        f'<div class="metric-tile"><div class="metric-value">{val}</div>'
        f'<div class="metric-label">{lbl}</div></div>',
        unsafe_allow_html=True)

st.markdown("<div style='margin:24px 0;'></div>", unsafe_allow_html=True)


# ── Quick nav cards pointing to Analytics ─────────────────────────────────────
_token = st.session_state.get("_auth_token", "")
_t = f"?t={_token}" if _token else ""

st.markdown(
    '<div class="glass-card">'
    '<div class="section-heading">Explore The Data</div>'
    '<div class="section-title">Analytics &amp; Model Performance</div>',
    unsafe_allow_html=True)

st.markdown("""
<div style="color:#8b949e;font-size:0.875rem;line-height:1.8;margin-bottom:20px;">
  All dataset charts, drug distribution figures, and model performance metrics are available
  on the <strong style="color:#e6edf3;">Analytics</strong> page.
</div>
""", unsafe_allow_html=True)

nav1, nav2 = st.columns(2)
nav1.markdown(f"""
<a href="/Analytics{_t}" target="_self" style="text-decoration:none;">
  <div class="metric-tile" style="border-top:3px solid #2563eb;cursor:pointer;transition:all .2s;">
    <div style="font-size:2rem;margin-bottom:8px;">📊</div>
    <div style="font-size:0.9rem;font-weight:700;color:#e6edf3;">Dataset Analytics</div>
    <div style="font-size:0.75rem;color:#484f58;margin-top:4px;">Condition charts, drug distributions &amp; rating histograms</div>
  </div>
</a>
""", unsafe_allow_html=True)
nav2.markdown(f"""
<a href="/Predict{_t}" target="_self" style="text-decoration:none;">
  <div class="metric-tile" style="border-top:3px solid #059669;cursor:pointer;transition:all .2s;">
    <div style="font-size:2rem;margin-bottom:8px;">⚕️</div>
    <div style="font-size:0.9rem;font-weight:700;color:#e6edf3;">Predict Condition</div>
    <div style="font-size:0.75rem;color:#484f58;margin-top:4px;">Enter symptoms &amp; get drug recommendations</div>
  </div>
</a>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:24px 0 8px;
            font-size:0.72rem;color:#30363d;letter-spacing:0.04em;">
  MedInsight AI · For research and educational purposes only
</div>
""", unsafe_allow_html=True)