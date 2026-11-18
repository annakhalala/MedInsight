"""
Shared CSS injected into every authenticated page (Home, Predict, Analytics,
Login).

These tokens and component styles are pulled directly from landing_page.html
so the in-app pages read as a continuation of that page rather than a
separate skin: same CSS variables, same font pairing, same card/button/pill
treatment, same soft background "glow" blobs.
"""

SHARED_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Design tokens — copied verbatim from landing_page.html :root ───────── */
:root{
    --bg:#0d1117; --surface:#161b22; --card:#161b22; --border:#21262d; --border2:#30363d;
    --text:#e6edf3; --muted:#8b949e; --dim:#484f58;
    --blue:#1d4ed8; --sky:#0ea5e9; --accent:#388bfd; --lb:#79c0ff;
    --dep:#7c3aed; --bp:#dc2626; --dia:#059669;
}

#MainMenu, footer, header, [data-testid="stToolbar"] { visibility: hidden; }
.block-container { padding: 2.2rem 3rem 3rem !important; max-width: 1180px !important; position: relative; z-index: 1; }

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: var(--text);
    line-height: 1.6;
}

/* Same ambient background blobs as .glow a / .glow b on the landing page */
body::before, body::after{
    content:''; position:fixed; border-radius:50%; pointer-events:none;
    z-index:0; filter: blur(100px);
}
body::before{ width:600px; height:600px; top:-180px; left:-180px; background:#1d4ed8; opacity:0.09; }
body::after{ width:450px; height:450px; bottom:-120px; right:-120px; background:#0ea5e9; opacity:0.06; }

::-webkit-scrollbar{ width:6px; }
::-webkit-scrollbar-track{ background:#161b22; }
::-webkit-scrollbar-thumb{ background:#2563eb; border-radius:3px; }

/* ── Header / nav — mirrors landing_page.html's <nav> ────────────────────── */
.mi-header{
    position: sticky; top: 0; z-index: 100;
    display:flex; align-items:center; justify-content:space-between;
    padding: 0 32px; height: 64px; margin: -2.2rem -3rem 26px;
    background: rgba(13,17,23,0.88); border-bottom:1px solid rgba(33,38,45,0.8);
    backdrop-filter: blur(16px);
}
.mi-logo{ display:flex; align-items:center; gap:11px; text-decoration:none; }
.mi-logo-icon{
    width:36px; height:36px; border-radius:10px;
    background: linear-gradient(135deg,#1d4ed8,#0ea5e9);
    display:flex; align-items:center; justify-content:center; font-size:17px;
    box-shadow: 0 4px 16px rgba(29,78,216,0.45);
    overflow: hidden;
}
.mi-logo-icon img{ width:100%; height:100%; object-fit:cover; }
.mi-logo-name{ font-weight:800; font-size:1.05rem; color:var(--text); letter-spacing:-0.01em; }
.mi-logo-name em{ font-style:normal; background:linear-gradient(135deg,#60a5fa,#38bdf8); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.mi-nav{ display:flex; align-items:center; gap:4px; }
.mi-nav-link{
    padding:7px 14px; border-radius:8px; font-size:0.85rem; font-weight:600;
    color:var(--muted); text-decoration:none; transition: all .2s;
}
.mi-nav-link:hover{ color:var(--text); background: rgba(33,38,45,0.6); }
.mi-nav-link.active{ color:var(--text); background: rgba(29,78,216,0.18); }
.mi-nav-user{ display:flex; align-items:center; gap:12px; }
.mi-nav-uname{ font-size:0.8rem; color:var(--muted); font-weight:600; }
.mi-nav-logout{
    padding:7px 14px; border-radius:9px; font-size:0.78rem; font-weight:700;
    color:#f87171; text-decoration:none; border:1px solid rgba(220,38,38,0.35);
    background: rgba(220,38,38,0.08); transition: all .2s;
}
.mi-nav-logout:hover{ background: rgba(220,38,38,0.18); }

/* ── Cards — same recipe as .cond / .feat on the landing page ───────────── */
.glass-card{
    background: var(--card); border:1px solid var(--border);
    border-radius:16px; padding: 28px 24px; margin-bottom: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.4), 0 8px 24px rgba(0,0,0,0.2);
    transition: all .25s;
}
.glass-card-accent{
    background: var(--card);
    border-top:3px solid var(--blue);
    border-left:1px solid var(--border); border-right:1px solid var(--border); border-bottom:1px solid var(--border);
    border-radius:16px; padding: 24px 20px; margin-bottom: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.4), 0 8px 24px rgba(0,0,0,0.2);
    transition: all .2s;
}
.glass-card-accent:hover{ transform: translateY(-3px); border-top-color: var(--sky); }

.section-heading{ font-size:0.68rem; font-weight:700; color:var(--accent); letter-spacing:0.14em; text-transform:uppercase; margin-bottom:8px; }
.section-title{ font-weight:800; font-size:1.5rem; line-height:1.15; letter-spacing:-0.02em; margin-bottom:14px; color:var(--text); }

/* ── Metric tiles — same recipe as .stats-row / .stat / .snum / .slbl ───── */
.metric-tile{
    background: var(--surface); border:1px solid var(--border); border-radius:14px;
    padding: 18px 20px; text-align:center; border-top:3px solid var(--blue);
}
.metric-value{
    font-family:'JetBrains Mono', monospace; font-size:1.6rem; font-weight:500; line-height:1;
    background: linear-gradient(135deg,#60a5fa,#38bdf8);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}
.metric-label{ font-size:0.65rem; color:var(--dim); font-weight:700; letter-spacing:0.08em; text-transform:uppercase; margin-top:4px; }

/* ── Pills / badges — identical to .cpill on the landing page ───────────── */
.mi-pill{ display:inline-flex; padding:4px 11px; border-radius:100px; font-size:0.68rem; font-weight:600; font-family:'JetBrains Mono', monospace; }
.mi-pill.dep{ background: rgba(124,58,237,0.15); color:#a78bfa; }
.mi-pill.bp{ background: rgba(220,38,38,0.15); color:#f87171; }
.mi-pill.dia{ background: rgba(5,150,105,0.15); color:#34d399; }

/* ── Form controls (Login / Predict) ─────────────────────────────────────── */
.stTextInput input, .stTextArea textarea{
    background: rgba(13,17,23,0.75) !important; border:1px solid var(--border2) !important;
    color: var(--text) !important; border-radius:10px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus{ border-color: var(--accent) !important; box-shadow: 0 0 0 1px var(--accent) !important; }

/* Streamlit buttons styled to match .btn-p on the landing page */
.stButton button{
    background: linear-gradient(135deg,#1d4ed8,#0ea5e9) !important; color:#fff !important;
    border:none !important; border-radius:12px !important; font-weight:700 !important;
    padding: 0.65rem 1.6rem !important;
    box-shadow: 0 4px 16px rgba(29,78,216,0.45) !important;
    transition: all .2s !important;
}
.stButton button:hover{
    box-shadow: 0 6px 24px rgba(37,99,235,0.55) !important;
    transform: translateY(-2px);
}

.stTabs [data-baseweb="tab-list"]{ gap: 6px; }
.stTabs [data-baseweb="tab"]{ background: var(--surface); border-radius: 9px 9px 0 0; color: var(--muted); }
.stTabs [aria-selected="true"]{ color: var(--text) !important; background: rgba(29,78,216,0.18) !important; }

/* ── Alerts ────────────────────────────────────────────────────────────── */
.stAlert{ border-radius: 12px !important; }

/* ── Footer note (Login page) — mirrors landing page's <footer> .fl text ── */
.mi-footnote{ font-size:0.75rem; color:var(--dim); line-height:1.65; text-align:center; }
</style>
"""
