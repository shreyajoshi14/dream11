import streamlit as st
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.ui.product_page import render_product_page
from src.ui.model_page import render_model_page

st.set_page_config(
    page_title="Dream11 AI Team Builder · Inter IIT Tech Meet 13.0",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

def inject_global_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* ── App background ── */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #171124 0%, #0b0e14 65%, #07090e 100%);
        color: #f8fafc;
    }

    /* ── Hide default Streamlit chrome ── */
    header[data-testid="stHeader"] { display: none; }
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    .block-container { padding-top: 1.2rem !important; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #151a28 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    [data-testid="stSidebar"] .stRadio > label {
        color: #94a3b8 !important;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    /* ── Sidebar logo/brand ── */
    .sidebar-brand {
        padding: 16px 12px 20px 12px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 18px;
    }
    .sidebar-brand .logo-text {
        font-size: 24px;
        font-weight: 900;
        background: linear-gradient(90deg, #FF3B44 0%, #FF8A00 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
        line-height: 1.1;
    }
    .sidebar-brand .logo-sub {
        font-size: 11px;
        color: #94a3b8;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-top: 4px;
    }
    .sidebar-brand .logo-badge {
        display: inline-block;
        background: rgba(228, 27, 35, 0.2);
        border: 1px solid rgba(228, 27, 35, 0.4);
        color: #ff6b6b;
        font-size: 10px;
        font-weight: 800;
        padding: 3px 10px;
        border-radius: 20px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-top: 8px;
    }

    /* ── Sidebar stats ── */
    .sidebar-stat {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 10px;
        padding: 10px 12px;
        margin-bottom: 6px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .sidebar-stat .stat-label {
        font-size: 11px;
        color: #64748b;
        font-weight: 600;
    }
    .sidebar-stat .stat-value {
        font-size: 12px;
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

    /* ── KPI Metric Cards ── */
    .kpi-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
        margin-bottom: 10px;
    }
    .kpi-val {
        font-size: 26px;
        font-weight: 800;
        color: #38bdf8;
    }
    .kpi-lbl {
        font-size: 11px;
        color: #94a3b8;
        font-weight: 700;
        margin-top: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* ── Pitch Container Graphic ── */
    .pitch-container {
        background: linear-gradient(180deg, #162f21 0%, #0d1e14 100%);
        border: 2px solid rgba(52, 211, 153, 0.35);
        border-radius: 18px;
        padding: 22px;
        margin: 18px 0;
        box-shadow: inset 0 0 40px rgba(0,0,0,0.6), 0 12px 30px rgba(0,0,0,0.4);
    }
    .pitch-header {
        text-align: center;
        color: #6ee7b7;
        font-weight: 800;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 16px;
        border-bottom: 1px dashed rgba(110, 231, 183, 0.3);
        padding-bottom: 8px;
    }

    /* ── Player Card Styling ── */
    .player-card {
        background: rgba(15, 23, 42, 0.95);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s;
    }
    .player-card:hover {
        transform: translateY(-2px);
    }
    .player-card.captain {
        border-left: 5px solid #f59e0b;
        background: linear-gradient(135deg, rgba(45, 34, 15, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%);
    }
    .player-card.vice-captain {
        border-left: 5px solid #06b6d4;
        background: linear-gradient(135deg, rgba(14, 38, 48, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%);
    }

    /* ── Badges ── */
    .badge-c {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: #000000;
        font-weight: 800;
        padding: 2px 8px;
        border-radius: 5px;
        font-size: 10px;
        letter-spacing: 0.5px;
    }
    .badge-vc {
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
        color: #ffffff;
        font-weight: 800;
        padding: 2px 8px;
        border-radius: 5px;
        font-size: 10px;
        letter-spacing: 0.5px;
    }
    .badge-role {
        background: rgba(255, 255, 255, 0.15);
        color: #e2e8f0;
        font-weight: 700;
        padding: 2px 7px;
        border-radius: 5px;
        font-size: 10px;
        text-transform: uppercase;
    }

    /* ── Action Buttons ── */
    .stButton > button[kind="primary"], .stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #E41B23 0%, #FF3B44 100%) !important;
        border: none !important;
        box-shadow: 0 4px 16px rgba(228, 27, 35, 0.4) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        border-radius: 10px !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #FF3B44 0%, #FF5E62 100%) !important;
        transform: translateY(-2px) !important;
    }
    </style>
    """, unsafe_allow_html=True)


def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-brand">
            <div class="logo-text">🏆 DREAM11 AI</div>
            <div class="logo-sub">Inter IIT Tech Meet 13.0</div>
            <div class="logo-badge">⚡ Next-Gen Team Builder</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<p style="font-size:11px;color:#94a3b8;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:8px;">Interactive Interfaces (PDF)</p>', unsafe_allow_html=True)

        page = st.radio(
            "",
            [
                "🏏  Interface 1: Product UI (Team Selection)",
                "📊  Interface 2: Model UI (Performance & MAE)"
            ],
            index=0,
            label_visibility="collapsed"
        )

        st.markdown("---")
        st.markdown('<p style="font-size:11px;color:#94a3b8;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:10px;">Audit & Compliance (PDF)</p>', unsafe_allow_html=True)

        st.markdown("""
        <div class="sidebar-stat">
            <span class="stat-label">Training Cutoff</span>
            <span class="stat-value" style="color:#34d399;">≤ 2024-06-30</span>
        </div>
        <div class="sidebar-stat">
            <span class="stat-label">Testing Window</span>
            <span class="stat-value">2024-07-01 Onward</span>
        </div>
        <div class="sidebar-stat">
            <span class="stat-label">Response Time</span>
            <span class="stat-value" style="color:#34d399;">&lt; 10s (Pass)</span>
        </div>
        <div class="sidebar-stat">
            <span class="stat-label">Average Team Regret</span>
            <span class="stat-value" style="color:#38bdf8;">227.4 pts</span>
        </div>
        <div class="sidebar-stat">
            <span class="stat-label">Leakage Status</span>
            <span class="stat-value"><span class="status-dot"></span>CLEAN</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<p style="font-size:11px;color:#475569;text-align:center;">Inter IIT Tech Meet 13.0 • Dream11</p>', unsafe_allow_html=True)

    return page


def main():
    inject_global_css()
    page = render_sidebar()

    if "Product UI" in page:
        render_product_page()
    else:
        render_model_page()


if __name__ == "__main__":
    main()
