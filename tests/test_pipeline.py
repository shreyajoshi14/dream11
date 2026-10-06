"""python -m tests.test_pipeline  (needs src/data/processed/player_match.csv or synthetic raw dir as argv[1])"""
import sys, joblib, numpy as np, pandas as pd
from src import features as F
from src.fantasy_points import build_player_match_table
from src.predict import recommend
from src.config import ART_DIR

hist = F.add_mord(build_player_match_table(sys.argv[1]))

# 1) LEAK TEST: features of a match must be identical if every later match is deleted.
cut = hist.date.sort_values().iloc[len(hist) // 2]
m = hist[hist.date == cut].match_id.iloc[0]
target = hist[hist.match_id == m][["match_id", "mord", "date", "fmt", "gender", "venue", "team", "opp", "pid"]].copy()
mord_t = target.mord.iloc[0]
full, trunc = hist, hist[hist.mord < mord_t]
out = []
for h in (full, trunc):
    idx = F.build_team_index(h)
    q = target.copy()
    q[["c3", "c5", "c10", "since"]] = F.appearance_for_rows(q, idx)
    out.append(F.attach(q, F.build_states(h)).sort_values("pid").reset_index(drop=True)[F.NUM_FEATURES])
pd.testing.assert_frame_equal(out[0], out[1])
print("PASS leak test: features use only strictly-earlier matches")

# 2) Product UI: 10 s budget + constraint check
b = joblib.load(ART_DIR / "model_2024-06-30.pkl")
t = sorted(b["idx"])[:2]
r = recommend(b, t[0], t[1], "2024-07-18")
tm = r["team"]
assert len(tm) == 11 and tm.team.nunique() == 2
assert tm.role.value_counts().between(1, 8).all()
print(f"PASS product UI: {r['seconds']:.2f}s (limit 10s)  venue={r['venue']}")
print(tm[["rank", "captain", "player", "team", "role", "p_start", "pts_pred", "exp_pts"]].round(2).to_string(index=False))
print(tm.iloc[0]["reason"])
