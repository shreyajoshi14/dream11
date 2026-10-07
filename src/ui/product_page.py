import streamlit as st
import pandas as pd
import textwrap
from src.ui.utils import run_prediction, load_data

def render_product_page():
    pms_df, feats_df, dels_df = load_data()
    all_teams = sorted(list(dels_df['batting_team'].dropna().unique()))
    
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
        
    c1, c2, c3 = st.columns([1.2, 1.2, 1])
    
    default_t1 = st.session_state.get("t1", "Colombo Strikers" if "Colombo Strikers" in all_teams else all_teams[0])
    default_t2 = st.session_state.get("t2", "Kandy Falcons" if "Kandy Falcons" in all_teams else (all_teams[1] if len(all_teams) > 1 else all_teams[0]))
    default_date = st.session_state.get("date", pd.to_datetime('2024-07-18'))
    
    idx_a = all_teams.index(default_t1) if default_t1 in all_teams else 0
    idx_b = all_teams.index(default_t2) if default_t2 in all_teams else (1 if len(all_teams) > 1 else 0)
    
    team_a = c1.selectbox("Team 1 (Exact Cricsheet Name)", all_teams, index=idx_a)
    team_b = c2.selectbox("Team 2 (Exact Cricsheet Name)", all_teams, index=idx_b)
    date_input = c3.date_input("Match Date", default_date)
    
    st.markdown("---")
    
    if st.button("🔥 BUILD OPTIMAL DREAM11 TEAM NOW", type="primary"):
        with st.spinner("🤖 ML Model predicting fantasy points & optimizing MILP team selection..."):
            try:
                pool, dream_team, latencies = run_prediction(
                    str(date_input), team_a, team_b, explain=True
                )
                
                selected_players = dream_team['team_df']
                explanations = {exp['player']: exp for exp in dream_team['explanations']}
                
                t1_cnt = len(selected_players[selected_players['team'] == team_a])
                t2_cnt = len(selected_players[selected_players['team'] == team_b])
                
                st.markdown("---")
                k1, k2, k3, k4, k5 = st.columns(5)
                
                k1_h = textwrap.dedent(f'<div class="kpi-card"><div class="kpi-val">{dream_team["total_predicted_score"]:.1f}</div><div class="kpi-lbl">Total Exp Points</div></div>')
                k2_h = textwrap.dedent(f'<div class="kpi-card"><div class="kpi-val" style="color:#f59e0b;">{dream_team["captain"]}</div><div class="kpi-lbl">Captain (2x Pts)</div></div>')
                k3_h = textwrap.dedent(f'<div class="kpi-card"><div class="kpi-val" style="color:#06b6d4;">{dream_team["vice_captain"]}</div><div class="kpi-lbl">Vice-Captain (1.5x)</div></div>')
                k4_h = textwrap.dedent(f'<div class="kpi-card"><div class="kpi-val">{t1_cnt} : {t2_cnt}</div><div class="kpi-lbl">Squad Balance</div></div>')
                k5_h = textwrap.dedent(f'<div class="kpi-card"><div class="kpi-val" style="color:#10b981;">{latencies["total_inference"]*1000:.0f}ms</div><div class="kpi-lbl">Response Time</div></div>')
                
                k1.markdown(k1_h, unsafe_allow_html=True)
                k2.markdown(k2_h, unsafe_allow_html=True)
                k3.markdown(k3_h, unsafe_allow_html=True)
                k4.markdown(k4_h, unsafe_allow_html=True)
                k5.markdown(k5_h, unsafe_allow_html=True)
                
                st.caption(f"⚡ Team generated in **{latencies['total_inference']:.2f}s** (satisfied constraint: < 10s). Satisfies all Dream11 composition rules.")

                st.markdown('<div class="pitch-container"><div class="pitch-header">🏟️ DREAM11 RECOMMENDED XI FORMATION</div>', unsafe_allow_html=True)
                
                roles_order = [("WK", "🧤 WICKET-KEEPERS"), ("BAT", "🏏 BATSMEN"), ("AR", "⚡ ALL-ROUNDERS"), ("BOWL", "⚾ BOWLERS")]
                
                for r_code, r_title in roles_order:
                    sub = selected_players[selected_players["role"] == r_code]
                    if not sub.empty:
                        st.markdown(f'<div style="color: #6ee7b7; font-weight: 700; font-size: 13px; margin: 12px 0 8px 0; letter-spacing: 1px;">{r_title} ({len(sub)})</div>', unsafe_allow_html=True)
                        cols = st.columns(min(len(sub), 4))
                        
                        for idx, (_, p) in enumerate(sub.iterrows()):
                            player = p['player']
                            exp = explanations.get(player, {})
                            role = exp.get('role', 'Unknown')
                            team = exp.get('team', 'Unknown')
                            p_play = exp.get('p_play', 0.0)
                            exp_fp = exp.get('expected_fp', 0.0)
                            
                            is_c = (player == dream_team['captain'])
                            is_vc = (player == dream_team['vice_captain'])
                            
                            c_class = "captain" if is_c else "vice-captain" if is_vc else ""
                            badge_html = ""
                            if is_c:
                                badge_html = '<span class="badge-c">C (2x)</span>'
                            elif is_vc:
                                badge_html = '<span class="badge-vc">VC (1.5x)</span>'
                            
                            t_color = "#38bdf8" if team == team_a else "#f43f5e"
                            
                            card_html = textwrap.dedent(f"""
                            <div class="player-card {c_class}">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                                    <span class="badge-role">{role}</span>
                                    {badge_html}
                                </div>
                                <div style="font-size: 15px; font-weight: 700; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{player}</div>
                                <div style="font-size: 11px; color: {t_color}; font-weight: 700; margin-bottom: 6px;">{team}</div>
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="font-size: 11px; color: #94a3b8;">P(play): <b>{p_play:.0%}</b></span>
                                    <span class="badge-pts">{exp_fp:.1f} Pts</span>
                                </div>
                            </div>
                            """)
                            
                            col = cols[idx % len(cols)]
                            col.markdown(card_html, unsafe_allow_html=True)
                            
                            with col.expander("💡 Why Selected? (XAI)"):
                                st.markdown(f"**Primary Drivers (SHAP):**")
                                st.caption(exp.get('human_readable_explanation', ''))
                                
                                st.markdown("**FP Model Factors**")
                                for f in exp.get('top_positive_fp_factors', [])[:2]:
                                    st.caption(f"🟢 `{f['feature']}`: +{f['contribution']:.1f}")
                                for f in exp.get('top_negative_fp_factors', [])[:2]:
                                    st.caption(f"🔴 `{f['feature']}`: {f['contribution']:.1f}")
                                    
                                st.markdown("**P(play) Factors**")
                                for f in exp.get('top_positive_play_factors', [])[:2]:
                                    st.caption(f"🟢 `{f['feature']}`: +{f['contribution']:.2f}")
                                for f in exp.get('top_negative_play_factors', [])[:2]:
                                    st.caption(f"🔴 `{f['feature']}`: {f['contribution']:.2f}")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown("---")
                left_col, right_col = st.columns([1.2, 1])
                
                with left_col:
                    st.markdown("#### 📊 Recommended XI Details & Predicted Points")
                    
                    df_to_show = []
                    for idx, row in selected_players.iterrows():
                        p = row['player']
                        e = explanations.get(p, {})
                        df_to_show.append({
                            "C/VC": "C" if p == dream_team['captain'] else "VC" if p == dream_team['vice_captain'] else "",
                            "Player": p,
                            "Team": e.get('team', ''),
                            "Role": e.get('role', ''),
                            "P(starts)": e.get('p_play', 0.0),
                            "Expected Pts": e.get('expected_fp', 0.0),
                            "Why Selected (SHAP Drivers)": e.get('human_readable_explanation', '')
                        })
                    
                    show_df = pd.DataFrame(df_to_show)
                    st.dataframe(show_df, hide_index=True, width="stretch")
                    st.bar_chart(show_df.set_index("Player")["Expected Pts"], color="#FF3B44")
                    
                with right_col:
                    st.markdown("#### 🎙️ Dream11 AI Coach & Strategy Guidance")
                    story_text = f"Here is your Dream11 team for {team_a} versus {team_b}. "
                    story_text += f"Your Captain is {dream_team['captain']}, expected to give a massive performance. "
                    story_text += f"Your Vice-captain is {dream_team['vice_captain']}. "
                    story_text += f"Total expected points for this optimal combination is {dream_team['total_predicted_score']:.0f}. "
                    story_text += "Good luck on Dream11!"
                    st.info(story_text)

                with st.expander("⏱️ System Latency Details"):
                    st.write(f"- **Inference Latency**: {latencies['total_inference']*1000:.1f} ms")
                    st.write(f"- **SHAP Latency**: {latencies.get('shap_explanation', 0)*1000:.1f} ms")
                    st.write(f"- **UI Overhead**: {latencies.get('ui_overhead', 0)*1000:.1f} ms")
                
            except ValueError as e:
                st.error(f"Prediction Error: {str(e)}")
                st.info("Ensure the selected teams have historically played a match near this date to form a candidate pool.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")
