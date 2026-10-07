import streamlit as st
import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.ui.product_page import render_product_page
from src.ui.model_page import render_model_page

# --- Page Configuration & Layout ---
st.set_page_config(
    page_title="Dream11 AI Team Builder",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def inject_custom_css():
    CUSTOM_CSS = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* Main Background */
        .stApp {
            background: radial-gradient(circle at 50% 0%, #1a1226 0%, #0b0e14 70%, #07090e 100%);
            color: #f8fafc;
        }
        
        /* Header Banner */
        .hero-banner {
            background: linear-gradient(135deg, rgba(228, 27, 35, 0.22) 0%, rgba(30, 20, 50, 0.65) 50%, rgba(15, 20, 32, 0.95) 100%);
            border: 1px solid rgba(239, 68, 68, 0.35);
            border-radius: 20px;
            padding: 24px 28px;
            margin-bottom: 24px;
            box-shadow: 0 20px 40px -15px rgba(228, 27, 35, 0.3);
        }
        
        .hero-title {
            font-size: 30px;
            font-weight: 800;
            background: linear-gradient(90deg, #FF3B44 0%, #FF8A00 50%, #FFC700 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
            letter-spacing: -0.8px;
        }
        
        .hero-subtitle {
            font-size: 14px;
            color: #94a3b8;
            font-weight: 500;
            margin-top: 4px;
        }
        
        /* Pitch Container Graphic */
        .pitch-container {
            background: linear-gradient(180deg, #193324 0%, #0f2117 100%);
            border: 2px solid rgba(52, 211, 153, 0.35);
            border-radius: 18px;
            padding: 20px;
            margin: 18px 0;
            box-shadow: inset 0 0 40px rgba(0,0,0,0.6), 0 12px 30px rgba(0,0,0,0.4);
        }
        
        .pitch-header {
            text-align: center;
            color: #6ee7b7;
            font-weight: 800;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 16px;
            border-bottom: 1px dashed rgba(110, 231, 183, 0.3);
            padding-bottom: 8px;
        }

        /* Player Card Styling */
        .player-card {
            background: rgba(15, 23, 42, 0.95);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 12px;
            padding: 12px;
            margin-bottom: 10px;
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
        
        /* Badges */
        .badge-c {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: #000000;
            font-weight: 800;
            padding: 2px 7px;
            border-radius: 5px;
            font-size: 10px;
            letter-spacing: 0.5px;
        }
        
        .badge-vc {
            background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
            color: #ffffff;
            font-weight: 800;
            padding: 2px 7px;
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

        .badge-pts {
            background: linear-gradient(135deg, rgba(228, 27, 35, 0.3) 0%, rgba(228, 27, 35, 0.15) 100%);
            color: #ff6b6b;
            border: 1px solid rgba(228, 27, 35, 0.4);
            font-weight: 800;
            padding: 3px 8px;
            border-radius: 20px;
            font-size: 12px;
        }
        
        /* KPI Metric Cards */
        .kpi-card {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 14px;
            padding: 14px;
            text-align: center;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
            margin-bottom: 10px;
        }
        
        .kpi-val {
            font-size: 24px;
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
        
        /* Streamlit Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 12px;
            background-color: rgba(15, 23, 42, 0.7);
            padding: 8px;
            border-radius: 14px;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 10px;
            color: #94a3b8;
            font-weight: 600;
            padding: 12px 24px;
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #E41B23 0%, #FF3B44 100%) !important;
            color: #ffffff !important;
            font-weight: 700 !important;
        }

        /* All Secondary / Preset Buttons */
        .stButton > button {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%) !important;
            color: #f8fafc !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            font-weight: 700 !important;
            padding: 10px 16px !important;
            border-radius: 10px !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
            transition: all 0.2s ease-in-out !important;
            width: 100%;
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, rgba(56, 189, 248, 0.2) 0%, rgba(30, 41, 59, 0.95) 100%) !important;
            border-color: #38bdf8 !important;
            transform: translateY(-2px) !important;
        }
        
        /* Primary Action Buttons */
        .stButton > button[kind="primary"], .stButton > button[data-testid="baseButton-primary"] {
            background: linear-gradient(135deg, #E41B23 0%, #FF3B44 100%) !important;
            border: none !important;
            box-shadow: 0 4px 16px rgba(228, 27, 35, 0.4) !important;
        }
        
        .stButton > button[kind="primary"] p, .stButton > button[kind="primary"] span,
        .stButton > button[data-testid="baseButton-primary"] p, .stButton > button[data-testid="baseButton-primary"] span {
            color: #ffffff !important;
            font-weight: 800 !important;
        }

        .stButton > button[kind="primary"]:hover, .stButton > button[data-testid="baseButton-primary"]:hover {
            background: linear-gradient(135deg, #FF3B44 0%, #FF5E62 100%) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 24px rgba(228, 27, 35, 0.6) !important;
        }
        
        /* Input Labels */
        .stSelectbox label, .stDateInput label, .stRadio label {
            color: #e2e8f0 !important;
            font-weight: 700 !important;
        }
        
        div[data-baseweb="select"] > div {
            background-color: rgba(15, 23, 42, 0.95) !important;
            border-color: rgba(255, 255, 255, 0.18) !important;
            border-radius: 10px !important;
        }

        header {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def render_header():
    import textwrap
    header_html = textwrap.dedent("""
    <div class="hero-banner">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
            <div>
                <div class="hero-title">🏆 DREAM11 NEXT-GEN TEAM BUILDER</div>
                <div class="hero-subtitle">Inter IIT Tech Meet 13.0 · Predictive Machine Learning & GenAI Explainability Engine</div>
            </div>
            <div style="display: flex; gap: 10px; align-items: center;">
                <span style="background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 700;">
                    🟢 PREDICTIVE MODEL LOADED
                </span>
                <span style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 700;">
                    🛡️ STRICT CUTOFF: 2024-06-30
                </span>
            </div>
        </div>
    </div>
    """)
    st.markdown(header_html, unsafe_allow_html=True)

def main():
    inject_custom_css()
    render_header()
    
    tab1, tab2 = st.tabs([
        "🏏 Product UI – Team Selection & AI Coach",
        "📊 Model UI – Benchmarking & Evaluation"
    ])
    
    with tab1:
        render_product_page()
        
    with tab2:
        render_model_page()

if __name__ == "__main__":
    main()
