"""Model UI backend: train on [train_start, train_end], predict every match in [test_start, test_end],
write the CSV in the format from the problem statement, save model + training data."""
import argparse
import joblib
import numpy as np
import pandas as pd
from . import features as F
from .config import PROC_DIR, ART_DIR, RAW_DIR
from .train import train_models
from .predict import score_candidates, select_best
from .fantasy_points import build_player_match_table


def load_history(csv=PROC_DIR / "player_match.csv", raw_dir=RAW_DIR, rebuild=False):
    if csv.exists() and not rebuild:
        df = pd.read_csv(csv, parse_dates=["date"])
    else:
        df = build_player_match_table(raw_dir, csv)
    return F.add_mord(df)


def run_model_ui(hist, train_start, train_end, test_start, test_end, squad_mode="proxy", progress=None, save=True):
    """squad_mode: 'proxy' = squad inferred from the team's last 10 matches (honest, default);
                   'xi'    = candidates are the 22 who actually played (upper bound, P(start)=1)."""
    tr = hist[(hist.date >= pd.Timestamp(train_start)) & (hist.date <= pd.Timestamp(train_end))]
    if tr.empty:
        raise ValueError("empty training period")
    bundle = train_models(tr, save_training_csv=(PROC_DIR / f"training_data_{train_end}.csv") if save else None)
    if save:
        joblib.dump(bundle, ART_DIR / f"model_{train_end}.pkl", compress=3)
    te = hist[(hist.date >= pd.Timestamp(test_start)) & (hist.date <= pd.Timestamp(test_end))]
    meta_cols = ["match_id", "date", "fmt", "gender", "venue", "team", "opp"]
    matches = te.drop_duplicates("match_id")["match_id"].tolist()

    # actual players (roles + actual points) scored with the same frozen model/state
    act_c = te[meta_cols + ["pid"]].copy()
    act_c[["c3", "c5", "c10", "since"]] = F.appearance_for_rows(act_c.assign(mord=bundle["max_mord"] + 1), bundle["idx"])
    act = score_candidates(bundle, act_c, assume_starts=True).merge(
        te[["match_id", "pid", "fantasy_points"]], on=["match_id", "pid"])
    act_by_match = {m: g for m, g in act.groupby("match_id")}

    if squad_mode == "proxy":
        tg = te.drop_duplicates(["match_id", "team"])[meta_cols].assign(mord=bundle["max_mord"] + 1)
        cand_all = F.make_candidates(tg, bundle["idx"], bundle["meta"]["window"])
        sc_all = score_candidates(bundle, cand_all)
    else:
        sc_all = act.copy()
    sc_by_match = {m: g for m, g in sc_all.groupby("match_id")}

    rows, per_player = [], []
    for i, m in enumerate(matches):
        a = act_by_match.get(m)
        s = sc_by_match.get(m)
        if a is None or s is None or s["team"].nunique() < 2 or len(s) < 11:
            continue
        pred = select_best(s, "exp_pts")
        dream = select_best(a, "fantasy_points")
        actual_of_pred = pred["pid"].map(a.set_index("pid")["fantasy_points"]).fillna(0.0)  # didn't play => 0 pts
        pred = pred.assign(actual=actual_of_pred.to_numpy())
        meta = te[te.match_id == m].iloc[0]
        t1, t2 = sorted(te[te.match_id == m]["team"].unique())
        r = {"Match Date": meta["date"].date(), "Team 1": t1, "Team 2": t2}
        for k, (_, p) in enumerate(pred.iterrows(), 1):
            r[f"Predicted Player {k}"] = p["player"]; r[f"Predicted Player {k} Points"] = round(p["exp_pts"], 1)
        for k, (_, p) in enumerate(dream.iterrows(), 1):
            r[f"Dream Team Player {k}"] = p["player"]; r[f"Dream Team Player {k} Points"] = p["fantasy_points"]
        r["Total Points Predicted"] = round(float(pred["actual"].sum()), 1)   # actual pts scored by the predicted XI
        r["Total Dream Team Points"] = float(dream["fantasy_points"].sum())
        r["Total points MAE"] = round(abs(r["Total Dream Team Points"] - r["Total Points Predicted"]), 1)
        r["Sum of model-predicted points"] = round(float(pred["exp_pts"].sum()), 1)
        r["Overlap with Dream Team"] = len(set(pred["pid"]) & set(dream["pid"]))
        base = select_best(s.assign(pts_mean=s["pts_mean"].fillna(0) * s["p_start"]), "pts_mean")
        r["_baseline_total"] = float(base["pid"].map(a.set_index("pid")["fantasy_points"]).fillna(0.0).sum())
        rows.append(r)
        pp = s.drop(columns=["fantasy_points"], errors="ignore").merge(a[["pid", "fantasy_points"]], on="pid", how="inner")
        per_player.append(pp[["exp_pts", "pts_pred", "fantasy_points"]])
        if progress and i % 50 == 0:
            progress(i / max(1, len(matches)))
    res = pd.DataFrame(rows)
    base_mae = float((res["Total Dream Team Points"] - res.pop("_baseline_total")).abs().mean()) if len(res) else np.nan
    pp = pd.concat(per_player) if per_player else pd.DataFrame(columns=["exp_pts", "pts_pred", "fantasy_points"])
    summary = dict(
        matches_evaluated=len(res), baseline_MAE_career_avg_xi=base_mae,
        MAE_total_points=float(res["Total points MAE"].mean()) if len(res) else np.nan,
        median_MAE=float(res["Total points MAE"].median()) if len(res) else np.nan,
        avg_overlap_with_dream_team=float(res["Overlap with Dream Team"].mean()) if len(res) else np.nan,
        avg_dream_team_points=float(res["Total Dream Team Points"].mean()) if len(res) else np.nan,
        avg_predicted_team_actual_points=float(res["Total Points Predicted"].mean()) if len(res) else np.nan,
        player_level_MAE_given_played=float((pp["pts_pred"] - pp["fantasy_points"]).abs().mean()) if len(pp) else np.nan,
        player_level_corr=float(pp["pts_pred"].corr(pp["fantasy_points"])) if len(pp) > 2 else np.nan,
        squad_mode=squad_mode, train=f"{train_start}..{train_end}", test=f"{test_start}..{test_end}")
    if save:
        res.to_csv(PROC_DIR / f"predictions_{test_start}_{test_end}.csv", index=False)
    return res, summary, bundle


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--train-start", default="2000-01-01"); ap.add_argument("--train-end", default="2024-06-30")
    ap.add_argument("--test-start", default="2024-07-01"); ap.add_argument("--test-end", default="2024-09-22")
    ap.add_argument("--squad-mode", default="proxy", choices=["proxy", "xi"])
    a = ap.parse_args()
    res, summ, _ = run_model_ui(load_history(), a.train_start, a.train_end, a.test_start, a.test_end, a.squad_mode)
    print(summ)
