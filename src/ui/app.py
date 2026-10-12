import streamlit as st
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.ui.product_page import render_product_page
from src.ui.model_page import render_model_page

st.set_page_config(
    page_title="Dream11 AI Optimizer",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

def inject_global_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── App background ── */
    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #0f1629 50%, #0a0e1a 100%);
        color: #e2e8f0;
    }

    /* ── Hide default Streamlit chrome ── */
    header[data-testid="stHeader"] { display: none; }
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    .block-container { padding-top: 1.5rem !important; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #161b2c 100%);
        border-right: 1px solid #1e2d47;
    }
    [data-testid="stSidebar"] .stRadio > label {
        color: #94a3b8 !important;
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    [data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
        color: #cbd5e1;
        font-size: 14px;
        font-weight: 500;
    }

    /* ── Sidebar logo/brand ── */
    .sidebar-brand {
        padding: 20px 16px 24px 16px;
        border-bottom: 1px solid #1e2d47;
        margin-bottom: 20px;
    }
    .sidebar-brand .logo-text {
        font-size: 26px;
        font-weight: 900;
        background: linear-gradient(90deg, #e63946, #ff6b6b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
        line-height: 1;
    }
    .sidebar-brand .logo-sub {
        font-size: 11px;
        color: #475569;
        font-weight: 600;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-top: 4px;
    }
    .sidebar-brand .logo-badge {
        display: inline-block;
        background: linear-gradient(90deg, #e63946, #b91c1c);
        color: white;
        font-size: 9px;
        font-weight: 800;
        padding: 2px 8px;
        border-radius: 20px;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-top: 8px;
    }

    /* ── Nav buttons ── */
    .nav-btn {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 14px;
        border-radius: 10px;
        margin-bottom: 4px;
        cursor: pointer;
        transition: all 0.15s ease;
        color: #94a3b8;
        font-size: 14px;
        font-weight: 500;
        border: 1px solid transparent;
        text-decoration: none;
    }
    .nav-btn.active {
        background: rgba(230,57,70,0.12);
        border-color: rgba(230,57,70,0.3);
        color: #f87171;
    }
    .nav-btn:hover {
        background: rgba(255,255,255,0.05);
        color: #e2e8f0;
    }
    .nav-icon { font-size: 18px; }

    /* ── Sidebar stats ── */
    .sidebar-stat {
        background: rgba(255,255,255,0.03);
        border: 1px solid #1e2d47;
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .sidebar-stat .stat-label {
        font-size: 12px;
        color: #64748b;
        font-weight: 500;
    }
    .sidebar-stat .stat-value {
        font-size: 14px;
        color: #e2e8f0;
        font-weight: 700;
    }
    .status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #22c55e;
        box-shadow: 0 0 6px #22c55e;
        margin-right: 5px;
    }

    /* ── Page header ── */
    .page-header {
        background: linear-gradient(135deg, #0f1629 0%, #1a2035 100%);
        border: 1px solid #1e2d47;
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }
    .page-header::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(135deg, rgba(230,57,70,0.08) 0%, transparent 60%);
        pointer-events: none;
    }
    .page-header h1 {
        font-size: 32px;
        font-weight: 900;
        color: #f1f5f9;
        margin: 0 0 6px 0;
        letter-spacing: -0.5px;
    }
    .page-header .subtitle {
        font-size: 15px;
        color: #64748b;
        font-weight: 400;
    }
    .page-header .accent {
        color: #e63946;
    }
    </style>
    """, unsafe_allow_html=True)


def render_sidebar(current_page):
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-brand">
            <div class="logo-text">DREAM11</div>
            <div class="logo-sub">AI Team Optimizer</div>
            <div class="logo-badge">⚡ Powered by ML</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<p style="font-size:11px;color:#475569;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:8px;">Navigation</p>', unsafe_allow_html=True)

        page = st.radio(
            "",
            ["🏏  Team Optimizer", "📊  Model Metrics"],
            index=0 if current_page == "product" else 1,
            label_visibility="collapsed"
        )

        st.markdown("---")
        st.markdown('<p style="font-size:11px;color:#475569;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:10px;">System Status</p>', unsafe_allow_html=True)

        st.markdown("""
        <div class="sidebar-stat">
            <span class="stat-label">Data Engine</span>
            <span class="stat-value"><span class="status-dot"></span>Active</span>
        </div>
        <div class="sidebar-stat">
            <span class="stat-label">Data Cutoff</span>
            <span class="stat-value">2024-06-30</span>
        </div>
        <div class="sidebar-stat">
            <span class="stat-label">Format</span>
            <span class="stat-value">T20 Cricket</span>
        </div>
        <div class="sidebar-stat">
            <span class="stat-label">Optimizer</span>
            <span class="stat-value">ILP + SHAP</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<p style="font-size:11px;color:#3b4559;text-align:center;">Dream11 AI • Milestone 1</p>', unsafe_allow_html=True)

    return page


def main():
    inject_global_css()

    if "page" not in st.session_state:
        st.session_state.page = "product"

    page = render_sidebar(st.session_state.page)

    if "Team Optimizer" in page:
        render_product_page()
    else:
        render_model_page()


if __name__ == "__main__":
    main()
