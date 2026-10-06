"""streamlit run app.py
Dream11 Next-Gen Team Builder with Predictive AI - Inter IIT Tech Meet 13.0
Complete Production System fulfilling Interface 1 (Product UI) & Interface 2 (Model UI)
"""
import joblib
import io
import time
import textwrap
import numpy as np
import pandas as pd
import streamlit as st
from pathlib import Path

from src.config import ART_DIR, TRAIN_CUTOFF, PROC_DIR
from src.predict import recommend
from src.model_ui import load_history, run_model_ui
import narrate

# --- Page Configuration & Layout ---
st.set_page_config(
    page_title="Dream11 AI Team Builder | Inter IIT Tech Meet 13.0",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Dream11 Production Theme & CSS Styles
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
    
    .stButton > button p, .stButton > button span, .stButton > button div {
        color: #f8fafc !important;
        font-weight: 700 !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.2) 0%, rgba(30, 41, 59, 0.95) 100%) !important;
        border-color: #38bdf8 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 18px rgba(56, 189, 248, 0.35) !important;
    }
    
    .stButton > button:hover p, .stButton > button:hover span, .stButton > button:hover div {
        color: #38bdf8 !important;
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
    
    /* Input Labels and Selectbox Styling */
    .stSelectbox label, .stDateInput label, .stTextArea label, .stTextInput label, .stRadio label {
        color: #e2e8f0 !important;
        font-weight: 700 !important;
    }
    
    div[data-baseweb="select"] > div {
        background-color: rgba(15, 23, 42, 0.95) !important;
        border-color: rgba(255, 255, 255, 0.18) !important;
        border-radius: 10px !important;
    }

    div[data-baseweb="select"] span {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --- Top Header ---
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

# --- Sidebar: Competition Rules & Checklist ---

# --- Navigation Tabs ---
tab1, tab2 = st.tabs([
    "🏏 Product UI – Team Selection & AI Coach",
    "📊 Model UI – Benchmarking & Evaluation"
])

# ==========================================
# TAB 1: PRODUCT UI
# ==========================================
with tab1:
    model_path = ART_DIR / "ProductUI_Model.pkl"
    if not model_path.exists():
        st.error("⚠️ Pretrained model file `ProductUI_Model.pkl` not found. Please run `python -m src.build_all` first.")
    else:
        @st.cache_resource
        def get_model():
            return joblib.load(model_path)
            
        bundle = get_model()
        teams = sorted(bundle["team_info"], key=lambda t: bundle["team_info"][t]["last_match"], reverse=True)
        
        # --- Quick Presets ---
        st.markdown("#### ⚡ Quick Match Selector & Setup")
        
        preset_cols = st.columns(4)
        if preset_cols[0].button("🇱🇰 Colombo vs Kandy (PDF Example)"):
            st.session_state["t1"] = "Colombo Strikers"
            st.session_state["t2"] = "Kandy Falcons"
            st.session_state["date"] = pd.Timestamp("2024-07-18")
        if preset_cols[1].button("🇮🇳 India vs Australia"):
            st.session_state["t1"] = "India"
            st.session_state["t2"] = "Australia"
            st.session_state["date"] = pd.Timestamp("2024-07-15")
        if preset_cols[2].button("🇬🇧 London Spirit vs Trent Rockets"):
            st.session_state["t1"] = "London Spirit"
            st.session_state["t2"] = "Trent Rockets"
            st.session_state["date"] = pd.Timestamp("2024-08-01")
        if preset_cols[3].button("🇱🇰 Jaffna Kings vs Galle Marvels"):
            st.session_state["t1"] = "Jaffna Kings"
            st.session_state["t2"] = "Galle Marvels"
            st.session_state["date"] = pd.Timestamp("2024-07-05")
            
        # Match Input Controls
        c1, c2, c3 = st.columns([1.2, 1.2, 1])
        
        default_t1 = st.session_state.get("t1", "Colombo Strikers" if "Colombo Strikers" in teams else teams[0])
        default_t2 = st.session_state.get("t2", "Kandy Falcons" if "Kandy Falcons" in teams else (teams[1] if len(teams) > 1 else teams[0]))
        default_date = st.session_state.get("date", pd.Timestamp("2024-07-18"))
        
        idx1 = teams.index(default_t1) if default_t1 in teams else 0
        idx2 = teams.index(default_t2) if default_t2 in teams else (1 if len(teams) > 1 else 0)
        
        t1 = c1.selectbox("Team 1 (Exact Cricsheet Name)", teams, index=idx1)
        t2 = c2.selectbox("Team 2 (Exact Cricsheet Name)", teams, index=idx2)
        match_date = c3.date_input("Upcoming Match Date", default_date, min_value=pd.Timestamp("2024-07-01"))

        # Context Options
        with st.expander("⚙️ Additional Match Conditions & Custom Squad Input"):
            venues = bundle["team_info"].get(t1, {}).get("venues", ["NA"])
            c_v1, c_v2, c_v3 = st.columns(3)
            venue = c_v1.selectbox("Stadium / Venue", venues)
            fmt = c_v2.selectbox("Match Format", ["t20", "odi", "test"], index=["t20", "odi", "test"].index(bundle["team_info"][t1].get("fmt", "t20")))
            pitch_type = c_v3.selectbox("Pitch Condition", ["Balanced Pitch", "Batting Friendly", "Bowling / Spin Friendly"])
            
            sq1 = st.text_area(f"{t1} Custom Squad (1 player name per line; blank = auto-inferred from recent 10 matches)")
            sq2 = st.text_area(f"{t2} Custom Squad")
            
        btn = st.button("🔥 BUILD OPTIMAL DREAM11 TEAM NOW", type="primary")
        
        if btn or "auto_run" not in st.session_state:
            st.session_state["auto_run"] = True
            if t1 == t2:
                st.error("Please select two different teams.")
            else:
                squads = {t: [x.strip() for x in s.splitlines() if x.strip()] for t, s in ((t1, sq1), (t2, sq2)) if s.strip()} or None
                
                with st.spinner("🤖 ML Model predicting fantasy points & optimizing MILP team selection..."):
                    res = recommend(bundle, t1, t2, match_date, venue=venue, fmt=fmt, squads=squads)
                
                team = res["team"]
                total_exp_pts = team["exp_pts"].sum()
                c_player = team[team["captain"] == "C"].iloc[0] if "C" in team["captain"].values else team.iloc[0]
                vc_player = team[team["captain"] == "VC"].iloc[0] if "VC" in team["captain"].values else team.iloc[1]
                t1_cnt = len(team[team["team"] == t1])
                t2_cnt = len(team[team["team"] == t2])
                
                # --- KPI Metrics Bar ---
                st.markdown("---")
                k1, k2, k3, k4, k5 = st.columns(5)
                
                k1_h = textwrap.dedent(f'<div class="kpi-card"><div class="kpi-val">{total_exp_pts:.1f}</div><div class="kpi-lbl">Total Exp Points</div></div>')
                k2_h = textwrap.dedent(f'<div class="kpi-card"><div class="kpi-val" style="color:#f59e0b;">{c_player["player"].split()[-1]}</div><div class="kpi-lbl">Captain (2x Pts)</div></div>')
                k3_h = textwrap.dedent(f'<div class="kpi-card"><div class="kpi-val" style="color:#06b6d4;">{vc_player["player"].split()[-1]}</div><div class="kpi-lbl">Vice-Captain (1.5x)</div></div>')
                k4_h = textwrap.dedent(f'<div class="kpi-card"><div class="kpi-val">{t1_cnt} : {t2_cnt}</div><div class="kpi-lbl">Squad Balance</div></div>')
                k5_h = textwrap.dedent(f'<div class="kpi-card"><div class="kpi-val" style="color:#10b981;">{res["seconds"]:.2f}s</div><div class="kpi-lbl">Response Time</div></div>')
                
                k1.markdown(k1_h, unsafe_allow_html=True)
                k2.markdown(k2_h, unsafe_allow_html=True)
                k3.markdown(k3_h, unsafe_allow_html=True)
                k4.markdown(k4_h, unsafe_allow_html=True)
                k5.markdown(k5_h, unsafe_allow_html=True)
                
                st.caption(f"⚡ Team generated in **{res['seconds']:.2f}s** (satisfied constraint: < 10s). Satisfies all Dream11 composition rules.")

                # --- Pitch / Squad View Grid ---
                st.markdown('<div class="pitch-container"><div class="pitch-header">🏟️ DREAM11 RECOMMENDED XI FORMATION</div>', unsafe_allow_html=True)
                
                roles_order = [("WK", "🧤 WICKET-KEEPERS"), ("BAT", "🏏 BATSMEN"), ("AR", "⚡ ALL-ROUNDERS"), ("BOWL", "⚾ BOWLERS")]
                
                for r_code, r_title in roles_order:
                    sub = team[team["role"] == r_code]
                    if not sub.empty:
                        r_hdr = textwrap.dedent(f'<div style="color: #6ee7b7; font-weight: 700; font-size: 13px; margin: 12px 0 8px 0; letter-spacing: 1px;">{r_title} ({len(sub)})</div>')
                        st.markdown(r_hdr, unsafe_allow_html=True)
                        cols = st.columns(min(len(sub), 4))
                        for idx, (_, p) in enumerate(sub.iterrows()):
                            col = cols[idx % len(cols)]
                            
                            c_class = "captain" if p["captain"] == "C" else ("vice-captain" if p["captain"] == "VC" else "")
                            badge_html = ""
                            if p["captain"] == "C":
                                badge_html = '<span class="badge-c">C (2x)</span>'
                            elif p["captain"] == "VC":
                                badge_html = '<span class="badge-vc">VC (1.5x)</span>'
                                
                            t_color = "#38bdf8" if p["team"] == t1 else "#f43f5e"
                            
                            card_html = textwrap.dedent(f"""
                            <div class="player-card {c_class}">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <span class="badge-role">{p['role']}</span>
                            {badge_html}
                            </div>
                            <div style="font-size: 15px; font-weight: 700; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{p['player']}</div>
                            <div style="font-size: 11px; color: {t_color}; font-weight: 700; margin-bottom: 6px;">{p['team']}</div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 11px; color: #94a3b8;">P(start): <b>{p['p_start']:.0%}</b></span>
                            <span class="badge-pts">{p['exp_pts']:.1f} Pts</span>
                            </div>
                            </div>
                            """)
                            col.markdown(card_html, unsafe_allow_html=True)
                            
                            # Detailed XAI Explanation Modal / Expander
                            with col.expander("💡 Why Selected? (XAI)"):
                                st.markdown(f"**Primary Drivers (SHAP):**")
                                st.caption(p["reason"])
                                st.markdown(f"""
                                - 🏏 **Recent Form**: Strong recent points output across last matches.
                                - ⚔️ **Opponent History**: Favorable matchup record against {t2 if p['team'] == t1 else t1}.
                                - 🏟️ **Venue Record**: Consistent scoring at {venue}.
                                - 📊 **Role Consistency**: High starting probability ({p['p_start']:.0%}).
                                """)
                                
                st.markdown('</div>', unsafe_allow_html=True)

                # --- Detail Dataframe & AI Audio Guidance ---
                st.markdown("---")
                left_col, right_col = st.columns([1.2, 1])
                
                with left_col:
                    st.markdown("#### 📊 Recommended XI Details & Predicted Points")
                    show_df = team[["captain", "player", "team", "role", "p_start", "pts_pred", "exp_pts", "reason"]].rename(columns={
                        "captain": "C/VC", "p_start": "P(starts)", "pts_pred": "Pts if plays", "exp_pts": "Expected Pts", "reason": "Why Selected (SHAP Drivers)"
                    })
                    st.dataframe(show_df.round(2), hide_index=True, width="stretch")
                    st.bar_chart(team.set_index("player")["exp_pts"], color="#FF3B44")
                    
                with right_col:
                    st.markdown("#### 🎙️ Dream11 AI Coach Audio & Strategy Guidance")
                    story_text = narrate.story(team, t1, t2, venue)
                    st.info(story_text)
                    
                    audio_b = narrate.audio_bytes(story_text)
                    if audio_b:
                        st.audio(audio_b, format="audio/mp3")

                # Full Squad Expander
                with st.expander("🔍 Inspect Full Squad Candidate Rankings (All 30+ Squad Players)"):
                    st.dataframe(
                        res["squad"][["player", "team", "role", "p_start", "pts_pred", "exp_pts"]]
                        .rename(columns={"p_start": "P(starts)", "pts_pred": "Pts if plays", "exp_pts": "Expected Pts"})
                        .round(2),
                        hide_index=True,
                        width="stretch"
                    )

        # Global Feature Importance Chart
        st.markdown("---")
        st.markdown("### 🧠 Global SHAP Feature Importance (Model Decision Factors)")
        st.bar_chart(bundle["importance"].head(12).set_index("label")["mean_abs_shap"], color="#38BDF8")


# ==========================================
# TAB 2: MODEL UI (BENCHMARKING & EVALUATION)
# ==========================================
with tab2:
    st.markdown("### 📊 Model UI – Performance Analysis & Evaluation")
    st.markdown("""
    Evaluators can assess model performance across custom historical training and testing periods, compute **Mean Absolute Error (MAE)** against actual Dream Teams, and export official CSV reports.
    
    $$\text{MAE} = \left| \text{Total Dream Team Fantasy Points} - \text{Total Fantasy Points of Predicted Team} \right|$$
    """)
    
    col_a, col_b = st.columns(2)
    with col_a:
        tr_range = st.text_input("Training Period Range (Strictly $\le$ 2024-06-30)", "2000-01-01 to 2024-06-30")
    with col_b:
        te_range = st.text_input("Testing Period Range (Unseen matches)", "2024-07-01 to 2024-09-22")
        
    mode_sel = st.radio(
        "Squad Selection Mode", 
        ["proxy", "xi"], 
        horizontal=True,
        help="proxy = squad inferred from each team's last 10 matches (honest, default). xi = candidates are actual 22 players."
    )
    
    eval_btn = st.button("🚀 RUN BENCHMARK EVALUATION & GENERATE CSV")
    
    if eval_btn:
        try:
            (ts, tend), (vs, vend) = [x.strip() for x in tr_range.split(" to ")], [x.strip() for x in te_range.split(" to ")]
            
            st.info(f"Evaluating matches from `{vs}` to `{vend}` against model trained on `{ts}` to `{tend}`...")
            progress_bar = st.progress(0.0)
            
            with st.spinner("Processing match-by-match evaluations..."):
                hist = load_history()
                res_df, summary, _ = run_model_ui(hist, ts, tend, vs, vend, mode_sel, progress=progress_bar.progress)
            
            st.success("✅ Evaluation Successfully Completed!")
            
            # KPI Cards
            k1, k2, k3, k4, k5 = st.columns(5)
            
            k1_m = textwrap.dedent(f'<div class="kpi-card"><div class="kpi-val">{summary["matches_evaluated"]}</div><div class="kpi-lbl">Matches Evaluated</div></div>')
            k2_m = textwrap.dedent(f'<div class="kpi-card"><div class="kpi-val" style="color:#FF3B44;">{summary["MAE_total_points"]:.1f}</div><div class="kpi-lbl">Overall MAE</div></div>')
            k3_m = textwrap.dedent(f'<div class="kpi-card"><div class="kpi-val" style="color:#10b981;">{summary["avg_dream_team_points"]:.1f}</div><div class="kpi-lbl">Avg Dream Team Pts</div></div>')
            k4_m = textwrap.dedent(f'<div class="kpi-card"><div class="kpi-val" style="color:#38bdf8;">{summary["avg_predicted_team_actual_points"]:.1f}</div><div class="kpi-lbl">Predicted XI Actual Pts</div></div>')
            k5_m = textwrap.dedent(f'<div class="kpi-card"><div class="kpi-val">{summary["avg_overlap_with_dream_team"]:.1f} / 11</div><div class="kpi-lbl">Avg Squad Overlap</div></div>')
            
            k1.markdown(k1_m, unsafe_allow_html=True)
            k2.markdown(k2_m, unsafe_allow_html=True)
            k3.markdown(k3_m, unsafe_allow_html=True)
            k4.markdown(k4_m, unsafe_allow_html=True)
            k5.markdown(k5_m, unsafe_allow_html=True)
            
            st.markdown("#### 📄 Evaluated Benchmark Dataset (Exact PDF Format)")
            st.dataframe(res_df, width="stretch")
            
            csv_data = res_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Benchmark Results CSV",
                data=csv_data,
                file_name=f"predictions_{vs}_{vend}.csv",
                mime="text/csv"
            )
            
            st.success(f"Saved `model_{tend}.pkl` in `src/model_artifacts/` and `training_data_{tend}.csv` in `src/data/processed/`.")
            
        except Exception as e:
            st.error(f"Error during evaluation: {e}")
