"""streamlit run app.py"""
import joblib, pandas as pd, streamlit as st
from src.config import ART_DIR, TRAIN_CUTOFF
from src.predict import recommend
from src.model_ui import load_history, run_model_ui
import narrate

st.set_page_config(page_title="Dream11 Team Builder", page_icon="🏏", layout="wide")
tab1, tab2 = st.tabs(["🏏 Product UI – Team Selection", "📊 Model UI – Evaluation"])

with tab1:
    path = ART_DIR / "ProductUI_Model.pkl"
    if not path.exists():
        st.error("Run `python -m src.build_all` first to create model_artifacts/ProductUI_Model.pkl")
    else:
        @st.cache_resource
        def get_bundle():
            return joblib.load(path)
        b = get_bundle()
        teams = sorted(b["team_info"], key=lambda t: b["team_info"][t]["last_match"], reverse=True)
        c1, c2, c3 = st.columns(3)
        t1 = c1.selectbox("Team 1 (exact Cricsheet name)", teams, index=0)
        t2 = c2.selectbox("Team 2", teams, index=1)
        date = c3.date_input("Match date", pd.Timestamp("2024-07-18"), min_value=pd.Timestamp("2024-07-01"))
        with st.expander("Optional: venue, format, custom squads"):
            venues = b["team_info"][t1]["venues"]
            venue = st.selectbox("Venue", venues)
            fmt = st.selectbox("Format", ["t20", "odi", "test"], index=["t20", "odi", "test"].index(b["team_info"][t1]["fmt"]))
            sq1 = st.text_area(f"{t1} squad (one name per line; blank = auto from recent matches)")
            sq2 = st.text_area(f"{t2} squad")
        if st.button("Build my Dream Team", type="primary") and t1 != t2:
            squads = {t: [x.strip() for x in s.splitlines() if x.strip()] for t, s in ((t1, sq1), (t2, sq2)) if s.strip()} or None
            r = recommend(b, t1, t2, date, venue=venue, fmt=fmt, squads=squads)
            team = r["team"]
            st.caption(f"Generated in {r['seconds']:.2f}s · model trained on data up to {b['meta']['train_end']} (cutoff {TRAIN_CUTOFF})")
            st.subheader("Your 11")
            show = team[["captain", "player", "team", "role", "p_start", "pts_pred", "exp_pts", "reason"]].rename(columns={
                "captain": "C/VC", "p_start": "P(starts)", "pts_pred": "Pts if plays", "exp_pts": "Expected pts", "reason": "Why (top SHAP drivers)"})
            st.dataframe(show.round(2), hide_index=True, width="stretch")
            st.bar_chart(team.set_index("player")["exp_pts"])
            txt = narrate.story(team, t1, t2, venue)
            st.subheader("🎙️ Guided walkthrough")
            st.write(txt)
            a = narrate.audio_bytes(txt)
            if a: st.audio(a, format="audio/mp3")
            else: st.caption("Audio needs internet (gTTS); text walkthrough shown above.")
            with st.expander("Whole squad ranking"):
                st.dataframe(r["squad"][["player", "team", "role", "p_start", "pts_pred", "exp_pts"]].round(2), hide_index=True)
        st.subheader("What drives the model (global SHAP importance)")
        st.bar_chart(b["importance"].head(15).set_index("label")["mean_abs_shap"])

with tab2:
    st.write("Train on a period, predict a test period, export the CSV described in the problem statement.")
    a, b_ = st.columns(2)
    tr = a.text_input("Training period", "2000-01-01 to 2024-05-30")
    te = b_.text_input("Testing period", "2024-08-01 to 2024-09-22")
    mode = st.radio("Squad assumption", ["proxy", "xi"], horizontal=True,
                    help="proxy = squad inferred from each team's last 10 matches (honest). xi = the 22 who actually played (upper bound).")
    if st.button("Train + evaluate"):
        (ts, tend), (vs, vend) = [x.split(" to ") for x in (tr, te)]
        bar = st.progress(0.0)
        res, summ, _ = run_model_ui(load_history(), ts, tend, vs, vend, mode, progress=bar.progress)
        st.json(summ)
        st.dataframe(res, width="stretch")
        st.download_button("Download CSV", res.to_csv(index=False), f"predictions_{vs}_{vend}.csv")
        st.success(f"Saved model_{tend}.pkl and training_data_{tend}.csv")
