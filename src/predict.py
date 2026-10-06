import time
import numpy as np
import pandas as pd
from scipy.optimize import milp, LinearConstraint, Bounds
from . import features as F
from .config import TEAM_MAX_PER_ROLE


def select_best(df, score_col, k=11):
    """Best XI under Dream11 rules from the PDF: 11 players, 1-8 per role, >=1 per team (exact MILP)."""
    df = df.reset_index(drop=True)
    n = len(df)
    if n <= k:
        return df.sort_values(score_col, ascending=False)
    for min_role in (1, 0):  # relax role minimum only if infeasible (e.g. role inference found no keeper)
        A, lb, ub = [np.ones(n)], [k], [k]
        for r in F.ROLES:
            A.append((df["role"] == r).to_numpy().astype(float)); lb.append(min_role); ub.append(TEAM_MAX_PER_ROLE)
        teams = df["team"].unique()
        for t in teams:
            A.append((df["team"] == t).to_numpy().astype(float)); lb.append(1 if len(teams) > 1 else 0); ub.append(k)
        res = milp(-df[score_col].to_numpy(), constraints=LinearConstraint(np.array(A), lb, ub),
                   integrality=np.ones(n), bounds=Bounds(0, 1))
        if res.success:
            return df[res.x > 0.5].sort_values(score_col, ascending=False)
    return df.nlargest(k, score_col)


def score_candidates(bundle, cand, assume_starts=False):
    """cand: match_id,date,fmt,gender,venue,team,opp,pid,c3,c5,c10,since. Frozen at training cutoff."""
    c = cand.copy()
    c["mord"] = bundle["max_mord"] + 1
    d = F.attach(c, bundle["states"])
    X = F.to_X(d)
    d["pts_pred"] = bundle["pts_model"].predict(X)
    d["p_start"] = 1.0 if assume_starts else bundle["play_model"].predict_proba(X)[:, 1]
    d["exp_pts"] = d["pts_pred"] * d["p_start"]
    d["player"] = d["pid"].map(bundle["names"]).fillna(d["pid"])
    return d


def explain(bundle, scored, top=3):
    """Per-player SHAP reasons (LightGBM pred_contrib) -> readable sentences."""
    X = F.to_X(scored)
    contrib = bundle["pts_model"].booster_.predict(X, pred_contrib=True)
    names = F.FEATURES
    out = []
    for i in range(len(scored)):
        order = np.argsort(-np.abs(contrib[i, :-1]))[:top]
        parts = []
        for j in order:
            f = names[j]
            v = X.iloc[i, j]
            vs = f"{v:.1f}" if isinstance(v, (float, np.floating)) and not pd.isna(v) else str(v)
            parts.append(f"{F.LABELS[f]} ({vs}) {'adds' if contrib[i, j] > 0 else 'costs'} {abs(contrib[i, j]):.1f} pts")
        out.append("; ".join(parts))
    return out


def recommend(bundle, team1, team2, date, venue=None, fmt=None, squads=None):
    """Product-UI entry point. squads: optional {team: [player names]} (else squad proxy = recent starters)."""
    t0 = time.time()
    ti = bundle["team_info"]
    for t in (team1, team2):
        if t not in bundle["idx"]:
            raise ValueError(f"Unknown team '{t}' (use exact Cricsheet names)")
    venue = venue or (ti.get(team1, {}).get("venues") or ["NA"])[0]
    fmt = fmt or ti.get(team1, {}).get("fmt", "t20")
    gender = ti.get(team1, {}).get("gender", "male")
    tg = pd.DataFrame([dict(match_id="q", mord=bundle["max_mord"] + 1, date=pd.Timestamp(date), fmt=fmt, gender=gender,
                            venue=venue, team=a, opp=b) for a, b in ((team1, team2), (team2, team1))])
    if squads:
        inv = {v: k for k, v in bundle["names"].items()}
        rows = [dict(r, pid=inv.get(p, p)) for r in tg.to_dict("records") for p in squads.get(r["team"], [])]
        cand = pd.DataFrame(rows)
        cand[["c3", "c5", "c10", "since"]] = F.appearance_for_rows(cand, bundle["idx"], bundle["meta"]["window"])
    else:
        cand = F.make_candidates(tg, bundle["idx"], bundle["meta"]["window"])
    sc = score_candidates(bundle, cand)
    best = select_best(sc, "exp_pts").copy()
    best["reason"] = explain(bundle, best)
    best["rank"] = np.arange(1, len(best) + 1)
    best["captain"] = np.where(best["rank"] == 1, "C", np.where(best["rank"] == 2, "VC", ""))
    return dict(team=best, squad=sc.sort_values("exp_pts", ascending=False), venue=venue, fmt=fmt, seconds=time.time() - t0)
