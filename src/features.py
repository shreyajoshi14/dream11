"""Leak-free feature engineering.

Every feature for a (player, target match) pair is looked up from a *state table* with
merge_asof(allow_exact_matches=False) on a global match-order index `mord`, so only matches
strictly before the target match can ever contribute. States built from data <= cutoff
therefore cannot see anything after the cutoff.
"""
import bisect
from collections import defaultdict
import numpy as np
import pandas as pd

ROLES = ["BAT", "BOWL", "AR", "WK"]
FMTS = ["t20", "odi", "test"]
GENDERS = ["male", "female"]

NUM_FEATURES = [
    "n", "pts_mean", "pts_l3", "pts_l5", "pts_l10", "pts_ewm", "bat_pos_avg", "balls_l10", "runs_l10",
    "bowl_balls_l10", "wkts_l10", "bowl_frac", "did_bat_frac", "days_since",
    "n_fmt", "pts_fmt", "n_ven", "pts_ven", "n_opp", "pts_opp",
    "ven_runs", "team_runs_l10", "team_conc_l10", "opp_runs_l10", "opp_conc_l10",
    "c3", "c5", "c10", "since",
]
CAT_FEATURES = ["role", "fmt", "gender"]
FEATURES = NUM_FEATURES + CAT_FEATURES

LABELS = {
    "n": "career matches", "pts_mean": "career avg fantasy pts", "pts_l3": "avg pts (last 3)", "pts_l5": "avg pts (last 5)",
    "pts_l10": "avg pts (last 10)", "pts_ewm": "recent-weighted form", "bat_pos_avg": "usual batting position",
    "balls_l10": "balls faced (last 10)", "runs_l10": "runs (last 10)", "bowl_balls_l10": "balls bowled (last 10)",
    "wkts_l10": "wickets (last 10)", "bowl_frac": "share of matches bowling", "did_bat_frac": "share of matches batting",
    "days_since": "days since last match", "n_fmt": "matches in this format", "pts_fmt": "avg pts in this format",
    "n_ven": "matches at this venue", "pts_ven": "avg pts at this venue", "n_opp": "matches vs this opponent",
    "pts_opp": "avg pts vs this opponent", "ven_runs": "venue scoring level", "team_runs_l10": "team batting form",
    "team_conc_l10": "team bowling form", "opp_runs_l10": "opposition batting form", "opp_conc_l10": "opposition bowling weakness",
    "c3": "starts in team's last 3", "c5": "starts in team's last 5", "c10": "starts in team's last 10",
    "since": "matches since last start", "role": "role", "fmt": "format", "gender": "competition type",
}


def add_mord(df):
    m = (df[["match_id", "date"]].drop_duplicates("match_id").sort_values(["date", "match_id"]).reset_index(drop=True))
    m["mord"] = np.arange(len(m))
    out = df.drop(columns=["mord"], errors="ignore").merge(m, on=["match_id", "date"], how="left")
    return out.sort_values(["mord"], kind="stable").reset_index(drop=True)


def _roll(h, col, k, by="pid"):
    r = h.groupby(by)[col].rolling(k, min_periods=1).mean()
    return r.reset_index(level=0, drop=True)


def _cum_state(h, by, prefix):
    g = h.groupby(by)
    out = h[["mord"] + by].copy()
    out[f"n_{prefix}"] = g.cumcount() + 1
    out[f"pts_{prefix}"] = g["fantasy_points"].cumsum() / out[f"n_{prefix}"]
    return out


def derive_role(n, stump_rate, stumps, bowl_frac, bat_pos):
    return np.select(
        [(stumps >= 2) & (stump_rate >= 0.06), (bowl_frac >= 0.4) & (bat_pos > 6.5), (bowl_frac >= 0.35) & (bat_pos <= 6.5)],
        ["WK", "BOWL", "AR"], default="BAT")


def build_states(hist):
    """State tables = cumulative stats AFTER each match."""
    h = hist.sort_values("mord", kind="stable").reset_index(drop=True).copy()
    h["bowled"] = (h.bowl_balls > 0).astype(float)
    h["did_bat"] = h["did_bat"].astype(float)
    g = h.groupby("pid")
    st = h[["pid", "mord", "date"]].rename(columns={"date": "last_date"})
    n = g.cumcount() + 1
    st["n"] = n
    st["pts_mean"] = g["fantasy_points"].cumsum() / n
    for k in (3, 5, 10):
        st[f"pts_l{k}"] = _roll(h, "fantasy_points", k)
    st["pts_ewm"] = g["fantasy_points"].ewm(alpha=0.25).mean().reset_index(level=0, drop=True)
    st["bat_pos_avg"] = g["bat_pos"].cumsum() / n
    st["balls_l10"] = _roll(h, "balls", 10)
    st["runs_l10"] = _roll(h, "runs", 10)
    st["bowl_balls_l10"] = _roll(h, "bowl_balls", 10)
    st["wkts_l10"] = _roll(h, "wkts", 10)
    st["bowl_frac"] = g["bowled"].cumsum() / n
    st["did_bat_frac"] = g["did_bat"].cumsum() / n
    stumps = g["stumps"].cumsum()
    st["role_state"] = derive_role(n, stumps / n, stumps, st.bowl_frac, st.bat_pos_avg)

    fmt_s = _cum_state(h, ["pid", "fmt"], "fmt")
    ven_s = _cum_state(h, ["pid", "venue"], "ven")
    opp_s = _cum_state(h, ["pid", "opp"], "opp")

    tm = h.drop_duplicates(["match_id", "team"])[["mord", "team", "venue", "fmt", "team_runs", "opp_runs"]].reset_index(drop=True)
    team_s = tm[["mord", "team"]].copy()
    team_s["team_runs_l10"] = _roll(tm, "team_runs", 10, by="team")
    team_s["team_conc_l10"] = _roll(tm, "opp_runs", 10, by="team")
    venue_s = tm[["mord", "venue", "fmt"]].copy()
    gv = tm.groupby(["venue", "fmt"])
    venue_s["ven_runs"] = gv["team_runs"].cumsum() / (gv.cumcount() + 1)
    return dict(gen=st, fmt=fmt_s, ven=ven_s, opp=opp_s, team=team_s, venue=venue_s)


def compress_states(states):
    """Keep only the latest row per key -> tiny tables, valid for any future target match."""
    keys = dict(gen=["pid"], fmt=["pid", "fmt"], ven=["pid", "venue"], opp=["pid", "opp"], team=["team"], venue=["venue", "fmt"])
    return {k: v.sort_values("mord").drop_duplicates(keys[k], keep="last").reset_index(drop=True) for k, v in states.items()}


def _asof(q, s, by, rename=None):
    s = s.copy()
    if rename:
        s = s.rename(columns=rename)
        by = [rename.get(b, b) for b in by]
    s = s.rename(columns={"mord": "_m"}).sort_values("_m", kind="stable")
    out = pd.merge_asof(q, s, left_on="mord", right_on="_m", by=by, allow_exact_matches=False)
    return out.drop(columns="_m")


def attach(q, states):
    """q needs: pid, team, opp, venue, fmt, gender, date, mord (+ appearance feats c3,c5,c10,since)."""
    q = q.sort_values("mord", kind="stable").reset_index(drop=True)
    q = _asof(q, states["gen"], ["pid"])
    q["days_since"] = (q["date"] - q["last_date"]).dt.days
    q = q.drop(columns="last_date")
    q = _asof(q, states["fmt"], ["pid", "fmt"])
    q = _asof(q, states["ven"], ["pid", "venue"])
    q = _asof(q, states["opp"], ["pid", "opp"])
    q = _asof(q, states["team"], ["team"])
    q = _asof(q, states["team"], ["team"], rename={"team": "opp", "team_runs_l10": "opp_runs_l10", "team_conc_l10": "opp_conc_l10"})
    q = _asof(q, states["venue"], ["venue", "fmt"])
    q["role"] = q["role_state"].fillna("BAT")
    return q


def to_X(df):
    X = df[FEATURES].copy()
    X["role"] = pd.Categorical(X["role"], categories=ROLES)
    X["fmt"] = pd.Categorical(X["fmt"], categories=FMTS)
    X["gender"] = pd.Categorical(X["gender"], categories=GENDERS)
    for c in NUM_FEATURES:
        X[c] = X[c].astype(float)
    return X


# ---------------------------------------------------------------- squad proxy / appearance
def build_team_index(hist):
    """team -> (sorted mords, list of sets of pids who started)."""
    tm = hist.groupby(["team", "mord"])["pid"].agg(set).reset_index().sort_values(["team", "mord"])
    idx = {}
    for team, g in tm.groupby("team"):
        idx[team] = (g["mord"].to_numpy(), list(g["pid"]))
    return idx


def _counts(sets_window):
    """sets_window: list of sets ordered oldest->newest. returns pid -> (c3,c5,c10,since)."""
    res = {}
    L = len(sets_window)
    for back, s in enumerate(reversed(sets_window)):  # back=0 is the most recent
        for p in s:
            c = res.setdefault(p, [0, 0, 0, back])
            c[2] += 1
            if back < 5:
                c[1] += 1
            if back < 3:
                c[0] += 1
    return res


def appearance_for_rows(df, idx, window=10):
    out = np.zeros((len(df), 4))
    for i, (team, mord, pid) in enumerate(zip(df["team"], df["mord"], df["pid"])):
        mords, sets = idx.get(team, (np.array([]), []))
        k = bisect.bisect_left(mords, mord)
        c = _counts(sets[max(0, k - window):k]).get(pid)
        out[i] = c if c else (0, 0, 0, window)
    return pd.DataFrame(out, columns=["c3", "c5", "c10", "since"], index=df.index)


def make_candidates(targets, idx, window=10):
    """targets: rows (match_id, mord, date, fmt, gender, venue, team, opp). Squad proxy = players used
    by the team in its previous `window` matches."""
    rows = []
    for t in targets.itertuples(index=False):
        mords, sets = idx.get(t.team, (np.array([]), []))
        k = bisect.bisect_left(mords, t.mord)
        for pid, (c3, c5, c10, since) in _counts(sets[max(0, k - window):k]).items():
            rows.append((t.match_id, t.mord, t.date, t.fmt, t.gender, t.venue, t.team, t.opp, pid, c3, c5, c10, since))
    return pd.DataFrame(rows, columns=["match_id", "mord", "date", "fmt", "gender", "venue", "team", "opp", "pid",
                                       "c3", "c5", "c10", "since"])
